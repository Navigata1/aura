#!/usr/bin/env python3
"""Regenerate contracts/registry/components.v1.json from the evidence register. Standard library only.

Inputs: docs/research/evidence-register.json (the verified research) and scripts/registry/register_overlay.json
(the studio's decisions: lane narrowing, release-blocker classes, obligations, v1-path flags and supplement rows, each
citing its ADR). The output is deterministic (sorted keys, two-space indent, components sorted by id), so
scripts/spec/validate.py can require that it regenerates byte-identically (ADR-0011 rule 1).

    python3 scripts/registry/sync.py           # rewrite components.v1.json
    python3 scripts/registry/sync.py --check   # exit 1 if the committed file differs
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "docs/research/evidence-register.json"
OVERLAY = ROOT / "scripts/registry/register_overlay.json"
OUTPUT = ROOT / "contracts/registry/components.v1.json"
PRODUCT_NAME = json.loads((ROOT / "contracts/product.json").read_text(encoding="utf-8"))["productName"]

LANE_ORDER = ("individual", "llc", "research")
BOUNDARY_CLASSES = {"non_commercial_weights", "non_commercial_by_author", "research_or_academic", "unknown_license",
                    "contested", "copyleft"}
COPYLEFT_CODE = re.compile(r"\b(A?GPL|LGPL)")
URL = re.compile(r"^https://[^\s]+$")


class SyncError(Exception):
    pass


def _lanes(row: dict, overlay: dict) -> list[str]:
    lanes = set(row.get("operator_lanes") or [])
    unknown = lanes - set(LANE_ORDER)
    if unknown:
        raise SyncError(f"{row['id']}: unknown lanes {sorted(unknown)}")
    if "individual" in lanes:
        lanes.add("research")
    override = overlay["allowed_lanes_override"].get(row["id"])
    if override is not None:
        lanes = set(override["lanes"])
    return [lane for lane in LANE_ORDER if lane in lanes]


def _sources(row: dict) -> list[str]:
    out = []
    for source in row.get("primary_sources") or []:
        token = source.split()[0] if source.split() else ""
        if URL.match(token) and token not in out:
            out.append(token)
    return out


def _neutral(value):
    """ADR-0035: the product name lives only in contracts/product.json, so text copied from the research register
    into shipped registry data (and from there into stored license chains) uses a neutral wording."""
    if isinstance(value, str):
        return value.replace(PRODUCT_NAME + "'s", "the studio's").replace(PRODUCT_NAME, "the studio")
    if isinstance(value, list):
        return [_neutral(v) for v in value]
    return value


def _component(row: dict, overlay: dict, blockers: dict[str, list[str]], v1_ids: set[str]) -> dict:
    classes = sorted(blockers.get(row["id"], []))
    code = row["code_license"]
    boundary = bool(set(classes) & BOUNDARY_CLASSES) or bool(COPYLEFT_CODE.search(code))
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "role": row["role"],
        "code_license": code,
        "weights_license": row["weights_license"],
        "output_terms": row["output_terms"],
        "gated": row.get("gated"),
        "verdict": row["verdict"],
        "verdict_condition": row.get("verdict_condition"),
        "allowed_lanes": _lanes(row, overlay),
        "redistribution_blocker": row["redistribution_blocker"],
        "release_blockers": classes,
        "obligations": sorted(overlay["obligations"].get(row["id"], [])),
        "process_boundary_required": boundary,
        "verification_status": row["evidence_status"],
        "v1_path": row["id"] in v1_ids,
        "test_only": False,
        "primary_sources": _sources(row),
        "notes": row.get("notes") or "",
    }


def generate(register_path: Path = REGISTER, overlay_path: Path = OVERLAY) -> bytes:
    register_bytes = register_path.read_bytes()
    overlay_bytes = overlay_path.read_bytes()
    register = json.loads(register_bytes)
    overlay = json.loads(overlay_bytes)
    rows = list(register["components"]) + list(overlay["supplement"]["rows"])
    ids = [row["id"] for row in rows]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise SyncError(f"duplicate component ids: {duplicates}")
    known = set(ids)
    blockers: dict[str, list[str]] = {}
    for cls, members in overlay["release_blockers"].items():
        if cls == "source":
            continue
        for member in members:
            if member not in known:
                raise SyncError(f"release_blockers.{cls}: unknown component {member!r}")
            blockers.setdefault(member, []).append(cls)
    for key in list(overlay["obligations"]) + list(overlay["allowed_lanes_override"]):
        if key != "source" and key not in known:
            raise SyncError(f"overlay names unknown component {key!r}")
    v1_ids = set(overlay["v1_path"]["ids"])
    missing = sorted(v1_ids - known)
    if missing:
        raise SyncError(f"v1_path names unknown components {missing}")
    overlay = dict(overlay)
    overlay["obligations"] = {k: v for k, v in overlay["obligations"].items() if k != "source"}
    components = sorted(({k: _neutral(v) for k, v in _component(row, overlay, blockers, v1_ids).items()} for row in rows),
                        key=lambda c: c["id"])
    doc = {
        "kind": "component-register",
        "schemaVersion": "1.0.0",
        "register_id": "components.v1",
        "overlay": False,
        "generated_from": [
            {"path": str(register_path.relative_to(ROOT)), "sha256": hashlib.sha256(register_bytes).hexdigest()},
            {"path": str(overlay_path.relative_to(ROOT)), "sha256": hashlib.sha256(overlay_bytes).hexdigest()},
        ],
        "components": components,
    }
    return (json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    data = generate()
    if "--check" in argv:
        current = OUTPUT.read_bytes() if OUTPUT.exists() else b""
        if current != data:
            print(f"{OUTPUT.relative_to(ROOT)} is stale: run python3 scripts/registry/sync.py")
            return 1
        print(f"{OUTPUT.relative_to(ROOT)} regenerates byte-identically")
        return 0
    OUTPUT.write_bytes(data)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(json.loads(data)['components'])} components)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
