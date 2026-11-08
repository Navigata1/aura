"""Cross-file reference rules over a World (registries + records). Standard library only.

Each rule has a stable id, a one-line statement and a function that returns (where, message) pairs. run_all() returns
every violation as (rule_id, where, message). The validator requires the valid fixture world to produce none, every
fixture scenario to produce exactly the rule ids it names, and every rule to be named by at least one failing
scenario, so no rule is vacuous.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable

from . import audition, ledger, timemodel
from .canonical import ceil_cents, float_paths, self_hash, sha256_hex, sha_of, usd_text
from .world import CANDIDATE_ORIGINS, GENERATIVE_ORIGINS, LANES, PROPAGATING, World, identity

Finding = tuple[str, str]
RULES: dict[str, tuple[Callable[[World], list[Finding]], str]] = {}

TASK_USE = {
    "cover": "conditioning", "reference_timbre": "conditioning", "assemble-audio": "conditioning",
    "text_to_song": "engine_input", "score_to_song": "engine_input", "instrumental": "engine_input", "guide": "engine_input",
    "repaint": "edit_source", "extend": "edit_source", "extract": "edit_source", "lego": "edit_source", "complete": "edit_source",
    "separate": "separation_input", "measure": "loudness_measure", "adherence": "analysis", "transcribe": "analysis",
    "probe": "analysis", "export": "export",
}
ANALYSIS_JOB_KINDS = {"measure", "adherence", "transcribe", "probe"}
LISTEN_ONLY_USES = {"listen", "loudness_measure", "eval_anchor"}
SUNO_BASE_USES = {"listen", "loudness_measure", "dsp_finish"}
ROUTE_TASK = {"R1": "score_to_song", "R2-raw": "cover", "R2-synth": "cover", "text": "text_to_song"}
JOB_TRANSITIONS = {
    "queued": {"awaiting_approval", "preparing", "failed", "cancelled"},
    "awaiting_approval": {"preparing", "failed", "cancelled"},
    "preparing": {"loading", "failed", "cancelled"},
    "loading": {"generating", "failed", "cancelled"},
    "generating": {"analyzing", "ready", "failed", "cancelled"},
    "analyzing": {"ready", "failed", "cancelled"},
}
LOADED_STATES = {"loading", "generating", "ready"}
PATHLIKE = re.compile(r"(://|^/|^~|^\\\\|^[A-Za-z]:[\\/]|\.\./)")


def rule(rule_id: str, statement: str):
    def deco(fn):
        RULES[rule_id] = (fn, statement)
        return fn
    return deco


def at(doc: dict) -> str:
    return "/".join(str(p) for p in identity(doc))


def ts(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def run_all(world: World) -> list[tuple[str, str, str]]:
    out = []
    for rule_id in sorted(RULES):
        fn, _ = RULES[rule_id]
        for where, message in fn(world):
            out.append((rule_id, where, message))
    return out


# ----- canonical form and self-hashes ------------------------------------------------------------------------------

@rule("canonical.integers_only", "No record or registry holds a non-integer JSON number; quantities are decimal strings.")
def _integers_only(w: World) -> list[Finding]:
    return [(at(d), f"non-integer number at {p}") for d in w.docs for p in float_paths(d)]


@rule("record.content_hash", "A record's self-hash (content_sha256, quote_sha256, prereg_sha256) equals the sha256 of its canonical JSON.")
def _content_hash(w: World) -> list[Finding]:
    out = []
    for kind in ("melody-spec", "song-spec"):
        for d in w.by_kind.get(kind, []):
            if d["content_sha256"] != self_hash(d, "content_sha256"):
                out.append((at(d), "content_sha256 does not match the record"))
    for q in w.by_kind.get("quote", []):
        if q["quote_sha256"] != sha_of(q["terms"]):
            out.append((at(q), "quote_sha256 does not match the terms"))
    for p in w.by_kind.get("prereg", []):
        if p["prereg_sha256"] != sha_of(p["body"]):
            out.append((at(p), "prereg_sha256 does not match the body"))
    return out


# ----- registry ------------------------------------------------------------------------------------------------------

@rule("registry.unique_ids", "Profile, component and capability ids are unique across the registry and its overlays.")
def _unique_ids(w: World) -> list[Finding]:
    return [("registry", f"duplicate {d}") for d in w.duplicates]


@rule("registry.overlay_test_only", "Overlay registries hold only test_only entries, and the shipped registries hold none.")
def _overlay_test_only(w: World) -> list[Finding]:
    out = []
    for reg in w.registries:
        if reg["kind"] == "engine-profile-registry":
            items = reg["profiles"]
        elif reg["kind"] == "component-register":
            items = reg["components"]
        else:
            continue
        for item in items:
            if item["test_only"] != reg["overlay"]:
                out.append((at(reg), f"{item['id']}: test_only={item['test_only']} in overlay={reg['overlay']}"))
    return out


@rule("license.component_known", "Every component named by a profile, license record or license chain is in the component register.")
def _component_known(w: World) -> list[Finding]:
    out = []
    for p in w.profiles.values():
        for cid in p["components"] + [e["component_id"] for e in p["license_record"]]:
            if cid not in w.components:
                out.append((f"profile/{p['id']}", f"unknown component {cid}"))
    for d in w.by_kind.get("artifact", []):
        for e in d["provenance"]["license_chain"]:
            if e["component_id"] not in w.components:
                out.append((at(d), f"unknown component {e['component_id']}"))
    for d in w.by_kind.get("export-manifest", []):
        for e in d["license_chain"]:
            if e["component_id"] not in w.components:
                out.append((at(d), f"unknown component {e['component_id']}"))
    return out


@rule("lane.profile_components", "A profile's allowed_lanes equal the intersection of its components' allowed lanes.")
def _profile_components(w: World) -> list[Finding]:
    out = []
    for p in w.profiles.values():
        expected = w.component_lanes(c for c in p["components"] if c in w.components)
        if set(p["allowed_lanes"]) != expected:
            out.append((f"profile/{p['id']}", f"allowed_lanes {sorted(p['allowed_lanes'])} != components' {sorted(expected)}"))
    return out


@rule("license.profile_record", "A profile's license_record copies the register's terms for exactly its components.")
def _profile_record(w: World) -> list[Finding]:
    out = []
    for p in w.profiles.values():
        known = [c for c in p["components"] if c in w.components]
        record = [e for e in p["license_record"] if e["component_id"] in w.components]
        if sorted(e["component_id"] for e in record) != sorted(known):
            out.append((f"profile/{p['id']}", "license_record does not list exactly the profile's components"))
        for e in record:
            if e != w.register_entry(e["component_id"]):
                out.append((f"profile/{p['id']}", f"license_record terms for {e['component_id']} differ from the register"))
    return out


def carries_weights(component: dict) -> bool:
    return not component["weights_license"].lower().startswith("n/a")


@rule("license.weights_pin", "A profile whose real components carry weights or a release blocker pins where its weights come from (Hugging Face, URL or package), with license acceptance required; FakeEngine-only profiles are exempt.")
def _weights_pin(w: World) -> list[Finding]:
    out = []
    for p in w.profiles.values():
        real = [w.components[c] for c in p["components"] if c in w.components and not w.components[c].get("test_only", False)]
        needs = [c["id"] for c in real if carries_weights(c) or c["release_blockers"]]
        if needs and p["pins"]["weights"] is None:
            out.append((f"profile/{p['id']}", f"components {needs} carry weights or release blockers, but no weights pin is declared"))
    return out


@rule("registry.lane_policy_consistent", "No component allows a lane that forbids one of its release-blocker classes.")
def _lane_policy(w: World) -> list[Finding]:
    out = []
    for c in w.components.values():
        for lane in c["allowed_lanes"]:
            clash = w.lane_forbidden.get(lane, set()) & set(c["release_blockers"])
            if clash:
                out.append((f"component/{c['id']}", f"lane {lane} forbids {sorted(clash)}"))
    return out


@rule("registry.tier_profiles_exist", "Every profile placed by compute-tiers or a compute profile exists, and tiers 1-4 each appear once.")
def _tier_profiles(w: World) -> list[Finding]:
    out = []
    if w.tiers is not None:
        if sorted(t["tier"] for t in w.tiers["tiers"]) != [1, 2, 3, 4]:
            out.append(("compute-tiers", "tiers must be exactly 1, 2, 3, 4"))
        for t in w.tiers["tiers"]:
            for p in t["placements"]:
                if p["profile_id"] not in w.profiles:
                    out.append(("compute-tiers", f"tier {t['tier']}: unknown profile {p['profile_id']}"))
    for cp in w.by_kind.get("compute-profile", []):
        for p in cp["placements"]:
            if p["profile_id"] not in w.profiles:
                out.append((at(cp), f"unknown profile {p['profile_id']}"))
    return out


@rule("registry.profile_known", "Every profile a job, candidate, plan, brief, quote, preregistration or task request names is declared.")
def _profile_known(w: World) -> list[Finding]:
    out = []

    def check(doc: dict, pid: str | None) -> None:
        if pid is not None and pid not in w.profiles:
            out.append((at(doc), f"unknown profile {pid}"))

    for d in w.by_kind.get("job", []) + w.by_kind.get("candidate", []) + w.by_kind.get("task-request", []):
        check(d, d["profile_id"])
    for d in w.by_kind.get("generation-request", []):
        for p in d["plan"]:
            check(d, p["profile_id"])
        for p in d["declined"]:
            check(d, p["profile_id"])
    for d in w.by_kind.get("eval-brief", []):
        for c in d["compared"]:
            check(d, c["profile_id"])
    for d in w.by_kind.get("quote", []):
        for j in d["terms"]["jobs"]:
            check(d, j["profile_id"])
    for d in w.by_kind.get("prereg", []):
        for p in d["body"]["pins"]:
            check(d, p["profile_id"])
    return out


@rule("registry.results_cite_evidence", "Every results_local entry cites a passing evidence record for that subject and host class.")
def _results_cite(w: World) -> list[Finding]:
    out = []
    subjects = [(f"profile/{p['id']}", p) for p in w.profiles.values()] + [(f"capability/{c['id']}", c) for c in w.capabilities.values()]
    for where, s in subjects:
        for r in s["results_local"]:
            ev = w.ids["evidence"].get(r["evidence_id"])
            if ev is None:
                out.append((where, f"results_local cites missing evidence {r['evidence_id']}"))
                continue
            host_ok = ev["host_class"] == r["host_class"] if "host_class" in r else True
            if ev["subject"]["subject_id"] != s["id"] or not host_ok or ev["result"] != "pass":
                out.append((where, f"evidence {r['evidence_id']} is not a passing record for this subject and host class"))
    return out


@rule("evidence.gates", "Evidence aims only at its subject's gates; synthetic evidence never meets a benchmark gate or a smoke gate that forbids it; preregistration hashes resolve only to prereg records and verdicts resolve; concluded benchmark/hum-benchmark results are unsupported until result binding exists; a passing smoke record lists every check its gate declares, passing, and a listening check cites an owner-ui verdict on this revision's own candidates.")
def _evidence_gates(w: World) -> list[Finding]:
    out = []
    prereg_hashes = {p["prereg_sha256"] for p in w.by_kind.get("prereg", [])}
    for e in w.by_kind.get("evidence", []):
        sid = e["subject"]["subject_id"]
        subject = w.profiles.get(sid) if e["subject"]["subject_type"] == "profile" else w.capabilities.get(sid)
        if e["prereg_sha256"] is not None and e["prereg_sha256"] not in prereg_hashes:
            out.append((at(e), "unknown preregistration hash"))
        for vid in e["verdict_ids"]:
            if vid not in w.ids["verdict"]:
                out.append((at(e), f"unknown verdict {vid}"))
        # A hash and verdict ids cannot bind the set, quotas, thresholds, pins and host to a conclusion.
        # Check before gate routing so a missing/wrong gate cannot bypass this admission refusal.
        if e["check"] in ("benchmark", "hum-benchmark") and e["result"] != "inconclusive":
            out.append((at(e), "benchmark conclusion unsupported: a bound concluded-result contract is required"))
        if e["gate_id"] is None:
            continue
        if subject is None:
            out.append((at(e), f"gate {e['gate_id']} on unknown subject {sid}"))
            continue
        if "gates" in subject:
            smoke, bench = subject["gates"]["smoke"], subject["gates"]["benchmark"]
        else:
            smoke, bench = subject["gate"], None
        if e["gate_id"].startswith("benchmark."):
            if bench is None or e["gate_id"] != bench["gate_id"]:
                out.append((at(e), f"{e['gate_id']} is not this subject's benchmark gate"))
            if e["synthetic"]:
                out.append((at(e), "synthetic evidence aimed at a benchmark gate"))
            if e["check"] not in ("benchmark", "hum-benchmark"):
                out.append((at(e), f"a {e['check']} record cannot meet a benchmark gate"))
        else:
            if e["gate_id"] != smoke["gate_id"]:
                out.append((at(e), f"{e['gate_id']} is not this subject's smoke gate"))
            elif e["synthetic"] and not smoke["synthetic_allowed"] and not subject.get("test_only", False):
                out.append((at(e), "synthetic evidence aimed at a smoke gate that does not allow it"))
            elif e["check"] == "smoke" and e["result"] == "pass":
                out.extend(_smoke_checks(w, e, smoke))
    return out


def _smoke_checks(w: World, e: dict, gate: dict) -> list[Finding]:
    """A passing smoke record carries every declared check, passing; a listening check's verdict is Jon's (owner-ui)
    and was given in an audition over this subject's own candidates at this revision."""
    out = []
    results = {c["check"]: c for c in e["checks"]}
    missing = [c for c in gate["checks"] if c not in results or results[c]["result"] != "pass"]
    if missing:
        out.append((at(e), f"a passing smoke record omits or fails declared checks {missing}"))
    for c in e["checks"]:
        vid = c["verdict_id"]
        if vid is None:
            continue
        if vid not in e["verdict_ids"]:
            out.append((at(e), f"check {c['check']} cites verdict {vid}, which verdict_ids does not list"))
        v = w.ids["verdict"].get(vid)
        if v is None:
            continue
        if v["act"]["scope"] != "owner-ui":
            out.append((at(e), f"verdict {vid} is not an owner-ui act"))
        aud = w.ids["audition"].get(v["audition_id"])
        if aud is None or e["subject"]["subject_type"] != "profile":
            continue
        for cid in aud["candidate_ids"]:
            cand = w.ids["candidate"].get(cid)
            if cand is not None and (cand["profile_id"] != e["subject"]["subject_id"] or cand["profile_revision"] != e["profile_revision"]):
                out.append((at(e), f"verdict {vid} answers candidate {cid} of another profile or revision"))
                break
    return out


