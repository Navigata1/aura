#!/usr/bin/env python3
"""Regenerate contracts/registry/components.v1.json from the evidence register. Standard library only.

Inputs: docs/research/evidence-register.json (the verified research) and scripts/registry/register_overlay.json
(the studio's decisions: lane narrowing, release-blocker classes, obligations, v1-path flags, supplement rows, license
verifications and open rows, each citing its ADR or ticket). The output is deterministic (sorted keys, two-space
indent, components sorted by id), so scripts/spec/validate.py can require that it regenerates byte-identically
(ADR-0011 rule 1). The open-source-readiness register (ADR-0011 rule 2, Q5) is generated from the same rows into
docs/research/licenses/, and lists every release blocker.

    python3 scripts/registry/sync.py           # rewrite components.v1.json and the open-source-readiness register
    python3 scripts/registry/sync.py --check   # exit 1 on a stale output or a missing release blocker
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
OUTPUT_PATH = "contracts/registry/components.v1.json"
OUTPUT = ROOT / OUTPUT_PATH
READINESS = ROOT / "docs/research/licenses/open-source-readiness.json"
READINESS_MD = READINESS.with_suffix(".md")
PRODUCT_NAME = json.loads((ROOT / "contracts/product.json").read_text(encoding="utf-8"))["productName"]

LANE_ORDER = ("individual", "llc", "research")
BOUNDARY_CLASSES = {"non_commercial_weights", "non_commercial_by_author", "research_or_academic", "unknown_license",
                    "contested", "copyleft"}
COPYLEFT_CODE = re.compile(r"\b(A?GPL|LGPL)")
URL = re.compile(r"^https://[^\s]+$")
# A license verification replaces these fields of a row; lanes, blockers and obligations stay overlay decisions.
VERIFIED_FIELDS = {"name", "code_license", "weights_license", "output_terms", "verdict", "verdict_condition",
                   "redistribution_blocker", "evidence_status", "primary_sources", "notes"}


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


def _verified(rows: list[dict], overlay: dict) -> list[dict]:
    """T03 and later license tickets: a verification replaces named fields of a row from its pinned primary sources."""
    entries = overlay.get("license_verification", {}).get("rows", {})
    known = {row["id"] for row in rows}
    for cid, fields in entries.items():
        if cid not in known:
            raise SyncError(f"license_verification names unknown component {cid!r}")
        if set(fields) - VERIFIED_FIELDS:
            raise SyncError(f"license_verification.{cid} cannot set {sorted(set(fields) - VERIFIED_FIELDS)}")
    return [dict(row, **entries.get(row["id"], {})) for row in rows]


def _apply_open_rows(components: list[dict], overlay: dict) -> None:
    """An open row names the gate that blocks it and the label shown meanwhile, and stays unverified in research."""
    entries = overlay.get("open_rows", {}).get("rows", {})
    by_id = {c["id"]: c for c in components}
    for cid, entry in entries.items():
        component = by_id.get(cid)
        if component is None:
            raise SyncError(f"open_rows names unknown component {cid!r}")
        if set(entry) != {"gate", "label"} or not all(isinstance(v, str) and v for v in entry.values()):
            raise SyncError(f"open_rows.{cid} needs exactly a gate and a label")
        if (component["verification_status"] != "unverified" or "unverified" not in component["release_blockers"]
                or component["allowed_lanes"] != ["research"]):
            raise SyncError(f"open_rows.{cid}: an open row stays unverified, research-only and release-blocking")
        component["verdict_condition"] = _neutral(f"Open until {entry['gate']}. Until then the studio shows "
                                                  f"\"{entry['label']}\".")


def _require_sources(components: list[dict]) -> None:
    """No row leaves UNVERIFIED without a cited primary source (P0-9)."""
    for component in components:
        if component["verification_status"] != "unverified" and not component["primary_sources"]:
            raise SyncError(f"{component['id']}: status {component['verification_status']!r} cites no primary source")


def generate(register_path: Path = REGISTER, overlay_path: Path = OVERLAY) -> bytes:
    register_bytes = register_path.read_bytes()
    overlay_bytes = overlay_path.read_bytes()
    doc = {
        "kind": "component-register",
        "schemaVersion": "1.0.0",
        "register_id": "components.v1",
        "overlay": False,
        "generated_from": [
            {"path": register_path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(register_bytes).hexdigest()},
            {"path": overlay_path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(overlay_bytes).hexdigest()},
        ],
        "components": build(json.loads(register_bytes), json.loads(overlay_bytes)),
    }
    return _dump(doc)


def build(register: dict, overlay: dict) -> list[dict]:
    """The component rows, from the evidence register plus the overlay; SyncError on any inconsistent decision."""
    rows = _verified(list(register["components"]) + list(overlay["supplement"]["rows"]), overlay)
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
    _apply_open_rows(components, overlay)
    _require_sources(components)
    return components


def _dump(doc: dict) -> bytes:
    return (json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def readiness(components: list[dict], overlay: dict, register_bytes: bytes) -> dict:
    """The open-source-readiness register: every component whose terms block releasing it as it is (ADR-0011 rule 7)."""
    open_rows = overlay.get("open_rows", {}).get("rows", {})
    entries = [{"id": c["id"], "name": c["name"], "release_blockers": c["release_blockers"],
                "allowed_lanes": c["allowed_lanes"], "process_boundary_required": c["process_boundary_required"],
                "verification_status": c["verification_status"], "verdict": c["verdict"], "v1_path": c["v1_path"],
                "condition": c["verdict_condition"], "gate": open_rows.get(c["id"], {}).get("gate"),
                "label": open_rows.get(c["id"], {}).get("label")} for c in components if c["release_blockers"]]
    by_class: dict[str, int] = {}
    for entry in entries:
        for cls in entry["release_blockers"]:
            by_class[cls] = by_class.get(cls, 0) + 1
    return {
        "register_id": "open-source-readiness.v1",
        "description": "Generated by scripts/registry/sync.py from the component register; never edit by hand. Every "
                       "component listed here blocks releasing the studio's code or outputs as they are until its "
                       "blockers are cleared or covered by an explicit permission. Interpretation, not legal advice.",
        "generated_from": [{"path": OUTPUT_PATH, "sha256": hashlib.sha256(register_bytes).hexdigest()}],
        "summary": {"components": len(components), "release_blockers": len(entries), "by_class": by_class,
                    "open_rows": sum(1 for e in entries if e["gate"])},
        "release_blockers": entries,
    }


def readiness_problems(register: dict, readiness_doc: dict) -> list[str]:
    """Every release-blocking row of the component register must be listed, with exactly its classes."""
    expected = {c["id"]: sorted(c["release_blockers"]) for c in register["components"] if c["release_blockers"]}
    listed: dict[str, list[str]] = {}
    problems = []
    for entry in readiness_doc["release_blockers"]:
        if entry["id"] in listed:
            problems.append(f"{entry['id']}: listed twice in the open-source-readiness register")
        listed[entry["id"]] = sorted(entry["release_blockers"])
    for cid in sorted(set(expected) - set(listed)):
        problems.append(f"{cid}: release blocker {expected[cid]} is missing from the open-source-readiness register")
    for cid in sorted(set(listed) - set(expected)):
        problems.append(f"{cid}: listed as a release blocker, but the component register gives it none")
    for cid in sorted(set(expected) & set(listed)):
        if expected[cid] != listed[cid]:
            problems.append(f"{cid}: listed with {listed[cid]}, but the component register gives {expected[cid]}")
    return problems


def _cell(value) -> str:
    if isinstance(value, list):
        text = ", ".join(value) or "none"
    else:
        text = "yes" if value is True else "no" if value is False else value or ""
    return str(text).replace("|", "\\|").replace("\n", " ")


def _markdown(doc: dict) -> str:
    summary = doc["summary"]
    lines = ["# Open-source-readiness register", "",
             f"Generated by `scripts/registry/sync.py` from `{OUTPUT_PATH}` (SHA-256 "
             f"`{doc['generated_from'][0]['sha256']}`); never edit by hand. {summary['release_blockers']} of "
             f"{summary['components']} components are release blockers; {summary['open_rows']} rows are open. A "
             "component that is not listed has no release-blocker class in the register; its obligations still apply. "
             "Every legal reading here is an interpretation, not legal advice.", "",
             "## Open rows", "", "| Component | Blocking gate | Shown until it closes |", "|---|---|---|"]
    lines += [f"| `{e['id']}` {_cell(e['name'])} | {_cell(e['gate'])} | {_cell(e['label'])} |"
              for e in doc["release_blockers"] if e["gate"]]
    lines += ["", "## Release blockers", "",
              "| Component | Classes | Allowed lanes | Process boundary | Status | v1 path | Condition |",
              "|---|---|---|---|---|---|---|"]
    lines += [f"| `{e['id']}` {_cell(e['name'])} | {_cell(e['release_blockers'])} | {_cell(e['allowed_lanes'])} | "
              f"{_cell(e['process_boundary_required'])} | {e['verification_status']} | {_cell(e['v1_path'])} | "
              f"{_cell(e['condition'])} |" for e in doc["release_blockers"]]
    return "\n".join(lines) + "\n"


def generate_readiness(register_path: Path = REGISTER, overlay_path: Path = OVERLAY) -> tuple[bytes, bytes]:
    data = generate(register_path, overlay_path)
    doc = readiness(json.loads(data)["components"], json.loads(overlay_path.read_bytes()), data)
    return _dump(doc), _markdown(doc).encode("utf-8")


def _check(outputs: dict[Path, bytes]) -> int:
    """Exit status 1 when a committed output is stale or the committed readiness register misses a release blocker."""
    problems = [f"{path.relative_to(ROOT)} is stale: run python3 scripts/registry/sync.py"
                for path, expected in outputs.items() if not path.exists() or path.read_bytes() != expected]
    if OUTPUT.exists() and READINESS.exists():
        problems += readiness_problems(json.loads(OUTPUT.read_bytes()), json.loads(READINESS.read_bytes()))
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"{OUTPUT_PATH} and the open-source-readiness register regenerate byte-identically")
    return 0


def main(argv: list[str]) -> int:
    try:
        data = generate()
        readiness_json, readiness_md = generate_readiness()
    except SyncError as error:
        print(f"the register overlay is inconsistent: {error}")
        return 1
    outputs = {OUTPUT: data, READINESS: readiness_json, READINESS_MD: readiness_md}
    if "--check" in argv:
        return _check(outputs)
    for path, expected in outputs.items():
        path.write_bytes(expected)
    print(f"wrote {OUTPUT_PATH} ({len(json.loads(data)['components'])} components) and the open-source-readiness "
          f"register ({json.loads(readiness_json)['summary']['release_blockers']} release blockers)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
