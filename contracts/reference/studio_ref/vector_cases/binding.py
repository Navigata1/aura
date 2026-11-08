"""Evidence-binding inputs (T02b): hand-derived golden cases and the public reference evaluator.

Every record here is a hypothetical input to studio_ref.binding: nothing was rendered, measured or heard and no owner
act took place. Expected findings are written by hand from each derivation, never computed by binding.py. No case
concludes a result or promotes, demotes or disables anything (C02 binds results; C01 still refuses them).
"""
import copy

from studio_ref import binding
from studio_ref.canonical import self_hash
from studio_ref.fixture_support import SV, H, R, owner

KIND = "fixture.binding"
ENGINE, HUM = "benchmark-48", "hum-benchmark"
ACE = {"profile_id": "ace-2b-sft-mlx", "profile_revision": R("ace-2b-sft-mlx"), "host_class": "mlx/m5pro"}
YUE = {"profile_id": "yue2-3b-score", "profile_revision": R("yue2-3b-score"), "host_class": "cuda/rtx4090"}
PYIN = {"profile_id": "analysis-transcribe-pyin-hmm", "profile_revision": R("analysis-transcribe-pyin-hmm"), "host_class": "cpu/m5pro"}
BP = {"profile_id": "transcribe-basic-pitch", "profile_revision": R("transcribe-basic-pitch"), "host_class": "cpu/m5pro"}
WITHHELD = ["route", "profile_id", "profile_revision", "seed", "placement", "job_id", "artifact_sha256", "preview_sha256",
            "measures", "adherence", "hard_constraints", "badges", "diagnostics", "source"]
BRIEF_CASE = {"case_id": "case_b01", "lane": "individual", "brief_id": "brief_b01"}
ENGINE_THRESHOLDS = [("preferred_rate", "gte", "0.50"), ("repeat_pair_agreement", "gte", "0.70")]
HUM_THRESHOLDS = [("con_f1", "gte", "0.40"), ("conp_f1", "gte", "0.30"), ("conpoff_f1", "gte", "0.20"), ("correction_ops", "lte", "60")]


def prereg(pid, bset, subjects, cases, thresholds, metrics, committed="2026-11-01T09:00:00Z"):
    doc = {"kind": "benchmark-prereg", "schemaVersion": SV, "id": pid, "prereg_sha256": "", "set": bset,
           "subjects": [dict(s) for s in subjects], "cases": [dict(c) for c in cases],
           "protocol": {"method": "eval_audition" if bset == ENGINE else "blind_correction", "metrics": list(metrics)},
           "thresholds": [{"metric": m, "comparator": c, "value": v} for m, c, v in thresholds],
           "quota": {"sessions_min": 1, "repeat_pair_fraction": "0.10" if bset == ENGINE else "0", "cases_complete_min": 1,
                     "short_quota_outcome": "inconclusive"},
           "gate_owner": "jon", "committed_at": committed}
    doc["prereg_sha256"] = self_hash(doc, "prereg_sha256")
    return doc


def engine_prereg(committed="2026-11-01T09:00:00Z", cases=(BRIEF_CASE,), thresholds=ENGINE_THRESHOLDS):
    return prereg("bp_engine", ENGINE, [ACE, YUE], cases, thresholds, ["preferred_rate", "repeat_pair_agreement"], committed)


def hum_prereg(subjects=(PYIN, BP), committed="2026-11-01T09:00:00Z"):
    case = {"case_id": "case_h01", "lane": "individual", "hum_sha256": H("hum:h01"), "ground_truth_sha256": H("midi:h01")}
    return prereg("bp_hum", HUM, subjects, [case], HUM_THRESHOLDS, [m for m, _, _ in HUM_THRESHOLDS], committed)


def job(jid, subject, kind, task, queued, placement, output, seed=None):
    states = ["queued", "preparing", "loading", "generating", "ready"]
    return {"kind": "job", "schemaVersion": SV, "id": jid, "project_id": "prj_bench", "job_kind": kind, "task": task,
            "profile_id": subject["profile_id"], "profile_revision": subject["profile_revision"], "lane": "individual",
            "session_id": "ses_bench", "compute_profile_id": "cp_bench", "placement": {"kind": placement, "host_class": subject["host_class"]},
            "request_id": "gr_bench" if kind == "generate" else None, "parent_job_id": None, "inputs": [], "record_inputs": [],
            "params": {"intent": {}, "actual": {}}, "seed": seed, "state": "ready",
            "history": [{"state": s, "at": f"{queued[:14]}{int(queued[14:16]) + i:02d}{queued[16:]}"} for i, s in enumerate(states)], "steps": [],
            "outputs": [{"role": output[0], "sha256": H(output[1])}], "error": None, "cost": {"usd": "0.00", "basis": "local_zero"},
            "egress": [], "quote_id": None, "approval_id": None, "retry": None, "created_at": queued}