# ----- lanes, licenses and provenance --------------------------------------------------------------------------------

@rule("lane.artifact_eligible", "eligible_lanes = components' lanes over the license chain, intersected with derived_from/converted_from parents only and with an import's own eligible lanes.")
def _artifact_eligible(w: World) -> list[Finding]:
    out = []
    for d in w.by_kind.get("artifact", []):
        expected = w.computed_eligible(d)
        if set(d["provenance"]["eligible_lanes"]) != expected:
            out.append((at(d), f"eligible_lanes {sorted(d['provenance']['eligible_lanes'])} != computed {sorted(expected)}"))
    return out


@rule("license.chain_complete", "An artifact's license chain is its profile's components plus its audio parents' chains, with the register's terms; a DAW bounce carries the license chains of the studio exports it contains.")
def _chain_complete(w: World) -> list[Finding]:
    out = []
    for d in w.by_kind.get("artifact", []):
        prov = d["provenance"]
        ids = [e["component_id"] for e in prov["license_chain"]]
        if len(ids) != len(set(ids)):
            out.append((at(d), "duplicate component in license chain"))
        for e in prov["license_chain"]:
            entry = w.register_entry(e["component_id"])
            if entry is not None and e != entry:
                out.append((at(d), f"terms for {e['component_id']} differ from the register"))
        if d["origin"] == "imported_mix":
            expected = {"suno-v6"} if d["sha256"] in w.suno_imports else set()
            terms = w.import_terms_by_artifact.get(d["sha256"])
            if terms is not None and terms["source_service"] == "daw_bounce":
                for ref in terms["contains_studio_exports"]:
                    m = w.ids["export-manifest"].get(ref["export_id"])
                    expected |= {e["component_id"] for e in m["license_chain"]} if m else set()
        else:
            expected = set()
            engine = prov["engine"]
            if engine is not None and engine["profile_id"] in w.profiles:
                expected |= {c for c in w.profiles[engine["profile_id"]]["components"] if c in w.components}
            for parent in prov["parents"]:
                if parent["edge"] in PROPAGATING and parent["sha256"] in w.artifacts:
                    expected |= {e["component_id"] for e in w.artifacts[parent["sha256"]]["provenance"]["license_chain"]}
        if set(ids) != expected:
            out.append((at(d), f"license chain {sorted(set(ids))} != expected {sorted(expected)}"))
    return out


@rule("provenance.parents_exist", "Every parent edge names an artifact in the store.")
def _parents_exist(w: World) -> list[Finding]:
    return [(at(d), f"parent {p['sha256'][:12]} ({p['edge']}) is not in the store")
            for d in w.by_kind.get("artifact", []) for p in d["provenance"]["parents"] if p["sha256"] not in w.artifacts]


@rule("provenance.acyclic", "Parent edges of every type form no cycle.")
def _acyclic(w: World) -> list[Finding]:
    out = []
    state: dict[str, int] = {}

    def visit(sha: str, trail: list[str]) -> None:
        state[sha] = 1
        for p in w.artifacts[sha]["provenance"]["parents"]:
            nxt = p["sha256"]
            if nxt not in w.artifacts:
                continue
            if state.get(nxt) == 1:
                out.append((f"artifact/{nxt}", "cycle through " + " -> ".join(s[:8] for s in trail + [nxt])))
            elif nxt not in state:
                visit(nxt, trail + [nxt])
        state[sha] = 2

    for sha in sorted(w.artifacts):
        if sha not in state:
            visit(sha, [sha])
    return out


