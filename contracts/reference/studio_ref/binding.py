"""Evidence-binding inputs (T02b): typed preregistration resolution and the checks that a benchmark's inputs bind.

A benchmark-prereg fixes what benchmark-48 or hum-benchmark evidence will be judged against, a benchmark-membership
records what the set holds, and an evidence-binding names one evidence record's subject, preregistration and
membership. These functions only report whether those inputs bind. They conclude nothing and never promote, demote
or disable anything: that is C02 (#4). evidence.gates still refuses concluded benchmark and hum-benchmark
records and the status fold ignores them (C01), and nothing here is wired into either.
"""

from __future__ import annotations

from datetime import datetime

from .canonical import self_hash


def _key(subject: dict) -> tuple:
    return subject["profile_id"], subject["profile_revision"], subject["host_class"]


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
    if self_hash(prereg, "prereg_sha256") != prereg["prereg_sha256"]:
        out.add("prereg_hash_mismatch")
    case_ids = [c["case_id"] for c in prereg["cases"]]
    if len(case_ids) != len(set(case_ids)):
        out.add("case_duplicate")
    if set(prereg["protocol"]["metrics"]) - {t["metric"] for t in prereg["thresholds"]}:
        out.add("threshold_missing")
    for subject in prereg["subjects"]:
        profile = profiles.get(subject["profile_id"])
        gate = profile["gates"]["benchmark"] if profile else None
        if gate is None or gate["set"] != prereg["set"]:
            out.add("subject_ungated")
        elif any(c["lane"] not in profile["allowed_lanes"] for c in prereg["cases"]):
            out.add("lane_forbidden")
    return sorted(out)


def binding_findings(binding: dict, records: list[dict], profiles: dict) -> list[str]:
    """Whether an evidence-binding's inputs bind: its typed preregistration and membership, preregistered subjects and
    cases, runs queued strictly after the commit, and every expected owner verdict or correction resolved, with no
    verdict given over synthetic test output. Checking quotas, thresholds and the conclusion itself is C02's work."""
    prereg = resolve_prereg(binding["prereg_sha256"], binding["set"], records)
    if prereg is None:
        return ["prereg_unresolved"]
    out = set(prereg_findings(prereg, profiles))
    ids: dict[str, dict] = {}
    for r in records:
        ids.setdefault(r["kind"], {})[r.get("id", r.get("melody_id"))] = r
    membership = ids.get("benchmark-membership", {}).get(binding["membership_id"])
    if membership is None or (membership["set"], membership["prereg_sha256"]) != (binding["set"], binding["prereg_sha256"]):
        return sorted(out | {"membership_unresolved"})
    subjects = {_key(s) for s in prereg["subjects"]}
    briefs = {c["case_id"]: c.get("brief_id") for c in prereg["cases"]}
    committed = _ts(prereg["committed_at"])
    jobs, verdicts = ids.get("job", {}), ids.get("verdict", {})
    auditions, candidates, logs = ids.get("audition", {}), ids.get("candidate", {}), ids.get("correction-log", {})
    if _key(binding["subject"]) not in subjects:
        out.add("subject_unregistered")
    for case in membership["cases"]:
        if case["case_id"] not in briefs:
            out.add("case_unregistered")
        for arm in case["arms"]:
            if _key(arm["subject"]) not in subjects:
                out.add("subject_unregistered")
            for job_id in arm["job_ids"]:
                job = jobs.get(job_id)
                if job is None or (job["profile_id"], job["profile_revision"], job["placement"]["host_class"]) != _key(arm["subject"]):
                    out.add("run_unresolved")
                elif _ts(job["created_at"]) <= committed:
                    out.add("committed_after_run")
            if any(m not in logs for m in arm["melody_ids"]):
                out.add("correction_unresolved")
        own = {c for arm in case["arms"] for c in arm["candidate_ids"]}
        for verdict_id in case["verdict_ids"]:
            verdict = verdicts.get(verdict_id)
            audition = auditions.get(verdict["audition_id"]) if verdict else None
            heard = [candidates.get(c) for c in audition["candidate_ids"]] if audition else [None]
            if (None in heard or verdict["evidence_kind"] != "listening-preregistered" or audition["mode"] != "eval"
                    or audition["prereg_sha256"] != binding["prereg_sha256"] or audition["brief_id"] != briefs.get(case["case_id"])
                    or not set(audition["candidate_ids"]) <= own):
                out.add("verdict_unresolved")
            elif any(c["synthetic_test"] for c in heard):
                out.add("verdict_synthetic")
    return sorted(out)