def candidate(cid, subject, route, job_id, seed, placement, synthetic, created):
    return {"kind": "candidate", "schemaVersion": SV, "id": cid, "project_id": "prj_bench", "source": {"generation_request_id": "gr_bench"},
            "ordinal": seed, "route": route, "profile_id": subject["profile_id"], "profile_revision": subject["profile_revision"],
            "seed": seed, "placement": {"kind": placement, "host_class": subject["host_class"]}, "job_id": job_id,
            "artifact_sha256": H("mix:" + cid), "preview_sha256": H("preview:" + cid), "measures": None,
            "adherence": {"state": "unmeasured", "reason": "pending"}, "hard_constraints": [],
            "badges": ["Synthetic test output"] if synthetic else ["unbenchmarked route"], "diagnostics": [],
            "synthetic_test": synthetic, "withheld_during_blind": WITHHELD, "created_at": created}


def arm(subject, jobs, candidates=(), melodies=()):
    return {"subject": dict(subject), "job_ids": list(jobs), "candidate_ids": list(candidates), "melody_ids": list(melodies)}


def records(bset, bid, evidence_id, subject, p, mid, cases, *rest):
    sha = p["prereg_sha256"]
    bound = {"kind": "evidence-binding", "schemaVersion": SV, "id": bid, "set": bset, "evidence_id": evidence_id,
             "subject": dict(subject), "prereg_sha256": sha, "membership_id": mid}
    return [bound, p, {"kind": "benchmark-membership", "schemaVersion": SV, "id": mid, "set": bset, "prereg_sha256": sha, "cases": cases}, *rest]


def engine(committed="2026-11-01T09:00:00Z", synthetic=False):
    p = engine_prereg(committed)
    audition = {"kind": "audition", "schemaVersion": SV, "id": "aud_b01", "project_id": None, "mode": "eval", "request_ids": [],
                "brief_id": "brief_b01", "opened_at": "2026-11-03T17:30:00Z", "all_arms_ready_at": "2026-11-02T10:09:00Z",
                "candidate_ids": ["cand_ace", "cand_yue"], "arms": [{"label": "A", "unplayable": False}, {"label": "B", "unplayable": False}],
                "anchors": [], "repeat_pairs": [], "commitment_sha256": H("commitment:aud_b01"), "preview": {"sample_rate": 48000, "bit_depth": 24},
                "gains": [{"label": "A", "gain_db": "-0.80"}, {"label": "B", "gain_db": "0.00"}], "loudness_standard": "BS.1770-4 (pyloudnorm)",
                "true_peak_meter": "studio-truepeak-4x", "residual_mismatch_lu": "0.04", "prereg_sha256": p["prereg_sha256"],
                "state": "revealed", "residual_leak_acknowledged": ["duration", "sonic_character"]}
    verdict = {"kind": "verdict", "schemaVersion": SV, "id": "vd_b01", "audition_id": "aud_b01", "preferred": "A", "axes": [],
               "problem_intervals": [], "seconds_listened": [{"label": "A", "seconds": 150}, {"label": "B", "seconds": 140}],
               "act": owner("give_verdict", "2026-11-03T17:45:00Z"), "evidence_kind": "listening-preregistered"}
    case = {"case_id": "case_b01", "verdict_ids": ["vd_b01"], "arms": [arm(ACE, ["job_ace"], ["cand_ace"]), arm(YUE, ["job_yue"], ["cand_yue"])]}
    return records(ENGINE, "eb_engine", "ev_bench_ace", ACE, p, "bm_engine", [case],
                   job("job_ace", ACE, "generate", "cover", "2026-11-02T10:00:00Z", "local", ("mix", "mix:cand_ace"), 1),
                   job("job_yue", YUE, "generate", "score_to_song", "2026-11-02T10:05:00Z", "worker_host", ("mix", "mix:cand_yue"), 2),
                   candidate("cand_ace", ACE, "R2-synth", "job_ace", 1, "local", synthetic, "2026-11-02T10:04:30Z"),
                   candidate("cand_yue", YUE, "R1", "job_yue", 2, "worker_host", synthetic, "2026-11-02T10:09:00Z"), audition, verdict)