@rule("provenance.sidecar_matches", "A provenance sidecar names its own blob and equals the artifact record.")
def _sidecar(w: World) -> list[Finding]:
    out = []
    for s in w.by_kind.get("provenance-sidecar", []):
        if s["blob_sha256"] != s["artifact"]["sha256"]:
            out.append((at(s), "blob_sha256 != artifact.sha256"))
        record = w.artifacts.get(s["artifact"]["sha256"])
        if record is not None and record != s["artifact"]:
            out.append((at(s), "sidecar artifact differs from the artifact record"))
    return out


@rule("provenance.job_output", "An artifact's producing job exists, lists it as an output and matches its profile, revision, seed, project and lane; every job output is a known artifact or record.")
def _job_output(w: World) -> list[Finding]:
    out = []
    for d in w.by_kind.get("artifact", []):
        prov = d["provenance"]
        jid = prov["producing_job_id"]
        if jid is None:
            continue
        job = w.ids["job"].get(jid)
        if job is None:
            out.append((at(d), f"producing job {jid} is missing"))
            continue
        engine = prov["engine"]
        if d["sha256"] not in {o["sha256"] for o in job["outputs"]}:
            out.append((at(d), f"job {jid} does not list this artifact as an output"))
        if (engine["profile_id"], engine["profile_revision"], engine["seed"]) != (job["profile_id"], job["profile_revision"], job["seed"]):
            out.append((at(d), f"profile, revision or seed differ from job {jid}"))
        if d["project_id"] != job["project_id"] or prov["operator_lane"] != job["lane"]:
            out.append((at(d), f"project or lane differ from job {jid}"))
    for job in w.by_kind.get("job", []):
        for o in job["outputs"]:
            art = w.artifacts.get(o["sha256"])
            if art is None and o["sha256"] not in w.record_hashes:
                out.append((at(job), f"output {o['role']} is neither a stored artifact nor a known record"))
            elif art is not None and art["provenance"]["producing_job_id"] != job["id"]:
                out.append((at(job), f"output {o['role']} names another job as its producer"))
    return out


@rule("provenance.synthetic_propagates", "Anything made from synthetic test material, or by a test_only profile, is itself synthetic_test.")
def _synthetic(w: World) -> list[Finding]:
    out = []
    for d in w.by_kind.get("artifact", []):
        if d["synthetic_test"]:
            continue
        prov = d["provenance"]
        if any(w.artifacts.get(p["sha256"], {}).get("synthetic_test") for p in prov["parents"]):
            out.append((at(d), "a parent is synthetic_test but this artifact is not"))
        engine = prov["engine"]
        if engine is not None and w.profiles.get(engine["profile_id"], {}).get("test_only"):
            out.append((at(d), "made by a test_only profile but not synthetic_test"))
    return out


@rule("retention.keeper_closure", "Captures, imports and the audio closure of every keeper are irreplaceable.")
def _retention(w: World) -> list[Finding]:
    out = []
    must = set()
    for k in w.by_kind.get("keeper", []):
        must |= set(w.closure(k["artifact_sha256"]))
    for d in w.by_kind.get("artifact", []):
        if d["origin"] in ("human_recording", "imported_mix"):
            must.add(d["sha256"])
    for sha in sorted(must):
        art = w.artifacts.get(sha)
        if art is not None and art["retention_class"] != "irreplaceable":
            out.append((at(art), f"retention_class {art['retention_class']} but must be irreplaceable"))
    return out


@rule("project.graph_complete", "The project graph lists exactly the artifacts, revisions, requests, keepers, exports, references, edits and timelines that name the project, and its heads are the latest revisions.")
def _graph(w: World) -> list[Finding]:
    out = []
    projects = w.ids["project"]
    owned: dict[str, dict[str, set]] = {pid: {} for pid in projects}

    def own(pid: str | None, field: str, value, where: str) -> None:
        if pid is None:
            return
        if pid not in projects:
            out.append((where, f"names unknown project {pid}"))
            return
        owned[pid].setdefault(field, set()).add(value)

    for d in w.by_kind.get("artifact", []):
        own(d["project_id"], "artifacts", d["sha256"], at(d))
    for d in w.by_kind.get("melody-spec", []):
        own(d["project_id"], "melody_ids", d["melody_id"], at(d))
    for d in w.by_kind.get("song-spec", []):
        own(d["project_id"], "song_ids", d["song_id"], at(d))
    for kind, field in (("generation-request", "generation_request_ids"), ("keeper", "keeper_ids"),
                        ("export-manifest", "export_ids"), ("reference", "reference_ids"),
                        ("edit-operation", "edit_operation_ids"), ("timeline", "timeline_ids")):
        for d in w.by_kind.get(kind, []):
            own(d["project_id"], field, d["id"], at(d))
    known = {"artifacts": set(w.artifacts), "melody_ids": {k[0] for k in w.melodies}, "song_ids": {k[0] for k in w.songs},
             "generation_request_ids": set(w.ids["generation-request"]), "keeper_ids": set(w.ids["keeper"]),
             "export_ids": set(w.ids["export-manifest"]), "reference_ids": set(w.ids["reference"]),
             "edit_operation_ids": set(w.ids["edit-operation"]), "timeline_ids": set(w.ids["timeline"])}
    for pid, p in projects.items():
        for field, members in known.items():
            listed = set(p[field])
            for missing in sorted(owned[pid].get(field, set()) - listed):
                out.append((at(p), f"{field} does not list {missing}"))
            for unknown in sorted(listed - members):
                out.append((at(p), f"{field} lists unknown {unknown}"))
        heads = p["heads"]
        if heads["melody"] is not None:
            revs = [k[1] for k in w.melodies if k[0] == heads["melody"]["melody_id"]]
            if not revs or heads["melody"]["rev"] != max(revs):
                out.append((at(p), "melody head is not the latest revision"))
        if heads["song"] is not None:
            revs = [k[1] for k in w.songs if k[0] == heads["song"]["song_id"]]
            if not revs or heads["song"]["rev"] != max(revs):
                out.append((at(p), "song head is not the latest revision"))
    return out


@rule("lane.store_write", "No artifact sits in a project whose current lane is not in its eligible_lanes (write path and lane change).")
def _store_write(w: World) -> list[Finding]:
    out = []
    for p in w.by_kind.get("project", []):
        for sha in p["artifacts"]:
            art = w.artifacts.get(sha)
            if art is not None and p["operator_lane"] not in art["provenance"]["eligible_lanes"]:
                out.append((at(p), f"artifact {sha[:12]} is not eligible for lane {p['operator_lane']}"))
    return out


@rule("lane.admission", "A job runs in its project's lane at admission; the profile allows the lane and the task; audio-ancestry inputs allow the lane.")
def _admission(w: World) -> list[Finding]:
    out = []
    for job in w.by_kind.get("job", []):
        project = w.ids["project"].get(job["project_id"])
        if project is None:
            out.append((at(job), f"unknown project {job['project_id']}"))
            continue
        lane = w.project_lane_at(project, job["created_at"])
        if job["lane"] != lane:
            out.append((at(job), f"job lane {job['lane']} != project lane {lane} at admission"))
        profile = w.profiles.get(job["profile_id"])
        if profile is not None:
            if job["lane"] not in profile["allowed_lanes"]:
                out.append((at(job), f"profile {profile['id']} does not allow lane {job['lane']}"))
            if job["task"] not in profile["tasks"]:
                out.append((at(job), f"profile {profile['id']} does not declare task {job['task']}"))
        if job["job_kind"] in ANALYSIS_JOB_KINDS:
            continue
        for inp in job["inputs"]:
            art = w.artifacts.get(inp["sha256"])
            if art is not None and job["lane"] not in art["provenance"]["eligible_lanes"]:
                out.append((at(job), f"input {inp['role']} is not eligible for lane {job['lane']}"))
    return out


@rule("use.allowed_uses", "Every job input's allowed_uses include the use its task makes of it.")
def _allowed_uses(w: World) -> list[Finding]:
    out = []
    for job in w.by_kind.get("job", []):
        use = TASK_USE[job["task"]]
        for inp in job["inputs"]:
            art = w.artifacts.get(inp["sha256"])
            if art is not None and use not in art["provenance"]["allowed_uses"]:
                out.append((at(job), f"input {inp['role']} does not allow {use}"))
    return out


@rule("use.reference_permission", "A reference's audio allows no more than its permission grants; a listening-only reference allows only listening uses; conditioning needs a grant.")
def _reference_permission(w: World) -> list[Finding]:
    out = []
    refs = w.ids["reference"]
    for r in refs.values():
        art = w.artifacts.get(r["artifact_sha256"])
        if art is None:
            out.append((at(r), "reference audio is not in the store"))
            continue
        uses = set(art["provenance"]["allowed_uses"])
        if not uses <= set(r["permission"]["granted_uses"]):
            out.append((at(r), f"audio allows {sorted(uses - set(r['permission']['granted_uses']))} beyond the permission"))
        if r["permission"]["listening_only"] and not uses <= LISTEN_ONLY_USES:
            out.append((at(r), f"listening-only reference audio allows {sorted(uses - LISTEN_ONLY_USES)}"))
    for s in w.by_kind.get("song-spec", []):
        for ref in s["references"]:
            r = refs.get(ref["reference_id"])
            if r is None:
                out.append((at(s), f"unknown reference {ref['reference_id']}"))
            elif ref["use"] == "conditioning" and (r["permission"]["listening_only"] or "conditioning" not in r["permission"]["granted_uses"]):
                out.append((at(s), f"reference {r['id']} is not granted for conditioning"))
    return out


