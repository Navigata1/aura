"""Evidence-binding inputs (T02b): typed preregistration resolution and the checks that a benchmark's inputs bind.

A benchmark-prereg fixes what benchmark-48 or hum-benchmark evidence will be judged against, a benchmark-membership
records what the set holds, and an evidence-binding names one evidence record's subject, preregistration and
membership. These functions only report whether those inputs bind. They conclude nothing and never promote, demote
or disable anything: that is C02 (#4). evidence.gates still refuses concluded benchmark and hum-benchmark records and
the status fold ignores them (C01), and nothing here is wired into either.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from .canonical import self_hash, sha_of
from .world import identity

ENGINE = "benchmark-48"


def _key(subject: dict) -> tuple:
    return subject["profile_id"], subject["profile_revision"], subject["host_class"]


def _job_key(job: dict) -> tuple:
    return job["profile_id"], job["profile_revision"], job["placement"]["host_class"]


def _ts(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def resolve_prereg(sha: str, benchmark_set: str, records: list[dict]) -> dict | None:
    """Typed resolution: exactly one benchmark-prereg of this set whose own canonical hash is sha. A MelodySpec, a
    prereg/1 or a preregistration of the other set never satisfies the reference, whatever hash it carries."""
    found = [r for r in records if r["kind"] == "benchmark-prereg" and r["set"] == benchmark_set
             and r["prereg_sha256"] == sha == self_hash(r, "prereg_sha256")]
    return found[0] if len(found) == 1 else None


def prereg_findings(prereg: dict, profiles: dict) -> list[str]:
    """What is wrong with a benchmark-prereg on its own, at preregistration (ADR-0010; ADR-0029 enforcement point 6)."""
    out = set()
    cases, metrics = prereg["cases"], set(prereg["protocol"]["metrics"])
    fixed = [t["metric"] for t in prereg["thresholds"]]
    if self_hash(prereg, "prereg_sha256") != prereg["prereg_sha256"]:
        out.add("prereg_hash_mismatch")
    if len({c["case_id"] for c in cases}) != len(cases):
        out.add("case_duplicate")
    if metrics - set(fixed):
        out.add("threshold_missing")
    if len(set(fixed)) != len(fixed):
        out.add("threshold_ambiguous")
    if prereg["decision"] is not None and prereg["decision"]["rank_by"] not in metrics:
        out.add("decision_unregistered")
    if any(c[f] not in prereg["asset_hashes"] for c in cases for f in ("hum_sha256", "ground_truth_sha256") if f in c):
        out.add("asset_unlisted")
    if Decimal(prereg["burst_run_ceiling_usd"]) > Decimal(prereg["budgets"]["compute_usd_cap"]):
        out.add("ceiling_exceeds_cap")
    if prereg["coverage"]["cases_complete_min"] > len(cases):
        out.add("coverage_unreachable")
    for subject in prereg["subjects"]:
        profile = profiles.get(subject["profile_id"])
        gate = profile["gates"]["benchmark"] if profile else None
        if gate is None or gate["set"] != prereg["set"]:
            out.add("subject_ungated")
        elif any(c["lane"] not in profile["allowed_lanes"] for c in cases):
            out.add("lane_forbidden")
    return sorted(out)


def binding_findings(binding: dict, records: list[dict], profiles: dict) -> list[str]:
    """Whether an evidence-binding's inputs bind: its typed preregistration and membership, one record per identity,
    preregistered subjects and cases, the benchmark set and pinned briefs, the candidate budget, jobs queued strictly
    after the commit, and every expected owner verdict or correction resolved, with no verdict given over synthetic
    test output. Checking quotas, thresholds and the conclusion itself is C02's work."""
    index, duplicated = {}, False
    for record in records:
        duplicated = duplicated or identity(record) in index
        index[identity(record)] = record
    prereg = resolve_prereg(binding["prereg_sha256"], binding["set"], records)
    out = {"prereg_unresolved"} if prereg is None else set(prereg_findings(prereg, profiles))
    if duplicated:
        out.add("record_duplicate")
    if prereg is None or duplicated:
        return sorted(out)

    def get(kind: str, record_id: str) -> dict | None:
        return index.get((kind, record_id))
    membership = get("benchmark-membership", binding["membership_id"])
    if membership is None or (membership["set"], membership["prereg_sha256"]) != (binding["set"], binding["prereg_sha256"]):
        return sorted(out | {"membership_unresolved"})
    subjects = {_key(s) for s in prereg["subjects"]}
    if _key(binding["subject"]) not in subjects:
        out.add("subject_unregistered")
    if prereg["set"] == ENGINE:
        out |= _brief_findings(prereg, get)
    case_briefs = {c["case_id"]: c.get("brief_id") for c in prereg["cases"]}
    for case in membership["cases"]:
        if case["case_id"] not in case_briefs:
            out.add("case_unregistered")
        for arm in case["arms"]:
            out |= _arm_findings(arm, prereg, subjects, get)
        out |= _verdict_findings(case, case_briefs.get(case["case_id"]), binding["prereg_sha256"], get)
    return sorted(out)


