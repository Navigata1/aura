"""Evidence-binding inputs (T02b): hand-derived golden cases and the public reference evaluator.

Every record here is a hypothetical input to studio_ref.binding: nothing was rendered, measured or heard and no owner
act took place. Expected findings are written by hand from each derivation, never computed by binding.py. No case
concludes a result or promotes, demotes or disables anything (C02 binds results; C01 still refuses them).
"""
import copy

from studio_ref import binding
from studio_ref.canonical import self_hash, sha_of
from studio_ref.fixture_support import SV, H, R, owner

KIND = "fixture.binding"
ENGINE, HUM = "benchmark-48", "hum-benchmark"
COMMITTED = "2026-11-01T09:00:00Z"
ACE = {"profile_id": "ace-2b-sft-mlx", "profile_revision": R("ace-2b-sft-mlx"), "host_class": "mlx/m5pro"}
YUE = {"profile_id": "yue2-3b-score", "profile_revision": R("yue2-3b-score"), "host_class": "cuda/rtx4090"}
PYIN = {"profile_id": "analysis-transcribe-pyin-hmm", "profile_revision": R("analysis-transcribe-pyin-hmm"), "host_class": "cpu/m5pro"}
BASIC_PITCH = {"profile_id": "transcribe-basic-pitch", "profile_revision": R("transcribe-basic-pitch"), "host_class": "cpu/m5pro"}
WITHHELD = ["route", "profile_id", "profile_revision", "seed", "placement", "job_id", "artifact_sha256", "preview_sha256",
            "measures", "adherence", "hard_constraints", "badges", "diagnostics", "source"]
ENGINE_THRESHOLDS = [("preferred_rate", "gte", "0.50"), ("repeat_pair_agreement", "gte", "0.70")]
HUM_THRESHOLDS = [("con_f1", "gte", "0.40"), ("conp_f1", "gte", "0.30"), ("conpoff_f1", "gte", "0.20"), ("correction_ops", "lte", "60")]
HUM_DECISION = {"rank_by": "correction_ops", "order": "lowest", "none_pass": "manual_entry"}
BENCHMARK_BRIEFS = [f"brief_b{i:02d}" for i in range(1, 49)]
C02_WILL_CHANGE = " C02 will change this golden when it requires all 48 briefs and resolves the evidence record."


def thresholds(rows):
    return [{"metric": m, "comparator": c, "value": v} for m, c, v in rows]


def brief(lane="individual"):
    return {"kind": "eval-brief", "schemaVersion": SV, "id": "brief_b01", "set": "benchmark", "case": "hummed_ballad",
            "feel": "worship_acoustic_ballad", "lane": lane, "seed": {"seed_kind": "hum", "sha256": H("hum:b01")}, "song": None,
            "compared": [{"route": "R2-synth", "profile_id": ACE["profile_id"]}, {"route": "R1", "profile_id": YUE["profile_id"]}],
            "candidates_per_arm": 1, "reference_ids": [], "notes": "Hypothetical benchmark brief."}


BRIEF_CASE = {"case_id": "case_b01", "lane": "individual", "brief_id": "brief_b01", "brief_sha256": sha_of(brief())}
HUM_CASE = {"case_id": "case_h01", "lane": "individual", "hum_sha256": H("hum:h01"), "ground_truth_sha256": H("midi:h01")}


def hashed(doc, overrides):
    doc = copy.deepcopy({**doc, **overrides})
    doc["prereg_sha256"] = self_hash(doc, "prereg_sha256")
    return doc