def hum(committed="2026-11-01T09:00:00Z"):
    def log(melody_id):
        return {"kind": "correction-log", "schemaVersion": SV, "melody_id": melody_id, "project_id": "prj_bench",
                "entries": [{"seq": 1, "at": "2026-11-02T12:00:00Z", "base_rev": 1, "new_rev": 2, "ops": [{"op": "move", "note_ids": ["n1"], "delta_ticks": 240}]}]}
    case = {"case_id": "case_h01", "verdict_ids": [], "arms": [arm(PYIN, ["job_pyin"], melodies=["mel_h01_pyin"]), arm(BP, ["job_bp"], melodies=["mel_h01_bp"])]}
    return records(HUM, "eb_hum", "ev_hum_pyin", PYIN, hum_prereg(committed=committed), "bm_hum", [case],
                   job("job_pyin", PYIN, "transcribe", "transcribe", "2026-11-02T11:00:00Z", "local", ("melody_spec", "melody:h01-pyin")),
                   job("job_bp", BP, "transcribe", "transcribe", "2026-11-02T11:10:00Z", "local", ("melody_spec", "melody:h01-bp")),
                   log("mel_h01_pyin"), log("mel_h01_bp"))


def melody():
    doc = {"kind": "melody-spec", "schemaVersion": SV, "melody_id": "mel_bench", "rev": 1, "base_rev": None, "project_id": "prj_bench",
           "created_at": "2026-10-30T09:00:00Z", "spec_kind": "melody", "ppq": 960,
           "tempo_map": {"rev": 1, "tempo": [{"tick": 0, "us_per_quarter": 500000}], "meter": [{"tick": 0, "numerator": 4, "denominator": 4}]},
           "key": {"tonic": "C", "mode": "major"}, "notes": [], "phrases": [],
           "source": {"seed_kind": "midi_file", "capture_sha256": H("midi:bench"), "transcription": None, "assembled_from": None},
           "quantize": None, "content_sha256": ""}
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


def edit(recs, key, change):
    """Apply one hand-written change to the record whose id (or correction-log melody_id) is key."""
    change(next(r for r in recs if r.get("id", r.get("melody_id")) == key))
    return recs


def drop(recs, key):
    return [r for r in recs if r.get("id", r.get("melody_id")) != key]