@rule("use.suno_boundary", "A Suno import allows only listen, loudness_measure and dsp_finish plus uses an owner-signed risk acceptance names; it is never a reference, a candidate or an audition arm.")
def _suno(w: World) -> list[Finding]:
    out = []
    accepted: dict[str, set] = {}
    for ra in w.by_kind.get("risk-acceptance", []):
        accepted.setdefault(ra["subject_sha256"], set()).update(ra["uses_added"])
    for sha in sorted(w.suno_imports):
        art = w.artifacts.get(sha)
        if art is None:
            continue
        extra = set(art["provenance"]["allowed_uses"]) - SUNO_BASE_USES - accepted.get(sha, set())
        if extra:
            out.append((at(art), f"Suno import allows {sorted(extra)} without a risk acceptance"))
    for r in w.by_kind.get("reference", []):
        if r["artifact_sha256"] in w.suno_imports:
            out.append((at(r), "a Suno import is never a reference"))
    arms = {cid for s in w.by_kind.get("audition", []) for cid in s["candidate_ids"]}
    for c in w.by_kind.get("candidate", []):
        if c["artifact_sha256"] in w.suno_imports:
            out.append((at(c), "a Suno import is never a candidate" + (" or an audition arm" if c["id"] in arms else "")))
    return out


@rule("use.import_terms", "An import's uses and lanes follow its source: its audio allows no use its terms do not; a licensed import's uses lie within its license grant; a DAW bounce's eligible lanes are the intersection of the studio exports it names (each existing with that closure hash); a Suno import is llc-eligible only when the LLC holds the account or a written license; a detected Suno mark forces source suno, and a detected studio export tag names an export the import lists.")
def _import_terms(w: World) -> list[Finding]:
    out = []
    accepted: dict[str, set] = {}
    for ra in w.by_kind.get("risk-acceptance", []):
        accepted.setdefault(ra["subject_sha256"], set()).update(ra["uses_added"])
    for t in w.by_kind.get("import-terms", []):
        src = t["source_service"]
        art = w.artifacts.get(t["artifact_sha256"])
        if art is not None:
            extra = set(art["provenance"]["allowed_uses"]) - set(t["base_allowed_uses"]) - accepted.get(t["artifact_sha256"], set())
            if extra and src != "suno":
                out.append((at(t), f"the imported audio allows {sorted(extra)} beyond its terms"))
        if src == "licensed" and t["license_grant"] is not None:
            beyond = set(t["base_allowed_uses"]) - set(t["license_grant"]["granted_uses"])
            if beyond:
                out.append((at(t), f"uses {sorted(beyond)} are not granted by the license record"))
        if src == "daw_bounce":
            lanes = set(LANES)
            for ref in t["contains_studio_exports"]:
                m = w.ids["export-manifest"].get(ref["export_id"])
                if m is None or m["closure_sha256"] != ref["closure_sha256"]:
                    out.append((at(t), f"names export {ref['export_id']}, which does not exist with that closure"))
                    continue
                lanes &= set(m["eligible_lanes"])
            if set(t["eligible_lanes"]) != lanes:
                out.append((at(t), f"a DAW bounce's lanes are {sorted(lanes)} (the exports it contains), not {sorted(t['eligible_lanes'])}"))
        if src == "suno":
            holder = t["account_holder"]
            llc_ok = holder is not None and (holder["holder"] == "llc" or holder["llc_license_in_writing"])
            if "llc" in t["eligible_lanes"] and not llc_ok:
                out.append((at(t), "a Suno import from Jon's own account is llc-eligible only with a written license to the LLC"))
        listed = {r["export_id"] for r in t["contains_studio_exports"]}
        for mark in t["detected_marks"]:
            if mark["mark"] == "suno_provenance" and src != "suno":
                out.append((at(t), f"a detected Suno mark forces source suno, not {src}"))
            if mark["mark"] == "studio_export_tag" and mark["export_id"] not in listed:
                out.append((at(t), "a detected studio export tag names an export the import does not list"))
    return out


@rule("use.egress_forbidden", "No Suno import and no listening-only reference ever leaves the studio host (quote and job egress).")
def _egress(w: World) -> list[Finding]:
    out = []
    listening = {r["artifact_sha256"] for r in w.by_kind.get("reference", []) if r["permission"]["listening_only"]}
    forbidden = w.suno_imports | listening
    for q in w.by_kind.get("quote", []):
        for e in q["terms"]["egress"]:
            if e["sha256"] in forbidden:
                out.append((at(q), f"egress lists forbidden asset {e['sha256'][:12]}"))
    for job in w.by_kind.get("job", []):
        for e in job["egress"]:
            if e["sha256"] in forbidden:
                out.append((at(job), f"egress lists forbidden asset {e['sha256'][:12]}"))
    return out


# ----- candidates, requests, auditions, keepers, exports -------------------------------------------------------------

@rule("candidate.artifact_origin", "A candidate's audio is a generated artifact from its own job, with matching profile, revision, seed, project and synthetic flag; its preview converts it.")
def _candidate_origin(w: World) -> list[Finding]:
    out = []
    for c in w.by_kind.get("candidate", []):
        art = w.artifacts.get(c["artifact_sha256"])
        if art is None:
            out.append((at(c), "candidate audio is not in the store"))
            continue
        if art["origin"] not in CANDIDATE_ORIGINS:
            out.append((at(c), f"origin {art['origin']} cannot be a candidate"))
        engine = art["provenance"]["engine"] or {}
        if (art["provenance"]["producing_job_id"], engine.get("profile_id"), engine.get("profile_revision"), engine.get("seed")) != \
                (c["job_id"], c["profile_id"], c["profile_revision"], c["seed"]):
            out.append((at(c), "job, profile, revision or seed differ from the artifact's provenance"))
        if art["project_id"] != c["project_id"] or art["synthetic_test"] != c["synthetic_test"]:
            out.append((at(c), "project or synthetic flag differ from the artifact"))
        if c["preview_sha256"] is not None:
            prev = w.artifacts.get(c["preview_sha256"])
            if prev is None or prev["origin"] != "preview" or {"edge": "converted_from", "sha256": c["artifact_sha256"]} not in prev["provenance"]["parents"]:
                out.append((at(c), "preview is not a preview converted from the candidate"))
    return out


@rule("request.plan_consistent", "A plan has candidate_count entries whose profiles do their route's task; candidates, jobs and labels match the plan; 'unbenchmarked routes' stays while benchmark conclusions are unsupported.")
def _plan(w: World) -> list[Finding]:
    out = []
    for r in w.by_kind.get("generation-request", []):
        song = w.songs.get((r["song"]["song_id"], r["song"]["rev"]))
        if song is not None and len(r["plan"]) != song["candidate_count"]:
            out.append((at(r), f"plan has {len(r['plan'])} entries but the SongSpec asks for {song['candidate_count']}"))
        if sorted(p["ordinal"] for p in r["plan"]) != list(range(1, len(r["plan"]) + 1)):
            out.append((at(r), "plan ordinals must be 1..n"))
        for p in r["plan"]:
            prof = w.profiles.get(p["profile_id"])
            if prof is not None and ROUTE_TASK[p["route"]] not in prof["tasks"]:
                out.append((at(r), f"{p['profile_id']} cannot do route {p['route']}"))
        cands = [c for c in w.by_kind.get("candidate", []) if c["source"].get("generation_request_id") == r["id"]]
        if {c["id"] for c in cands} != set(r["candidate_ids"]):
            out.append((at(r), "candidate_ids differ from the candidates that name this request"))
        plan = {p["ordinal"]: p for p in r["plan"]}
        for c in cands:
            p = plan.get(c["ordinal"])
            if p is None or (p["route"], p["profile_id"], p["seed"]) != (c["route"], c["profile_id"], c["seed"]):
                out.append((at(r), f"candidate {c['id']} does not match plan entry {c['ordinal']}"))
        if cands and {c["job_id"] for c in cands} != set(r["job_ids"]):
            out.append((at(r), "job_ids differ from the candidates' jobs"))
        if any(c["synthetic_test"] for c in cands) != ("Synthetic test output" in r["labels"]):
            out.append((at(r), "'Synthetic test output' label does not match the candidates"))
        if "unbenchmarked routes" not in r["labels"]:
            out.append((at(r), "plan without supported benchmark conclusions must be labelled 'unbenchmarked routes'"))
    return out


@rule("audition.arms_ready", "An audition opens only when every arm's job is ready, over candidates of the requests it names in its own project.")
def _arms_ready(w: World) -> list[Finding]:
    out = []
    for s in w.by_kind.get("audition", []):
        if len(s["arms"]) != len(s["candidate_ids"]):
            out.append((at(s), "arms and candidates differ in number"))
        if ts(s["all_arms_ready_at"]) > ts(s["opened_at"]):
            out.append((at(s), "opened before every arm was ready"))
        for cid in s["candidate_ids"]:
            c = w.ids["candidate"].get(cid)
            if c is None:
                out.append((at(s), f"unknown candidate {cid}"))
                continue
            job = w.ids["job"].get(c["job_id"])
            ready = [h["at"] for h in job["history"] if h["state"] == "ready"] if job else []
            if job is None or job["state"] != "ready" or not ready or ts(ready[-1]) > ts(s["all_arms_ready_at"]):
                out.append((at(s), f"candidate {cid} was not ready when the arms were declared ready"))
            source = c["source"].get("generation_request_id") or c["source"].get("edit_operation_id")
            if s["mode"] == "product" and (source not in s["request_ids"] or c["project_id"] != s["project_id"]):
                out.append((at(s), f"candidate {cid} belongs to a request or project the audition does not name"))
    return out