def engine_prereg(**overrides):
    return hashed({"kind": "benchmark-prereg", "schemaVersion": SV, "id": "bp_engine", "prereg_sha256": "", "set": ENGINE,
                   "eval_set_id": "es_bench", "subjects": [ACE, YUE], "cases": [BRIEF_CASE], "asset_hashes": [H("hum:b01")],
                   "budgets": {"candidates_per_brief": 1, "compute_usd_cap": "5.00", "listening_minutes": 60}, "burst_run_ceiling_usd": "2.00",
                   "listening_quota": {"sessions_min": 1, "repeat_pair_fraction": "0.10", "short_quota_outcome": "inconclusive"},
                   "coverage": {"cases_complete_min": 1}, "protocol": {"method": "eval_audition", "metrics": [m for m, _, _ in ENGINE_THRESHOLDS]},
                   "thresholds": thresholds(ENGINE_THRESHOLDS), "decision": None, "gate_owner": "jon", "committed_at": COMMITTED}, overrides)


def hum_prereg(**overrides):
    return hashed({"kind": "benchmark-prereg", "schemaVersion": SV, "id": "bp_hum", "prereg_sha256": "", "set": HUM, "eval_set_id": None,
                   "subjects": [PYIN, BASIC_PITCH], "cases": [HUM_CASE], "asset_hashes": sorted([H("hum:h01"), H("midi:h01")]),
                   "budgets": {"candidates_per_brief": 1, "compute_usd_cap": "0.00", "listening_minutes": 30}, "burst_run_ceiling_usd": "0.00",
                   "listening_quota": {"sessions_min": 1, "repeat_pair_fraction": "0", "short_quota_outcome": "inconclusive"},
                   "coverage": {"cases_complete_min": 1}, "protocol": {"method": "blind_correction", "metrics": [m for m, _, _ in HUM_THRESHOLDS]},
                   "thresholds": thresholds(HUM_THRESHOLDS), "decision": dict(HUM_DECISION), "gate_owner": "jon", "committed_at": COMMITTED}, overrides)


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
    return copy.deepcopy([bound, p, {"kind": "benchmark-membership", "schemaVersion": SV, "id": mid, "set": bset, "prereg_sha256": sha,
                                     "cases": cases}, *rest])


def engine(synthetic=False, **prereg_overrides):
    p = engine_prereg(**prereg_overrides)
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
    return records(ENGINE, "eb_engine", "ev_bench_ace", ACE, p, "bm_engine", [case], brief(),
                   {"kind": "eval-set", "schemaVersion": SV, "id": "es_bench", "set": "benchmark", "brief_ids": BENCHMARK_BRIEFS},
                   job("job_ace", ACE, "generate", "cover", "2026-11-02T10:00:00Z", "local", ("mix", "mix:cand_ace"), 1),
                   job("job_yue", YUE, "generate", "score_to_song", "2026-11-02T10:05:00Z", "worker_host", ("mix", "mix:cand_yue"), 2),
                   candidate("cand_ace", ACE, "R2-synth", "job_ace", 1, "local", synthetic, "2026-11-02T10:04:30Z"),
                   candidate("cand_yue", YUE, "R1", "job_yue", 2, "worker_host", synthetic, "2026-11-02T10:09:00Z"), audition, verdict)


def correction_log(melody_id):
    return {"kind": "correction-log", "schemaVersion": SV, "melody_id": melody_id, "project_id": "prj_bench",
            "entries": [{"seq": 1, "at": "2026-11-02T12:00:00Z", "base_rev": 1, "new_rev": 2, "ops": [{"op": "move", "note_ids": ["n1"], "delta_ticks": 240}]}]}


def transcription(jid, subject, queued, melody):
    return job(jid, subject, "transcribe", "transcribe", queued, "local", ("melody_spec", "melody:" + melody))


def hum(**prereg_overrides):
    case = {"case_id": "case_h01", "verdict_ids": [],
            "arms": [arm(PYIN, ["job_pyin"], melodies=["mel_h01_pyin"]), arm(BASIC_PITCH, ["job_bp"], melodies=["mel_h01_bp"])]}
    return records(HUM, "eb_hum", "ev_hum_pyin", PYIN, hum_prereg(**prereg_overrides), "bm_hum", [case],
                   transcription("job_pyin", PYIN, "2026-11-02T11:00:00Z", "mel_h01_pyin"),
                   transcription("job_bp", BASIC_PITCH, "2026-11-02T11:10:00Z", "mel_h01_bp"),
                   correction_log("mel_h01_pyin"), correction_log("mel_h01_bp"))