def build(profiles):
    def case(name, op, check_id, recs, expected, why):
        return {"name": name, "derivation": why, "op": op, "check_id": check_id, "records": recs, "expected": expected}
    hum_edited = edit([hum_prereg()], "bp_hum", lambda p: p["thresholds"][1].update(value="0.20"))
    two_cases = [BRIEF_CASE, {"case_id": "case_b01", "lane": "individual", "brief_id": "brief_b02"}]
    mel = melody()
    cases = [
        case("valid mixed-profile engine-benchmark preregistration", "prereg", "bp_engine", [engine_prereg()], [],
             "ACE SFT on mlx/m5pro and YuE2 on cuda/rtx4090 both declare a benchmark-48 gate and allow the case's individual lane; both "
             "protocol metrics have a threshold; the stored hash is the record's own."),
        case("valid hum-benchmark preregistration", "prereg", "bp_hum", [hum_prereg()], [],
             "pYIN+HMM and Basic Pitch both declare a hum-benchmark gate and allow the individual lane; COn, COnP, COnPOff and "
             "correction effort each have a threshold; the stored hash is the record's own."),
        case("a protocol metric without a threshold", "prereg", "bp_engine", [engine_prereg(thresholds=ENGINE_THRESHOLDS[:1])],
             ["threshold_missing"], "The decision reads repeat_pair_agreement, but no threshold was fixed for it before any run."),
        case("duplicate case ids", "prereg", "bp_engine", [engine_prereg(cases=two_cases)], ["case_duplicate"],
             "Two cases share the id case_b01 (briefs b01 and b02), so a run or verdict could be bound to either."),
        case("a threshold edited after hashing", "prereg", "bp_hum", hum_edited, ["prereg_hash_mismatch"],
             "The conp_f1 threshold moved from 0.30 to 0.20 after prereg_sha256 was computed, so the hash no longer names the record."),
        case("an llc case names YuE2", "prereg", "bp_engine", [engine_prereg(cases=[dict(BRIEF_CASE, lane="llc")])], ["lane_forbidden"],
             "YuE2 is allowed only in individual and research, and an llc case may not name it (ADR-0029 point 6). ACE allows llc."),
        case("an engine profile in a hum benchmark", "prereg", "bp_hum", [hum_prereg(subjects=(PYIN, BP, ACE))], ["subject_ungated"],
             "ACE's benchmark gate set is benchmark-48, so a hum-benchmark preregistration cannot govern it."),
        case("valid mixed-profile engine-benchmark binding", "binding", "eb_engine", engine(), [],
             "ACE's binding names its preregistered subject; both runs were queued after the 09:00 commit; vd_b01 is a preregistered "
             "listening verdict on the eval audition of brief_b01 under this hash, over the case's own non-synthetic candidates."),
        case("valid hum-benchmark binding", "binding", "eb_hum", hum(), [],
             "pYIN's binding names its preregistered subject; both transcription runs were queued after the commit; each draft melody "
             "has a correction log; the case is preregistered."),
        case("engine binding citing a MelodySpec hash", "binding", "eb_engine",
             [edit(engine()[:1], "eb_engine", lambda b: b.update(prereg_sha256=mel["content_sha256"]))[0], mel, engine_prereg()],
             ["prereg_unresolved"], "The cited hash is a known MelodySpec's content hash, not a benchmark preregistration's; nothing else binds."),
        case("hum binding citing a MelodySpec hash", "binding", "eb_hum",
             [edit(hum()[:1], "eb_hum", lambda b: b.update(prereg_sha256=mel["content_sha256"]))[0], mel, hum_prereg()],
             ["prereg_unresolved"], "The cited hash is a known MelodySpec's content hash, not a benchmark preregistration's; nothing else binds."),
        case("hum binding citing the engine preregistration", "binding", "eb_hum",
             [edit(hum()[:1], "eb_hum", lambda b: b.update(prereg_sha256=engine_prereg()["prereg_sha256"]))[0], engine_prereg(), hum_prereg()],
             ["prereg_unresolved"], "The cited hash is a real benchmark preregistration, but of benchmark-48; a hum-benchmark reference never resolves to it."),
        case("preregistration committed after a run it governs", "binding", "eb_engine", engine(committed="2026-11-02T10:01:00Z"),
             ["committed_after_run"], "job_ace was queued at 10:00:00, a minute before the 10:01:00 commit; job_yue (10:05:00) is later."),
        case("a run queued the same second the preregistration was committed", "binding", "eb_hum", hum(committed="2026-11-02T11:00:00Z"),
             ["committed_after_run"], "job_pyin was queued at 11:00:00, the commit time itself; the commit must be strictly earlier than every run."),
        case("synthetic-only verdicts presented as owner listening", "binding", "eb_engine", engine(synthetic=True), ["verdict_synthetic"],
             "vd_b01 is an owner-ui verdict, but both arms of aud_b01 are Synthetic test output; synthetic material never meets a benchmark gate."),
        case("membership of another preregistration", "binding", "eb_hum",
             edit(hum(), "bm_hum", lambda m: m.update(prereg_sha256=H("prereg:another"))), ["membership_unresolved"],
             "bm_hum names a different preregistration hash than the binding, so it is not this set's membership."),
        case("binding for an unpreregistered host class", "binding", "eb_hum",
             edit(hum(), "eb_hum", lambda b: b["subject"].update(host_class="cpu/linux-ci")), ["subject_unregistered"],
             "pYIN was preregistered on cpu/m5pro; evidence from cpu/linux-ci would credit a host class that was never under test."),
        case("membership case not preregistered", "binding", "eb_hum",
             edit(hum(), "bm_hum", lambda m: m["cases"][0].update(case_id="case_h99")), ["case_unregistered"],
             "The preregistration's only case is case_h01; case_h99 was added afterwards."),
        case("a governed run without its job record", "binding", "eb_hum", drop(hum(), "job_bp"), ["run_unresolved"],
             "Basic Pitch's arm names job_bp, but no such job exists, so its start cannot be checked against the commit."),
        case("an expected verdict that does not resolve", "binding", "eb_engine", drop(engine(), "vd_b01"), ["verdict_unresolved"],
             "The membership expects vd_b01 but no such verdict exists."),
        case("a draft melody without its correction log", "binding", "eb_hum", drop(hum(), "mel_h01_bp"), ["correction_unresolved"],
             "Basic Pitch's draft mel_h01_bp has no correction log, so its correction effort is not linked."),
    ]
    return {"kind": KIND, "schemaVersion": SV, "cases": copy.deepcopy(cases)}


def evaluate(case, world):
    want = {"prereg": "benchmark-prereg", "binding": "evidence-binding"}[case["op"]]
    targets = [r for r in case["records"] if r.get("id") == case["check_id"]]
    if len(targets) != 1 or targets[0]["kind"] != want:
        raise ValueError(f"check_id {case['check_id']} must name exactly one {want}")
    if case["op"] == "prereg":
        return binding.prereg_findings(targets[0], world.profiles), case["expected"]
    return binding.binding_findings(targets[0], case["records"], world.profiles), case["expected"]
