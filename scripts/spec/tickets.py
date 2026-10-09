#!/usr/bin/env python3
"""Validate docs/spec/tickets.json and render docs/spec/tickets.md (stdlib only).

The JSON is the source of truth for the v1 ticket DAG; the Markdown is generated from it and never edited by hand.

Checks (any failure exits non-zero):
  - shape: required keys and types, ids T01..Tnn in list order, unique ids and slugs, sizes S|M|L
  - graph: blockers exist, no self-blocks, every blocker comes earlier in the list (so the graph is acyclic),
    every ticket reaches T01, and the blocking edges are transitively reduced
  - preconditions: owner-only steps that precede the repository (a 'preconditions' list, P01..), each needing Jon
  - stories: every numbered user story in docs/spec/aura-v1-spec.md is covered by a ticket or listed in the
    'OUT OF V1 STORIES: [...]' note, and every story a ticket cites exists
  - coverage: every v1-core and v1-studio row of docs/research/feature-inventory.md is cited by a story group's Covers
    line or by Out of Scope in the spec; every row of the spec's 'Unverified capabilities' table names an existing
    ticket slug in code formatting; every owner decision O-01..O-11 and every ADR is cited in some ticket's notes
  - labels: drawn from the vocabulary in docs/agents/issue-tracker.md; exactly one triage label
    (ready-for-agent | ready-for-human), exactly one stream:*, at least one area:*;
    owner_gate true <=> ready-for-human, and owner tickets carry gate:evidence and owner_needs
  - prose: every acceptance criterion names its evidence ('Evidence:'), what_to_build ends with a 'Why blocked:'
    tail naming every blocker, prefactor tickets justify themselves in notes, screens exist in screens.md,
    and no title, what_to_build or criterion uses a phrase from a curated list of terms GLOSSARY.md says to avoid
  - conflicts: two tickets that can run in parallel (neither is an ancestor of the other) never own the same or a
    nested path; a ticket that fills a slot has the ticket declaring that slot among its ancestors

Usage:
  python3 scripts/spec/tickets.py            # validate, then write docs/spec/tickets.md
  python3 scripts/spec/tickets.py --check    # validate, and fail if docs/spec/tickets.md is stale
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TICKETS_JSON = REPO / "docs" / "spec" / "tickets.json"
TICKETS_MD = REPO / "docs" / "spec" / "tickets.md"
SPEC_MD = REPO / "docs" / "spec" / "aura-v1-spec.md"
SCREENS_MD = REPO / "docs" / "spec" / "screens.md"
TRACKER_MD = REPO / "docs" / "agents" / "issue-tracker.md"
INVENTORY_MD = REPO / "docs" / "research" / "feature-inventory.md"
ADR_DIR = REPO / "docs" / "adr"
PRODUCT_JSON = REPO / "contracts" / "product.json"

REQUIRED = {
    "id": str, "slug": str, "title": str, "labels": list, "size": str, "blocked_by": list, "stories": list,
    "what_to_build": str, "acceptance_criteria": list, "owner_gate": bool, "notes": str,
}
OPTIONAL = {"prefactor": bool, "screens": list, "owned_areas": list, "owner_needs": str, "slots": list, "fills": list}
PRECONDITION_KEYS = {"id": str, "title": str, "what": str, "owner_needs": str, "blocks": list}
SIZES = ("S", "M", "L")
SIZE_WEIGHT = {"S": 1, "M": 2, "L": 3}
TRIAGE = ("ready-for-agent", "ready-for-human")
STREAMS = ("engine", "studio", "voice", "eval", "shared")
OWNER_DECISIONS = [f"O-{i:02d}" for i in range(1, 12)]
# A curated list of phrases GLOSSARY.md lists under _Avoid_ that are easy to slip into ticket prose (deriving the
# whole list automatically would flag common words such as 'task' or 'version' that are right in other senses).
AVOID = [
    (r"\btake lanes?\b", re.I, "Track: avoid 'take lane'"),
    (r"\bversion lanes?\b", re.I, "Track: avoid 'version lane'"),
    (r"\blistening sessions?\b", re.I, "Audition: avoid 'listening session'"),
    (r"\brender routes?\b", re.I, "Route: avoid 'render route'"),
    (r"\bvoice memos?\b", re.I, "Hum: avoid 'voice memo'"),
    (r"\bpods?\b", re.I, "Burst run: avoid 'pod' (say burst machine)"),
    (r"\bunblind\w*\b", re.I, "Reveal: avoid 'unblind'"),
    (r"\bnormaliz\w+\b", re.I, "Level matching: avoid 'normalization'"),
    (r"\bpreservation gates?\b", re.I, "Preservation check: a gate is a status pass rule"),
    (r"\bListeningVerdict\b|\bAuditionSession\b", 0, "Verdict, Audition: the glossary terms"),
    (r"\bvariants?\b", re.I, "Candidate: avoid 'variant'"),
    (r"\bowner gates?\b", re.I, "Owner act: say 'needs Jon'"),
]
OUT_OF_V1_PREFIX = "OUT OF V1 STORIES:"
RANGE_DASH = "–"


class Problems(list):
    def add(self, where: str, msg: str) -> None:
        self.append(f"{where}: {msg}")


def spec_stories(problems: Problems) -> list[int]:
    text = SPEC_MD.read_text(encoding="utf-8")
    m = re.search(r"^## User Stories\s*$(.*?)^## ", text, re.M | re.S)
    if not m:
        problems.add("aura-v1-spec.md", "no '## User Stories' section found")
        return []
    nums = [int(x) for x in re.findall(r"^(\d+)\. ", m.group(1), re.M)]
    if not nums:
        problems.add("aura-v1-spec.md", "no numbered user stories found")
    elif nums != list(range(1, len(nums) + 1)):
        problems.add("aura-v1-spec.md", "user stories are not numbered continuously from 1")
    return nums


def label_vocabulary(problems: Problems) -> tuple[set[str], list[re.Pattern]]:
    text = TRACKER_MD.read_text(encoding="utf-8")
    m = re.search(r"Labels in use:(.*?)(?:\n\s*\n|\n- |\Z)", text, re.S)
    if not m:
        problems.add("issue-tracker.md", "no 'Labels in use:' line found")
        return set(), []
    literal, patterns = set(), []
    for token in re.findall(r"`([^`]+)`", m.group(1)):
        if "<" in token:
            rx = re.escape(token)
            rx = re.sub(r"\\<[^>]*\\>|<[^>]*>", "[a-z0-9][a-z0-9-]*", rx)
            patterns.append(re.compile(rf"^{rx}$"))
        else:
            literal.add(token)
    return literal, patterns


def screen_ids() -> set[str]:
    text = SCREENS_MD.read_text(encoding="utf-8")
    return set(re.findall(r"^#{3,4} (S\d\d|O\d{1,2})\b", text, re.M))


def out_of_v1(notes: list[str], problems: Problems) -> set[int]:
    hits = [n for n in notes if n.startswith(OUT_OF_V1_PREFIX)]
    if len(hits) != 1:
        problems.add("notes", f"expected exactly one note starting '{OUT_OF_V1_PREFIX}', found {len(hits)}")
        return set()
    m = re.match(re.escape(OUT_OF_V1_PREFIX) + r"\s*(\[[^\]]*\])", hits[0])
    if not m:
        problems.add("notes", f"'{OUT_OF_V1_PREFIX}' must be followed by a JSON list of story numbers")
        return set()
    try:
        vals = json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        problems.add("notes", f"cannot parse the out-of-v1 list: {exc}")
        return set()
    if not all(isinstance(v, int) for v in vals):
        problems.add("notes", "the out-of-v1 list must hold integers")
        return set()
    return set(vals)


def check_shape(tickets: list, problems: Problems) -> None:
    """Required keys and types, ids in list order, unique ids and slugs, sizes, evidence on every criterion."""
    for i, t in enumerate(tickets):
        where = t.get("id", f"tickets[{i}]") if isinstance(t, dict) else f"tickets[{i}]"
        if not isinstance(t, dict):
            problems.add(where, "ticket must be an object")
            continue
        for key, typ in REQUIRED.items():
            if key not in t:
                problems.add(where, f"missing '{key}'")
            elif not isinstance(t[key], typ):
                problems.add(where, f"'{key}' must be {typ.__name__}")
        for key, typ in OPTIONAL.items():
            if key in t and not isinstance(t[key], typ):
                problems.add(where, f"'{key}' must be {typ.__name__}")
        unknown = set(t) - set(REQUIRED) - set(OPTIONAL)
        if unknown:
            problems.add(where, f"unknown keys {sorted(unknown)}")
        if t.get("id") != f"T{i + 1:02d}":
            problems.add(where, f"id must be T{i + 1:02d} (ids follow list order)")
        if t.get("size") not in SIZES:
            problems.add(where, f"size must be one of {SIZES}")
        if isinstance(t.get("slug"), str) and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", t["slug"]):
            problems.add(where, "slug must be kebab-case")
        for key in ("title", "what_to_build", "notes"):
            if isinstance(t.get(key), str) and not t[key].strip():
                problems.add(where, f"'{key}' is empty")
        acs = t.get("acceptance_criteria")
        if isinstance(acs, list):
            if not acs:
                problems.add(where, "needs at least one acceptance criterion")
            for j, ac in enumerate(acs):
                if not isinstance(ac, str) or "Evidence:" not in ac:
                    problems.add(where, f"acceptance criterion {j + 1} does not name its evidence ('Evidence: ...')")
    for key in ("id", "slug"):
        values = [t.get(key) for t in tickets if isinstance(t, dict)]
        for dup in sorted({str(x) for x in values if values.count(x) > 1}):
            problems.add(dup, f"duplicate {key}")


def check_preconditions(pre: list, tickets: list, problems: Problems) -> None:
    """Owner-only steps that precede the repository: each is a ready-for-human issue that blocks the tickets it names."""
    ids = {t["id"] for t in tickets}
    for i, p in enumerate(pre):
        where = f"preconditions[{i}]"
        if not isinstance(p, dict) or set(p) != set(PRECONDITION_KEYS):
            problems.add(where, f"must have exactly the keys {sorted(PRECONDITION_KEYS)}")
            continue
        for key, typ in PRECONDITION_KEYS.items():
            if not isinstance(p[key], typ) or (typ is str and not p[key].strip()):
                problems.add(where, f"'{key}' must be a non-empty {typ.__name__}")
        if p.get("id") != f"P{i + 1:02d}":
            problems.add(where, f"id must be P{i + 1:02d}")
        for b in p.get("blocks", []):
            if b not in ids:
                problems.add(where, f"blocks unknown ticket {b}")


def check_edges(tickets: list, problems: Problems) -> None:
    """Blockers exist, are not self-blocks, come earlier in the list; only T01 is a root."""
    index = {t["id"]: i for i, t in enumerate(tickets)}
    for t in tickets:
        where, bl = t["id"], t["blocked_by"]
        if len(set(bl)) != len(bl):
            problems.add(where, "duplicate blocker")
        for b in bl:
            if b not in index:
                problems.add(where, f"blocker {b} does not exist")
            elif b == where:
                problems.add(where, "blocks itself")
            elif index[b] >= index[where]:
                problems.add(where, f"blocker {b} does not come earlier in the list")
    if tickets[0]["blocked_by"]:
        problems.add(tickets[0]["id"], "T01 must have no blockers")
    for t in tickets[1:]:
        if not t["blocked_by"]:
            problems.add(t["id"], "only T01 may have no blockers")


def ancestor_sets(tickets: list) -> dict[str, set[str]]:
    ancestors: dict[str, set[str]] = {}
    for t in tickets:  # list order is a topological order (check_edges proved it)
        ancestors[t["id"]] = set().union(*([{b} | ancestors[b] for b in t["blocked_by"]] or [set()]))
    return ancestors


def check_reduction(tickets: list, ancestors: dict[str, set[str]], problems: Problems) -> None:
    """Every ticket reaches T01, and no blocker is reachable through another blocker (transitive reduction)."""
    root = tickets[0]["id"]
    for t in tickets[1:]:
        if root not in ancestors[t["id"]]:
            problems.add(t["id"], f"does not reach {root}")
        bl = t["blocked_by"]
        for b in bl:
            via = [o for o in bl if o != b and b in ancestors[o]]
            if via:
                problems.add(t["id"], f"edge to {b} is redundant (already reached through {', '.join(via)}); "
                                      "blocking edges must be transitively reduced")


def check_stories(tickets: list, notes: list[str], stories: list[int], problems: Problems) -> tuple[set, set]:
    """Every spec story is covered or listed out of v1; every cited story exists. Returns (cited, excluded)."""
    story_set, cited = set(stories), set()
    for t in tickets:
        s = t["stories"]
        if not all(isinstance(x, int) for x in s):
            problems.add(t["id"], "stories must be integers")
            continue
        if len(set(s)) != len(s):
            problems.add(t["id"], "duplicate story number")
        for x in s:
            if x not in story_set:
                problems.add(t["id"], f"story {x} does not exist in aura-v1-spec.md")
        cited |= set(s)
    excluded = out_of_v1(notes, problems)
    for x in sorted(excluded - story_set):
        problems.add("notes", f"out-of-v1 story {x} does not exist in aura-v1-spec.md")
    for x in sorted(excluded & cited):
        problems.add("notes", f"story {x} is listed out of v1 but a ticket covers it")
    missing = sorted(story_set - cited - excluded)
    if missing:
        problems.add("stories", f"{len(missing)} user stories are neither covered nor listed out of v1: {missing}")
    return cited, excluded


def _expand_ids(group: str) -> set[str]:
    """'A1, A2, K1–K5' -> {'A1', 'A2', 'K1', ..., 'K5'}; ranges stay inside one letter."""
    out: set[str] = set()
    for part in re.split(r",\s*", group):
        m = re.fullmatch(rf"([A-L])(\d+)\s*[{RANGE_DASH}-]\s*([A-L])?(\d+)", part.strip())
        if m:
            out |= {f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(4)) + 1)}
            continue
        m = re.match(r"([A-L]\d+)\b", part.strip())
        if m:
            out.add(m.group(1))
    return out


def check_coverage(tickets: list, problems: Problems) -> dict:
    """Inventory rows, unverified-capability rows, owner decisions and ADRs all trace to the spec and the tickets."""
    spec = SPEC_MD.read_text(encoding="utf-8")
    inventory = INVENTORY_MD.read_text(encoding="utf-8")
    in_scope = {m.group(1) for m in re.finditer(r"^\| ([A-L]\d+) \|(.*)$", inventory, re.M)
                if re.search(r"\*\*v1-(core|studio)\*\*", m.group(2))}
    covers: set[str] = set()
    for line in re.findall(r"^_Scope:.*$", spec, re.M):
        for group in re.findall(r"\[([^\]]+)\]", line):
            covers |= _expand_ids(group)
    oos = re.search(r"^## Out of Scope\s*$(.*?)^## ", spec, re.M | re.S)
    out_of_scope: set[str] = set()
    for group in re.findall(r"\[([^\]]+)\]", oos.group(1) if oos else ""):
        out_of_scope |= _expand_ids(group)
    for fid in sorted(in_scope - covers - out_of_scope, key=lambda x: (x[0], int(x[1:]))):
        problems.add("coverage", f"inventory row {fid} (v1-core or v1-studio) is cited by no story group and not listed out of scope")

    slugs = {t["slug"] for t in tickets}
    table = re.search(r"^### Unverified capabilities and the tickets that gate them\s*$(.*?)^### ", spec, re.M | re.S)
    rows = 0
    for line in (table.group(1) if table else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not line.startswith("|") or set(cells[0]) <= {"-"} or cells[0].startswith("Capability"):
            continue
        rows += 1
        named = re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", cells[2])
        if not named:
            problems.add("coverage", f"unverified capability '{cells[0][:50]}' names no ticket slug in code formatting")
        for slug in named:
            if slug not in slugs:
                problems.add("coverage", f"unverified capability '{cells[0][:50]}' names unknown ticket slug {slug}")
    if not rows:
        problems.add("coverage", "the spec's 'Unverified capabilities' table has no rows")

    notes = " ".join(t["notes"] for t in tickets)
    for oid in OWNER_DECISIONS:
        if not re.search(rf"\b{oid}\b", notes):
            problems.add("coverage", f"owner decision {oid} is cited in no ticket's notes")
    adrs = sorted(int(p.name[:4]) for p in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md"))
    for n in adrs:
        if f"ADR-{n:04d}" not in notes:
            problems.add("coverage", f"ADR-{n:04d} is cited in no ticket's notes")
    return {"inventory": len(in_scope), "unverified_rows": rows, "adrs": len(adrs)}


def check_labels(tickets: list, literal: set[str], patterns: list[re.Pattern], problems: Problems) -> None:
    """Vocabulary, one triage label, one stream:*, an area:*, and owner_gate <=> ready-for-human."""
    for t in tickets:
        where, labels = t["id"], t["labels"]
        if len(set(labels)) != len(labels):
            problems.add(where, "duplicate label")
        for lab in labels:
            if lab not in literal and not any(p.match(lab) for p in patterns):
                problems.add(where, f"label '{lab}' is not in the vocabulary of docs/agents/issue-tracker.md")
        if sum(1 for x in labels if x in TRIAGE) != 1:
            problems.add(where, f"needs exactly one of {TRIAGE}")
        streams = [x for x in labels if x.startswith("stream:")]
        if len(streams) != 1 or streams[0].split(":", 1)[1] not in STREAMS:
            problems.add(where, f"needs exactly one stream label from {['stream:' + x for x in STREAMS]}")
        if not any(x.startswith("area:") for x in labels):
            problems.add(where, "needs at least one area:<name> label")
        check_owner_gate(t, problems)


def check_owner_gate(t: dict, problems: Problems) -> None:
    where, labels = t["id"], t["labels"]
    if t["owner_gate"]:
        if "ready-for-human" not in labels:
            problems.add(where, "owner_gate tickets must carry ready-for-human")
        if "gate:evidence" not in labels:
            problems.add(where, "owner_gate tickets must carry gate:evidence")
        if not t.get("owner_needs", "").strip():
            problems.add(where, "owner_gate tickets must say what Jon supplies in owner_needs")
        return
    if "ready-for-human" in labels:
        problems.add(where, "ready-for-human is reserved for owner_gate tickets")
    if "owner_needs" in t:
        problems.add(where, "owner_needs only belongs on owner_gate tickets")


def check_prose(tickets: list, screens_known: set[str], problems: Problems) -> None:
    """'Why blocked:' tail, prefactor justification, known screens, owned areas, glossary-avoided phrases."""
    for t in tickets:
        where, what = t["id"], t["what_to_build"]
        parts = what.split("Why blocked:")
        if len(parts) != 2:
            problems.add(where, "what_to_build must contain exactly one 'Why blocked:' tail")
        else:
            named = set(re.findall(r"\bT\d{2,3}\b", parts[1]))
            for b in t["blocked_by"]:
                if b not in named:
                    problems.add(where, f"'Why blocked:' does not give a reason for {b}")
            for extra in sorted(named - set(t["blocked_by"])):
                problems.add(where, f"'Why blocked:' names {extra}, which is not a blocker")
        if t.get("prefactor") and "Prefactor" not in t["notes"]:
            problems.add(where, "prefactor tickets must justify themselves in notes ('Prefactor: ...')")
        for sid in t.get("screens", []):
            if sid not in screens_known:
                problems.add(where, f"screen {sid} is not defined in screens.md")
        if not t["owner_gate"] and not t.get("owned_areas"):
            problems.add(where, "agent tickets must list their owned_areas (one feature per folder)")
        prose = " ".join([t["title"], what] + list(t["acceptance_criteria"]))
        for rx, flags, why in AVOID:
            hit = re.search(rx, prose, flags)
            if hit:
                problems.add(where, f"uses '{hit.group(0)}' ({why})")


def owned_paths(t: dict) -> list[str]:
    """Base paths of a ticket's owned areas: the text before ' (', when it is a path. Areas changed only through a
    contract-fix PR are separate small PRs and are left out."""
    out = []
    for area in t.get("owned_areas", []):
        if "contract-fix PR" in area:
            continue
        base = area.split(" (", 1)[0].strip().rstrip("/")
        if "/" not in base and not base.startswith("."):
            continue
        if " " in base:
            continue
        out.append(base)
    return out


def _nested(a: str, b: str) -> bool:
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def check_conflicts(tickets: list, ancestors: dict[str, set[str]], problems: Problems) -> None:
    """Parallel tickets own disjoint paths; slot fillers come after the ticket that declares the slot."""
    paths = {t["id"]: owned_paths(t) for t in tickets}
    ids = [t["id"] for t in tickets]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if a in ancestors[b] or b in ancestors[a]:
                continue
            for pa in paths[a]:
                for pb in paths[b]:
                    if _nested(pa, pb):
                        problems.add(f"{a}/{b}", f"can run in parallel but both own '{pa}' and '{pb}'")
    declared: dict[str, str] = {}
    for t in tickets:
        for slot in t.get("slots", []):
            if slot in declared:
                problems.add(t["id"], f"slot {slot} is already declared by {declared[slot]}")
            declared[slot] = t["id"]
    for t in tickets:
        for slot in t.get("fills", []):
            owner = declared.get(slot)
            if owner is None:
                problems.add(t["id"], f"fills slot {slot}, which no ticket declares")
            elif owner != t["id"] and owner not in ancestors[t["id"]]:
                problems.add(t["id"], f"fills slot {slot}, but {owner}, which declares it, is not an ancestor")


def compute_depth(tickets: list) -> dict[str, int]:
    depth: dict[str, int] = {}
    for t in tickets:
        depth[t["id"]] = 0 if not t["blocked_by"] else 1 + max(depth[b] for b in t["blocked_by"])
    return depth


def critical_path(tickets: list) -> tuple[int, list[str]]:
    """Heaviest path from T01 with S=1, M=2, L=3."""
    best: dict[str, tuple[int, list[str]]] = {}
    for t in tickets:
        w = SIZE_WEIGHT[t["size"]]
        prev = max((best[b] for b in t["blocked_by"]), key=lambda x: x[0], default=(0, []))
        best[t["id"]] = (prev[0] + w, prev[1] + [t["id"]])
    return max(best.values(), key=lambda x: x[0])


def validate(doc: dict) -> tuple[Problems, dict]:
    problems = Problems()
    if not isinstance(doc, dict) or not {"notes", "tickets"} <= set(doc) or not set(doc) <= {"notes", "tickets", "preconditions"}:
        problems.add("tickets.json", "top level must be an object with 'notes' and 'tickets' (and optionally 'preconditions')")
        return problems, {}
    notes, tickets, pre = doc["notes"], doc["tickets"], doc.get("preconditions", [])
    if not isinstance(notes, list) or not all(isinstance(n, str) and n.strip() for n in notes):
        problems.add("notes", "must be a list of non-empty strings")
        notes = [n for n in notes if isinstance(n, str)] if isinstance(notes, list) else []
    if not isinstance(tickets, list) or not tickets:
        problems.add("tickets", "must be a non-empty list")
        return problems, {}
    if not isinstance(pre, list):
        problems.add("preconditions", "must be a list")
        pre = []

    stories = spec_stories(problems)
    literal, patterns = label_vocabulary(problems)
    check_shape(tickets, problems)
    if problems:
        return problems, {}
    check_edges(tickets, problems)
    if problems:
        return problems, {}
    ancestors = ancestor_sets(tickets)
    check_reduction(tickets, ancestors, problems)
    check_preconditions(pre, tickets, problems)
    cited, excluded = check_stories(tickets, notes, stories, problems)
    coverage = check_coverage(tickets, problems)
    check_labels(tickets, literal, patterns, problems)
    check_prose(tickets, screen_ids(), problems)
    check_conflicts(tickets, ancestors, problems)

    info = {
        "tickets": tickets, "notes": notes, "preconditions": pre, "depth": compute_depth(tickets),
        "critical": critical_path(tickets), "stories": stories, "covered": sorted(cited & set(stories)),
        "excluded": sorted(excluded), "coverage": coverage,
    }
    return problems, info


def stream_of(t: dict) -> str:
    return next(x for x in t["labels"] if x.startswith("stream:")).split(":", 1)[1]


def md_escape(s: str) -> str:
    return s.replace("|", "\\|")


def render(info: dict) -> str:
    tickets, depth, pre = info["tickets"], info["depth"], info["preconditions"]
    n = len(tickets)
    first, last = tickets[0]["id"], tickets[-1]["id"]
    sizes = {k: sum(1 for t in tickets if t["size"] == k) for k in SIZES}
    streams = {k: sum(1 for t in tickets if stream_of(t) == k) for k in STREAMS}
    owners = [t for t in tickets if t["owner_gate"]]
    prefactors = [t["id"] for t in tickets if t.get("prefactor")]
    evidence = [t["id"] for t in tickets if "gate:evidence" in t["labels"]]
    max_depth = max(depth.values())
    cp_weight, cp_path = info["critical"]

    product = json.loads(PRODUCT_JSON.read_text(encoding="utf-8"))  # ADR-0035, ADR-0037: name and contact stored once
    out = []
    out.append(f"# {product['productName']} v1 ticket DAG")
    out.append("")
    out.append("Generated by `scripts/spec/tickets.py` from `docs/spec/tickets.json`, which is the source of truth. Do not edit "
               "this file by hand: change the JSON and re-run the script. Every blocker comes earlier in the list, the graph is "
               f"acyclic, every ticket reaches {first}, and blockers are direct edges after transitive reduction. Depth counts "
               f"from {first}. Tickets that can run in parallel own disjoint paths, and every slot filler comes after the ticket "
               "that declares its slot.")
    out.append("")
    out.append(f"- **{n} tickets** ({first}–{last}): {sizes['L']} L, {sizes['M']} M, {sizes['S']} S.")
    out.append("- **Work streams:** " + ", ".join(f"stream:{k} {v}" for k, v in streams.items()) + ". These name work "
               "streams, never operator lanes.")
    out.append(f"- **Needs Jon:** {len(owners)} tickets, labelled `ready-for-human`, plus {len(pre)} precondition(s) before "
               f"{first}. Every other ticket is `ready-for-agent`.")
    out.append(f"- **Evidence-gated** (`gate:evidence`): {len(evidence)} tickets.")
    out.append(f"- **Prefactors** (horizontal by design, justified in each ticket's notes): {', '.join(prefactors)}.")
    out.append(f"- **User stories:** {len(info['covered'])} of {len(info['stories'])} covered"
               + (f"; listed out of v1: {info['excluded']}." if info["excluded"] else "; none listed out of v1."))
    cov = info["coverage"]
    out.append(f"- **Traceability:** {cov['inventory']} v1-core and v1-studio inventory rows each cited by a story group or "
               f"Out of Scope; {cov['unverified_rows']} unverified-capability rows each gated by a named ticket; O-01 to "
               f"O-11 and all {cov['adrs']} ADRs cited in ticket notes.")
    out.append(f"- **Depth:** {max_depth}. **Weighted critical path** (S=1, M=2, L=3) is {cp_weight}: "
               + ", ".join(cp_path) + ".")
    out.append("")
    out.append("\"Needs Jon\" means the ticket cannot close without an owner act (a license acceptance, a paid-run approval, a "
               "verdict, a 'not garbled' check, a risk acceptance) or an input only he can supply. The JSON field is "
               "`owner_gate`; in GLOSSARY terms a gate is a pass rule, so prose says \"needs Jon\".")
    out.append("")
    if pre:
        out.append("## Preconditions (need Jon, before the repository)")
        out.append("")
        for p in pre:
            out.append(f"- **{p['id']}** {p['title']}. {p['what']} Needs: {p['owner_needs']} Blocks: {', '.join(p['blocks'])}.")
        out.append("")
    out.append("| ID | Title | Blocked by | Size | Depth | Stream | Needs Jon |")
    out.append("|---|---|---|---|---|---|---|")
    for t in tickets:
        bl = ", ".join(t["blocked_by"]) if t["blocked_by"] else "—"
        if len(t["blocked_by"]) > 8:
            bl = f"{len(t['blocked_by'])} tickets (see tickets.json)"
        og = "yes" if t["owner_gate"] else "—"
        out.append(f"| {t['id']} | {md_escape(t['title'])} | {bl} | {t['size']} | {depth[t['id']]} | {stream_of(t)} | {og} |")
    out.append("")
    wide = [t for t in tickets if len(t["blocked_by"]) > 8]
    if wide:
        out.append("Aggregation tickets with many blockers:")
        out.append("")
        for t in wide:
            out.append(f"- **{t['id']}** is blocked by {', '.join(t['blocked_by'])}.")
        out.append("")
    out.append("## Frontier by depth")
    out.append("")
    out.append("A ticket is on the frontier once every ticket it is blocked by is done. Grouped by depth from "
               f"{first}; tickets that need Jon are marked (Jon).")
    out.append("")
    for d in range(max_depth + 1):
        row = [t["id"] + (" (Jon)" if t["owner_gate"] else "") for t in tickets if depth[t["id"]] == d]
        out.append(f"- d{d} ({len(row)}): {', '.join(row)}")
    out.append("")
    out.append("## Tickets that need Jon")
    out.append("")
    out.append("Each of these cannot close without Jon. An agent prepares everything up to the owner act or input and then "
               "waits; it never performs an owner act for him.")
    out.append("")
    for t in owners:
        bl = ", ".join(t["blocked_by"])
        out.append(f"- **{t['id']}** {t['title']}. Needs: {t['owner_needs']} (blocked by {bl}; depth {depth[t['id']]})")
    out.append("")
    out.append("## Notes")
    out.append("")
    for note in info["notes"]:
        out.append(f"- {note}")
    out.append("")
    out.append(f"Contact for the project, as text only: `{product['publicContactText']}`.")
    out.append("")
    text = "\n".join(out)
    # IDC Rule 07 / ADR-0037: GitHub autolinks a bare address in Markdown, so the contact is always in code formatting.
    contact = re.escape(product["publicContactText"])
    return re.sub(rf"(?<!`){contact}(?!`)", f"`{product['publicContactText']}`", text)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    try:
        doc = json.loads(TICKETS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: cannot read {TICKETS_JSON}: {exc}")
        return 1
    problems, info = validate(doc)
    if problems:
        for p in problems:
            print(f"fail  {p}")
        print(f"FAILED: {len(problems)} problem(s)")
        return 1
    text = render(info)
    if check:
        current = TICKETS_MD.read_text(encoding="utf-8") if TICKETS_MD.exists() else ""
        if current != text:
            print(f"FAILED: {TICKETS_MD.relative_to(REPO)} is stale; run scripts/spec/tickets.py")
            return 1
    else:
        TICKETS_MD.write_text(text, encoding="utf-8")

    tickets, depth = info["tickets"], info["depth"]
    sizes = {k: sum(1 for t in tickets if t["size"] == k) for k in SIZES}
    streams = {k: sum(1 for t in tickets if stream_of(t) == k) for k in STREAMS}
    owners = [t["id"] for t in tickets if t["owner_gate"]]
    cov = info["coverage"]
    print(f"ok    {len(tickets)} tickets ({sizes['L']} L, {sizes['M']} M, {sizes['S']} S); {len(info['preconditions'])} precondition(s)")
    print("ok    streams: " + ", ".join(f"{k} {v}" for k, v in streams.items()))
    print(f"ok    graph acyclic, every ticket reaches {tickets[0]['id']}, blockers transitively reduced")
    print("ok    parallel tickets own disjoint paths; every slot filler descends from its slot's declarer")
    print(f"ok    {len(info['covered'])}/{len(info['stories'])} user stories covered; out of v1: {info['excluded'] or 'none'}")
    print(f"ok    {cov['inventory']} in-scope inventory rows traced; {cov['unverified_rows']} unverified-capability rows gated; "
          f"O-01..O-11 and {cov['adrs']} ADRs cited")
    print(f"ok    labels from docs/agents/issue-tracker.md; {len(owners)} tickets need Jon, all ready-for-human: {', '.join(owners)}")
    print("ok    every acceptance criterion names its evidence; every 'Why blocked:' names its blockers")
    d1 = [t["id"] for t in tickets if depth[t["id"]] == 1]
    print(f"ok    depth-1 frontier: {', '.join(d1)}; max depth {max(depth.values())}; "
          f"critical path weight {info['critical'][0]}")
    print(f"{'checked' if check else 'wrote'} {TICKETS_MD.relative_to(REPO)}")
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