def melody():
    doc = {"kind": "melody-spec", "schemaVersion": SV, "melody_id": "mel_bench", "rev": 1, "base_rev": None, "project_id": "prj_bench",
           "created_at": "2026-10-30T09:00:00Z", "spec_kind": "melody", "ppq": 960,
           "tempo_map": {"rev": 1, "tempo": [{"tick": 0, "us_per_quarter": 500000}], "meter": [{"tick": 0, "numerator": 4, "denominator": 4}]},
           "key": {"tonic": "C", "mode": "major"}, "notes": [], "phrases": [],
           "source": {"seed_kind": "midi_file", "capture_sha256": H("midi:bench"), "transcription": None, "assembled_from": None},
           "quantize": None, "content_sha256": ""}
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


def key(record):
    return record.get("id", record.get("melody_id"))


def edit(recs, name, change):
    """Apply one hand-written change to the record named name (its id, or a correction log's melody_id)."""
    change(next(r for r in recs if key(r) == name))
    return recs


def drop(recs, name):
    return [r for r in recs if key(r) != name]


def citing(recs, sha, *others):
    """Just the binding from recs, made to cite sha, beside the other records given."""
    return [dict(recs[0], prereg_sha256=sha), *others]


def heard_extra(recs):
    """aud_b01 also played cand_extra, an ACE candidate the membership does not list."""
    recs.append(candidate("cand_extra", ACE, "R2-synth", "job_ace", 3, "local", False, "2026-11-02T10:04:40Z"))
    return edit(recs, "aud_b01", lambda a: a.update(candidate_ids=["cand_ace", "cand_extra", "cand_yue"],
                                                    arms=[{"label": x, "unplayable": False} for x in "ABC"],
                                                    gains=[{"label": "A", "gain_db": "-0.80"}, {"label": "B", "gain_db": "0.00"},
                                                           {"label": "C", "gain_db": "-0.30"}]))


def other_set_membership():
    """bm_hum replaced by a benchmark-48 membership that cites the hum preregistration's hash."""
    recs = hum()
    engine_shaped = dict(engine()[2], id="bm_hum", prereg_sha256=recs[1]["prereg_sha256"])
    return [recs[0], recs[1], engine_shaped, *recs[3:]]


def second_basic_pitch_melody(recs):
    recs.append(correction_log("mel_h01_bp2"))
    return edit(recs, "bm_hum", lambda m: m["cases"][0]["arms"][1]["melody_ids"].append("mel_h01_bp2"))