@rule("audition.candidates_sorted", "An audition lists its candidates sorted, so their order cannot leak the label mapping.")
def _sorted(w: World) -> list[Finding]:
    return [(at(s), "candidate_ids are not sorted") for s in w.by_kind.get("audition", []) if s["candidate_ids"] != sorted(s["candidate_ids"])]


@rule("audition.labels_consistent", "Arm and anchor labels are unique; gains cover exactly them; anchors are listening-only reference standards; verdict labels exist.")
def _labels(w: World) -> list[Finding]:
    out = []
    for s in w.by_kind.get("audition", []):
        arms = [a["label"] for a in s["arms"]]
        anchors = [a["label"] for a in s["anchors"]]
        labels = arms + anchors
        if len(set(labels)) != len(labels):
            out.append((at(s), "duplicate labels"))
        if sorted(g["label"] for g in s["gains"]) != sorted(labels):
            out.append((at(s), "gains do not cover exactly the arms and anchors"))
        for a in s["anchors"]:
            r = w.ids["reference"].get(a["reference_id"])
            if r is None or r["role"] != "reference_standard" or not r["permission"]["listening_only"]:
                out.append((at(s), f"anchor {a['label']} is not a listening-only reference standard"))
        for p in s["repeat_pairs"]:
            if p["first_label"] not in arms or p["second_label"] not in arms:
                out.append((at(s), "repeat pair names an unknown arm"))
        for v in w.by_kind.get("verdict", []):
            if v["audition_id"] != s["id"]:
                continue
            used = {v["preferred"]} | {a["preferred"] for a in v["axes"]} | {i["label"] for i in v["problem_intervals"]} | {x["label"] for x in v["seconds_listened"]}
            if used - set(labels) - {"tie", "neither"}:
                out.append((at(v), f"verdict uses unknown labels {sorted(used - set(labels) - {'tie', 'neither'})}"))
    return out


@rule("audition.reveal_commitment", "The reveal's mapping and nonce hash to the commitment published at open time, over exactly the audition's arms, after the verdict.")
def _reveal(w: World) -> list[Finding]:
    out = []
    for r in w.by_kind.get("reveal", []):
        s = w.ids["audition"].get(r["audition_id"])
        if s is None:
            out.append((at(r), "unknown audition"))
            continue
        if sorted(m["label"] for m in r["mapping"]) != sorted(a["label"] for a in s["arms"]):
            out.append((at(r), "mapping labels differ from the arms"))
        if sorted(m["candidate_id"] for m in r["mapping"]) != sorted(s["candidate_ids"]):
            out.append((at(r), "mapping candidates differ from the audition"))
        if audition.commitment(r["mapping"], r["nonce"]) != s["commitment_sha256"]:
            out.append((at(r), "mapping and nonce do not match the commitment"))
        v = w.ids["verdict"].get(r["verdict_id"])
        if v is None or v["audition_id"] != s["id"] or ts(r["revealed_at"]) < ts(v["act"]["at"]):
            out.append((at(r), "reveal does not follow a verdict on this audition"))
    return out


@rule("keeper.matches_verdict", "A keeper is the candidate its verdict preferred, by the revealed mapping, with the same audio; after a tie either arm may be kept; after neither, none.")
def _keeper(w: World) -> list[Finding]:
    out = []
    reveals = {r["audition_id"]: r for r in w.by_kind.get("reveal", [])}
    for k in w.by_kind.get("keeper", []):
        v = w.ids["verdict"].get(k["verdict_id"])
        r = reveals.get(v["audition_id"]) if v else None
        if v is None or r is None:
            out.append((at(k), "verdict or reveal missing"))
            continue
        mapping = {m["label"]: m["candidate_id"] for m in r["mapping"]}
        if v["preferred"] == "tie":
            if k["candidate_id"] not in mapping.values():
                out.append((at(k), f"after a tie only an arm of the audition may be kept, not {k['candidate_id']}"))
        else:
            chosen = mapping.get(v["preferred"])
            if chosen != k["candidate_id"]:
                out.append((at(k), f"verdict preferred {v['preferred']} -> {chosen}, not {k['candidate_id']}"))
        c = w.ids["candidate"].get(k["candidate_id"])
        if c is None or c["artifact_sha256"] != k["artifact_sha256"] or c["project_id"] != k["project_id"]:
            out.append((at(k), "keeper audio or project differ from its candidate"))
    return out


