#!/usr/bin/env python3
"""Validate the studio's cross-language contracts (contracts/). Standard library only, Python 3.11+.

 1. Schemas use only keywords the bundled checker implements, every $ref resolves, no schema has an $id, and every
    record schema requires kind and schemaVersion.
 2. Checker self-tests: hand-written known-bad instances fail and known-good ones pass, keyword by keyword, so the
    checker is not vacuous; an unsupported keyword and a dangling $ref are refused.
 3. Every JSON file under contracts/ validates against the schema its "kind" names; no file holds a float
    (integers only); scenario overlay records validate against their own kinds.
 4. contracts/registry/components.v1.json regenerates byte-identically from the evidence register (ADR-0011).
 5. contracts/fixtures regenerates byte-identically from contracts/reference/generate_fixtures.py.
 6. The valid fixture world, with the shipped registries and the test overlays, breaks no reference rule, and the
    hand-derived world assertions (eligible lanes, closures) hold.
 7. Every scenario triggers exactly the rules it names; every rule is triggered by at least one scenario.
 8. Every invalid record is rejected by its schema with an error naming the expected location.
 9. Golden vectors: the reference functions reproduce every expected value exactly.
10. docs/evidence (a hash-checked export of the store: evidence plus the verdicts and preregistrations it cites) validates
    by kind and breaks no reference rule; then the computed status of the shipped registry (a pure fold; nothing stored).
11. Frozen legacy fixtures (contracts/fixtures/legacy) load at HEAD.
12. IDC Rule 07 and ADR-0035 lint over contracts/ and scripts/: no mailto, no address but the public one, no bare address
    in Markdown outside code formatting, and the product name only in product records.

Exit status is non-zero on any failure.  Usage:  python3 scripts/spec/validate.py [-v] [--rules]
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
FIXTURES = CONTRACTS / "fixtures"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(CONTRACTS / "reference"))

from jsonschema_subset import SUPPORTED, SchemaError, SchemaSet  # noqa: E402

from studio_ref import status  # noqa: E402
from studio_ref.canonical import float_paths, sha256_hex  # noqa: E402
from studio_ref.rules import RULES, run_all  # noqa: E402
from studio_ref.world import World, apply_overlay  # noqa: E402

PUBLIC_CONTACT = "hello@islanddevcrew.com"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
NOT_RECORDS = {"common.schema.json"}


class Report:
    def __init__(self, verbose: bool):
        self.verbose = verbose
        self.failures: list[str] = []
        self.counts: dict[str, int] = {}
        self.notes: list[str] = []

    def ok(self, what: str, n: int = 1) -> None:
        self.counts[what] = self.counts.get(what, 0) + n

    def fail(self, where: str, message: str) -> None:
        self.failures.append(f"FAIL {where}: {message}")

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def has_key(node, key: str) -> bool:
    if isinstance(node, dict):
        return key in node or any(has_key(v, key) for v in node.values())
    if isinstance(node, list):
        return any(has_key(v, key) for v in node)
    return False


# ----- 1: schemas ---------------------------------------------------------------------------------------------------

def kind_map(schemas: SchemaSet, rep: Report) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for name, schema in sorted(schemas.files.items()):
        if has_key(schema, "$id"):
            rep.fail(name, "schemas carry no $id (relative references only)")
        if name in NOT_RECORDS:
            continue
        kind = schema.get("properties", {}).get("kind", {})
        kinds = [kind["const"]] if "const" in kind else kind.get("enum", [])
        if not kinds:
            rep.fail(name, "record schema without a kind const or enum")
        if not {"kind", "schemaVersion"} <= set(schema.get("required", [])):
            rep.fail(name, "record schema must require kind and schemaVersion")
        for k in kinds:
            if k in mapping:
                rep.fail(name, f"kind {k} also claimed by {mapping[k]}")
            mapping[k] = name
    rep.ok("schemas", len(schemas.files))
    return mapping


# ----- 2: checker self-tests ----------------------------------------------------------------------------------------

def checker_self_tests(schemas: SchemaSet, rep: Report) -> None:
    S = lambda d: d  # noqa: E731
    cases = [
        (S({"type": "integer"}), 3, True), (S({"type": "integer"}), 3.5, False), (S({"type": "integer"}), "3", False),
        (S({"type": ["string", "null"]}), None, True), (S({"type": "string"}), True, False),
        (S({"enum": ["a", "b"]}), "a", True), (S({"enum": ["a", "b"]}), "c", False),
        (S({"const": 960}), 960, True), (S({"const": 960}), 480, False),
        (S({"required": ["k"]}), {}, False), (S({"required": ["k"]}), {"k": 1}, True),
        (S({"minProperties": 1}), {}, False), (S({"maxProperties": 1}), {"a": 1, "b": 2}, False),
        (S({"dependentRequired": {"index": ["total"]}}), {"index": 1}, False),
        (S({"dependentRequired": {"index": ["total"]}}), {"index": 1, "total": 2}, True),
        (S({"minItems": 2}), [1], False), (S({"maxItems": 1}), [1, 2], False), (S({"uniqueItems": True}), [1, 1], False),
        (S({"uniqueItems": True}), [1, 2], True), (S({"minimum": 1}), 0, False), (S({"maximum": 4}), 5, False),
        (S({"exclusiveMinimum": 0}), 0, False), (S({"exclusiveMaximum": 1}), 1, False), (S({"multipleOf": 960}), 1920, True),
        (S({"multipleOf": 960}), 1000, False), (S({"minLength": 2}), "a", False), (S({"maxLength": 2}), "abc", False),
        (S({"pattern": "^[0-9a-f]{4}$"}), "beef", True), (S({"pattern": "^[0-9a-f]{4}$"}), "BEEF", False),
        (S({"properties": {"a": {"type": "integer"}}}), {"a": "x"}, False),
        (S({"additionalProperties": False}), {"x": 1}, False),
        (S({"patternProperties": {"^[A-Z]$": {"type": "integer"}}, "additionalProperties": False}), {"A": 1}, True),
        (S({"patternProperties": {"^[A-Z]$": {"type": "integer"}}, "additionalProperties": False}), {"a": 1}, False),
        (S({"propertyNames": {"pattern": "^[a-z]+$"}}), {"Ab": 1}, False),
        (S({"items": {"type": "integer"}}), [1, "2"], False), (S({"prefixItems": [{"const": 1}]}), [2], False),
        (S({"contains": {"const": "x"}}), ["a"], False), (S({"contains": {"const": "x"}}), ["a", "x"], True),
        (S({"allOf": [{"minimum": 1}, {"maximum": 2}]}), 3, False), (S({"anyOf": [{"const": 1}, {"const": 2}]}), 3, False),
        (S({"oneOf": [{"type": "integer"}, {"minimum": 0}]}), 1, False), (S({"oneOf": [{"type": "integer"}, {"type": "string"}]}), "s", True),
        (S({"not": {"const": "fake"}}), "fake", False),
        (S({"if": {"properties": {"s": {"const": "failed"}}}, "then": {"required": ["error"]}}), {"s": "failed"}, False),
        (S({"if": {"properties": {"s": {"const": "failed"}}}, "then": {"required": ["error"]}, "else": {"required": ["ok"]}}), {"s": "ready"}, False),
        (S({"$ref": "common.schema.json#/$defs/sha256"}), "0" * 64, True), (S({"$ref": "common.schema.json#/$defs/sha256"}), "0" * 63, False),
        (S({"$ref": "common.schema.json#/$defs/gainDb"}), "1.20", False), (S({"$ref": "common.schema.json#/$defs/gainDb"}), "-1.20", True),
        (S({"$ref": "common.schema.json#/$defs/usd"}), "25.00", True), (S({"$ref": "common.schema.json#/$defs/usd"}), "25", False),
    ]
    for schema, instance, must_pass in cases:
        errors = schemas._validate(instance, schema, "common.schema.json", "$")
        if (not errors) != must_pass:
            rep.fail("checker self-test", f"{schema} on {instance!r}: expected {'pass' if must_pass else 'fail'}")
        else:
            rep.ok("checker self-tests")
    probe = SchemaSet.__new__(SchemaSet)
    probe.dir, probe._patterns = CONTRACTS / "schemas", {}
    probe.files = {"a.schema.json": {"type": "object", "unevaluatedProperties": False, "properties": {"x": {"$ref": "missing.schema.json#/$defs/x"}}}}
    problems = probe.check_all()
    if not any("unevaluatedProperties" in p for p in problems) or not any("unresolvable" in p for p in problems):
        rep.fail("checker self-test", "an unsupported keyword and a dangling $ref must both be refused")
    else:
        rep.ok("checker self-tests", 2)
    if "$id" in SUPPORTED:
        rep.fail("checker self-test", "$id must not be a supported keyword")


# ----- 3: every file by its kind ------------------------------------------------------------------------------------

def contract_files() -> list[Path]:
    files = [CONTRACTS / "product.json"] + sorted((CONTRACTS / "registry").rglob("*.json")) + sorted(FIXTURES.rglob("*.json"))
    return [f for f in files if f.exists()]


def validate_files(schemas: SchemaSet, kinds: dict[str, str], rep: Report) -> dict[Path, dict]:
    docs: dict[Path, dict] = {}
    for path in contract_files():
        doc = load(path)
        kind = doc.get("kind") if isinstance(doc, dict) else None
        schema = kinds.get(kind)
        if schema is None:
            rep.fail(rel(path), f"unknown kind {kind!r}")
            continue
        errors = schemas.validate(doc, schema)
        if errors:
            rep.fail(rel(path), f"{schema}: " + "; ".join(errors[:4]))
            continue
        if kind not in ("fixture.invalid-record", "fixture.scenario"):
            floats = float_paths(doc)
            if floats:
                rep.fail(rel(path), "non-integer numbers at " + ", ".join(floats[:3]))
                continue
        if kind == "fixture.scenario":
            bad = False
            for i, rec in enumerate(doc["overlay"]):
                rs = kinds.get(rec.get("kind"))
                errs = ["unknown kind"] if rs is None else schemas.validate(rec, rs)
                if errs:
                    rep.fail(rel(path), f"overlay[{i}] ({rec.get('kind')}): " + "; ".join(errs[:3]))
                    bad = True
            if bad:
                continue
        docs[path] = doc
        rep.ok("files valid by kind")
    return docs


# ----- 4 and 5: byte-identical regeneration -------------------------------------------------------------------------

def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_regeneration(rep: Report) -> None:
    sync = import_path("registry_sync", ROOT / "scripts/registry/sync.py")
    register = CONTRACTS / "registry/components.v1.json"
    if sync.generate() != register.read_bytes():
        rep.fail(rel(register), "does not regenerate byte-identically (run python3 scripts/registry/sync.py)")
    else:
        rep.ok("byte-identical regenerations")
    gen = import_path("generate_fixtures", CONTRACTS / "reference/generate_fixtures.py")
    planned = gen.plan_files()
    existing = {p for p in FIXTURES.rglob("*.json") if "legacy" not in p.relative_to(FIXTURES).parts}
    stale = [p for p, data in planned.items() if not p.exists() or p.read_bytes() != data]
    extra = existing - set(planned)
    for p in stale:
        rep.fail(rel(p), "fixture differs from generate_fixtures.py output")
    for p in sorted(extra):
        rep.fail(rel(p), "fixture not produced by generate_fixtures.py")
    if not stale and not extra:
        rep.ok("byte-identical regenerations")


# ----- 6 and 7: reference rules -------------------------------------------------------------------------------------

def base_documents(docs: dict[Path, dict]) -> list[dict]:
    base = []
    for path, doc in docs.items():
        parts = path.relative_to(CONTRACTS).parts
        if path == CONTRACTS / "product.json" or parts[0] == "registry" or parts[:2] in (("fixtures", "registry"), ("fixtures", "world")):
            if doc["kind"] != "fixture.world-assertions":
                base.append(doc)
    return base


def check_world(docs: dict[Path, dict], rep: Report) -> list[dict]:
    base = base_documents(docs)
    world = World(base)
    violations = run_all(world)
    for rule_id, where, message in violations:
        rep.fail(f"world {where}", f"[{rule_id}] {message}")
    if not violations:
        rep.ok("world records checked", len(world.records))
    assertions = docs.get(FIXTURES / "world/assertions.json")
    if assertions is None:
        rep.fail("fixtures/world/assertions.json", "missing")
        return base
    for a in assertions["eligible_lanes"]:
        art = world.artifacts.get(a["sha256"])
        if art is None:
            rep.fail("world assertion", f"{a['label']}: no such artifact")
            continue
        if set(art["provenance"]["eligible_lanes"]) != set(a["lanes"]) or world.computed_eligible(art) != set(a["lanes"]):
            rep.fail("world assertion", f"{a['label']}: eligible lanes are not {a['lanes']}")
        else:
            rep.ok("hand assertions")
    for c in assertions["closures"]:
        keeper = world.ids["keeper"].get(c["keeper_id"])
        if keeper is None or world.closure(keeper["artifact_sha256"]) != sorted(c["closure"]):
            rep.fail("world assertion", f"closure of {c['keeper_id']} is not {c['closure_labels']}")
        else:
            rep.ok("hand assertions")
    return base


def check_scenarios(docs: dict[Path, dict], base: list[dict], rep: Report) -> None:
    covered: set[str] = set()
    for path, doc in sorted(docs.items()):
        if doc["kind"] != "fixture.scenario":
            continue
        unknown = set(doc["expect_rules"]) - set(RULES)
        if unknown:
            rep.fail(rel(path), f"names unknown rules {sorted(unknown)}")
            continue
        world = World(apply_overlay(base, doc["overlay"], doc["remove"]))
        fired = run_all(world)
        got = sorted({r for r, _, _ in fired})
        if got != sorted(doc["expect_rules"]):
            detail = "; ".join(f"[{r}] {w}: {m}" for r, w, m in fired[:4])
            rep.fail(rel(path), f"expected {doc['expect_rules']}, rules fired {got} ({detail})")
            continue
        covered |= set(got)
        rep.ok("scenarios" if got else "valid scenarios")
        rep.log(f"  {doc['id']}: {got or 'valid'}")
    for rule_id in sorted(set(RULES) - covered):
        rep.fail("rule coverage", f"{rule_id} is never triggered by a scenario, so it could be vacuous")
    rep.ok("rules exercised", len(covered & set(RULES)))


# ----- 8: invalid records -------------------------------------------------------------------------------------------

def check_invalid_records(schemas: SchemaSet, kinds: dict[str, str], docs: dict[Path, dict], rep: Report) -> None:
    for path, doc in sorted(docs.items()):
        if doc["kind"] != "fixture.invalid-record":
            continue
        schema = kinds.get(doc["record_kind"])
        if schema is None:
            rep.fail(rel(path), f"unknown record_kind {doc['record_kind']}")
            continue
        errors = schemas.validate(doc["record"], schema)
        if not errors:
            rep.fail(rel(path), "the schema accepted a record it must reject")
        elif not any(doc["error_contains"] in e for e in errors):
            rep.fail(rel(path), f"rejected, but not for the named reason ({doc['error_contains']!r}); got: {errors[:2]}")
        else:
            rep.ok("invalid records rejected for the named reason")


# ----- 9: golden vectors --------------------------------------------------------------------------------------------

def check_vectors(docs: dict[Path, dict], base: list[dict], rep: Report) -> None:
    from studio_ref.vector_discovery import discover
    try:
        handlers = discover(ROOT)
    except (ValueError, OSError, ImportError) as exc:
        rep.fail("vector discovery", str(exc))
        return
    world = World(base)
    seen = set()
    for path, doc in sorted(docs.items()):
        kind = doc["kind"]
        if not kind.startswith("fixture.") or kind in ("fixture.scenario", "fixture.invalid-record", "fixture.world-assertions"):
            continue
        if kind not in handlers:
            rep.fail(rel(path), f"unknown vector kind: {kind}")
            continue
        if "legacy" not in path.relative_to(CONTRACTS).parts:
            if kind in seen:
                rep.fail(rel(path), f"duplicate vector kind: {kind}")
            seen.add(kind)
        for case in doc["cases"]:
            where = f"{rel(path)} [{case['name']}]"
            try:
                got, want = handlers[kind].evaluate(case, world)
                if got != want:
                    rep.fail(where, f"reference gives {got!r}, fixture expects {want!r}")
                else:
                    rep.ok(f"{kind} vectors")
            except (ValueError, KeyError, TypeError) as exc:
                rep.fail(where, str(exc))
    for kind in sorted(set(handlers) - seen):
        rep.fail("vectors", f"missing generated vector kind: {kind}")


# ----- 10: computed status of the shipped registry ------------------------------------------------------------------

def report_status(schemas: SchemaSet, kinds: dict[str, str], base: list[dict], rep: Report) -> None:
    """docs/evidence is a hash-checked export of the store (the system of record, ADR-0027): evidence records plus the
    canonical JSON of every verdict and preregistration they cite (no audio). Every file validates by kind, and the full
    reference rule set runs over the shipped registries plus those records, so a hand-committed passing record that
    lacks its declared checks, cites an unknown verdict or preregistration, or aims at another gate fails the gate
    instead of turning into a status."""
    shipped_regs = [d for d in base if d["kind"] in ("engine-profile-registry", "capability-registry", "component-register",
                                                      "lane-policy", "compute-tiers", "product") and not d.get("overlay")]
    shipped = World([d for d in shipped_regs if d["kind"] in ("engine-profile-registry", "capability-registry")])
    evidence, exported = [], []
    evidence_dir = ROOT / "docs/evidence"
    for path in sorted(evidence_dir.rglob("*.json")) if evidence_dir.exists() else []:
        doc = load(path)
        schema = kinds.get(doc.get("kind")) if isinstance(doc, dict) else None
        if schema is None:
            continue
        errors = schemas.validate(doc, schema)
        if errors:
            rep.fail(rel(path), "; ".join(errors[:3]))
            continue
        exported.append(doc)
        if doc["kind"] == "evidence":
            evidence.append(doc)
    if exported:
        for rule_id, where, message in run_all(World(shipped_regs + exported)):
            rep.fail(f"docs/evidence {where}", f"[{rule_id}] {message}")
        rep.ok("exported evidence records checked against every rule", len(exported))
    tally: dict[str, int] = {}
    for subject in list(shipped.profiles.values()) + list(shipped.capabilities.values()):
        mine = [e for e in evidence if e["subject"]["subject_id"] == subject["id"] and e["host_class"]]
        pairs = sorted({(e["profile_revision"], e["host_class"]) for e in mine}, key=str)
        if not pairs:
            tally["declared"] = tally.get("declared", 0) + 1
            continue
        for revision, host in pairs:
            s = status.compute_status(subject, evidence, revision, host)
            tally[s] = tally.get(s, 0) + 1
            rep.log(f"  status {subject['id']} @ {host}: {s}")
    rep.notes.append(f"computed status of {len(shipped.profiles)} shipped profiles and {len(shipped.capabilities)} capabilities "
                     f"from {len(evidence)} evidence records: " + ", ".join(f"{n} {s}" for s, n in sorted(tally.items())))


# ----- 11: legacy ---------------------------------------------------------------------------------------------------

def check_legacy(rep: Report) -> None:
    legacy = FIXTURES / "legacy"
    files = sorted(legacy.rglob("*.json")) if legacy.exists() else []
    if not files:
        rep.notes.append("no frozen legacy fixtures yet (they are frozen at the first release)")
    for path in files:
        rep.ok("legacy fixtures (validated with the files above)")


# ----- 12: lint -----------------------------------------------------------------------------------------------------

def lint(rep: Report) -> None:
    product = load(CONTRACTS / "product.json")
    name = product["productName"]
    if product["publicContactText"] != PUBLIC_CONTACT:
        rep.fail("contracts/product.json", "public contact must be the IDC role address")
    paths = [p for p in sorted(CONTRACTS.rglob("*")) + sorted((ROOT / "scripts").rglob("*")) if p.is_file() and p.suffix in (".json", ".py", ".md")]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "mail" + "to:" in text:
            rep.fail(rel(path), "contains a mailto link (IDC Rule 07)")
        if path.suffix == ".md":
            prose = re.sub(r"`[^`\n]*`", "", re.sub(r"^```.*?^```", "", text, flags=re.M | re.S))
            if EMAIL.search(prose):
                rep.fail(rel(path), "writes an address outside code formatting; GitHub would autolink it as mailto (IDC Rule 07, ADR-0037)")
        for m in EMAIL.finditer(text):
            if m.group(0) != PUBLIC_CONTACT:
                rep.fail(rel(path), f"contains an address other than the public contact: {m.group(0)}")
        if name in text and path.suffix == ".json":
            doc = load(path)
            is_product = doc.get("kind") == "product" or (doc.get("kind") == "fixture.invalid-record" and doc.get("record_kind") == "product")
            if not is_product:
                rep.fail(rel(path), "names the product outside a product record (ADR-0035)")
        elif name in text and path.suffix == ".py":
            rep.fail(rel(path), "names the product in code (ADR-0035)")
    rep.ok("files linted", len(paths))


# ----- main ---------------------------------------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if "--rules" in argv:
        for rule_id in sorted(RULES):
            print(f"{rule_id:36s} {RULES[rule_id][1]}")
        return 0
    rep = Report("-v" in argv)
    schemas = SchemaSet(CONTRACTS / "schemas")
    try:
        problems = schemas.check_all()
    except SchemaError as exc:
        problems = [str(exc)]
    for p in problems:
        rep.fail("schema check", p)
    kinds = kind_map(schemas, rep)
    checker_self_tests(schemas, rep)
    if problems:
        print("\n".join(rep.failures))
        return 1
    docs = validate_files(schemas, kinds, rep)
    try:
        check_regeneration(rep)
    except (ValueError, OSError, ImportError) as exc:
        rep.fail("fixture regeneration", str(exc))
    base = check_world(docs, rep)
    check_scenarios(docs, base, rep)
    check_invalid_records(schemas, kinds, docs, rep)
    check_vectors(docs, base, rep)
    report_status(schemas, kinds, base, rep)
    check_legacy(rep)
    lint(rep)
    for line in rep.failures:
        print(line)
    for key in sorted(rep.counts):
        print(f"ok  {rep.counts[key]:4d}  {key}")
    for note in rep.notes:
        print(f"note  {note}")
    print(f"{'FAILED' if rep.failures else 'PASSED'}: {len(rep.failures)} failure(s), {len(RULES)} reference rules")
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