def build(profiles):
    def case(name, op, check_id, recs, expected, why):
        return {"name": name, "derivation": why, "op": op, "check_id": check_id, "records": recs, "expected": expected}
    mel, linux = melody(), "cpu/linux-ci"
    cases = [
        case("valid mixed-profile engine-benchmark preregistration", "prereg", "bp_engine", [engine_prereg()], [],
             "ACE SFT on mlx/m5pro and YuE2 on cuda/rtx4090 both declare a benchmark-48 gate and allow the case's individual lane; each "
             "protocol metric has one threshold; the 2.00 ceiling is within the 5.00 cap; coverage 1 fits one case; the hash is the record's own."
             + C02_WILL_CHANGE),
        case("valid hum-benchmark preregistration", "prereg", "bp_hum", [hum_prereg()], [],
             "pYIN+HMM and Basic Pitch declare hum-benchmark gates and allow individual; COn, COnP, COnPOff and correction_ops have one "
             "threshold each; the decision ranks by correction_ops with manual entry when none passes; the hum and its ground truth are listed."),
        case("a protocol metric without a threshold", "prereg", "bp_engine", [engine_prereg(thresholds=thresholds(ENGINE_THRESHOLDS[:1]))],
             ["threshold_missing"], "The decision reads repeat_pair_agreement, but no threshold was fixed for it before any run."),
        case("two thresholds for one metric", "prereg", "bp_engine",
             [engine_prereg(thresholds=thresholds(ENGINE_THRESHOLDS + [("preferred_rate", "gte", "0.10")]))], ["threshold_ambiguous"],
             "preferred_rate carries gte 0.50 and gte 0.10, so which value is the preregistered one would be chosen after the output."),
        case("duplicate case ids", "prereg", "bp_engine", [engine_prereg(cases=[BRIEF_CASE, dict(BRIEF_CASE, brief_id="brief_b02")])],
             ["case_duplicate"], "Two cases share the id case_b01 (briefs b01 and b02), so a job or verdict could be bound to either."),
        case("a threshold edited after hashing", "prereg", "bp_hum", edit([hum_prereg()], "bp_hum", lambda p: p["thresholds"][1].update(value="0.20")),
             ["prereg_hash_mismatch"], "The conp_f1 threshold moved from 0.30 to 0.20 after prereg_sha256 was computed, so the hash no longer names the record."),
        case("an llc case names YuE2", "prereg", "bp_engine", [engine_prereg(cases=[dict(BRIEF_CASE, lane="llc")])], ["lane_forbidden"],
             "YuE2 is allowed only in individual and research, and an llc case may not name it (ADR-0029 point 6). ACE allows llc."),
        case("an engine profile in a hum benchmark", "prereg", "bp_hum", [hum_prereg(subjects=[PYIN, BASIC_PITCH, ACE])], ["subject_ungated"],
             "ACE's benchmark gate set is benchmark-48, so a hum-benchmark preregistration cannot govern it."),
        case("a subject the registry does not declare", "prereg", "bp_hum",
             [hum_prereg(subjects=[PYIN, dict(BASIC_PITCH, profile_id="transcribe-unknown")])], ["subject_ungated"],
             "No declared profile is called transcribe-unknown, so it has no benchmark gate at all."),
        case("a decision ranked by a metric the protocol does not read", "prereg", "bp_hum",
             [hum_prereg(decision=dict(HUM_DECISION, rank_by="note_count"))], ["decision_unregistered"],
             "note_count is not among the four protocol metrics, so it has no preregistered threshold to rank passing subjects by."),
        case("a hum case whose ground truth is not among the asset hashes", "prereg", "bp_hum", [hum_prereg(asset_hashes=[H("hum:h01")])],
             ["asset_unlisted"], "case_h01's MIDI ground truth is missing from asset_hashes, so it is not pinned by the preregistration."),
        case("a burst-run ceiling above the compute cap", "prereg", "bp_engine", [engine_prereg(burst_run_ceiling_usd="6.00")],
             ["ceiling_exceeds_cap"], "One burst run could carry a 6.00 ceiling while the whole evaluation is capped at 5.00."),
        case("coverage the case set cannot reach", "prereg", "bp_engine", [engine_prereg(coverage={"cases_complete_min": 2})],
             ["coverage_unreachable"], "Coverage asks for two complete cases, but only one case is preregistered."),
        case("valid mixed-profile engine-benchmark binding", "binding", "eb_engine", engine(), [],
             "ACE's binding names its subject; brief_b01 still hashes to its pinned content, sits in the 48-brief benchmark set and its seed is "
             "listed; both jobs were queued after the 09:00 commit with one candidate each; vd_b01 is a preregistered listening verdict on "
             "aud_b01 for brief_b01 under this hash, over the case's own non-synthetic candidates." + C02_WILL_CHANGE),
        case("valid hum-benchmark binding", "binding", "eb_hum", hum(), [],
             "pYIN's binding names its subject; both transcription jobs match their arms and were queued after the commit; each arm holds one "
             "MelodySpec, as the budget fixes, and each has a correction log; the case is preregistered."),
        case("engine binding citing a MelodySpec hash", "binding", "eb_engine", citing(engine(), mel["content_sha256"], mel, engine_prereg()),
             ["prereg_unresolved"], "The cited hash is a known MelodySpec's content hash, not a benchmark preregistration's; nothing else binds."),
        case("hum binding citing a MelodySpec hash", "binding", "eb_hum", citing(hum(), mel["content_sha256"], mel, hum_prereg()),
             ["prereg_unresolved"], "The cited hash is a known MelodySpec's content hash, not a benchmark preregistration's; nothing else binds."),
        case("hum binding citing the engine preregistration", "binding", "eb_hum",
             citing(hum(), engine_prereg()["prereg_sha256"], engine_prereg(), hum_prereg()), ["prereg_unresolved"],
             "The cited hash is a real benchmark preregistration, but of benchmark-48; a hum-benchmark reference never resolves to it."),
        case("a binding citing the stale hash of an edited preregistration", "binding", "eb_hum",
             edit(hum(), "bp_hum", lambda p: p["thresholds"][1].update(value="0.20")), ["prereg_unresolved"],
             "bp_hum still stores the hash it had before conp_f1 moved to 0.20; a reference resolves only to a record whose own hash it is."),
        case("the preregistration recorded twice", "binding", "eb_hum", hum() + [hum_prereg()], ["prereg_unresolved", "record_duplicate"],
             "bp_hum appears twice, so the record set is ambiguous and the reference does not resolve to exactly one preregistration."),
        case("a job recorded twice", "binding", "eb_hum", hum() + [transcription("job_pyin", PYIN, "2026-10-31T08:00:00Z", "mel_h01_pyin")],
             ["record_duplicate"], "job_pyin appears twice, once queued before the commit; with two records for one id nothing binds."),
        case("membership of another preregistration", "binding", "eb_hum",
             edit(hum(), "bm_hum", lambda m: m.update(prereg_sha256=H("prereg:another"))), ["membership_unresolved"],
             "bm_hum names a different preregistration hash than the binding, so it is not this set's membership."),
        case("membership of the other benchmark set", "binding", "eb_hum", other_set_membership(), ["membership_unresolved"],
             "bm_hum cites the hum preregistration's hash but is a benchmark-48 membership, not a hum-benchmark one."),
        case("binding for an unpreregistered host class", "binding", "eb_hum",
             edit(hum(), "eb_hum", lambda b: b["subject"].update(host_class=linux)), ["subject_unregistered"],
             "pYIN was preregistered on cpu/m5pro; evidence from cpu/linux-ci would credit a host class that was never under test."),
        case("an arm whose subject was not preregistered", "binding", "eb_hum",
             edit(edit(hum(), "bm_hum", lambda m: m["cases"][0]["arms"][1]["subject"].update(host_class=linux)),
                  "job_bp", lambda j: j["placement"].update(host_class=linux)), ["subject_unregistered"],
             "Basic Pitch's arm and its job ran on cpu/linux-ci, but only cpu/m5pro was preregistered for it."),
        case("a transcription job on another host class", "binding", "eb_hum",
             edit(hum(), "job_bp", lambda j: j["placement"].update(host_class=linux)), ["job_unresolved"],
             "Basic Pitch's arm is cpu/m5pro, but job_bp ran on cpu/linux-ci, so the job is not that arm's."),
        case("membership case not preregistered", "binding", "eb_hum",
             edit(hum(), "bm_hum", lambda m: m["cases"][0].update(case_id="case_h99")), ["case_unregistered"],
             "The preregistration's only case is case_h01; case_h99 was added afterwards."),
        case("a governed job without its record", "binding", "eb_hum", drop(hum(), "job_bp"), ["job_unresolved"],
             "Basic Pitch's arm names job_bp, but no such job exists, so its start cannot be checked against the commit."),
        case("preregistration committed after a run it governs", "binding", "eb_engine", engine(committed_at="2026-11-02T10:01:00Z"),
             ["committed_after_run"], "job_ace was queued at 10:00:00, a minute before the 10:01:00 commit; job_yue (10:05:00) is later."),
        case("a job queued the same second the preregistration was committed", "binding", "eb_hum",
             hum(committed_at="2026-11-02T11:00:00Z"), ["committed_after_run"],
             "job_pyin was queued at 11:00:00, the commit time itself; the commit must be strictly earlier than every job."),
        case("an arm with more MelodySpecs than the candidate budget", "binding", "eb_hum", second_basic_pitch_melody(hum()),
             ["candidates_unequal"], "Basic Pitch's arm holds two transcribed MelodySpecs, but the budget fixes one per arm (equal-candidate track)."),
        case("a transcribed MelodySpec without its correction log", "binding", "eb_hum", drop(hum(), "mel_h01_bp"), ["correction_unresolved"],
             "Basic Pitch's MelodySpec mel_h01_bp has no correction log, so its correction effort is not linked."),
        case("an expected verdict that does not resolve", "binding", "eb_engine", drop(engine(), "vd_b01"), ["verdict_unresolved"],
             "The membership expects vd_b01, but no such verdict exists."),
        case("a listening-unregistered verdict expected as preregistered", "binding", "eb_engine",
             edit(engine(), "vd_b01", lambda v: v.update(evidence_kind="listening-unregistered")), ["verdict_unresolved"],
             "vd_b01 is an everyday product verdict, which never changes a status, not a preregistered listening verdict."),
        case("an eval audition of another preregistration", "binding", "eb_engine",
             edit(engine(), "aud_b01", lambda a: a.update(prereg_sha256=H("prereg:another"))), ["verdict_unresolved"],
             "aud_b01 was opened under a different preregistration hash, so its verdict is not this set's."),
        case("an eval audition of another brief", "binding", "eb_engine", edit(engine(), "aud_b01", lambda a: a.update(brief_id="brief_b02")),
             ["verdict_unresolved"], "aud_b01 auditioned brief_b02, but case_b01 is brief_b01."),
        case("an audition that also heard a candidate outside the case", "binding", "eb_engine", heard_extra(engine()), ["verdict_unresolved"],
             "aud_b01 also played cand_extra, which no arm of case_b01 lists, so the verdict judged material outside the case."),
        case("synthetic-only verdicts presented as owner listening", "binding", "eb_engine", engine(synthetic=True), ["verdict_synthetic"],
             "vd_b01 is an owner-ui verdict, but both arms of aud_b01 are Synthetic test output; synthetic material never meets a benchmark gate."),
        case("a brief edited after the commit", "binding", "eb_engine",
             edit(engine(), "brief_b01", lambda b: b.update(notes="Edited after the commit.")), ["brief_unresolved"],
             "brief_b01's notes changed after the preregistration pinned its content, so it no longer hashes to brief_sha256."),
        case("a case lane that differs from its brief", "binding", "eb_engine", engine(cases=[dict(BRIEF_CASE, lane="research")]),
             ["brief_unresolved"], "case_b01 is preregistered in research, but brief_b01 runs in individual. Both profiles allow research."),
        case("a brief seed missing from the asset hashes", "binding", "eb_engine", engine(asset_hashes=[]), ["asset_unlisted"],
             "brief_b01's hum seed is not among the preregistered asset hashes."),
        case("the benchmark set missing", "binding", "eb_engine", drop(engine(), "es_bench"), ["eval_set_unresolved"],
             "The preregistration names es_bench, but no such eval set exists."),
        case("the smoke set named as the benchmark set", "binding", "eb_engine",
             edit(engine(), "es_bench", lambda s: s.update(set="smoke", brief_ids=BENCHMARK_BRIEFS[:12])), ["eval_set_unresolved"],
             "es_bench is a 12-brief smoke set, not the benchmark set a benchmark-48 preregistration draws on."),
        case("a case brief outside the benchmark set", "binding", "eb_engine",
             edit(engine(), "es_bench", lambda s: s.update(brief_ids=[f"brief_b{i:02d}" for i in range(2, 50)])), ["eval_set_unresolved"],
             "es_bench lists 48 briefs, brief_b02 to brief_b49, but not brief_b01."),
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