@rule("lane.export", "An export runs in its project's lane, and its eligible_lanes equal the keeper's (audio ancestry only) and contain that lane.")
def _export_lane(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("export-manifest", []):
        project = w.ids["project"].get(m["project_id"])
        keeper = w.ids["keeper"].get(m["keeper_id"])
        if project is None or keeper is None:
            out.append((at(m), "project or keeper missing"))
            continue
        lane = w.project_lane_at(project, m["verified_at"])
        if m["operator_lane"] != lane:
            out.append((at(m), f"export lane {m['operator_lane']} != project lane {lane}"))
        art = w.artifacts.get(keeper["artifact_sha256"])
        if art is not None and set(m["eligible_lanes"]) != set(art["provenance"]["eligible_lanes"]):
            out.append((at(m), f"eligible_lanes {sorted(m['eligible_lanes'])} != keeper's {sorted(art['provenance']['eligible_lanes'])}"))
        if m["operator_lane"] not in m["eligible_lanes"]:
            out.append((at(m), "the export's lane is not among its eligible lanes"))
    return out


@rule("license.manifest_chain", "A manifest's closure, closure hash, license chain and model chain are computed from the keeper's audio ancestry; its mix and deliverable files are the keeper and its conversions.")
def _manifest_chain(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("export-manifest", []):
        keeper = w.ids["keeper"].get(m["keeper_id"])
        if keeper is None:
            continue
        closure = w.closure(keeper["artifact_sha256"])
        if m["closure"] != closure:
            out.append((at(m), "closure differs from the keeper's audio ancestry"))
        if m["closure_sha256"] != sha256_hex("\n".join(m["closure"]).encode("utf-8")):
            out.append((at(m), "closure_sha256 does not match the closure"))
        arts = [w.artifacts[s] for s in closure]
        expected_ids = {e["component_id"] for a in arts for e in a["provenance"]["license_chain"]}
        if {e["component_id"] for e in m["license_chain"]} != expected_ids or len(m["license_chain"]) != len(expected_ids):
            out.append((at(m), "license chain differs from the closure's components"))
        for e in m["license_chain"]:
            if w.register_entry(e["component_id"]) not in (None, e):
                out.append((at(m), f"terms for {e['component_id']} differ from the register"))
        models = {(a["provenance"]["engine"]["profile_id"], a["provenance"]["engine"]["profile_revision"])
                  for a in arts if a["origin"] in GENERATIVE_ORIGINS}
        if {(x["profile_id"], x["profile_revision"]) for x in m["model_chain"]} != models or len(m["model_chain"]) != len(models):
            out.append((at(m), "model chain differs from the closure's generative artifacts"))
        for f in m["files"]:
            if f["role"] == "mix_native" and f["sha256"] != keeper["artifact_sha256"]:
                out.append((at(m), "mix_native is not the keeper's audio"))
            if f["role"] == "deliverable_48k_24":
                art = w.artifacts.get(f["sha256"])
                if art is None or {"edge": "converted_from", "sha256": keeper["artifact_sha256"]} not in art["provenance"]["parents"]:
                    out.append((at(m), "the deliverable is not a conversion of the keeper"))
    return out


@rule("release.manifest_blockers", "A manifest's release blockers are the register's release-blocker classes (obligations aside, which travel in the license chain) of every component in the closure; a blocker is covered only by a non-voided license acceptance whose release permission names the export's lane; release_clear is true only when the lane is releasable and every blocker is covered.")
def _release_blockers(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("export-manifest", []):
        keeper = w.ids["keeper"].get(m["keeper_id"])
        if keeper is None:
            continue
        comps = {e["component_id"] for s in w.closure(keeper["artifact_sha256"]) for e in w.artifacts[s]["provenance"]["license_chain"]}
        expected = {(c, cls) for c in comps for cls in (w.components[c]["release_blockers"] if c in w.components else [])
                    if cls != "obligations"}
        got = {(b["component_id"], b["class"]) for b in m["release_blockers"]}
        if got != expected or len(got) != len(m["release_blockers"]):
            out.append((at(m), f"release blockers {sorted(got)} != the closure's {sorted(expected)}"))
        covered = True
        for b in m["release_blockers"]:
            la = w.ids["license-acceptance"].get(b["covered_by"]) if b["covered_by"] else None
            ok = la is not None and la["voided"] is None and la["component_id"] == b["component_id"] \
                and la["release_permission"] is not None and m["operator_lane"] in la["release_permission"]["lanes"]
            if b["covered_by"] and not ok:
                out.append((at(m), f"{b['component_id']} is not covered by {b['covered_by']} in lane {m['operator_lane']}"))
            covered = covered and ok
        clear = w.lane_releasable.get(m["operator_lane"], False) and covered
        if m["release_clear"] != clear:
            out.append((at(m), f"release_clear should be {clear}"))
    return out


@rule("lane.record_eligible", "A transcribed MelodySpec carries its transcriber's lanes, and every revision built on it (corrections, assembly) inherits them; an assembled revision carries its source revision's capture and transcription exactly (a 1.0 record may leave them null, inheriting by reference); no project holds, and no job reads, a melody revision outside its lanes.")
def _record_eligible(w: World) -> list[Finding]:
    out = []
    memo: dict[tuple, set] = {}

    def lanes_of_rev(m: dict) -> set:
        key = (m["melody_id"], m["rev"])
        if key not in memo:
            memo[key] = set(LANES)
            lanes = set(LANES)
            tr = m["source"]["transcription"]
            if tr is not None and tr["profile_id"] in w.profiles:
                lanes &= w.component_lanes(w.profiles[tr["profile_id"]]["components"])
            if m["base_rev"] is not None and (m["melody_id"], m["base_rev"]) in w.melodies:
                lanes &= lanes_of_rev(w.melodies[(m["melody_id"], m["base_rev"])])
            af = m["source"]["assembled_from"]
            if af is not None and (af["melody"]["melody_id"], af["melody"]["rev"]) in w.melodies:
                lanes &= lanes_of_rev(w.melodies[(af["melody"]["melody_id"], af["melody"]["rev"])])
            memo[key] = lanes
        return memo[key]

    by_sha: dict[str, tuple[dict, set]] = {}
    for m in w.by_kind.get("melody-spec", []):
        tr = m["source"]["transcription"]
        if tr is not None and tr["profile_id"] in w.profiles:
            declared = w.component_lanes(w.profiles[tr["profile_id"]]["components"])
            if set(tr["eligible_lanes"]) != declared:
                out.append((at(m), f"transcription lanes {sorted(tr['eligible_lanes'])} != its transcriber's {sorted(declared)}"))
        af = m["source"]["assembled_from"]
        origin = w.melodies.get((af["melody"]["melody_id"], af["melody"]["rev"])) if af is not None else None
        legacy = m["schemaVersion"].startswith("1.0.")
        for field in ("capture_sha256", "transcription"):
            mine = m["source"][field]
            if origin is not None and mine != origin["source"][field] and not (legacy and mine is None):
                out.append((at(m), f"{field} is not inherited from {af['melody']['melody_id']} rev {af['melody']['rev']}"))
        lanes = lanes_of_rev(m)
        by_sha[m["content_sha256"]] = (m, lanes)
        project = w.ids["project"].get(m["project_id"])
        if project is not None and project["operator_lane"] not in lanes:
            out.append((at(m), f"project {project['id']} is {project['operator_lane']}, outside this melody revision's lanes {sorted(lanes)}"))
    for job in w.by_kind.get("job", []):
        for ref in job["record_inputs"]:
            hit = by_sha.get(ref["sha256"]) if ref["kind"] == "melody-spec" else None
            if hit is not None and job["lane"] not in hit[1]:
                out.append((at(job), f"reads a melody revision whose lanes {sorted(hit[1])} exclude {job['lane']}"))
    return out


@rule("license.ai_disclosure", "The AI-disclosure flag, its reasons, imported sources and synthetic flag are computed from the closure.")
def _ai_disclosure(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("export-manifest", []):
        keeper = w.ids["keeper"].get(m["keeper_id"])
        if keeper is None:
            continue
        arts = [w.artifacts[s] for s in w.closure(keeper["artifact_sha256"])]
        reasons = set()
        if any(a["origin"] in GENERATIVE_ORIGINS for a in arts):
            reasons.add("generated_audio_in_closure")
        if any("ai_disclosure" in e["obligations"] for a in arts for e in a["provenance"]["license_chain"]):
            reasons.add("component_obligation_ai_disclosure")
        if m["ai_disclosure"]["required"] != bool(reasons) or set(m["ai_disclosure"]["reasons"]) != reasons:
            out.append((at(m), f"ai_disclosure should be required={bool(reasons)} with reasons {sorted(reasons)}"))
        imports = {a["provenance"]["import_terms_id"] for a in arts if a["origin"] == "imported_mix"}
        if {s["import_terms_id"] for s in m["imported_sources"]} != imports:
            out.append((at(m), "imported_sources differ from the closure's imports"))
        if m["synthetic_test"] != any(a["synthetic_test"] for a in arts):
            out.append((at(m), "synthetic_test differs from the closure"))
    return out


# ----- melody, song and time -----------------------------------------------------------------------------------------

def _melody_refs(w: World):
    for s in w.by_kind.get("song-spec", []):
        if s["melody"] is not None:
            yield s, s["melody"]
    for t in w.by_kind.get("timeline", []):
        yield t, t["melody"]
        for track in t["tracks"]:
            for clip in track["clips"]:
                if clip["clip_kind"] == "midi":
                    yield t, clip["melody"]
    for m in w.by_kind.get("melody-spec", []):
        if m["source"]["assembled_from"] is not None:
            yield m, m["source"]["assembled_from"]["melody"]


@rule("tempo.ref_resolves", "Every MelodySpec reference resolves to that revision and its tempo-map revision; every SongSpec reference resolves.")
def _tempo_refs(w: World) -> list[Finding]:
    out = []
    for doc, ref in _melody_refs(w):
        mel = w.melodies.get((ref["melody_id"], ref["rev"]))
        if mel is None:
            out.append((at(doc), f"{ref['melody_id']} rev {ref['rev']} does not exist"))
        elif mel["tempo_map"]["rev"] != ref["tempo_map_rev"]:
            out.append((at(doc), f"{ref['melody_id']} rev {ref['rev']} carries tempo map rev {mel['tempo_map']['rev']}, not {ref['tempo_map_rev']}"))
    song_refs = [(m, m["source"]["assembled_from"]["song"]) for m in w.by_kind.get("melody-spec", []) if m["source"]["assembled_from"]]
    song_refs += [(r, r["song"]) for r in w.by_kind.get("generation-request", [])]
    song_refs += [(b, b["song"]) for b in w.by_kind.get("eval-brief", []) if b["song"] is not None]
    for doc, ref in song_refs:
        if (ref["song_id"], ref["rev"]) not in w.songs:
            out.append((at(doc), f"{ref['song_id']} rev {ref['rev']} does not exist"))
    return out


@rule("tempo.rev_on_change", "The tempo-map revision starts at 1 and rises by exactly one when, and only when, the tempo or meter changes.")
def _tempo_rev(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("melody-spec", []):
        tm = m["tempo_map"]
        if m["rev"] == 1:
            if tm["rev"] != 1:
                out.append((at(m), "first revision must carry tempo map rev 1"))
            continue
        base = w.melodies.get((m["melody_id"], m["base_rev"]))
        if base is None:
            continue
        changed = (tm["tempo"], tm["meter"]) != (base["tempo_map"]["tempo"], base["tempo_map"]["meter"])
        want = base["tempo_map"]["rev"] + (1 if changed else 0)
        if tm["rev"] != want:
            out.append((at(m), f"tempo map rev {tm['rev']} but {'a change' if changed else 'no change'} requires {want}"))
    return out


@rule("melody.revision_chain", "Each MelodySpec and SongSpec revision builds on the previous one in the same project, and every correction-log entry joins two existing revisions.")
def _revision_chain(w: World) -> list[Finding]:
    out = []
    for kind, index, key in (("melody-spec", w.melodies, "melody_id"), ("song-spec", w.songs, "song_id")):
        for d in w.by_kind.get(kind, []):
            if d["rev"] == 1:
                continue
            base = index.get((d[key], d["base_rev"]))
            if d["base_rev"] != d["rev"] - 1 or base is None or base["project_id"] != d["project_id"]:
                out.append((at(d), f"rev {d['rev']} must build on rev {d['rev'] - 1} of the same project"))
    for log in w.by_kind.get("correction-log", []):
        seqs = [e["seq"] for e in log["entries"]]
        if seqs != sorted(set(seqs)):
            out.append((at(log), "entry seq must strictly increase"))
        for e in log["entries"]:
            if e["new_rev"] != e["base_rev"] + 1 or (log["melody_id"], e["base_rev"]) not in w.melodies \
                    or (log["melody_id"], e["new_rev"]) not in w.melodies:
                out.append((at(log), f"entry {e['seq']} does not join two existing consecutive revisions"))
    return out


@rule("melody.wellformed", "Tempo and meter start at tick 0 and strictly increase, and the meter changes only on a bar line; phrases have positive length; note ids are unique; the seed capture and transcription job exist.")
def _melody_wellformed(w: World) -> list[Finding]:
    out = []
    for m in w.by_kind.get("melody-spec", []):
        for name in ("tempo", "meter"):
            ticks = [s["tick"] for s in m["tempo_map"][name]]
            if ticks[0] != 0 or any(b <= a for a, b in zip(ticks, ticks[1:])):
                out.append((at(m), f"{name} segments must start at 0 and strictly increase"))
        meter = m["tempo_map"]["meter"]
        if any((b["tick"] - a["tick"]) % timemodel.bar_ticks(a["numerator"], a["denominator"]) for a, b in zip(meter, meter[1:])):
            out.append((at(m), "a meter change lands inside a bar of the meter before it"))
        if any(p["end_tick"] <= p["start_tick"] for p in m["phrases"]):
            out.append((at(m), "a phrase ends before it starts"))
        ids = [n["id"] for n in m["notes"]] + [p["id"] for p in m["phrases"]]
        if len(ids) != len(set(ids)):
            out.append((at(m), "duplicate note or phrase id"))
        src = m["source"]
        if src["capture_sha256"] is not None:
            cap = w.artifacts.get(src["capture_sha256"])
            if cap is None or cap["origin"] != "human_recording":
                out.append((at(m), "the seed capture is not a stored human recording"))
        if src["transcription"] is not None:
            job = w.ids["job"].get(src["transcription"]["job_id"])
            # An assembled revision carries its source's transcription, which output revision 1 of the source melody.
            source_melody_id = src["assembled_from"]["melody"]["melody_id"] if src["assembled_from"] else m["melody_id"]
            first = w.melodies.get((source_melody_id, 1))
            if job is None or job["job_kind"] != "transcribe" or first is None \
                    or first["content_sha256"] not in {o["sha256"] for o in job["outputs"]}:
                out.append((at(m), "the transcription job is missing or did not output revision 1 of this melody"))
    return out


@rule("song.phrase_refs", "SongForm sections place only phrases that exist in the referenced MelodySpec revision, and section ids are unique.")
def _phrase_refs(w: World) -> list[Finding]:
    out = []
    for s in w.by_kind.get("song-spec", []):
        ids = [sec["id"] for sec in s["form"]["sections"]]
        if len(ids) != len(set(ids)):
            out.append((at(s), "duplicate section id"))
        if s["melody"] is None:
            continue
        mel = w.melodies.get((s["melody"]["melody_id"], s["melody"]["rev"]))
        if mel is None:
            continue
        phrases = {p["id"] for p in mel["phrases"]}
        for sec in s["form"]["sections"]:
            missing = set(sec["phrase_ids"]) - phrases
            if missing:
                out.append((at(s), f"section {sec['id']} places unknown phrases {sorted(missing)}"))
    return out


# ----- jobs, paid runs and events ------------------------------------------------------------------------------------

@rule("job.state_machine", "Job history starts queued, follows the state machine in time order and ends at the current state; burst jobs pass awaiting_approval, free jobs never do.")
def _state_machine(w: World) -> list[Finding]:
    out = []
    for job in w.by_kind.get("job", []):
        states = [h["state"] for h in job["history"]]
        times = [h["at"] for h in job["history"]]
        if states[0] != "queued" or states[-1] != job["state"]:
            out.append((at(job), "history must start queued and end at the current state"))
        for a, b in zip(states, states[1:]):
            if b not in JOB_TRANSITIONS.get(a, set()):
                out.append((at(job), f"illegal transition {a} -> {b}"))
        if any(ts(b) < ts(a) for a, b in zip(times, times[1:])):
            out.append((at(job), "history goes back in time"))
        burst = job["placement"]["kind"] == "burst"
        if burst and "preparing" in states and "awaiting_approval" not in states[: states.index("preparing")]:
            out.append((at(job), "a burst job reached preparing without awaiting approval"))
        if not burst and "awaiting_approval" in states:
            out.append((at(job), "a free job never awaits approval"))
    return out


@rule("budget.ceiling_arithmetic", "max_minutes adds up; the ceiling is total minutes at the highest listed rate, rounded up to the cent, plus fixed lines; quotes expire 15 minutes after creation.")
def _ceiling(w: World) -> list[Finding]:
    out = []
    for q in w.by_kind.get("quote", []):
        t = q["terms"]
        mm = t["max_minutes"]
        parts = sum(Decimal(mm[k]) for k in ("boot", "weights_download", "jobs_total", "teardown_margin"))
        if Decimal(mm["total"]) != parts:
            out.append((at(q), "max_minutes.total is not the sum of its parts"))
        if Decimal(mm["jobs_total"]) != sum((Decimal(j["estimate_minutes"]) for j in t["jobs"]), Decimal(0)):
            out.append((at(q), "jobs_total is not the sum of the job estimates"))
        if t["gpu_class"] not in {r["gpu_class"] for r in t["rates"]}:
            out.append((at(q), "the chosen GPU class has no rate"))
        top = max(Decimal(r["usd_per_hour"]) for r in t["rates"])
        expected = ceil_cents(Decimal(mm["total"]) * top / 60) + sum((Decimal(f["usd"]) for f in t["fixed_lines"]), Decimal(0))
        if Decimal(t["ceiling_usd"]) != expected:
            out.append((at(q), f"ceiling {t['ceiling_usd']} != {usd_text(expected)}"))
        if ts(t["expires_at"]) != ts(t["created_at"]) + timedelta(minutes=15):
            out.append((at(q), "a quote expires exactly 15 minutes after creation"))
    return out


@rule("budget.cap_check", "A quote's month-to-date is the ledger's before it; a quote that would exceed the cap, or that meets an unacknowledged overrun, is refused; a refusal for being over cap is true.")
def _cap(w: World) -> list[Finding]:
    out = []
    for q in w.by_kind.get("quote", []):
        t = q["terms"]
        if t["month"] != t["created_at"][:7]:
            out.append((at(q), "month is not the quote's UTC month"))
        mtd = ledger.month_to_date(w.ledger, t["month"], before=t["created_at"])
        if Decimal(t["month_to_date_usd"]) != mtd:
            out.append((at(q), f"month_to_date {t['month_to_date_usd']} != ledger {usd_text(mtd)}"))
        over = not ledger.cap_allows(Decimal(t["month_to_date_usd"]), Decimal(t["ceiling_usd"]), Decimal(t["cap_usd"]))
        refused_over = q["status"] == "refused" and q["refusal_reason"] == "over_cap"
        if over and not refused_over:
            out.append((at(q), "month-to-date plus ceiling exceeds the cap but the quote was not refused"))
        if refused_over and not over:
            out.append((at(q), "refused as over cap although it fits"))
        blocked = ledger.overrun_blocks([e for e in w.ledger if e["at"] < t["created_at"]])
        if blocked and q["status"] in ("offered", "approved"):
            out.append((at(q), "an unacknowledged overrun blocks new leases"))
    return out


@rule("budget.approval_binds_quote", "An approval binds one quote's hash, falls inside its 15-minute window and expires with it; a burst job's approval is for its own quote, which lists the job.")
def _approval(w: World) -> list[Finding]:
    out = []
    for a in w.by_kind.get("approval", []):
        q = w.ids["quote"].get(a["quote_id"])
        if q is None:
            out.append((at(a), "unknown quote"))
            continue
        t = q["terms"]
        if a["quote_sha256"] != q["quote_sha256"]:
            out.append((at(a), "approval is bound to another quote hash"))
        if not ts(t["created_at"]) <= ts(a["act"]["at"]) <= ts(t["expires_at"]):
            out.append((at(a), "approval falls outside the quote's window"))
        if a["expires_at"] != t["expires_at"]:
            out.append((at(a), "approval must expire with its quote"))
    for q in w.by_kind.get("quote", []):
        live = [a for a in w.by_kind.get("approval", []) if a["quote_id"] == q["id"] and a["state"] in ("valid", "used")]
        if len(live) > 1:
            out.append((at(q), "more than one live approval"))
        if (q["status"] == "approved") != bool(live):
            out.append((at(q), "status approved must match a live approval"))
    for job in w.by_kind.get("job", []):
        if job["placement"]["kind"] != "burst":
            continue
        q = w.ids["quote"].get(job["quote_id"])
        if q is None or job["id"] not in {j["job_id"] for j in q["terms"]["jobs"]}:
            out.append((at(job), "its quote is missing or does not list the job"))
        if job["approval_id"] is not None:
            a = w.ids["approval"].get(job["approval_id"])
            if a is None or a["quote_id"] != job["quote_id"]:
                out.append((at(job), "its approval is for another quote"))
    return out


@rule("budget.reserve_before_provision", "A burst run follows its approval; its reserve entry at the ceiling is written, and evented, before anything is provisioned.")
def _reserve(w: World) -> list[Finding]:
    out = []
    for run in w.by_kind.get("burst-run", []):
        q = w.ids["quote"].get(run["quote_id"])
        a = w.ids["approval"].get(run["approval_id"])
        if q is None or a is None or a["quote_id"] != run["quote_id"]:
            out.append((at(run), "quote or approval missing or mismatched"))
            continue
        if ts(a["act"]["at"]) > ts(run["reserved_at"]):
            out.append((at(run), "reserved before the approval"))
        if run["provisioned_at"] is not None and ts(run["provisioned_at"]) <= ts(run["reserved_at"]):
            out.append((at(run), "provisioned before the reservation"))
        reserves = [e for e in w.ledger if e["entry_type"] == "reserve" and e["run_id"] == run["id"]]
        if len(reserves) != 1 or reserves[0]["at"] != run["reserved_at"] or reserves[0]["usd"] != q["terms"]["ceiling_usd"]:
            out.append((at(run), "needs exactly one reserve entry at reserved_at for the ceiling"))
        seq = {e["type"]: e["seq"] for e in w.events if e["data"].get("run_id") == run["id"]}
        if "burst.provisioned" in seq and seq.get("ledger.reserve", 10 ** 9) > seq["burst.provisioned"]:
            out.append((at(run), "the provision event precedes the reserve event"))
    return out


@rule("budget.settlement", "A settled run has a settle entry for its amount; settled_at_ceiling means exactly the ceiling; an overrun entry exists exactly when the amount exceeds the ceiling; the run's jobs carry the cost.")
def _settlement(w: World) -> list[Finding]:
    out = []
    for run in w.by_kind.get("burst-run", []):
        q = w.ids["quote"].get(run["quote_id"])
        s = run["settlement"]
        if s is None or q is None:
            continue
        ceiling = Decimal(q["terms"]["ceiling_usd"])
        amount = Decimal(s["usd"])
        settles = [e for e in w.ledger if e["entry_type"] == "settle" and e["run_id"] == run["id"]]
        if len(settles) != 1 or Decimal(settles[0]["usd"]) != amount:
            out.append((at(run), "needs exactly one settle entry for the settled amount"))
        if s["basis"] == "settled_at_ceiling" and amount != ceiling:
            out.append((at(run), "settled_at_ceiling must equal the ceiling"))
        overruns = [e for e in w.ledger if e["entry_type"] == "overrun" and e["run_id"] == run["id"]]
        if bool(overruns) != (amount > ceiling):
            out.append((at(run), "an overrun entry exists exactly when the amount exceeds the ceiling"))
        jobs = [w.ids["job"][j["job_id"]] for j in q["terms"]["jobs"] if j["job_id"] in w.ids["job"]]
        if jobs and (sum((Decimal(j["cost"]["usd"]) for j in jobs), Decimal(0)) != amount
                     or any(j["cost"]["basis"] != s["basis"] for j in jobs)):
            out.append((at(run), "the run's jobs do not carry its settled cost and basis"))
    return out


@rule("events.ordered", "Event time never decreases as seq increases.")
def _events(w: World) -> list[Finding]:
    return [(at(b), "event time goes back") for a, b in zip(w.events, w.events[1:]) if ts(b["at"]) < ts(a["at"])]


@rule("lane.quote", "A quote is only for its project's lane, every quoted job runs in that lane on a profile that allows it, and its lane check copies the registry.")
def _quote_lane(w: World) -> list[Finding]:
    out = []
    for q in w.by_kind.get("quote", []):
        t = q["terms"]
        project = w.ids["project"].get(t["project_id"])
        if project is not None and t["lane"] != w.project_lane_at(project, t["created_at"]):
            out.append((at(q), "quote lane differs from the project's lane"))
        for j in t["jobs"]:
            job = w.ids["job"].get(j["job_id"])
            prof = w.profiles.get(j["profile_id"])
            if job is not None and job["lane"] != t["lane"]:
                out.append((at(q), f"job {j['job_id']} runs in another lane"))
            if prof is not None and t["lane"] not in prof["allowed_lanes"]:
                out.append((at(q), f"{j['profile_id']} does not allow lane {t['lane']}: no quote may exist"))
        for p in t["lane_check"]["profiles"]:
            prof = w.profiles.get(p["profile_id"])
            if prof is not None and sorted(p["allowed_lanes"]) != sorted(prof["allowed_lanes"]):
                out.append((at(q), f"lane check for {p['profile_id']} differs from the registry"))
    return out


@rule("lane.eval", "Each brief runs in its own lane: every compared profile allows it; preregistrations and sets name existing briefs in the same lanes.")
def _eval_lane(w: World) -> list[Finding]:
    out = []
    briefs = w.ids["eval-brief"]
    for b in briefs.values():
        for c in b["compared"]:
            prof = w.profiles.get(c["profile_id"])
            if prof is not None and b["lane"] not in prof["allowed_lanes"]:
                out.append((at(b), f"{c['profile_id']} is not allowed in lane {b['lane']}"))
    for s in w.by_kind.get("eval-set", []):
        for bid in s["brief_ids"]:
            if bid not in briefs or briefs[bid]["set"] != s["set"]:
                out.append((at(s), f"brief {bid} is missing or belongs to another set"))
    for p in w.by_kind.get("prereg", []):
        if p["eval_set_id"] not in w.ids["eval-set"]:
            out.append((at(p), "unknown eval set"))
        for entry in p["body"]["briefs"]:
            b = briefs.get(entry["brief_id"])
            if b is None or b["lane"] != entry["lane"]:
                out.append((at(p), f"brief {entry['brief_id']} is missing or in another lane"))
    return out


# ----- worker protocol -----------------------------------------------------------------------------------------------

@rule("worker.describe_matches_registry", "A worker describes only declared profiles, with tasks within, lanes equal to and limits equal to the declaration.")
def _describe(w: World) -> list[Finding]:
    out = []
    for d in w.by_kind.get("worker-describe", []):
        for p in d["profiles"]:
            prof = w.profiles.get(p["profile_id"])
            if prof is None:
                out.append((at(d), f"describes undeclared profile {p['profile_id']}"))
                continue
            if not set(p["tasks"]) <= set(prof["tasks"]):
                out.append((at(d), f"{p['profile_id']}: tasks beyond the declaration"))
            if sorted(p["lanes"]) != sorted(prof["allowed_lanes"]):
                out.append((at(d), f"{p['profile_id']}: lanes differ from the declaration"))
            if p["limits"] != prof["limits"]:
                out.append((at(d), f"{p['profile_id']}: limits differ from the declaration"))
    return out


@rule("worker.refuse_before_load", "A request in a forbidden lane or for an undeclared task is refused with that code and nothing loads; a permitted request is never refused for those reasons.")
def _refuse(w: World) -> list[Finding]:
    out = []
    refusals = {r["job_id"]: r for r in w.by_kind.get("refusal", [])}
    statuses = {s["job_id"]: s for s in w.by_kind.get("task-status", [])}
    for req in w.by_kind.get("task-request", []):
        prof = w.profiles.get(req["profile_id"])
        if prof is None:
            continue
        code = "lane_forbidden" if req["lane"] not in prof["allowed_lanes"] else (
            "unsupported_task" if req["task"] not in prof["tasks"] else None)
        refusal = refusals.get(req["job_id"])
        status = statuses.get(req["job_id"])
        if code is not None:
            if refusal is None or refusal["code"] != code:
                out.append((at(req), f"must be refused with {code}"))
            if status is not None and status["state"] in LOADED_STATES:
                out.append((at(req), f"loaded anyway (task-status {status['state']})"))
        elif refusal is not None and refusal["code"] in ("lane_forbidden", "unsupported_task"):
            out.append((at(req), f"refused with {refusal['code']} although the profile allows it"))
    return out


@rule("worker.no_paths_or_urls", "Parameters never carry file paths or URLs; assets move by sha256 only.")
def _no_paths(w: World) -> list[Finding]:
    out = []

    def scan(doc: dict, value, path: str) -> None:
        if isinstance(value, str) and PATHLIKE.search(value):
            out.append((at(doc), f"{path} looks like a path or URL"))
        elif isinstance(value, dict):
            for k in sorted(value):
                scan(doc, value[k], f"{path}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                scan(doc, v, f"{path}[{i}]")

    for req in w.by_kind.get("task-request", []):
        scan(req, req["params"], "params")
    for job in w.by_kind.get("job", []):
        scan(job, job["params"], "params")
    for art in w.by_kind.get("artifact", []):
        if art["provenance"]["engine"] is not None:
            scan(art, art["provenance"]["engine"]["params"], "engine.params")
    return out


# ----- studio ------------------------------------------------------------------------------------------------------------

@rule("edit.mask_wellformed", "An edit's mask has positive length, locked context never overlaps the mask and its crossfades, the base is the keeper's audio, and candidates belong to the edit.")
def _edit(w: World) -> list[Finding]:
    out = []
    for e in w.by_kind.get("edit-operation", []):
        lo = e["mask"]["start_frame"] - e["crossfade"]["in_frames"]
        hi = e["mask"]["end_frame"] + e["crossfade"]["out_frames"]
        if e["mask"]["end_frame"] <= e["mask"]["start_frame"]:
            out.append((at(e), "empty mask"))
        for r in e["locked_context"]:
            if r["end_frame"] <= r["start_frame"] or (r["start_frame"] < hi and r["end_frame"] > lo):
                out.append((at(e), f"locked context {r['start_frame']}-{r['end_frame']} overlaps the mask or is empty"))
        keeper = w.ids["keeper"].get(e["keeper_id"])
        if keeper is None or keeper["artifact_sha256"] != e["base_artifact_sha256"]:
            out.append((at(e), "base audio is not the keeper's"))
        for cid in e["candidate_ids"]:
            c = w.ids["candidate"].get(cid)
            if c is None or c["source"].get("edit_operation_id") != e["id"]:
                out.append((at(e), f"candidate {cid} does not belong to this edit"))
        if e["accepted_candidate_id"] is not None and e["accepted_candidate_id"] not in e["candidate_ids"]:
            out.append((at(e), "accepted a candidate the edit never had"))
    return out