def _brief_findings(prereg: dict, get) -> set:
    """benchmark-48: every case brief belongs to the named benchmark set, still hashes to its pinned content in the
    case's lane, and has its seed among the asset hashes."""
    out = set()
    eval_set = get("eval-set", prereg["eval_set_id"])
    if eval_set is None or eval_set["set"] != "benchmark" or any(c["brief_id"] not in eval_set["brief_ids"] for c in prereg["cases"]):
        out.add("eval_set_unresolved")
    for case in prereg["cases"]:
        brief = get("eval-brief", case["brief_id"])
        # A missing brief hashes as JSON null, which no pinned content hash names, so the lane is read only from a real brief.
        if sha_of(brief) != case["brief_sha256"] or brief["lane"] != case["lane"]:
            out.add("brief_unresolved")
        elif brief["seed"]["sha256"] not in (None, *prereg["asset_hashes"]):
            out.add("asset_unlisted")
    return out


def _arm_findings(arm: dict, prereg: dict, subjects: set, get) -> set:
    """An arm's subject is preregistered and holds the budgeted number of candidates or transcribed MelodySpecs; each
    job is that subject's on that host class and was queued strictly after the commit; each MelodySpec has its
    correction log."""
    out = set()
    if _key(arm["subject"]) not in subjects:
        out.add("subject_unregistered")
    if len(arm["candidate_ids"]) + len(arm["melody_ids"]) != prereg["budgets"]["candidates_per_brief"]:
        out.add("candidates_unequal")
    for job_id in arm["job_ids"]:
        job = get("job", job_id)
        if job is None or _job_key(job) != _key(arm["subject"]):
            out.add("job_unresolved")
        elif _ts(job["created_at"]) <= _ts(prereg["committed_at"]):
            out.add("committed_after_run")
    if any(get("correction-log", m) is None for m in arm["melody_ids"]):
        out.add("correction_unresolved")
    return out


def _verdict_findings(case: dict, brief_id: str | None, prereg_sha: str, get) -> set:
    """Each expected verdict is a preregistered listening verdict on an eval audition of this preregistration for the
    case's brief, over the case's own candidates only, none of them synthetic test output. The eval-mode test is a
    fail-closed guard: audition/1 already lets only eval auditions carry a preregistration hash, so no schema-valid
    record reaches it on its own (an equivalent mutant)."""
    out = set()
    own = {c for arm in case["arms"] for c in arm["candidate_ids"]}
    for verdict_id in case["verdict_ids"]:
        verdict = get("verdict", verdict_id)
        audition = get("audition", verdict["audition_id"]) if verdict else None
        heard = [get("candidate", c) for c in audition["candidate_ids"]] if audition else [None]
        if (None in heard or verdict["evidence_kind"] != "listening-preregistered" or audition["mode"] != "eval"
                or audition["prereg_sha256"] != prereg_sha
                or audition["brief_id"] != brief_id or not set(audition["candidate_ids"]) <= own):
            out.add("verdict_unresolved")
        elif any(c["synthetic_test"] for c in heard):
            out.add("verdict_synthetic")
    return out
