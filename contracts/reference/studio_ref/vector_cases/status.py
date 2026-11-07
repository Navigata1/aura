"""Status hand-derived golden cases and public reference evaluator."""
from studio_ref import status
from studio_ref.fixture_support import SV, H, R

KIND = "fixture.status"

def build(profiles):
    PROFILES = profiles
    def evr(eid, check, pid, rev, host, when, result="pass", gate=None, synthetic=False, prereg=None, verdicts=(), checks=(),
            subject_type="profile"):
        return {"kind": "evidence", "schemaVersion": SV, "id": eid, "check": check, "subject": {"subject_type": subject_type, "subject_id": pid},
                "profile_revision": rev, "host_class": host, "gate_id": gate, "result": result, "measured": [],
                "checks": [dict(c) for c in checks], "synthetic": synthetic,
                "attachments": [], "prereg_sha256": prereg, "verdict_ids": list(verdicts), "recorded_at": when}

    def passing(names, verdict=None, drop=()):
        return [{"check": n, "result": "pass", "verdict_id": verdict if n in ("owner_not_garbled", "preregistered_listening") else None,
                 "measured": []} for n in names if n not in drop]
    ACE_SMOKE = PROFILES["ace-2b-sft-mlx"]["gates"]["smoke"]["checks"]
    ace, rev, rev2, host = "ace-2b-sft-mlx", R("ace-2b-sft-mlx"), R("ace-2b-sft-mlx@pin2"), "mlx/m5pro"
    inst = evr("ev_i", "install", ace, rev, host, "2026-10-10T10:00:00Z")
    conf = evr("ev_c", "conformance", ace, rev, host, "2026-10-10T10:05:00Z")
    smoke = evr("ev_s", "smoke", ace, rev, host, "2026-10-10T10:10:00Z", gate="smoke.ace-2b-sft-mlx", verdicts=["vd_smoke"],
                checks=passing(ACE_SMOKE, "vd_smoke"))
    smoke_syn = evr("ev_ss", "smoke", ace, rev, host, "2026-10-10T10:10:00Z", gate="smoke.ace-2b-sft-mlx", synthetic=True,
                    verdicts=["vd_smoke"], checks=passing(ACE_SMOKE, "vd_smoke"))
    smoke_no_ear = evr("ev_sne", "smoke", ace, rev, host, "2026-10-10T10:10:00Z", gate="smoke.ace-2b-sft-mlx",
                       checks=passing(ACE_SMOKE, None, drop=("owner_not_garbled",)))
    smoke_short = evr("ev_ssh", "smoke", ace, rev, host, "2026-10-10T10:10:00Z", gate="smoke.ace-2b-sft-mlx", verdicts=["vd_smoke"],
                      checks=passing(ACE_SMOKE, "vd_smoke", drop=("install_bytes_match_manifest",)))
    bench = evr("ev_b", "benchmark", ace, rev, host, "2026-10-12T10:00:00Z", gate="benchmark.ace-2b-sft-mlx", prereg=H("prereg-bench"))
    later_fail = evr("ev_f", "smoke", ace, rev, host, "2026-10-11T10:00:00Z", result="fail", gate="smoke.ace-2b-sft-mlx",
                     checks=[{"check": "decodes", "result": "fail", "verdict_id": None, "measured": []}])
    early_fail = evr("ev_ef", "install", ace, rev, host, "2026-10-10T09:00:00Z", result="fail")
    listen = {**evr("ev_l", "listening-unregistered", ace, rev, host, "2026-10-11T12:00:00Z", verdicts=["vd_x"])}

    def stc(name, pid, r, h, evs, exp, why):
        return {"name": name, "derivation": why, "profile_id": pid, "profile_revision": r, "host_class": h, "evidence": evs, "expected": exp}
    status = {"kind": "fixture.status", "schemaVersion": SV, "cases": [
        stc("no evidence", ace, rev, host, [], "declared", "Nothing has been checked."),
        stc("install only", ace, rev, host, [inst], "declared", "installed needs install AND conformance."),
        stc("install and conformance", ace, rev, host, [inst, conf], "installed", "Both records pass at this revision and host class."),
        stc("smoke passes", ace, rev, host, [inst, conf, smoke], "smoke-passed",
            "The declared smoke gate passed with real evidence: every declared check passes and Jon's verdict answers 'not garbled'."),
        stc("smoke pass without owner verdict", ace, rev, host, [inst, conf, smoke_no_ear], "installed",
            "The record has no owner_not_garbled check (a verdict id is the only way to answer it), so Jon never listened; it cannot promote."),
        stc("smoke pass missing a declared check", ace, rev, host, [inst, conf, smoke_short], "installed",
            "install_bytes_match_manifest is declared by the gate but absent from the record."),
        stc("synthetic smoke on a real engine", ace, rev, host, [inst, conf, smoke_syn], "installed",
            "ACE's smoke gate does not allow synthetic evidence (ADR-0027)."),
        stc("benchmark without a bound conclusion", ace, rev, host, [inst, conf, smoke, bench], "smoke-passed",
            "A preregistration hash alone proves no concluded result; benchmark promotion is unavailable until its binding contract lands."),
        stc("later failing smoke", ace, rev, host, [inst, conf, smoke, later_fail], "disabled", "A failing record after promotion disables."),
        stc("benchmark after a failure stays disabled", ace, rev, host, [inst, conf, smoke, later_fail, bench], "disabled", "disabled is terminal."),
        stc("early failure then success", ace, rev, host, [early_fail, inst, conf], "installed", "A failure while declared changes nothing."),
        stc("pin change starts over", ace, rev2, host, [inst, conf, smoke], "declared",
            "A pin change is a new revision; with no records at it, it computes to declared (not installed)."),
        stc("pin change reinstalled", ace, rev2, host,
            [inst, conf, smoke, evr("ev_i2", "install", ace, rev2, host, "2026-10-13T10:00:00Z"),
             evr("ev_c2", "conformance", ace, rev2, host, "2026-10-13T10:05:00Z")], "installed",
            "A new revision with install and conformance returns to installed, not smoke-passed."),
        stc("other host class", ace, rev, "cuda/rtx4090", [inst, conf, smoke], "declared", "A status on one host class says nothing about another."),
        stc("unregistered listening changes nothing", ace, rev, host, [inst, conf, smoke, listen], "smoke-passed", "Product verdicts never promote."),
        stc("test_only synthetic smoke", "fake-route-a", R("fake-route-a"), "fake/local",
            [evr("ev_fi", "install", "fake-route-a", R("fake-route-a"), "fake/local", "2026-10-09T09:00:00Z", synthetic=True),
             evr("ev_fc", "conformance", "fake-route-a", R("fake-route-a"), "fake/local", "2026-10-09T09:01:00Z", synthetic=True),
             evr("ev_fs", "smoke", "fake-route-a", R("fake-route-a"), "fake/local", "2026-10-09T09:02:00Z", gate="smoke.fake-route-a", synthetic=True,
                 checks=passing(["conformance", "decodes", "non_silent"]))],
            "smoke-passed", "test_only profiles accept synthetic smoke evidence."),
        stc("transcriber synthetic floor", "analysis-transcribe-pyin-hmm", R("analysis-transcribe-pyin-hmm"), "cpu/m5pro",
            [evr("ev_ti", "install", "analysis-transcribe-pyin-hmm", R("analysis-transcribe-pyin-hmm"), "cpu/m5pro", "2026-10-09T09:00:00Z"),
             evr("ev_tc", "conformance", "analysis-transcribe-pyin-hmm", R("analysis-transcribe-pyin-hmm"), "cpu/m5pro", "2026-10-09T09:01:00Z"),
             evr("ev_ts", "smoke", "analysis-transcribe-pyin-hmm", R("analysis-transcribe-pyin-hmm"), "cpu/m5pro", "2026-10-09T09:02:00Z",
                 gate="smoke.analysis-transcribe-pyin-hmm", synthetic=True, checks=passing(["conformance", "transcription_floor_synthetic"]))],
            "smoke-passed", "The transcriber's smoke gate is the synthetic floor, which allows synthetic evidence."),
        stc("no benchmark gate", "analysis-measure", R("analysis-measure"), "cpu/m5pro",
            [evr("ev_mi", "install", "analysis-measure", R("analysis-measure"), "cpu/m5pro", "2026-10-09T09:00:00Z"),
             evr("ev_mc", "conformance", "analysis-measure", R("analysis-measure"), "cpu/m5pro", "2026-10-09T09:01:00Z"),
             evr("ev_ms", "smoke", "analysis-measure", R("analysis-measure"), "cpu/m5pro", "2026-10-09T09:02:00Z", gate="smoke.analysis-measure",
                 checks=passing(["conformance", "decodes"])),
             evr("ev_mb", "benchmark", "analysis-measure", R("analysis-measure"), "cpu/m5pro", "2026-10-12T09:00:00Z",
                 gate="benchmark.analysis-measure", prereg=H("prereg-x"))],
            "smoke-passed", "analysis-measure declares no benchmark gate, so nothing can benchmark it."),
        stc("capability smoke missing the ui_p95 check", "studio.playback.darwin", None, "cpu/m5pro",
            [evr("ev_pb_i", "install", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:00:00Z", subject_type="capability"),
             evr("ev_pb_c", "conformance", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:01:00Z", subject_type="capability"),
             evr("ev_pb_s", "smoke", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:40:00Z", gate="smoke.studio-playback-darwin",
                 subject_type="capability", checks=passing(["playback_underruns_zero"]))],
            "installed", "The playback gate declares ui_p95_under_100ms; a record without it cannot pass the gate."),
        stc("capability smoke with every check", "studio.playback.darwin", None, "cpu/m5pro",
            [evr("ev_pb_i", "install", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:00:00Z", subject_type="capability"),
             evr("ev_pb_c", "conformance", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:01:00Z", subject_type="capability"),
             evr("ev_pb_s", "smoke", "studio.playback.darwin", None, "cpu/m5pro", "2026-10-20T09:40:00Z", gate="smoke.studio-playback-darwin",
                 subject_type="capability", checks=passing(["playback_underruns_zero", "ui_p95_under_100ms"]))],
            "smoke-passed", "Both declared playback checks pass on a real host of this OS."),
    ]}

    for name in ("smoke passes", "transcriber synthetic floor"):
        case = next(c for c in status["cases"] if c["name"] == name)
        pid, revision, host_class = case["profile_id"], case["profile_revision"], case["host_class"]
        check = "hum-benchmark" if pid == "analysis-transcribe-pyin-hmm" else "benchmark"
        for outcome in ("pass", "fail", "inconclusive"):
            record = evr("ev_unbound_" + outcome, check, pid, revision, host_class, "2026-10-12T10:00:00Z",
                         result=outcome, gate="benchmark." + pid, prereg=H("prereg-bench"),
                         checks=passing(["preregistered_listening"], "vd_existing"), verdicts=["vd_existing"])
            status["cases"].append(stc(check + " " + outcome + " is unsupported", pid, revision, host_class,
                                      case["evidence"] + [record], "smoke-passed",
                                      "A preregistration hash and verdict id cannot establish a bound conclusion, so it neither promotes nor disables."))
    return status

def evaluate(case, world):
    subject = world.profiles.get(case["profile_id"]) or world.capabilities.get(case["profile_id"])
    got = status.compute_status(subject, case["evidence"], case["profile_revision"], case["host_class"]) if subject else "unknown profile"
    return got, case["expected"]
