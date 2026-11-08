#!/usr/bin/env python3
"""Write contracts/fixtures deterministically (same bytes every run). Standard library only.

    python3 contracts/reference/generate_fixtures.py          # rewrite contracts/fixtures
    python3 contracts/reference/generate_fixtures.py --check  # exit 1 if any file would change

What it writes:

- fixtures/registry/   test overlays: the fake-* engine profiles and fake-* components (FakeEngine stand-ins for
                       YuE2, Demucs and the non-commercial components, architecture.md §4.10).
- fixtures/world/      one valid world: two projects (individual and llc) carried from capture to export through the
                       real contracts, every record its own file. All audio hashes are synthetic labels; nothing here
                       was rendered, measured or listened to, and every engine output is marked synthetic_test.
- fixtures/world/assertions.json   hand-derived lane and closure expectations about that world.
- fixtures/scenarios/  reference-rule cases: the world plus an overlay, with the exact rule ids they must trigger.
- fixtures/invalid/    schema-rule cases: one record each that its schema must reject, with the expected error.
- fixtures/vectors/    golden vectors for the pure functions, expected values derived by hand.

The world and scenarios are built here so that hashes stay consistent; the expectations are not computed by the
rules under test.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIX = ROOT / "contracts" / "fixtures"
sys.path.insert(0, str(HERE))

from studio_ref.canonical import self_hash, sha256_hex, sha_of  # noqa: E402

from studio_ref.fixture_support import SV, H, R, owner
LANES = ["individual", "llc", "research"]
REGISTER = json.loads((ROOT / "contracts/registry/components.v1.json").read_text(encoding="utf-8"))
REAL_PROFILES = json.loads((ROOT / "contracts/registry/engine-profiles.v1.json").read_text(encoding="utf-8"))


def dump(doc) -> bytes:
    return (json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


# ======================================================================================================================
# Test overlays
# ======================================================================================================================

def fake_component(cid, name, blockers, lanes, boundary, note):
    return {"id": cid, "name": name, "category": "song-engine", "role": note, "code_license": "Own test code",
            "weights_license": "Fixture stand-in for a non-commercial or research-only license", "output_terms": "Test only.",
            "gated": None, "verdict": "research-only", "verdict_condition": None, "allowed_lanes": lanes,
            "redistribution_blocker": "Stand-in for a release blocker.", "release_blockers": blockers, "obligations": [],
            "process_boundary_required": boundary, "verification_status": "unverified", "v1_path": False,
            "test_only": True, "primary_sources": [], "notes": "FakeEngine stand-in (architecture.md §4.10); never shipped."}


FAKE_COMPONENTS = [
    fake_component("fake-nc-weights", "Fake non-commercial weights", ["non_commercial_weights"], ["individual", "research"], True,
                   "Declared by fake-nc and fake-burst so lane tests run without YuE2."),
    fake_component("fake-nc-separator-weights", "Fake separator weights (non-commercial by author)", ["non_commercial_by_author"],
                   ["individual", "research"], True, "Declared by fake-separate, the Demucs stand-in."),
    fake_component("fake-research-scorer", "Fake research-only scorer", ["research_or_academic"], ["research"], True,
                   "A research-lane-only component for lane-policy tests."),
]
COMPONENTS = {c["id"]: c for c in REGISTER["components"]} | {c["id"]: c for c in FAKE_COMPONENTS}


def lic(ids):
    return [{"component_id": i, "code_license": COMPONENTS[i]["code_license"], "weights_license": COMPONENTS[i]["weights_license"],
             "obligations": COMPONENTS[i]["obligations"]} for i in ids]


def lanes_of(ids, parents=()):
    s = set(LANES)
    for i in ids:
        s &= set(COMPONENTS[i]["allowed_lanes"])
    for p in parents:
        s &= set(p["provenance"]["eligible_lanes"])
    return [lane for lane in LANES if lane in s]


def fake_profile(pid, title, tasks, comps, rate, langs=("en",)):
    return {"id": pid, "engine": "fake", "title": title, "checkpoint": "FakeEngine (NeutralVoice guide plus a key-derived pad)",
            "tasks": tasks, "limits": {"max_duration_s": 600, "sample_rate": rate, "channels": 2 if rate else None,
                                       "lyric_languages": list(langs) if langs else None, "instrumental_only": False},
            "backend": "fake", "host_os": ["darwin", "linux", "windows"], "heavy": False, "components": comps,
            "allowed_lanes": lanes_of(comps), "license_record": lic(comps),
            "pins": {"code": {"repo": "Navigata1/aura", "commit": None, "min_commit": None}, "weights": None,
                     "env": {"kind": "uv_lock", "ref": None}},
            "gates": {"smoke": {"gate_id": f"smoke.{pid}", "checks": ["conformance", "decodes", "non_silent"],
                                "synthetic_allowed": True, "owner": "jon"}, "benchmark": None},
            "test_only": True, "claims_published": [], "results_local": [],
            "notes": "test_only: visible only when STUDIO_ENV is dev or test; outputs read 'Synthetic test output'."}


FAKE_PROFILES = [
    fake_profile("fake-route-a", "FakeEngine route A (stands in for an ACE cover)", ["cover", "text_to_song"], ["studio-own-code", "neutralvoice"], 44100),
    fake_profile("fake-route-b", "FakeEngine route B", ["cover", "text_to_song"], ["studio-own-code", "neutralvoice"], 48000),
    fake_profile("fake-burst", "FakeEngine burst pod (stands in for YuE2 on a paid burst)", ["score_to_song"], ["studio-own-code", "fake-nc-weights"], 48000),
    fake_profile("fake-nc", "FakeEngine with a non-commercial component", ["cover"], ["studio-own-code", "fake-nc-weights"], 48000),
    fake_profile("fake-separate", "FakeEngine separator (stands in for Demucs; returns the vocal it embedded)", ["separate"],
                 ["studio-own-code", "fake-nc-separator-weights"], None, langs=None),
]
FAKE_PROFILES[0]["results_local"] = [{"evidence_id": "ev_fra_smoke", "metric": "total_wall_ms", "value": "1200", "unit": "ms",
                                      "label": "MEASURED-LOCAL", "host_class": "fake/local"}]
PROFILES = {p["id"]: p for p in REAL_PROFILES["profiles"]} | {p["id"]: p for p in FAKE_PROFILES}

OVERLAY_PROFILES = {"kind": "engine-profile-registry", "schemaVersion": SV, "registry_id": "engine-profiles.fake-overlay",
                    "overlay": True, "updated_at": "2026-10-09T09:00:00Z", "profiles": FAKE_PROFILES}
OVERLAY_COMPONENTS = {"kind": "component-register", "schemaVersion": SV, "register_id": "components.fake-overlay",
                      "overlay": True, "generated_from": [], "components": FAKE_COMPONENTS}

# ======================================================================================================================
# The valid world
# ======================================================================================================================

HOST_FAKE = {"host_id": "host_mac", "os": "darwin", "arch": "arm64", "backend": "fake", "host_class": "fake/local"}
HOST_BURST = {"host_id": "host_fakepod", "os": "linux", "arch": "x86_64", "backend": "fake", "host_class": "fake/burst"}
HOST_CPU = {"host_id": "host_mac", "os": "darwin", "arch": "arm64", "backend": "cpu", "host_class": "cpu/m5pro"}
CP_LOCAL = {"compute_profile_id": "cp_tier4", "tier": 4, "placement": "local"}
CP_BURST = {"compute_profile_id": "cp_tier4", "tier": 4, "placement": "burst"}
SYN = "Synthetic test output"


def timings(load, run):
    return {"cold": True, "load_wall_ms": load, "run_wall_ms": run, "total_wall_ms": load + run, "peak_rss_bytes": 268435456,
            "label": "MEASURED-LOCAL", "measured_by": "worker-sdk"}


def wav(rate, channels, seconds, fmt="pcm_f32"):
    return {"sample_rate": rate, "channels": channels, "frames": rate * seconds, "sample_format": fmt}


def artifact(sha, origin, project, created, *, audio=None, media="audio/wav", retention="derived", synthetic=True, job=None,
             profile=None, seed=None, params=None, record_inputs=(), host=HOST_FAKE, compute=CP_LOCAL, load=50, run=900,
             parents=(), lane="individual", chain=None, uses=(), capture=None, import_terms=None, parent_docs=(), import_lanes=None):
    chain = chain if chain is not None else (PROFILES[profile]["components"] if profile else [])
    produced = origin not in ("human_recording", "imported_mix")
    engine = None
    if produced:
        engine = {"profile_id": profile, "profile_revision": R(profile), "code_commit": "0000000",
                  "env": {"lock_sha256": H("lock:" + profile)}, "sdk_version": "0.1.0", "weights": None, "seed": seed,
                  "params": params or {"intent": {}, "actual": {}}}
    return {
        "kind": "artifact", "schemaVersion": SV, "sha256": sha, "bytes": 1024, "media_type": media, "origin": origin,
        "audio": audio, "project_id": project, "created_at": created, "retention_class": retention, "synthetic_test": synthetic,
        "provenance": {
            "producing_job_id": job, "engine": engine, "record_inputs": list(record_inputs),
            "host": host if (produced or origin == "human_recording") else None,
            "compute": compute if produced else None, "timings": timings(load, run) if produced else None,
            "parents": list(parents), "operator_lane": lane,
            "eligible_lanes": [x for x in lanes_of(chain, parent_docs) if import_lanes is None or x in import_lanes],
            "license_chain": lic(chain), "allowed_uses": list(uses), "capture": capture, "import_terms_id": import_terms,
        },
    }


def job(jid, project, kind, task, profile, created, history, *, lane="individual", placement=("local", "fake/local"),
        inputs=(), record_inputs=(), outputs=(), seed=None, params=None, request=None, parent=None, steps=(),
        cost=("0.00", "local_zero"), egress=(), quote=None, approval=None):
    return {"kind": "job", "schemaVersion": SV, "id": jid, "project_id": project, "job_kind": kind, "task": task,
            "profile_id": profile, "profile_revision": R(profile), "lane": lane, "session_id": "ses_1",
            "compute_profile_id": "cp_tier4", "placement": {"kind": placement[0], "host_class": placement[1]},
            "request_id": request, "parent_job_id": parent, "inputs": [{"role": r, "sha256": s} for r, s in inputs],
            "record_inputs": list(record_inputs), "params": params or {"intent": {}, "actual": {}}, "seed": seed,
            "state": history[-1][0], "history": [{"state": s, "at": t} for s, t in history], "steps": list(steps),
            "outputs": [{"role": r, "sha256": s} for r, s in outputs], "error": None,
            "cost": {"usd": cost[0], "basis": cost[1]}, "egress": [{"sha256": s, "destination": d} for s, d in egress],
            "quote_id": quote, "approval_id": approval, "retry": None, "created_at": history[0][1]}


def free_history(start, ready, analyzing=None):
    """queued -> preparing -> loading -> generating [-> analyzing] -> ready, at second offsets from start."""
    h, m, s = (int(x) for x in start[11:19].split(":"))
    base = h * 3600 + m * 60 + s

    def t(off):
        x = base + off
        return f"{start[:11]}{x // 3600:02d}:{(x % 3600) // 60:02d}:{x % 60:02d}Z"
    out = [("queued", t(0)), ("preparing", t(1)), ("loading", t(2)), ("generating", t(3))]
    if analyzing is not None:
        out.append(("analyzing", t(analyzing)))
    out.append(("ready", t(ready)))
    return out


def melody(mid, rev, project, created, *, notes, tempo, tempo_rev, phrases, seed_kind, capture=None, transcription=None,
           assembled_from=None, spec_kind="melody"):
    doc = {"kind": "melody-spec", "schemaVersion": SV, "melody_id": mid, "rev": rev, "base_rev": None if rev == 1 else rev - 1,
           "project_id": project, "created_at": created, "spec_kind": spec_kind, "ppq": 960,
           "tempo_map": {"rev": tempo_rev, "tempo": tempo, "meter": [{"tick": 0, "numerator": 4, "denominator": 4}]},
           "key": {"tonic": "C", "mode": "major"}, "notes": notes, "phrases": phrases,
           "source": {"seed_kind": seed_kind, "capture_sha256": capture, "transcription": transcription, "assembled_from": assembled_from},
           "quantize": None, "content_sha256": ""}
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


def note(i, start, dur, pitch, origin, conf=None):
    return {"id": f"n{i}", "start_tick": start, "duration_ticks": dur, "pitch": pitch, "velocity": 90, "confidence": conf, "origin": origin}


def tracked(value, profiles):
    return {"requested": value, "support": [{"profile_id": p, "status": "supported"} for p in profiles], "observed": []}


def song(sid, project, created, melody_ref, profiles, sections, routes, lyrics_text):
    doc = {"kind": "song-spec", "schemaVersion": SV, "song_id": sid, "rev": 1, "base_rev": None, "project_id": project,
           "created_at": created, "melody": melody_ref,
           "approved_lyrics": {"text": lyrics_text, "language": "en", "source": "written", "approved_at": created},
           "asr_transcripts": [],
           "controls": {"style": tracked("acoustic worship ballad, piano and warm pad", profiles),
                        "exclude_styles": tracked(["trap hi-hats"], profiles), "vocal_mode": tracked("vocal", profiles),
                        "duration_s": tracked(120, profiles)},
           "form": {"sections": sections}, "references": [], "candidate_count": 2, "larger_n_budget": None,
           "render_routes": routes, "validation": {"conflicts": [], "unsupported_by_profile": []}, "content_sha256": ""}
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


ALL_USES_GEN = ["listen", "loudness_measure", "dsp_finish", "analysis", "engine_input", "conditioning", "separation_input",
                "edit_source", "audition_arm", "export"]


def build_world() -> tuple[list[dict], dict, dict]:
    docs: list[dict] = []
    L: dict[str, str] = {}   # human labels -> sha256, for assertions and scenarios

    # ----- shared: store, hardware, compute profile, session -------------------------------------------------------
    docs.append({"kind": "store", "schemaVersion": SV, "store_id": "sto_main", "layout_version": 1,
                 "volume": {"adapter": "macos_sparsebundle", "name": "STUDIO"}, "band_size_sectors": None,
                 "created_at": "2026-10-09T08:00:00Z", "last_clean_detach": None})
    docs.append({"kind": "hardware-snapshot", "schemaVersion": SV, "id": "hw_mac", "host_id": "host_mac",
                 "taken_at": "2026-10-09T09:59:00Z", "os": {"family": "darwin", "version": "26.6.2", "arch": "arm64"},
                 "cpu": "Apple M5 Pro", "memory_bytes": 51539607552,
                 "accelerators": [{"vendor": "apple", "name": "Apple M5 Pro GPU", "vram_bytes": None, "unified_memory": True,
                                   "compute_capability": None, "driver_version": None, "cuda_runtime": None,
                                   "metal_recommended_max_working_set_bytes": None}],
                 "wsl2": None, "volumes": [{"mount": "/Volumes/STUDIO", "filesystem": "apfs", "free_bytes": 966367641600, "role": "studio_volume"}],
                 "raw_outputs": [{"command": "sysctl -n hw.memsize machdep.cpu.brand_string", "sha256": H("raw:sysctl")}]})
    placements = [{"profile_id": p, "placement": "burst" if p == "fake-burst" else "local", "worker_host_id": None,
                   "reason": "fake profile under the test overlay", "remedy": None} for p in sorted(p["id"] for p in FAKE_PROFILES)]
    placements += [{"profile_id": p, "placement": "local", "worker_host_id": None, "reason": "analysis runs on the studio host",
                    "remedy": None} for p in ("analysis-adherence-pyin", "analysis-export", "analysis-guide-neutralvoice",
                                              "analysis-measure", "analysis-transcribe-pyin-hmm")]
    placements += [{"profile_id": "yue2-3b-score", "placement": "burst", "worker_host_id": None,
                    "reason": "tier 4: CUDA-only profiles run on an approved burst", "remedy": None}]
    docs.append({"kind": "compute-profile", "schemaVersion": SV, "id": "cp_tier4", "tier": 4, "chosen_by": "recommendation",
                 "recommendation": {"tier": 4, "snapshot_ids": ["hw_mac"], "reasons": ["apple_silicon"], "warnings": []},
                 "placements": placements,
                 "burst": {"provider": "fake", "cloud": "secure", "gpu_class_fallback": ["FAKE-24GB", "FAKE-24GB-ALT"],
                           "monthly_cap_usd": "25.00", "per_run_approval": True, "approval_expiry_minutes": 15,
                           "automatic_paid_retry": False},
                 "created_at": "2026-10-09T09:59:30Z"})
    docs.append({"kind": "session", "schemaVersion": SV, "id": "ses_1", "started_at": "2026-10-09T10:00:00Z", "ended_at": None,
                 "compute_profile_id": "cp_tier4", "snapshot_ids": ["hw_mac"], "changes_since_last": [], "switches": []})

    # ----- project 1: individual lane, hum -> burst + local pair -> keeper -> export -------------------------------
    P1 = "prj_hymn"
    hum = H("hum")
    L["hum"] = hum
    a_hum = artifact(hum, "human_recording", P1, "2026-10-09T10:01:00Z", audio=wav(48000, 1, 10), retention="irreplaceable",
                     host=HOST_CPU, uses=["listen", "loudness_measure", "analysis", "engine_input", "conditioning", "separation_input", "export"],
                     capture={"captured_via": "browser_audioworklet_pcm", "processing_off_verified": True, "client_sha256": hum})
    m1_notes = [note(1, 0, 960, 60, "transcribed", "0.91"), note(2, 960, 960, 62, "transcribed", "0.64"),
                note(3, 1920, 1920, 64, "transcribed", "0.88"), note(4, 3840, 1920, 65, "transcribed", "0.79"),
                note(5, 5760, 1920, 67, "transcribed", "0.83")]
    phrases = [{"id": "ph1", "name": "opening line", "start_tick": 0, "end_tick": 3840},
               {"id": "ph2", "name": "answer line", "start_tick": 3840, "end_tick": 7680}]
    tempo1 = [{"tick": 0, "us_per_quarter": 500000}]
    tempo2 = [{"tick": 0, "us_per_quarter": 500000}, {"tick": 3840, "us_per_quarter": 600000}]
    transcription = {"method": "pyin-hmm", "profile_id": "analysis-transcribe-pyin-hmm", "job_id": "job_tr1",
                     "eligible_lanes": lanes_of(PROFILES["analysis-transcribe-pyin-hmm"]["components"]),
                     "license_chain": lic(PROFILES["analysis-transcribe-pyin-hmm"]["components"]), "note": "unverified on real hums"}
    mel1 = melody("mel_hymn", 1, P1, "2026-10-09T10:01:20Z", notes=m1_notes, tempo=tempo1, tempo_rev=1, phrases=phrases,
                  seed_kind="hum", capture=hum, transcription=transcription)
    m2_notes = copy.deepcopy(m1_notes)
    m2_notes[1].update({"pitch": 63, "origin": "corrected", "confidence": None})
    mel2 = melody("mel_hymn", 2, P1, "2026-10-09T10:05:00Z", notes=m2_notes, tempo=tempo2, tempo_rev=2, phrases=phrases,
                  seed_kind="hum", capture=hum, transcription=transcription)
    j_tr = job("job_tr1", P1, "transcribe", "transcribe", "analysis-transcribe-pyin-hmm", None,
               free_history("2026-10-09T10:01:05Z", 15), placement=("local", "cpu/m5pro"), inputs=[("hum", hum)],
               outputs=[("melody_spec", mel1["content_sha256"])], steps=[{"name": "pyin"}, {"name": "hmm-segmentation"}])
    corrections = {"kind": "correction-log", "schemaVersion": SV, "melody_id": "mel_hymn", "project_id": P1,
                   "entries": [{"seq": 1, "at": "2026-10-09T10:05:00Z", "base_rev": 1, "new_rev": 2,
                                "ops": [{"op": "transpose", "note_ids": ["n2"], "delta_semitones": 1},
                                        {"op": "set_tempo", "note_ids": [], "us_per_quarter": 600000}]}]}
    sections = [{"id": "s1", "name": "verse", "section_kind": "vocal", "phrase_ids": ["ph1"], "bars": 8, "repeats": 1},
                {"id": "s2", "name": "chorus", "section_kind": "vocal", "phrase_ids": ["ph2"], "bars": 8, "repeats": 2}]
    s1 = song("song_hymn", P1, "2026-10-09T10:08:00Z", {"melody_id": "mel_hymn", "rev": 2, "tempo_map_rev": 2},
              ["fake-route-a", "fake-burst"], sections, {"mode": "explicit", "routes": ["R2-synth", "R1"]},
              "[verse]\nQuiet water, morning light\n[chorus]\nHold me steady through the night")
    asm_notes = [dict(n, origin="assembled", confidence=None) for n in m2_notes]
    asm = melody("mel_hymn_asm", 1, P1, "2026-10-09T10:09:00Z", notes=asm_notes, tempo=tempo2, tempo_rev=1, phrases=phrases,
                 seed_kind="assembled", spec_kind="assembled",
                 assembled_from={"melody": {"melody_id": "mel_hymn", "rev": 2, "tempo_map_rev": 2}, "song": {"song_id": "song_hymn", "rev": 1}})
    asm_ref = {"kind": "melody-spec", "sha256": asm["content_sha256"]}
    guide = H("guide-hymn")
    L["guide"] = guide
    j_guide = job("job_guide", P1, "guide", "guide", "analysis-guide-neutralvoice", None, free_history("2026-10-09T10:09:30Z", 15),
                  placement=("local", "cpu/m5pro"), record_inputs=[asm_ref], outputs=[("guide", guide)], steps=[{"name": "render"}])
    a_guide = artifact(guide, "rendered_guide", P1, "2026-10-09T10:09:45Z", audio=wav(48000, 1, 120), retention="irreplaceable",
                       synthetic=False, job="job_guide", profile="analysis-guide-neutralvoice", record_inputs=[asm_ref],
                       host=HOST_CPU, uses=["listen", "analysis", "conditioning", "engine_input", "export"])

    # candidate A: fake-route-a cover of the guide (stands in for ACE R2-synth), local
    ca = H("cand-a-mix")
    L["cand_a"] = ca
    params_a = {"intent": {"audio_cover_strength": "0.9"}, "actual": {"audio_cover_strength": "0.9", "cover_noise_strength": "0.1"}}
    j_ca = job("job_ca", P1, "generate", "cover", "fake-route-a", None, free_history("2026-10-09T10:10:01Z", 39, analyzing=19),
               inputs=[("guide", guide)], outputs=[("mix", ca)], seed=11, params=params_a, request="gr_hymn",
               steps=[{"name": "diffusion", "index": 8, "total": 8}])
    a_ca = artifact(ca, "generated_mix", P1, "2026-10-09T10:10:20Z", audio=wav(44100, 2, 120), retention="irreplaceable",
                    job="job_ca", profile="fake-route-a", seed=11, params=params_a, parents=[{"edge": "derived_from", "sha256": guide}],
                    chain=["studio-own-code", "neutralvoice"], parent_docs=[a_guide], uses=ALL_USES_GEN)
    # candidate B: fake-burst score_to_song (stands in for YuE2 R1 on an approved burst)
    cb = H("cand-b-mix")
    L["cand_b"] = cb
    abc = {"kind": "abc-score", "sha256": H("abc-hymn")}
    lplan = {"kind": "lyrics-plan", "sha256": H("lyrics-plan-hymn")}
    j_cb = job("job_cb", P1, "generate", "score_to_song", "fake-burst", None,
               [("queued", "2026-10-09T10:10:01Z"), ("awaiting_approval", "2026-10-09T10:20:00Z"), ("preparing", "2026-10-09T10:22:06Z"),
                ("loading", "2026-10-09T10:22:10Z"), ("generating", "2026-10-09T10:24:00Z"), ("analyzing", "2026-10-09T10:30:00Z"),
                ("ready", "2026-10-09T10:30:40Z")],
               placement=("burst", "fake/burst"), record_inputs=[abc, lplan], outputs=[("mix", cb)], seed=7,
               params={"intent": {"cot": "melody"}, "actual": {"cot": "melody"}}, request="gr_hymn",
               steps=[{"name": "stage1"}, {"name": "stage2"}], cost=("0.21", "provider_reported"),
               egress=[(abc["sha256"], "burst"), (lplan["sha256"], "burst")], quote="q_hymn", approval="ap_hymn")
    a_cb = artifact(cb, "generated_mix", P1, "2026-10-09T10:30:00Z", audio=wav(48000, 2, 120), job="job_cb", profile="fake-burst",
                    seed=7, params={"intent": {"cot": "melody"}, "actual": {"cot": "melody"}}, record_inputs=[abc, lplan],
                    host=HOST_BURST, compute=CP_BURST, uses=ALL_USES_GEN)
    # measurements and previews
    pa, ma, pb, mb = H("preview-a"), H("measure-a"), H("preview-b"), H("measure-b")
    L.update({"preview_a": pa, "measure_a": ma, "preview_b": pb, "measure_b": mb})
    j_ma = job("job_ma", P1, "measure", "measure", "analysis-measure", None, free_history("2026-10-09T10:10:21Z", 9),
               placement=("local", "cpu/m5pro"), inputs=[("candidate", ca)], outputs=[("preview", pa), ("measures", ma)], parent="job_ca")
    j_mb = job("job_mb", P1, "measure", "measure", "analysis-measure", None, free_history("2026-10-09T10:30:01Z", 29),
               placement=("local", "cpu/m5pro"), inputs=[("candidate", cb)], outputs=[("preview", pb), ("measures", mb)], parent="job_cb")
    a_pa = artifact(pa, "preview", P1, "2026-10-09T10:10:30Z", audio=wav(48000, 2, 120, "pcm_s24"), retention="reproducible",
                    job="job_ma", profile="analysis-measure", host=HOST_CPU, parents=[{"edge": "converted_from", "sha256": ca}],
                    chain=["pyloudnorm", "studio-own-code", "neutralvoice"], parent_docs=[a_ca], uses=["listen", "audition_arm"])
    a_ma = artifact(ma, "analysis", P1, "2026-10-09T10:10:30Z", media="application/json", job="job_ma", profile="analysis-measure",
                    host=HOST_CPU, parents=[{"edge": "analyzed_by", "sha256": ca}], uses=["analysis"])
    a_pb = artifact(pb, "preview", P1, "2026-10-09T10:30:30Z", audio=wav(48000, 2, 120, "pcm_s24"), retention="reproducible",
                    job="job_mb", profile="analysis-measure", host=HOST_CPU, parents=[{"edge": "converted_from", "sha256": cb}],
                    chain=["pyloudnorm", "studio-own-code", "fake-nc-weights"], parent_docs=[a_cb], uses=["listen", "audition_arm"])
    a_mb = artifact(mb, "analysis", P1, "2026-10-09T10:30:30Z", media="application/json", job="job_mb", profile="analysis-measure",
                    host=HOST_CPU, parents=[{"edge": "analyzed_by", "sha256": cb}], uses=["analysis"])
    # internal separation (fake-separate stands in for Demucs) and adherence, on candidate A only
    va, adh = H("vocal-a"), H("adherence-a")
    L.update({"vocal_a": va, "adherence_a": adh})
    j_sep = job("job_sep", P1, "separate", "separate", "fake-separate", None, free_history("2026-10-09T10:10:21Z", 11),
                inputs=[("candidate", ca)], outputs=[("vocal", va)], parent="job_ca")
    j_adh = job("job_adh", P1, "adherence", "adherence", "analysis-adherence-pyin", None, free_history("2026-10-09T10:10:33Z", 5),
                placement=("local", "cpu/m5pro"), inputs=[("vocal", va)], record_inputs=[asm_ref], outputs=[("adherence", adh)], parent="job_ca")
    a_vocal = artifact(va, "analysis", P1, "2026-10-09T10:10:32Z", audio=wav(44100, 1, 120), job="job_sep", profile="fake-separate",
                    parents=[{"edge": "analyzed_by", "sha256": ca}], uses=["analysis"])
    a_adh = artifact(adh, "analysis", P1, "2026-10-09T10:10:38Z", media="application/json", job="job_adh",
                     profile="analysis-adherence-pyin", host=HOST_CPU, record_inputs=[asm_ref],
                     parents=[{"edge": "analyzed_by", "sha256": va}], uses=["analysis"])

    def measures(lufs, tp, analysis_sha):
        return {"duration_ms": 120000, "integrated_lufs": lufs, "true_peak_dbtp": tp, "loudness_standard": "BS.1770-4 (pyloudnorm)",
                "true_peak_meter": "studio-truepeak-4x", "label": "MEASURED-LOCAL", "analysis_sha256": analysis_sha}

    hard = [{"check": c, "result": "pass"} for c in ("decodes", "non_silent", "duration_fit", "no_clipping", "no_true_peak_over")]
    cand_a = {"kind": "candidate", "schemaVersion": SV, "id": "cand_a", "project_id": P1, "source": {"generation_request_id": "gr_hymn"},
              "ordinal": 1, "route": "R2-synth", "profile_id": "fake-route-a", "profile_revision": R("fake-route-a"), "seed": 11,
              "placement": {"kind": "local", "host_class": "fake/local"}, "job_id": "job_ca", "artifact_sha256": ca, "preview_sha256": pa,
              "measures": measures("-14.20", "-1.10", ma),
              "adherence": {"state": "measured", "median_cents_error": "18.5", "octave_error_rate": "0.02", "onset_f1": "0.81",
                            "contour_correlation": "0.93", "label": "MEASURED-LOCAL", "analysis_sha256": adh},
              "hard_constraints": hard + [{"check": "melody_adherence", "result": "pass"}, {"check": "lyric_per", "result": "unmeasured"}],
              "badges": [SYN, "lyric errors unmeasured", "unbenchmarked route"], "diagnostics": [], "synthetic_test": True,
              "withheld_during_blind": ["route", "profile_id", "profile_revision", "seed", "placement", "job_id", "artifact_sha256",
                                        "preview_sha256", "measures", "adherence", "hard_constraints", "badges", "diagnostics", "source"],
              "created_at": "2026-10-09T10:10:40Z"}
    cand_b = copy.deepcopy(cand_a)
    cand_b.update({"id": "cand_b", "ordinal": 2, "route": "R1", "profile_id": "fake-burst", "profile_revision": R("fake-burst"),
                   "seed": 7, "placement": {"kind": "burst", "host_class": "fake/burst"}, "job_id": "job_cb", "artifact_sha256": cb,
                   "preview_sha256": pb, "measures": measures("-15.40", "-1.60", mb),
                   "adherence": {"state": "unmeasured", "reason": "not_yet_validated"},
                   "hard_constraints": hard + [{"check": "melody_adherence", "result": "unmeasured"}, {"check": "lyric_per", "result": "unmeasured"}],
                   "badges": [SYN, "adherence unmeasured", "lyric errors unmeasured", "unbenchmarked route"],
                   "created_at": "2026-10-09T10:30:40Z"})
    gr = {"kind": "generation-request", "schemaVersion": SV, "id": "gr_hymn", "project_id": P1, "song": {"song_id": "song_hymn", "rev": 1},
          "mode": "explicit", "session_id": "ses_1", "compute_profile_id": "cp_tier4",
          "plan": [{"ordinal": 1, "route": "R2-synth", "profile_id": "fake-route-a", "seed": 11, "placement": "local",
                    "reason": "Mac route: cover of the NeutralVoice guide"},
                   {"ordinal": 2, "route": "R1", "profile_id": "fake-burst", "seed": 7, "placement": "burst",
                    "reason": "score route on an approved burst (individual lane)"}],
          "declined": [], "job_ids": ["job_ca", "job_cb"], "quote_ids": ["q_hymn"], "candidate_ids": ["cand_a", "cand_b"],
          "labels": ["unbenchmarked routes", SYN], "created_at": "2026-10-09T10:10:00Z"}

    # paid run: quote -> approval -> reservation -> provision -> settle
    terms = {"project_id": P1, "request_id": "gr_hymn", "lane": "individual", "created_at": "2026-10-09T10:20:00Z",
             "expires_at": "2026-10-09T10:35:00Z", "provider": "fake", "cloud": "secure", "gpu_class": "FAKE-24GB",
             "rates": [{"gpu_class": "FAKE-24GB", "usd_per_hour": "1.10", "read_at": "2026-10-09T10:20:00Z", "source": "fake",
                        "snapshot_date": None, "label": "UNVERIFIED"},
                       {"gpu_class": "FAKE-24GB-ALT", "usd_per_hour": "1.50", "read_at": "2026-10-09T10:20:00Z", "source": "fake",
                        "snapshot_date": None, "label": "UNVERIFIED"}],
             "jobs": [{"job_id": "job_cb", "profile_id": "fake-burst", "estimate_minutes": "6", "estimate_basis": "fake", "label": "UNVERIFIED"}],
             "max_minutes": {"boot": "3", "weights_download": "4", "jobs_total": "6", "teardown_margin": "2", "total": "15"},
             "fixed_lines": [], "ceiling_usd": "0.38", "month": "2026-10", "month_to_date_usd": "0.00", "cap_usd": "25.00",
             "egress": [{"sha256": abc["sha256"], "role": "abc_score"}, {"sha256": lplan["sha256"], "role": "lyrics_plan"}],
             "lane_check": {"result": "pass", "profiles": [{"profile_id": "fake-burst", "allowed_lanes": ["individual", "research"]}]},
             "synthetic_test": True}
    quote = {"kind": "quote", "schemaVersion": SV, "id": "q_hymn", "status": "approved", "refusal_reason": None,
             "quote_sha256": sha_of(terms), "terms": terms}
    approval = {"kind": "approval", "schemaVersion": SV, "id": "ap_hymn", "quote_id": "q_hymn", "quote_sha256": quote["quote_sha256"],
                "nonce_sha256": H("approval-nonce"), "act": owner("approve_quote", "2026-10-09T10:22:00Z"),
                "expires_at": "2026-10-09T10:35:00Z", "single_use": True, "state": "used", "used_by_run_id": "br_hymn"}
    run = {"kind": "burst-run", "schemaVersion": SV, "id": "br_hymn", "quote_id": "q_hymn", "approval_id": "ap_hymn", "provider": "fake",
           "pod_tag": "studio-burst", "lease_token_sha256": H("lease-token"), "hard_max_minutes": 15,
           "image_digest": "sha256:" + H("fake-image"), "reserved_at": "2026-10-09T10:22:01Z", "provisioned_at": "2026-10-09T10:22:05Z",
           "terminated_at": "2026-10-09T10:31:00Z", "termination_confirmed": True,
           "settlement": {"basis": "provider_reported", "usd": "0.21", "settled_at": "2026-10-09T10:31:30Z"}, "state": "settled",
           "synthetic_test": True}
    ledger_entries = [
        {"kind": "ledger-entry", "schemaVersion": SV, "seq": 1, "at": "2026-10-09T10:22:01Z", "entry_type": "reserve", "run_id": "br_hymn",
         "usd": "0.38", "month": "2026-10", "note": "reserve at ceiling before provisioning", "act": None},
        {"kind": "ledger-entry", "schemaVersion": SV, "seq": 2, "at": "2026-10-09T10:31:30Z", "entry_type": "settle", "run_id": "br_hymn",
         "usd": "0.21", "month": "2026-10", "note": "provider-reported cost", "act": None},
    ]
    events = [
        {"kind": "event", "schemaVersion": SV, "seq": 1, "at": "2026-10-09T10:22:01Z", "type": "ledger.reserve", "subject_id": "br_hymn", "data": {"run_id": "br_hymn"}},
        {"kind": "event", "schemaVersion": SV, "seq": 2, "at": "2026-10-09T10:22:05Z", "type": "burst.provisioned", "subject_id": "br_hymn", "data": {"run_id": "br_hymn"}},
        {"kind": "event", "schemaVersion": SV, "seq": 3, "at": "2026-10-09T10:30:40Z", "type": "job.state", "subject_id": "job_cb", "data": {"state": "ready"}},
        {"kind": "event", "schemaVersion": SV, "seq": 4, "at": "2026-10-09T10:31:00Z", "type": "burst.terminated", "subject_id": "br_hymn", "data": {"run_id": "br_hymn"}},
        {"kind": "event", "schemaVersion": SV, "seq": 5, "at": "2026-10-09T10:31:30Z", "type": "ledger.settle", "subject_id": "br_hymn", "data": {"run_id": "br_hymn"}},
    ]

    # blind audition -> verdict -> reveal -> keeper
    nonce = H("audition-nonce-hymn")
    mapping = [{"label": "A", "candidate_id": "cand_b"}, {"label": "B", "candidate_id": "cand_a"}]
    from studio_ref.audition import commitment
    aud = {"kind": "audition", "schemaVersion": SV, "id": "aud_hymn", "project_id": P1, "mode": "product", "request_ids": ["gr_hymn"],
           "brief_id": None, "opened_at": "2026-10-09T10:31:00Z", "all_arms_ready_at": "2026-10-09T10:30:40Z",
           "candidate_ids": ["cand_a", "cand_b"], "arms": [{"label": "A", "unplayable": False}, {"label": "B", "unplayable": False}],
           "anchors": [], "repeat_pairs": [], "commitment_sha256": commitment(mapping, nonce),
           "preview": {"sample_rate": 48000, "bit_depth": 24}, "gains": [{"label": "A", "gain_db": "0.00"}, {"label": "B", "gain_db": "-1.20"}],
           "loudness_standard": "BS.1770-4 (pyloudnorm)", "true_peak_meter": "studio-truepeak-4x", "residual_mismatch_lu": "0.04",
           "prereg_sha256": None, "state": "revealed", "residual_leak_acknowledged": ["duration", "sonic_character"]}
    verdict = {"kind": "verdict", "schemaVersion": SV, "id": "vd_hymn", "audition_id": "aud_hymn", "preferred": "B",
               "axes": [{"axis": "melody", "preferred": "B"}, {"axis": "overall", "preferred": "B"}],
               "problem_intervals": [{"label": "A", "start_ms": 30000, "end_ms": 34000, "note": "breath noise over the chorus entry"}],
               "seconds_listened": [{"label": "A", "seconds": 95}, {"label": "B", "seconds": 140}],
               "act": owner("give_verdict", "2026-10-09T10:40:00Z"), "evidence_kind": "listening-unregistered"}
    reveal = {"kind": "reveal", "schemaVersion": SV, "id": "rv_hymn", "audition_id": "aud_hymn", "verdict_id": "vd_hymn", "mapping": mapping,
              "nonce": nonce, "revealed_at": "2026-10-09T10:40:05Z"}
    keeper = {"kind": "keeper", "schemaVersion": SV, "id": "kp_hymn", "project_id": P1, "candidate_id": "cand_a", "verdict_id": "vd_hymn",
              "artifact_sha256": ca, "keeper_rev": 1, "supersedes_keeper_id": None, "kept_at": "2026-10-09T10:41:00Z"}

    # export: native 44.1 kHz copy plus a 48 kHz / 24-bit deliverable (dithered, seeded from the export id)
    da = H("deliverable-a")
    L["deliverable_a"] = da
    j_exp = job("job_exp", P1, "export", "export", "analysis-export", None, free_history("2026-10-09T10:42:00Z", 30),
                placement=("local", "cpu/m5pro"), inputs=[("keeper_mix", ca)], outputs=[("deliverable_48k_24", da)])
    a_da = artifact(da, "conversion", P1, "2026-10-09T10:42:30Z", audio=wav(48000, 2, 120, "pcm_s24"), retention="reproducible",
                    job="job_exp", profile="analysis-export", host=HOST_CPU, parents=[{"edge": "converted_from", "sha256": ca}],
                    chain=["studio-own-code", "neutralvoice"], parent_docs=[a_ca], uses=["listen", "loudness_measure", "export"])
    closure = sorted([ca, guide])
    export = {"kind": "export-manifest", "schemaVersion": SV, "id": "ex_hymn", "project_id": P1, "keeper_id": "kp_hymn",
              "operator_lane": "individual", "eligible_lanes": ["individual", "llc", "research"],
              "files": [{"path": "mix-native.wav", "role": "mix_native", "sha256": ca, "bytes": 1024, "media_type": "audio/wav", "audio": wav(44100, 2, 120)},
                        {"path": "mix-48k-24.wav", "role": "deliverable_48k_24", "sha256": da, "bytes": 1024, "media_type": "audio/wav",
                         "audio": wav(48000, 2, 120, "pcm_s24")},
                        {"path": "melody-spec.json", "role": "melody_spec", "sha256": H("file:melody-spec"), "bytes": 2048,
                         "media_type": "application/json", "audio": None},
                        {"path": "song-spec.json", "role": "song_spec", "sha256": H("file:song-spec"), "bytes": 2048,
                         "media_type": "application/json", "audio": None}],
              "human_contributions": [{"contribution": "melody", "detail": "Hummed the melody and corrected the transcription", "refs": [hum]},
                                      {"contribution": "lyrics", "detail": "Wrote the approved lyrics", "refs": []},
                                      {"contribution": "choices", "detail": "Kept this candidate in a blind audition", "refs": []}],
              "model_chain": [{"profile_id": "fake-route-a", "profile_revision": R("fake-route-a")}],
              "license_chain": lic(["neutralvoice", "studio-own-code"]),
              "ai_disclosure": {"required": True, "reasons": ["generated_audio_in_closure"]}, "converted_vocal": False,
              "imported_sources": [],
              "loudness": {"standard": "BS.1770-4", "meter": "pyloudnorm 0.1.1", "true_peak_meter": "studio-truepeak-4x",
                           "integrated_lufs": "-14.20", "true_peak_dbtp": "-1.10", "label": "MEASURED-LOCAL"},
              "dither": {"kind": "tpdf", "seed_source": "export_id"}, "closure": closure,
              "closure_sha256": sha256_hex("\n".join(closure).encode("utf-8")), "release_blockers": [], "release_clear": True,
              "synthetic_test": True,
              "verified_at": "2026-10-09T10:42:40Z"}

    # an eval-mode audition over the same pair with a reference-standard anchor (open, no verdict yet)
    ref_audio = H("reference-standard-worship")
    L["reference"] = ref_audio
    a_ref = artifact(ref_audio, "imported_mix", None, "2026-10-09T09:30:00Z", audio=wav(44100, 2, 240), retention="irreplaceable",
                     synthetic=True, uses=["listen", "loudness_measure", "eval_anchor"], import_terms="it_ref")
    it_ref = {"kind": "import-terms", "schemaVersion": SV, "id": "it_ref", "artifact_sha256": ref_audio, "source_service": "owned_purchase",
              "plan": None, "account_holder": None, "terms_url": None, "terms_date": None, "rights_assignment": None,
              "license_grant": None, "contains_studio_exports": [], "contains_third_party_or_suno": True, "detected_marks": [],
              "base_allowed_uses": ["listen", "loudness_measure", "eval_anchor"], "eligible_lanes": ["individual", "llc", "research"],
              "provenance_marks_preserved": True, "act": owner("attest_import", "2026-10-09T09:30:00Z"),
              "imported_at": "2026-10-09T09:30:00Z"}
    reference = {"kind": "reference", "schemaVersion": SV, "id": "ref_worship", "project_id": None, "artifact_sha256": ref_audio,
                 "role": "reference_standard", "feel": "worship_acoustic_ballad", "crop": None, "source": "owned_purchase",
                 "permission": {"granted_uses": ["listen", "loudness_measure", "eval_anchor"], "listening_only": True,
                                "act": owner("record_reference_permission", "2026-10-09T09:31:00Z"),
                                "note": "Fixture stand-in for one of Jon's four reference standards (O-05)."},
                 "created_at": "2026-10-09T09:31:00Z"}

    # a license acceptance for YuE2: two documents, because the individual-creator permission lives only in the GitHub MODEL_LICENSE
    perm_doc = H("doc:yue2-github-model-license")
    la_yue2 = {"kind": "license-acceptance", "schemaVersion": SV, "id": "la_yue2", "component_id": "yue2-3b", "profile_id": "yue2-3b-score",
               "documents": [{"role": "weights_license", "url": "https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE",
                              "commit_or_revision": None, "sha256": H("doc:yue2-hf-license")},
                             {"role": "permission", "url": "https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE",
                              "commit_or_revision": None, "sha256": perm_doc}],
               "weights_source": {"source": "hf", "repo": "m-a-p/YuE2-3B", "revision": None, "allow_patterns": [],
                                  "license_acceptance_required": True},
               "allowed_lanes": COMPONENTS["yue2-3b"]["allowed_lanes"], "obligations": COMPONENTS["yue2-3b"]["obligations"],
               "release_permission": {"lanes": ["individual"], "document_sha256": perm_doc,
                                      "note": "Fixture stand-in: individual creators may release and monetize outputs."},
               "act": owner("accept_model_license", "2026-10-09T09:20:00Z"), "voided": None}

    # Suno import: listen, loudness_measure and dsp_finish only (ADR-0036)
    suno = H("suno-import")
    L["suno"] = suno
    a_suno = artifact(suno, "imported_mix", P1, "2026-10-09T10:55:00Z", audio=wav(44100, 2, 180), retention="irreplaceable",
                      chain=["suno-v6"], uses=["listen", "loudness_measure", "dsp_finish"], import_terms="it_suno",
                      import_lanes=["individual", "research"])
    it_suno = {"kind": "import-terms", "schemaVersion": SV, "id": "it_suno", "artifact_sha256": suno, "source_service": "suno",
               "plan": "pro", "account_holder": {"holder": "jon", "llc_license_in_writing": False},
               "terms_url": "https://suno.com/terms-september-2026", "terms_date": "2026-09-03",
               "rights_assignment": "Pro plan: Suno assigns its rights in the output, with no warranty that copyright vests",
               "license_grant": None, "contains_studio_exports": [], "contains_third_party_or_suno": True,
               "detected_marks": [{"mark": "suno_provenance", "export_id": None}],
               "base_allowed_uses": ["listen", "loudness_measure", "dsp_finish"], "eligible_lanes": ["individual", "research"],
               "provenance_marks_preserved": True, "act": owner("attest_import", "2026-10-09T10:55:00Z"),
               "imported_at": "2026-10-09T10:55:00Z"}

    # eval: 12 smoke briefs, the smoke set and its preregistration
    cases = ["hummed_melody", "midi_chord_seed", "guide_vocal_corrected_lyrics", "instrumental_no_vocal", "three_reference_roles",
             "one_word_replace", "chorus_replace_protected_verses", "over_four_minutes", "sparse_acoustic_worship", "dense_pop",
             "rhythm_heavy", "cinematic_instrumental_bed"]
    feels = ["worship_acoustic_ballad", "broad_mix", "rnb_soul_pop_ballad", "cinematic_orchestral"]
    briefs = []
    for i, case in enumerate(cases, start=1):
        lane = "individual" if i % 2 else "llc"
        compared = [{"route": "R2-synth", "profile_id": "fake-route-a"}]
        compared += [{"route": "R1", "profile_id": "fake-burst"}] if lane == "individual" else [{"route": "R2-synth", "profile_id": "fake-route-b"}]
        briefs.append({"kind": "eval-brief", "schemaVersion": SV, "id": f"brief_smoke_{i:02d}", "set": "smoke", "case": case,
                       "feel": feels[i % 4], "lane": lane,
                       "seed": {"seed_kind": "hum", "sha256": hum} if case == "hummed_melody" else {"seed_kind": "none", "sha256": None},
                       "song": {"song_id": "song_hymn", "rev": 1} if case == "hummed_melody" else None,
                       "compared": compared, "candidates_per_arm": 1,
                       "reference_ids": ["ref_worship"] if case == "hummed_melody" else [],
                       "notes": "Fixture brief; each brief runs in its own lane."})
    eval_set = {"kind": "eval-set", "schemaVersion": SV, "id": "es_smoke", "set": "smoke", "brief_ids": [b["id"] for b in briefs]}
    body = {"briefs": [{"brief_id": b["id"], "lane": b["lane"]} for b in briefs], "asset_hashes": sorted([hum, ref_audio]),
            "pins": [{"profile_id": p, "profile_revision": R(p)} for p in ("fake-burst", "fake-route-a", "fake-route-b")],
            "budgets": {"candidates_per_brief": 2, "compute_usd_cap": "5.00", "listening_minutes": 120},
            "listening_quota": {"sessions_min": 12, "repeat_pair_fraction": "0.10", "short_quota_outcome": "inconclusive"},
            "thresholds": [{"metric": "keeper_preferred_over_reference_rate", "comparator": "gte", "value": "0.25"}],
            "gate_owner": "jon", "committed_at": "2026-10-09T09:45:00Z"}
    prereg = {"kind": "prereg", "schemaVersion": SV, "id": "pr_smoke", "eval_set_id": "es_smoke", "prereg_sha256": sha_of(body), "body": body}
    eval_nonce = H("audition-nonce-eval")
    eval_mapping = [{"label": "A", "candidate_id": "cand_a"}, {"label": "B", "candidate_id": "cand_b"}]
    aud_eval = {"kind": "audition", "schemaVersion": SV, "id": "aud_eval", "project_id": None, "mode": "eval", "request_ids": [],
                "brief_id": "brief_smoke_01", "opened_at": "2026-10-09T10:50:00Z", "all_arms_ready_at": "2026-10-09T10:30:40Z",
                "candidate_ids": ["cand_a", "cand_b"], "arms": [{"label": "A", "unplayable": False}, {"label": "B", "unplayable": False}],
                "anchors": [{"label": "C", "reference_id": "ref_worship", "acknowledged_recognizable": True}], "repeat_pairs": [],
                "commitment_sha256": commitment(eval_mapping, eval_nonce), "preview": {"sample_rate": 48000, "bit_depth": 24},
                "gains": [{"label": "A", "gain_db": "-1.20"}, {"label": "B", "gain_db": "0.00"}, {"label": "C", "gain_db": "-3.10"}],
                "loudness_standard": "BS.1770-4 (pyloudnorm)", "true_peak_meter": "studio-truepeak-4x", "residual_mismatch_lu": "0.06",
                "prereg_sha256": prereg["prereg_sha256"], "state": "open", "residual_leak_acknowledged": ["duration", "sonic_character"]}

    # evidence: fake-route-a install, conformance and synthetic smoke (test_only allows it); one unregistered listening record
    def ev(eid, check, gate, measured=(), synthetic=True, verdicts=(), subject=("profile", "fake-route-a"), host="fake/local", when="2026-10-09T09:00:00Z"):
        gate_checks = PROFILES[subject[1]]["gates"]["smoke"]["checks"] if check == "smoke" else []
        return {"kind": "evidence", "schemaVersion": SV, "id": eid, "check": check,
                "subject": {"subject_type": subject[0], "subject_id": subject[1]},
                "profile_revision": R(subject[1]) if subject[0] == "profile" else None, "host_class": host, "gate_id": gate,
                "result": "pass", "measured": list(measured),
                "checks": [{"check": c, "result": "pass", "verdict_id": None, "measured": []} for c in gate_checks],
                "synthetic": synthetic,
                "attachments": [{"name": f"{check}-log.json", "sha256": H("attachment:" + eid)}], "prereg_sha256": None,
                "verdict_ids": list(verdicts), "recorded_at": when}
    evidence = [ev("ev_fra_install", "install", None), ev("ev_fra_conformance", "conformance", None, when="2026-10-09T09:01:00Z"),
                ev("ev_fra_smoke", "smoke", "smoke.fake-route-a", when="2026-10-09T09:02:00Z",
                   measured=[{"metric": "total_wall_ms", "value": "1200", "unit": "ms", "label": "MEASURED-LOCAL"}]),
                ev("ev_listen_hymn", "listening-unregistered", None, synthetic=True, verdicts=["vd_hymn"], subject=("route", "r2-synth"),
                   host=None, when="2026-10-09T10:40:10Z")]

    # worker protocol transcripts
    def describe_profile(pid):
        p = PROFILES[pid]
        return {"profile_id": pid, "tasks": p["tasks"], "limits": p["limits"], "lanes": p["allowed_lanes"], "weights_present": True,
                "weights_manifest_sha256": None}
    worker = [
        {"kind": "worker-describe", "schemaVersion": SV, "protocol_version": 1, "sdk_version": "0.1.0", "worker_id": "wkr_fake",
         "host": {"os": "darwin", "arch": "arm64", "backend": "fake", "device": "fake-device", "memory_bytes": 51539607552,
                  "free_disk_bytes": 966367641600, "nvidia": None, "metal": None},
         "env": {"lock_sha256": H("lock:fake")}, "code_commit": "0000000",
         "profiles": [describe_profile(p) for p in ("fake-route-a", "fake-route-b", "fake-burst", "fake-nc")]},
        {"kind": "worker-health", "schemaVersion": SV, "worker_id": "wkr_fake", "state": "idle", "resident_profile": None,
         "mem": {"rss_bytes": 134217728, "device_bytes": None}},
        {"kind": "task-request", "schemaVersion": SV, "job_id": "job_ca", "profile_id": "fake-route-a", "task": "cover", "lane": "individual",
         "inputs": [{"role": "guide", "sha256": guide, "media_type": "audio/wav", "bytes": 1024}], "params": {"audio_cover_strength": "0.9"},
         "seed": 11, "deadline_s": 600},
        {"kind": "task-status", "schemaVersion": SV, "job_id": "job_ca", "state": "ready",
         "steps": [{"name": "diffusion", "index": 8, "total": 8}], "outputs": [{"role": "mix", "sha256": ca, "audio": wav(44100, 2, 120)}],
         "params_actual": {"audio_cover_strength": "0.9", "cover_noise_strength": "0.1"},
         "timings": {"queue_ms": 4, "load_ms": 50, "run_ms": 900, "cold": True, "peak_rss_bytes": 268435456, "measured_by": "worker-sdk"},
         "error": None},
        {"kind": "task-request", "schemaVersion": SV, "job_id": "job_nc_llc", "profile_id": "fake-nc", "task": "cover", "lane": "llc",
         "inputs": [], "params": {}, "seed": 3, "deadline_s": 600},
        {"kind": "refusal", "schemaVersion": SV, "job_id": "job_nc_llc", "code": "lane_forbidden",
         "detail": "fake-nc declares a non-commercial component: individual and research lanes only", "loaded_nothing": True},
    ]

    # studio (v1-studio): a timeline and a proposed edit
    timeline = {"kind": "timeline", "schemaVersion": SV, "id": "tl_hymn", "project_id": P1, "rev": 1,
                "melody": {"melody_id": "mel_hymn", "rev": 2, "tempo_map_rev": 2}, "sample_rate": 44100,
                "tracks": [{"id": "t1", "name": "Mix", "part": "mix", "main": True,
                            "clips": [{"id": "c1", "clip_kind": "audio", "artifact_sha256": ca, "source_rate": 44100, "source_start_frame": 0,
                                       "source_end_frame": 5292000, "project_start_frame": 0, "gain_db": "0.0", "fade_in_frames": 0,
                                       "fade_out_frames": 4410}]},
                           {"id": "t2", "name": "Melody", "part": "melody", "main": False,
                            "clips": [{"id": "c2", "clip_kind": "midi", "melody": {"melody_id": "mel_hymn", "rev": 2, "tempo_map_rev": 2},
                                       "start_tick": 0, "end_tick": 7680, "project_start_tick": 0}]}],
                "markers": [{"name": "verse", "tick": 0}, {"name": "chorus", "tick": 3840}]}
    edit = {"kind": "edit-operation", "schemaVersion": SV, "id": "eo_hymn", "project_id": P1, "keeper_id": "kp_hymn",
            "base_artifact_sha256": ca, "op": "replace_section", "section_name": "chorus",
            "mask": {"start_frame": 1764000, "end_frame": 2646000}, "crossfade": {"in_frames": 2205, "out_frames": 2205},
            "locked_context": [{"start_frame": 0, "end_frame": 1700000}, {"start_frame": 2700000, "end_frame": 5292000}],
            "domain": wav(44100, 2, 120), "candidate_ids": [], "state": "proposed", "accepted_candidate_id": None,
            "result_keeper_id": None, "preservation": None, "undo": None, "whole_song_rerender": False,
            "created_at": "2026-10-09T11:30:00Z"}
    sidecar = {"kind": "provenance-sidecar", "schemaVersion": SV, "blob_sha256": hum, "written_at": "2026-10-09T10:01:00Z", "artifact": a_hum}

    # ----- project 2: llc lane, MIDI -> two local fake candidates -> keeper -> export --------------------------------
    P2 = "prj_venture"
    midi = H("midi-capture")
    L["midi"] = midi
    a_midi = artifact(midi, "human_recording", P2, "2026-10-09T11:00:00Z", media="audio/midi", retention="irreplaceable", host=HOST_CPU,
                      lane="llc", uses=["listen", "analysis", "engine_input", "export"],
                      capture={"captured_via": "midi_file", "processing_off_verified": None, "client_sha256": midi})
    v_notes = [note(1, 0, 960, 67, "midi_file"), note(2, 960, 960, 69, "midi_file"), note(3, 1920, 1920, 71, "midi_file")]
    v_phr = [{"id": "ph1", "name": "hook", "start_tick": 0, "end_tick": 3840}]
    mel_v = melody("mel_venture", 1, P2, "2026-10-09T11:00:10Z", notes=v_notes, tempo=tempo1, tempo_rev=1, phrases=v_phr,
                   seed_kind="midi_file", capture=midi)
    s2 = song("song_venture", P2, "2026-10-09T11:02:00Z", {"melody_id": "mel_venture", "rev": 1, "tempo_map_rev": 1},
              ["fake-route-a", "fake-route-b"], [{"id": "s1", "name": "hook", "section_kind": "vocal", "phrase_ids": ["ph1"], "bars": 4, "repeats": 2}],
              {"mode": "auto", "routes": []}, "[hook]\nCarry the morning")
    asm_v = melody("mel_venture_asm", 1, P2, "2026-10-09T11:03:00Z", notes=[dict(n, origin="assembled") for n in v_notes], tempo=tempo1,
                   tempo_rev=1, phrases=v_phr, seed_kind="assembled", spec_kind="assembled",
                   assembled_from={"melody": {"melody_id": "mel_venture", "rev": 1, "tempo_map_rev": 1}, "song": {"song_id": "song_venture", "rev": 1}})
    asm_v_ref = {"kind": "melody-spec", "sha256": asm_v["content_sha256"]}
    vguide = H("guide-venture")
    L["vguide"] = vguide
    j_vguide = job("job_vguide", P2, "guide", "guide", "analysis-guide-neutralvoice", None, free_history("2026-10-09T11:03:10Z", 10),
                   lane="llc", placement=("local", "cpu/m5pro"), record_inputs=[asm_v_ref], outputs=[("guide", vguide)])
    a_vguide = artifact(vguide, "rendered_guide", P2, "2026-10-09T11:03:20Z", audio=wav(48000, 1, 30), retention="irreplaceable",
                        synthetic=False, job="job_vguide", profile="analysis-guide-neutralvoice", record_inputs=[asm_v_ref], host=HOST_CPU,
                        lane="llc", uses=["listen", "analysis", "conditioning", "engine_input", "export"])
    va_mix, vb_mix = H("venture-a-mix"), H("venture-b-mix")
    L.update({"venture_a": va_mix, "venture_b": vb_mix})
    p_v = {"intent": {"audio_cover_strength": "1.0"}, "actual": {"audio_cover_strength": "1.0", "cover_noise_strength": "0.0"}}
    j_va = job("job_va", P2, "generate", "cover", "fake-route-a", None, free_history("2026-10-09T11:04:01Z", 49, analyzing=29), lane="llc",
               inputs=[("guide", vguide)], outputs=[("mix", va_mix)], seed=21, params=p_v, request="gr_venture")
    j_vb = job("job_vb", P2, "generate", "cover", "fake-route-b", None, free_history("2026-10-09T11:04:01Z", 49, analyzing=29), lane="llc",
               inputs=[("guide", vguide)], outputs=[("mix", vb_mix)], seed=22, params=p_v, request="gr_venture")
    a_va = artifact(va_mix, "generated_mix", P2, "2026-10-09T11:04:30Z", audio=wav(44100, 2, 30), retention="derived", job="job_va",
                    profile="fake-route-a", seed=21, params=p_v, parents=[{"edge": "derived_from", "sha256": vguide}], lane="llc",
                    chain=["studio-own-code", "neutralvoice"], parent_docs=[a_vguide], uses=ALL_USES_GEN)
    a_vb = artifact(vb_mix, "generated_mix", P2, "2026-10-09T11:04:30Z", audio=wav(48000, 2, 30), retention="irreplaceable", job="job_vb",
                    profile="fake-route-b", seed=22, params=p_v, parents=[{"edge": "derived_from", "sha256": vguide}], lane="llc",
                    chain=["studio-own-code", "neutralvoice"], parent_docs=[a_vguide], uses=ALL_USES_GEN)
    pva, mva, pvb, mvb = H("venture-preview-a"), H("venture-measure-a"), H("venture-preview-b"), H("venture-measure-b")
    j_mva = job("job_mva", P2, "measure", "measure", "analysis-measure", None, free_history("2026-10-09T11:04:31Z", 9), lane="llc",
                placement=("local", "cpu/m5pro"), inputs=[("candidate", va_mix)], outputs=[("preview", pva), ("measures", mva)], parent="job_va")
    j_mvb = job("job_mvb", P2, "measure", "measure", "analysis-measure", None, free_history("2026-10-09T11:04:31Z", 9), lane="llc",
                placement=("local", "cpu/m5pro"), inputs=[("candidate", vb_mix)], outputs=[("preview", pvb), ("measures", mvb)], parent="job_vb")
    a_pva = artifact(pva, "preview", P2, "2026-10-09T11:04:40Z", audio=wav(48000, 2, 30, "pcm_s24"), retention="reproducible", job="job_mva",
                     profile="analysis-measure", host=HOST_CPU, parents=[{"edge": "converted_from", "sha256": va_mix}], lane="llc",
                     chain=["pyloudnorm", "studio-own-code", "neutralvoice"], parent_docs=[a_va], uses=["listen", "audition_arm"])
    a_mva = artifact(mva, "analysis", P2, "2026-10-09T11:04:40Z", media="application/json", job="job_mva", profile="analysis-measure",
                     host=HOST_CPU, parents=[{"edge": "analyzed_by", "sha256": va_mix}], lane="llc", uses=["analysis"])
    a_pvb = artifact(pvb, "preview", P2, "2026-10-09T11:04:40Z", audio=wav(48000, 2, 30, "pcm_s24"), retention="reproducible", job="job_mvb",
                     profile="analysis-measure", host=HOST_CPU, parents=[{"edge": "converted_from", "sha256": vb_mix}], lane="llc",
                     chain=["pyloudnorm", "studio-own-code", "neutralvoice"], parent_docs=[a_vb], uses=["listen", "audition_arm"])
    a_mvb = artifact(mvb, "analysis", P2, "2026-10-09T11:04:40Z", media="application/json", job="job_mvb", profile="analysis-measure",
                     host=HOST_CPU, parents=[{"edge": "analyzed_by", "sha256": vb_mix}], lane="llc", uses=["analysis"])
    unmeasured_llc = {"state": "unmeasured", "reason": "no_eligible_separator"}
    cand_va = copy.deepcopy(cand_a)
    cand_va.update({"id": "cand_va", "project_id": P2, "source": {"generation_request_id": "gr_venture"}, "ordinal": 1, "route": "R2-synth",
                    "profile_id": "fake-route-a", "profile_revision": R("fake-route-a"), "seed": 21, "job_id": "job_va",
                    "artifact_sha256": va_mix, "preview_sha256": pva, "measures": measures("-13.00", "-1.00", mva) | {"duration_ms": 30000},
                    "adherence": unmeasured_llc,
                    "hard_constraints": hard + [{"check": "melody_adherence", "result": "unmeasured"}, {"check": "lyric_per", "result": "unmeasured"}],
                    "badges": [SYN, "adherence unmeasured (no LLC separator yet)", "lyric errors unmeasured", "unbenchmarked route"],
                    "created_at": "2026-10-09T11:04:50Z"})
    cand_vb = copy.deepcopy(cand_va)
    cand_vb.update({"id": "cand_vb", "ordinal": 2, "profile_id": "fake-route-b", "profile_revision": R("fake-route-b"), "seed": 22,
                    "job_id": "job_vb", "artifact_sha256": vb_mix, "preview_sha256": pvb, "measures": measures("-13.80", "-1.30", mvb) | {"duration_ms": 30000}})
    gr_v = {"kind": "generation-request", "schemaVersion": SV, "id": "gr_venture", "project_id": P2, "song": {"song_id": "song_venture", "rev": 1},
            "mode": "auto", "session_id": "ses_1", "compute_profile_id": "cp_tier4",
            "plan": [{"ordinal": 1, "route": "R2-synth", "profile_id": "fake-route-a", "seed": 21, "placement": "local",
                      "reason": "first in the default route order for the llc lane (unbenchmarked)"},
                     {"ordinal": 2, "route": "R2-synth", "profile_id": "fake-route-b", "seed": 22, "placement": "local",
                      "reason": "second eligible profile for the same route"}],
            "declined": [{"route": "R1", "profile_id": "fake-burst", "reason_code": "lane_forbidden",
                          "reason": "fake-burst stands in for YuE2: individual and research lanes only"}],
            "job_ids": ["job_va", "job_vb"], "quote_ids": [], "candidate_ids": ["cand_va", "cand_vb"],
            "labels": ["unbenchmarked routes", SYN], "created_at": "2026-10-09T11:04:00Z"}
    v_nonce = H("audition-nonce-venture")
    v_map = [{"label": "A", "candidate_id": "cand_vb"}, {"label": "B", "candidate_id": "cand_va"}]
    aud_v = copy.deepcopy(aud)
    aud_v.update({"id": "aud_venture", "project_id": P2, "request_ids": ["gr_venture"], "opened_at": "2026-10-09T11:05:00Z",
                  "all_arms_ready_at": "2026-10-09T11:04:50Z", "candidate_ids": ["cand_va", "cand_vb"],
                  "commitment_sha256": commitment(v_map, v_nonce),
                  "gains": [{"label": "A", "gain_db": "0.00"}, {"label": "B", "gain_db": "-0.80"}], "residual_mismatch_lu": "0.03"})
    vd_v = {"kind": "verdict", "schemaVersion": SV, "id": "vd_venture", "audition_id": "aud_venture", "preferred": "A", "axes": [],
            "problem_intervals": [], "seconds_listened": [{"label": "A", "seconds": 60}, {"label": "B", "seconds": 45}],
            "act": owner("give_verdict", "2026-10-09T11:10:00Z"), "evidence_kind": "listening-unregistered"}
    rv_v = {"kind": "reveal", "schemaVersion": SV, "id": "rv_venture", "audition_id": "aud_venture", "verdict_id": "vd_venture",
            "mapping": v_map, "nonce": v_nonce, "revealed_at": "2026-10-09T11:10:05Z"}
    kp_v = {"kind": "keeper", "schemaVersion": SV, "id": "kp_venture", "project_id": P2, "candidate_id": "cand_vb", "verdict_id": "vd_venture",
            "artifact_sha256": vb_mix, "keeper_rev": 1, "supersedes_keeper_id": None, "kept_at": "2026-10-09T11:11:00Z"}
    v_closure = sorted([vb_mix, vguide])
    ex_v = copy.deepcopy(export)
    ex_v.update({"id": "ex_venture", "project_id": P2, "keeper_id": "kp_venture", "operator_lane": "llc",
                 "files": [{"path": "mix-native.wav", "role": "mix_native", "sha256": vb_mix, "bytes": 1024, "media_type": "audio/wav",
                            "audio": wav(48000, 2, 30)},
                           {"path": "melody-spec.json", "role": "melody_spec", "sha256": H("file:venture-melody-spec"), "bytes": 1024,
                            "media_type": "application/json", "audio": None}],
                 "human_contributions": [{"contribution": "melody", "detail": "Played the MIDI melody", "refs": [midi]},
                                         {"contribution": "choices", "detail": "Kept this candidate in a blind audition", "refs": []}],
                 "model_chain": [{"profile_id": "fake-route-b", "profile_revision": R("fake-route-b")}],
                 "loudness": export["loudness"] | {"integrated_lufs": "-13.80", "true_peak_dbtp": "-1.30"}, "dither": None,
                 "closure": v_closure, "closure_sha256": sha256_hex("\n".join(v_closure).encode("utf-8")),
                 "verified_at": "2026-10-09T11:12:00Z"})

    p1_artifacts = sorted([hum, guide, ca, cb, pa, ma, pb, mb, va, adh, da, suno])
    p2_artifacts = sorted([midi, vguide, va_mix, vb_mix, pva, mva, pvb, mvb])

    def project(pid, name, lane, created, arts, melodies, songs, requests, keepers, exports, heads, edits=(), timelines=()):
        return {"kind": "project", "schemaVersion": SV, "id": pid, "name": name, "project_kind": "song", "operator_lane": lane,
                "created_at": created, "lane_changes": [], "heads": heads, "artifacts": arts, "melody_ids": melodies, "song_ids": songs,
                "generation_request_ids": requests, "keeper_ids": keepers, "export_ids": exports, "reference_ids": [],
                "edit_operation_ids": list(edits), "timeline_ids": list(timelines)}

    proj1 = project(P1, "Quiet Water (fixture)", "individual", "2026-10-09T10:00:30Z", p1_artifacts, ["mel_hymn", "mel_hymn_asm"],
                    ["song_hymn"], ["gr_hymn"], ["kp_hymn"], ["ex_hymn"],
                    {"melody": {"melody_id": "mel_hymn", "rev": 2}, "song": {"song_id": "song_hymn", "rev": 1}}, ["eo_hymn"], ["tl_hymn"])
    proj2 = project(P2, "Venture hook (fixture)", "llc", "2026-10-09T10:59:00Z", p2_artifacts, ["mel_venture", "mel_venture_asm"],
                    ["song_venture"], ["gr_venture"], ["kp_venture"], ["ex_venture"],
                    {"melody": {"melody_id": "mel_venture", "rev": 1}, "song": {"song_id": "song_venture", "rev": 1}})

    docs += [proj1, proj2, a_hum, mel1, mel2, j_tr, corrections, s1, asm, j_guide, a_guide, j_ca, a_ca, j_cb, a_cb, j_ma, j_mb, a_pa, a_ma,
             a_pb, a_mb, j_sep, j_adh, a_vocal, a_adh, cand_a, cand_b, gr, quote, approval, run, *ledger_entries, *events, aud, verdict,
             reveal, keeper, j_exp, a_da, export, a_ref, it_ref, reference, la_yue2, a_suno, it_suno, *briefs, eval_set, prereg, aud_eval,
             *evidence, *worker, timeline, edit, sidecar,
             a_midi, mel_v, s2, asm_v, j_vguide, a_vguide, j_va, j_vb, a_va, a_vb, j_mva, j_mvb, a_pva, a_mva, a_pvb, a_mvb,
             cand_va, cand_vb, gr_v, aud_v, vd_v, rv_v, kp_v, ex_v]

    ALL3 = ["individual", "llc", "research"]
    IR = ["individual", "research"]
    assertions = {
        "kind": "fixture.world-assertions", "schemaVersion": SV,
        "eligible_lanes": [
            {"label": "hum", "sha256": hum, "lanes": ALL3, "why": "A human recording has no components and no parents."},
            {"label": "guide", "sha256": guide, "lanes": ALL3, "why": "NeutralVoice and the studio's own code allow every lane."},
            {"label": "cand_a", "sha256": ca, "lanes": ALL3, "why": "fake-route-a (own code + NeutralVoice) derived from the guide."},
            {"label": "cand_b", "sha256": cb, "lanes": IR, "why": "fake-burst declares fake-nc-weights (non-commercial)."},
            {"label": "preview_b", "sha256": pb, "lanes": IR, "why": "converted_from candidate B carries its lanes."},
            {"label": "measure_a", "sha256": ma, "lanes": ALL3, "why": "analyzed_by never propagates; pyloudnorm and own code allow every lane."},
            {"label": "vocal_a", "sha256": va, "lanes": IR, "why": "fake-separate declares non-commercial-by-author separator weights."},
            {"label": "adherence_a", "sha256": adh, "lanes": ALL3, "why": "analyzed_by the individual-only vocal does not propagate."},
            {"label": "deliverable_a", "sha256": da, "lanes": ALL3, "why": "converted_from candidate A."},
            {"label": "suno", "sha256": suno, "lanes": IR, "why": "The suno-v6 row allows every lane, but Jon's own Pro account holds this output and the LLC has no written license to it, so its import terms narrow it to individual and research."},
        ],
        "closures": [
            {"keeper_id": "kp_hymn", "closure_labels": ["cand_a", "guide"], "closure": sorted([ca, guide])},
            {"keeper_id": "kp_venture", "closure_labels": ["venture_b", "vguide"], "closure": sorted([vb_mix, vguide])},
        ],
    }
    return docs, assertions, L


# ======================================================================================================================
# Scenarios (reference rules) and invalid records (schema rules)
# ======================================================================================================================

def rehash(doc: dict) -> dict:
    if doc["kind"] in ("melody-spec", "song-spec"):
        doc["content_sha256"] = self_hash(doc, "content_sha256")
    elif doc["kind"] == "quote":
        doc["quote_sha256"] = sha_of(doc["terms"])
    elif doc["kind"] == "prereg":
        doc["prereg_sha256"] = sha_of(doc["body"])
    return doc


def build_scenarios(docs: list[dict], L: dict) -> list[dict]:
    from studio_ref.world import identity
    by = {identity(d): d for d in docs}

    def get(*key):
        return copy.deepcopy(by[key])

    def edit(key, fn, rehash_it=True):
        d = get(*key)
        fn(d)
        return rehash(d) if rehash_it else d

    out = []

    def sc(sid, rules, description, overlay, remove=()):
        out.append({"kind": "fixture.scenario", "schemaVersion": SV, "id": "SC-" + sid, "description": description,
                    "expect_rules": sorted(rules), "overlay": overlay, "remove": [list(r) for r in remove]})

    art = lambda label: ("artifact", L[label])  # noqa: E731
    P1, P2 = ("project", "prj_hymn"), ("project", "prj_venture")

    # --- a real YuE2 artifact, then forced into the llc project (ADR-0029 point 4; the task's lane-violation example)
    yue_out = H("yue2-mix")
    yue_job = job("job_yue2", "prj_hymn", "generate", "score_to_song", "yue2-3b-score", None, free_history("2026-10-09T12:00:00Z", 60),
                  placement=("worker_host", "cuda/rtx4090"), record_inputs=[{"kind": "abc-score", "sha256": H("abc-hymn")}],
                  outputs=[("mix", yue_out)], seed=5, params={"intent": {"cot": "melody"}, "actual": {"cot": "melody"}})
    yue_art = artifact(yue_out, "generated_mix", "prj_hymn", "2026-10-09T12:01:00Z", audio=wav(44100, 2, 120), synthetic=False,
                       job="job_yue2", profile="yue2-3b-score", seed=5, params={"intent": {"cot": "melody"}, "actual": {"cot": "melody"}},
                       record_inputs=[{"kind": "abc-score", "sha256": H("abc-hymn")}],
                       host={"host_id": "host_cuda1", "os": "linux", "arch": "x86_64", "backend": "cuda", "host_class": "cuda/rtx4090"},
                       compute={"compute_profile_id": "cp_tier4", "tier": 4, "placement": "worker_host"}, uses=ALL_USES_GEN)
    p1_with = edit(P1, lambda d: d.update(artifacts=sorted(d["artifacts"] + [yue_out])))
    p2_with = edit(P2, lambda d: d.update(artifacts=sorted(d["artifacts"] + [yue_out])))
    sc("LANE-STORE-YUE2", ["lane.store_write"],
       "A YuE2 artifact (individual and research only) made in the individual project is committed into the llc project.",
       [yue_job, yue_art, p1_with, p2_with])
    sc("LANE-STORE-YUE2-OWN-PROJECT-OK", [],
       "The same YuE2 artifact kept in the individual project it was made in is valid.", [yue_job, yue_art, p1_with])
    sc("LANE-ADMIT-YUE2", ["lane.admission"], "A YuE2 job submitted in the llc project (refused at submit, before any load).",
       [job("job_yue2_llc", "prj_venture", "generate", "score_to_song", "yue2-3b-score", None, [("queued", "2026-10-09T12:00:00Z")],
            lane="llc", placement=("worker_host", "cuda/rtx4090"), seed=5)])
    sc("LANE-ADMIT-SEPARATE-LLC", ["lane.admission"],
       "Internal separation with the Demucs stand-in in the llc project: analysis is still lane-admitted, so it cannot run.",
       [job("job_sep_llc", "prj_venture", "separate", "separate", "fake-separate", None, [("queued", "2026-10-09T12:00:00Z")], lane="llc",
            inputs=[("candidate", L["venture_b"])])])
    def add_roformer(d):
        prof = fake_profile("fake-roformer", "FakeEngine separator on Kim Mel-Band-RoFormer's register row", ["separate"],
                            ["studio-own-code", "melband-roformer-kim"], None, langs=None)
        prof["pins"]["weights"] = {"source": "hf", "repo": "KimberleyJSN/melbandroformer", "revision": None, "allow_patterns": [],
                                   "license_acceptance_required": True}
        d["profiles"].append(prof)
    sc("LANE-ADMIT-ROFORMER-LLC-BEFORE-REVIEW", ["lane.admission"],
       "An llc separation on a profile built on Kim Mel-Band-RoFormer is refused until its training-data review widens the row.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), add_roformer),
        job("job_rof_llc", "prj_venture", "separate", "separate", "fake-roformer", None, [("queued", "2026-10-09T12:00:00Z")], lane="llc",
            inputs=[("candidate", L["venture_b"])])])

    def unverified_everywhere(d):
        d["components"].append(fake_component("fake-unverified-lib", "Fake library whose license is unchecked", ["unverified"],
                                               ["individual", "llc", "research"], False, "Stands in for an UNVERIFIED register row."))
    def unpinned_demucs(d):
        d["profiles"].append(fake_profile("fake-demucs-wrapper", "FakeEngine wrapper that loads the real Demucs weights", ["separate"],
                                          ["studio-own-code", "demucs-4.1.0"], None, langs=None))
    sc("LICENSE-WEIGHTS-UNPINNED", ["license.weights_pin"],
       "A profile loads Demucs weights (ungated, research or personal use only) with no weights pin, so no license acceptance would be asked.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), unpinned_demucs)])
    # --- records carry lanes: a melody drafted by a lane-restricted transcriber
    bp_tr = {"method": "basic-pitch", "profile_id": "transcribe-basic-pitch", "job_id": "job_tr1",
             "eligible_lanes": lanes_of(PROFILES["transcribe-basic-pitch"]["components"]),
             "license_chain": lic(PROFILES["transcribe-basic-pitch"]["components"]), "note": "unverified on real hums"}
    m1_bp, m2_bp = copy.deepcopy(get("melody-spec", "mel_hymn", 1)), copy.deepcopy(get("melody-spec", "mel_hymn", 2))
    for m in (m1_bp, m2_bp):
        m["source"]["transcription"] = copy.deepcopy(bp_tr)
        rehash(m)
    tr_bp = copy.deepcopy(get("job", "job_tr1"))
    tr_bp.update(profile_id="transcribe-basic-pitch", profile_revision=R("transcribe-basic-pitch"),
                 outputs=[{"role": "melody_spec", "sha256": m1_bp["content_sha256"]}])
    sc("LANE-RECORD-INDIVIDUAL-OK", [], "A melody Basic Pitch drafted, corrected by hand, is valid in the individual project it was made in.",
       [m1_bp, m2_bp, tr_bp])
    sc("LANE-RECORD-READ-IN-LLC", ["lane.record_eligible"],
       "An llc job reads the corrected melody that Basic Pitch (individual and research until its provenance review) drafted: "
       "the transcriber's lanes travel with every revision built on its output.",
       [m1_bp, m2_bp, tr_bp,
        job("job_rec_llc", "prj_venture", "guide", "guide", "analysis-guide-neutralvoice", None, [("queued", "2026-10-09T12:00:00Z")],
            lane="llc", placement=("local", "cpu/m5pro"), record_inputs=[{"kind": "melody-spec", "sha256": m2_bp["content_sha256"]}])])
    # --- SongForm assembly (T02c): an assembled revision inherits its source revision's lanes and license chain
    from studio_ref.vector_cases.songform import hymn_assembled
    asm_bp = hymn_assembled(m2_bp, get("song-spec", "song_hymn", 1), {"melody_id": "mel_hymn_asm", "rev": 1, "base_rev": None,
                                                                       "tempo_map_rev": 1, "created_at": "2026-10-09T10:09:00Z"})
    asm_dropped, asm_laundered, asm_capture = copy.deepcopy(asm_bp), copy.deepcopy(asm_bp), copy.deepcopy(asm_bp)
    asm_dropped["source"]["transcription"] = None
    asm_laundered["source"]["transcription"]["license_chain"] = lic(PROFILES["analysis-transcribe-pyin-hmm"]["components"])
    asm_capture["source"]["capture_sha256"] = L["midi"]
    rehash(asm_dropped), rehash(asm_laundered), rehash(asm_capture)

    def reads(jid, project, lane, melody_doc):
        return job(jid, project, "guide", "guide", "analysis-guide-neutralvoice", None, [("queued", "2026-10-09T12:00:00Z")], lane=lane,
                   placement=("local", "cpu/m5pro"), record_inputs=[{"kind": "melody-spec", "sha256": melody_doc["content_sha256"]}])
    sc("LANE-RECORD-ASSEMBLED-INDIVIDUAL-OK", [], "The 1.1.0 assembled hymn carries its Basic Pitch source's capture and "
       "transcription, so its lanes and license chain, and an individual job reads it.",
       [m1_bp, m2_bp, tr_bp, asm_bp, reads("job_asm_read", "prj_hymn", "individual", asm_bp)])
    sc("LANE-RECORD-ASSEMBLED-READ-IN-LLC", ["lane.record_eligible"], "An llc job reads the assembled hymn: assembling an "
       "individual-only transcription never yields an llc-eligible melody.",
       [m1_bp, m2_bp, tr_bp, asm_bp, reads("job_asm_llc", "prj_venture", "llc", asm_bp)])
    sc("LANE-RECORD-ASSEMBLED-LINEAGE-DROPPED", ["lane.record_eligible"], "A 1.1.0 assembled hymn drops its source's Basic "
       "Pitch transcription, so the record would hide the transcriber's lanes and license chain.",
       [m1_bp, m2_bp, tr_bp, asm_dropped, reads("job_asm_read", "prj_hymn", "individual", asm_dropped)])
    sc("LANE-RECORD-ASSEMBLED-CHAIN-LAUNDERED", ["lane.record_eligible"], "A 1.1.0 assembled hymn keeps Basic Pitch's lanes "
       "but swaps in the all-lanes pYIN transcriber's license chain; the license chain is inherited exactly too.",
       [m1_bp, m2_bp, tr_bp, asm_laundered, reads("job_asm_read", "prj_hymn", "individual", asm_laundered)])
    sc("LANE-RECORD-ASSEMBLED-CAPTURE-SWAPPED", ["lane.record_eligible"], "A 1.1.0 assembled hymn names the venture's MIDI "
       "capture, a stored human recording, instead of its source's hum; the capture is inherited exactly too.",
       [m1_bp, m2_bp, tr_bp, asm_capture, reads("job_asm_read", "prj_hymn", "individual", asm_capture)])
    sc("LANE-RECORD-LEGACY-ASSEMBLED-READ-IN-LLC", ["lane.record_eligible"], "An llc job reads the world's 1.0.0 assembled "
       "hymn, whose lineage is by reference only: its lanes still come from the Basic Pitch source through assembled_from.",
       [m1_bp, m2_bp, tr_bp, reads("job_asm_llc", "prj_venture", "llc", get("melody-spec", "mel_hymn_asm", 1))])
    sc("REGISTRY-UNVERIFIED-IN-LLC", ["registry.lane_policy_consistent"],
       "A component whose license is still UNVERIFIED claims the individual and llc lanes; both forbid an unverified license.",
       [edit(("component-register", "components.fake-overlay"), unverified_everywhere)])
    sc("LANE-CHANGE-TO-LLC", ["lane.store_write"],
       "Moving the individual project, which holds non-commercial candidate B and an individual-only analysis, to llc is refused.",
       [edit(P1, lambda d: d.update(operator_lane="llc", lane_changes=[{"from": "individual", "to": "llc",
                                                                        "act": owner("change_lane", "2026-10-09T12:00:00Z")}]))])
    sc("LANE-ELIGIBLE-TOO-WIDE", ["lane.artifact_eligible"], "Candidate B claims llc although its chain holds fake-nc-weights.",
       [edit(art("cand_b"), lambda d: d["provenance"].update(eligible_lanes=["individual", "llc", "research"]))])
    sc("LANE-ELIGIBLE-ANALYZED-BY-PROPAGATED", ["lane.artifact_eligible"],
       "The adherence result narrowed its lanes through an analyzed_by edge, which never propagates.",
       [edit(art("adherence_a"), lambda d: d["provenance"].update(eligible_lanes=["individual", "research"]))])
    sc("LANE-EXPORT-NARROWED", ["lane.export"],
       "The export of keeper A dropped llc because a Demucs stand-in analysed it; analysis never narrows an export.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(eligible_lanes=["individual", "research"]))])

    def widen_separate(d):
        for p in d["profiles"]:
            if p["id"] == "fake-separate":
                p["allowed_lanes"] = ["individual", "llc", "research"]
    sc("LANE-PROFILE-WIDER-THAN-COMPONENTS", ["lane.profile_components"],
       "fake-separate declares llc although its separator weights forbid it.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), widen_separate)])
    sc("LANE-EVAL-LLC-BRIEF-NAMES-NC", ["lane.eval"], "An llc smoke brief compares the YuE2 stand-in.",
       [edit(("eval-brief", "brief_smoke_02"), lambda d: d.update(compared=d["compared"] + [{"route": "R1", "profile_id": "fake-burst"}]))])
    q_llc_terms = copy.deepcopy(by[("quote", "q_hymn")]["terms"])
    q_llc_terms.update(project_id="prj_venture", request_id="gr_venture", lane="llc", created_at="2026-10-09T12:00:00Z",
                       expires_at="2026-10-09T12:15:00Z", month_to_date_usd="0.21",
                       jobs=[{"job_id": "job_vburst", "profile_id": "fake-burst", "estimate_minutes": "6", "estimate_basis": "fake", "label": "UNVERIFIED"}])
    sc("LANE-QUOTE-LLC-NC", ["lane.admission", "lane.quote"],
       "A burst quote is created for an llc project's YuE2-stand-in job; it must be refused at admission and never quoted.",
       [job("job_vburst", "prj_venture", "generate", "score_to_song", "fake-burst", None,
            [("queued", "2026-10-09T11:59:00Z"), ("awaiting_approval", "2026-10-09T12:00:00Z")], lane="llc",
            placement=("burst", "fake/burst"), seed=9, quote="q_llc"),
        rehash({"kind": "quote", "schemaVersion": SV, "id": "q_llc", "status": "offered", "refusal_reason": None, "quote_sha256": "",
                "terms": q_llc_terms})])

    # --- worker protocol
    sc("WORKER-LOADED-AFTER-FORBIDDEN-LANE", ["worker.refuse_before_load"],
       "The fake-nc worker reported generating for an llc request instead of refusing before load.",
       [{"kind": "task-status", "schemaVersion": SV, "job_id": "job_nc_llc", "state": "generating", "steps": [{"name": "diffusion"}],
         "outputs": [], "params_actual": None, "timings": None, "error": None}])
    sc("WORKER-REFUSED-PERMITTED", ["worker.refuse_before_load"], "A permitted request was refused with lane_forbidden.",
       [{"kind": "refusal", "schemaVersion": SV, "job_id": "job_ca", "code": "lane_forbidden", "detail": "wrongly refused",
         "loaded_nothing": True}])

    def describe_llc(d):
        for p in d["profiles"]:
            if p["profile_id"] == "fake-nc":
                p["lanes"] = ["individual", "llc", "research"]
    sc("WORKER-DESCRIBE-LANES", ["worker.describe_matches_registry"], "A worker describes fake-nc with an llc lane it does not have.",
       [edit(("worker-describe", "wkr_fake"), describe_llc)])
    sc("WORKER-PARAM-PATH", ["worker.no_paths_or_urls"], "A task request smuggles a file path in its params.",
       [edit(("task-request", "job_ca"), lambda d: d["params"].update(reference_audio="/tmp/hum.wav"))])
    sc("WORKER-PARAM-URL", ["worker.no_paths_or_urls"], "A job's params carry a URL for the worker to fetch.",
       [edit(("job", "job_ca"), lambda d: d["params"]["intent"].update(reference_audio="https://example.invalid/hum.wav"))])

    # --- licenses and provenance
    sc("LICENSE-CHAIN-MISSING", ["license.chain_complete"],
       "Candidate A's chain drops NeutralVoice, which its profile declares and its guide parent carries (its preview then over-claims).",
       [edit(art("cand_a"), lambda d: d["provenance"].update(license_chain=lic(["studio-own-code"])))])

    def alter_terms(d):
        d["provenance"]["license_chain"][0]["code_license"] = "MIT"
    sc("LICENSE-TERMS-ALTERED", ["license.chain_complete"], "The guide's chain rewrites NeutralVoice's terms instead of copying the register.",
       [edit(art("guide"), alter_terms)])

    def add_unknown(d):
        for p in d["profiles"]:
            if p["id"] == "fake-separate":
                p["components"] = p["components"] + ["fake-missing"]
    sc("LICENSE-COMPONENT-UNKNOWN", ["license.component_known"], "A profile names a component the register does not have.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), add_unknown)])

    def alter_record(d):
        for p in d["profiles"]:
            if p["id"] == "fake-route-a":
                p["license_record"][0]["weights_license"] = "MIT"
    sc("LICENSE-PROFILE-RECORD", ["license.profile_record"], "fake-route-a's license record differs from the register.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), alter_record)])
    sc("LICENSE-MANIFEST-CHAIN", ["license.manifest_chain"], "The export manifest omits a closure component from its license chain.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(license_chain=lic(["neutralvoice"])))])
    sc("LICENSE-CLOSURE-HASH", ["license.manifest_chain"], "The export's closure_sha256 does not hash its closure.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(closure_sha256=H("wrong-closure")))])
    sc("LICENSE-AI-DISCLOSURE", ["license.ai_disclosure"], "Generated audio is in the closure but the manifest says no disclosure is needed.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(ai_disclosure={"required": False, "reasons": []}))])
    sc("PROV-PARENT-MISSING", ["provenance.parents_exist"], "Candidate B names a parent that is not in the store.",
       [edit(art("cand_b"), lambda d: d["provenance"].update(parents=[{"edge": "analyzed_by", "sha256": H("missing-parent")}]))])
    sc("PROV-CYCLE", ["provenance.acyclic"], "Candidate B and its measurement point at each other.",
       [edit(art("cand_b"), lambda d: d["provenance"].update(parents=[{"edge": "analyzed_by", "sha256": L["measure_b"]}]))])
    sc("PROV-SIDECAR", ["provenance.sidecar_matches"], "A provenance sidecar names another blob.",
       [edit(("provenance-sidecar", L["hum"]), lambda d: d.update(blob_sha256=L["cand_b"]))])
    sc("PROV-JOB-OUTPUT", ["provenance.job_output"], "The burst job no longer lists candidate B, and names an output nobody stored.",
       [edit(("job", "job_cb"), lambda d: d.update(outputs=[{"role": "mix", "sha256": H("never-stored")}]))])
    sc("PROV-SYNTHETIC", ["provenance.synthetic_propagates"], "A preview of synthetic candidate A claims to be real.",
       [edit(art("preview_a"), lambda d: d.update(synthetic_test=False))])
    sc("RETENTION-KEEPER-CLOSURE", ["retention.keeper_closure"], "The keeper's guide parent is marked reproducible.",
       [edit(art("guide"), lambda d: d.update(retention_class="reproducible"))])
    sc("PROJECT-GRAPH", ["project.graph_complete"], "The project graph forgets the separated vocal it holds.",
       [edit(P1, lambda d: d.update(artifacts=[s for s in d["artifacts"] if s != L["vocal_a"]]))])

    # --- uses, references and the Suno boundary
    sc("USE-SUNO-AS-COVER-INPUT", ["use.allowed_uses"], "A cover job takes the Suno import as conditioning input.",
       [job("job_suno_cover", "prj_hymn", "generate", "cover", "fake-route-a", None, [("queued", "2026-10-09T12:00:00Z")],
            inputs=[("conditioning", L["suno"])], seed=1)])
    sc("USE-SUNO-WIDENED", ["use.suno_boundary"], "The Suno import allows conditioning without a risk acceptance.",
       [edit(art("suno"), lambda d: d["provenance"].update(allowed_uses=d["provenance"]["allowed_uses"] + ["conditioning"]))])
    sc("USE-SUNO-WIDENED-WITH-RISK-ACCEPTANCE", [],
       "The same widening is valid once Jon signs a risk acceptance naming that use (an owner act).",
       [edit(art("suno"), lambda d: d["provenance"].update(allowed_uses=d["provenance"]["allowed_uses"] + ["conditioning"])),
        {"kind": "risk-acceptance", "schemaVersion": SV, "id": "ra_suno", "risk": "suno_further_use", "subject_sha256": L["suno"],
         "uses_added": ["conditioning"], "statement": "Fixture: accepts one named further use of this Suno import.",
         "act": owner("accept_risk", "2026-10-09T12:00:00Z")}])
    sc("USE-SUNO-AS-ARM", ["candidate.artifact_origin", "use.suno_boundary"],
       "Candidate B's audio is swapped for the Suno import, making it an audition arm.",
       [edit(("candidate", "cand_b"), lambda d: d.update(artifact_sha256=L["suno"]))])
    sc("USE-SUNO-AS-REFERENCE", ["use.suno_boundary"], "The Suno import is attached as a style reference.",
       [{"kind": "reference", "schemaVersion": SV, "id": "ref_suno", "project_id": None, "artifact_sha256": L["suno"],
         "role": "style_reference", "feel": None, "crop": None, "source": "licensed",
         "permission": {"granted_uses": ["listen", "loudness_measure", "dsp_finish"], "listening_only": False,
                        "act": owner("record_reference_permission", "2026-10-09T12:00:00Z"), "note": "wrongly attached"},
         "created_at": "2026-10-09T12:00:00Z"}])
    sc("USE-REFERENCE-AS-INPUT", ["use.allowed_uses"], "A cover job takes the listening-only reference standard as input.",
       [job("job_ref_cover", "prj_hymn", "generate", "cover", "fake-route-a", None, [("queued", "2026-10-09T12:00:00Z")],
            inputs=[("conditioning", L["reference"])], seed=1)])
    sc("USE-REFERENCE-PERMISSION", ["use.import_terms", "use.reference_permission"],
       "The listening-only reference's audio allows conditioning, beyond both its permission and its owned-purchase import terms.",
       [edit(art("reference"), lambda d: d["provenance"].update(allowed_uses=d["provenance"]["allowed_uses"] + ["conditioning"]))])

    def egress_ref(d):
        d["terms"]["egress"].append({"sha256": L["reference"], "role": "conditioning_audio"})
    q_eg = edit(("quote", "q_hymn"), egress_ref)
    sc("USE-EGRESS-REFERENCE", ["use.egress_forbidden"], "A quote would send the reference standard to the burst pod.",
       [q_eg, edit(("approval", "ap_hymn"), lambda d: d.update(quote_sha256=q_eg["quote_sha256"]))])

    # --- melody, song and time
    sc("TEMPO-REF-SONG", ["tempo.ref_resolves"], "The SongSpec points at a tempo-map revision its melody revision does not carry.",
       [edit(("song-spec", "song_hymn", 1), lambda d: d["melody"].update(tempo_map_rev=3))])
    sc("TEMPO-REF-TIMELINE", ["tempo.ref_resolves"], "The timeline points at a melody revision that does not exist.",
       [edit(("timeline", "tl_hymn"), lambda d: d["melody"].update(rev=9))])
    sc("TEMPO-REV-WITHOUT-CHANGE", ["tempo.rev_on_change"], "Revision 2 bumps the tempo-map revision without changing the tempo.",
       [edit(("melody-spec", "mel_hymn", 2), lambda d: d["tempo_map"].update(tempo=[{"tick": 0, "us_per_quarter": 500000}]))])
    sc("RECORD-HASH-STALE", ["record.content_hash"], "Revision 1's notes changed but its content hash did not.",
       [edit(("melody-spec", "mel_hymn", 1), lambda d: d["notes"][0].update(pitch=59), rehash_it=False)])
    sc("RECORD-HASH-QUOTE", ["record.content_hash"], "The quote's terms changed after it was hashed and approved.",
       [edit(("quote", "q_hymn"), lambda d: d["terms"].update(gpu_class="FAKE-24GB-ALT"), rehash_it=False)])
    sc("RECORD-HASH-PREREG", ["record.content_hash"], "A threshold was edited after the preregistration was hashed.",
       [edit(("prereg", "pr_smoke"), lambda d: d["body"]["thresholds"][0].update(value="0.10"), rehash_it=False)])
    sc("MELODY-BASE", ["melody.revision_chain"], "Revision 2 claims to build on revision 5.",
       [edit(("melody-spec", "mel_hymn", 2), lambda d: d.update(base_rev=5))])
    bad_start = edit(("melody-spec", "mel_hymn", 1), lambda d: d["tempo_map"].update(tempo=[{"tick": 960, "us_per_quarter": 500000}]))
    sc("MELODY-TEMPO-START", ["melody.wellformed"], "Revision 1's first tempo segment starts at tick 960.",
       [bad_start, edit(("job", "job_tr1"), lambda d: d.update(outputs=[{"role": "melody_spec", "sha256": bad_start["content_sha256"]}]))])
    sc("MELODY-METER-INSIDE-BAR", ["melody.wellformed"], "Revision 2 turns 3/4 at tick 1920, the middle of a 4/4 bar; a meter "
       "changes only on a bar line, so bars and beats count on across it (T02c).",
       [edit(("melody-spec", "mel_hymn", 2), lambda d: d["tempo_map"].update(meter=[{"tick": 0, "numerator": 4, "denominator": 4},
                                                                                    {"tick": 1920, "numerator": 3, "denominator": 4}]))])
    sc("SONG-PHRASE", ["song.phrase_refs"], "The chorus places a phrase the melody does not have.",
       [edit(("song-spec", "song_hymn", 1), lambda d: d["form"]["sections"][1].update(phrase_ids=["ph9"]))])

    # --- jobs, requests, auditions, keepers
    sc("JOB-SKIPS-STATES", ["job.state_machine"], "Job A jumps from queued to generating.",
       [edit(("job", "job_ca"), lambda d: d.update(history=[d["history"][0], d["history"][3], d["history"][-1]]))])
    sc("JOB-BURST-WITHOUT-APPROVAL-WAIT", ["job.state_machine"], "The burst job never waited for approval.",
       [edit(("job", "job_cb"), lambda d: d.update(history=[h for h in d["history"] if h["state"] != "awaiting_approval"]))])
    sc("CANDIDATE-IS-GUIDE", ["candidate.artifact_origin"], "Candidate B points at the guide, which is never a candidate.",
       [edit(("candidate", "cand_b"), lambda d: d.update(artifact_sha256=L["guide"]))])

    def three(d):
        d["candidate_count"] = 3
        d["larger_n_budget"] = {"usd_ceiling": "1.00", "reason": "fixture"}
    sc("REQUEST-COUNT", ["request.plan_consistent"], "The SongSpec asks for 3 candidates but the plan has 2.",
       [edit(("song-spec", "song_hymn", 1), three)])
    sc("REQUEST-LABEL", ["request.plan_consistent"], "The plan dropped 'unbenchmarked routes' with no benchmark record.",
       [edit(("generation-request", "gr_hymn"), lambda d: d.update(labels=[SYN]))])
    sc("AUDITION-OPENED-EARLY", ["audition.arms_ready"], "The audition declared its arms ready before candidate B's job was.",
       [edit(("audition", "aud_hymn"), lambda d: d.update(all_arms_ready_at="2026-10-09T10:20:00Z"))])
    sc("AUDITION-ORDER", ["audition.candidates_sorted"], "The session lists candidates in arrival order.",
       [edit(("audition", "aud_hymn"), lambda d: d.update(candidate_ids=["cand_b", "cand_a"]))])
    sc("AUDITION-COMMITMENT", ["audition.reveal_commitment"], "The reveal's nonce does not reproduce the published commitment.",
       [edit(("reveal", "rv_hymn"), lambda d: d.update(nonce=H("another-nonce")))])
    sc("AUDITION-GAINS-LABELS", ["audition.labels_consistent"], "The eval audition has no gain for its anchor.",
       [edit(("audition", "aud_eval"), lambda d: d.update(gains=d["gains"][:2]))])
    sc("KEEPER-NOT-PREFERRED", ["keeper.matches_verdict"], "The keeper names candidate B although the verdict preferred candidate A.",
       [edit(("keeper", "kp_hymn"), lambda d: d.update(candidate_id="cand_b"))])
    sc("KEEPER-AFTER-TIE", [], "After a tie Jon may keep either arm: the same keeper is valid when the verdict was a tie (screens S09).",
       [edit(("verdict", "vd_hymn"), lambda d: d.update(preferred="tie"), rehash_it=False)])
    sc("KEEPER-AFTER-NEITHER", ["keeper.matches_verdict"], "After 'neither' there is nothing to keep: the verdict re-rolls instead.",
       [edit(("verdict", "vd_hymn"), lambda d: d.update(preferred="neither"), rehash_it=False)])
    sc("EDIT-LOCKED-OVERLAP", ["edit.mask_wellformed"], "Locked context overlaps the edit's crossfade.",
       [edit(("edit-operation", "eo_hymn"), lambda d: d.update(locked_context=[{"start_frame": 0, "end_frame": 1763000}]))])

    # --- paid runs
    def ceiling_down(d):
        d["terms"]["ceiling_usd"] = "0.37"
    q_low = edit(("quote", "q_hymn"), ceiling_down)

    def reserve_low(d):
        d["usd"] = "0.37"
    sc("BUDGET-CEILING-ROUNDED-DOWN", ["budget.ceiling_arithmetic"], "The ceiling 15 min x $1.50/h = $0.375 was rounded down to $0.37.",
       [q_low, edit(("approval", "ap_hymn"), lambda d: d.update(quote_sha256=q_low["quote_sha256"])), edit(("ledger-entry", 1), reserve_low)])
    over_terms = copy.deepcopy(by[("quote", "q_hymn")]["terms"])
    over_terms.update(created_at="2026-10-09T10:45:00Z", expires_at="2026-10-09T11:00:00Z", month_to_date_usd="24.80")
    fixed = {"kind": "ledger-entry", "schemaVersion": SV, "seq": 3, "at": "2026-10-09T10:40:00Z", "entry_type": "fixed_line", "run_id": None,
             "usd": "24.59", "month": "2026-10", "note": "fixture fixed line", "act": None}
    sc("BUDGET-OVER-CAP-OFFERED", ["budget.cap_check"], "Month-to-date $24.80 plus a $0.38 ceiling exceeds $25.00, yet the quote was offered.",
       [fixed, rehash({"kind": "quote", "schemaVersion": SV, "id": "q_over", "status": "offered", "refusal_reason": None, "quote_sha256": "",
                       "terms": over_terms})])
    sc("BUDGET-OVER-CAP-REFUSED-OK", [], "The same quote, refused as over cap, is valid.",
       [fixed, rehash({"kind": "quote", "schemaVersion": SV, "id": "q_over", "status": "refused", "refusal_reason": "over_cap",
                       "quote_sha256": "", "terms": over_terms})])
    sc("BUDGET-APPROVAL-HASH", ["budget.approval_binds_quote"], "The approval is bound to a different quote hash.",
       [edit(("approval", "ap_hymn"), lambda d: d.update(quote_sha256=H("other-quote")))])
    sc("BUDGET-APPROVAL-LATE", ["budget.approval_binds_quote", "budget.reserve_before_provision"],
       "The approval came after the quote expired, and after the reservation it should precede.",
       [edit(("approval", "ap_hymn"), lambda d: d.update(act=owner("approve_quote", "2026-10-09T10:36:00Z")))])
    sc("BUDGET-PROVISION-BEFORE-RESERVE", ["budget.reserve_before_provision"], "The pod was provisioned before the reservation.",
       [edit(("burst-run", "br_hymn"), lambda d: d.update(provisioned_at="2026-10-09T10:22:00Z"))])

    def swap_event(d, new_type):
        d["type"] = new_type
    sc("BUDGET-EVENT-ORDER", ["budget.reserve_before_provision"], "The provision event was emitted before the reserve event.",
       [edit(("event", 1), lambda d: swap_event(d, "burst.provisioned")), edit(("event", 2), lambda d: swap_event(d, "ledger.reserve"))])
    sc("BUDGET-SETTLED-AT-CEILING", ["budget.settlement"], "A run settled 'at ceiling' for less than the ceiling.",
       [edit(("burst-run", "br_hymn"), lambda d: d["settlement"].update(basis="settled_at_ceiling")),
        edit(("job", "job_cb"), lambda d: d["cost"].update(basis="settled_at_ceiling"))])
    sc("EVENTS-TIME", ["events.ordered"], "A later event carries an earlier time.",
       [edit(("event", 5), lambda d: d.update(at="2026-10-09T10:00:00Z"))])

    # --- registry and evidence
    def research_scorer_individual(d):
        for c in d["components"]:
            if c["id"] == "fake-research-scorer":
                c["allowed_lanes"] = ["individual", "research"]
    sc("REGISTRY-LANE-POLICY", ["registry.lane_policy_consistent"], "A research-only component claims the individual lane.",
       [edit(("component-register", "components.fake-overlay"), research_scorer_individual)])

    def not_test_only(d):
        d["profiles"].append(dict(copy.deepcopy(d["profiles"][1]), id="fake-real", engine="studio-analysis", backend="cpu", test_only=False))
    sc("REGISTRY-OVERLAY-NOT-TEST-ONLY", ["registry.overlay_test_only"], "The test overlay smuggles in a profile that is not test_only.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), not_test_only)])

    def unknown_tier_profile(d):
        d["tiers"][3]["placements"].append({"profile_id": "ace-9b-mlx", "placement": "local", "condition": None})
    sc("REGISTRY-TIER-UNKNOWN", ["registry.tier_profiles_exist"], "Tier 4 places a profile nobody declared.",
       [edit(("compute-tiers",), unknown_tier_profile)])

    def dup(d):
        d["profiles"].append(dict(copy.deepcopy(d["profiles"][1]), id="ace-2b-sft-mlx"))
    sc("REGISTRY-DUPLICATE", ["registry.unique_ids"], "The overlay redeclares a shipped profile id.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), dup)])
    sc("REGISTRY-PROFILE-UNKNOWN", ["registry.profile_known"], "A job names a profile nobody declared.",
       [job("job_unknown", "prj_hymn", "generate", "cover", "ace-9b-mlx", None, [("queued", "2026-10-09T12:00:00Z")], seed=1)])

    def bad_result(d):
        d["profiles"][0]["results_local"][0]["evidence_id"] = "ev_missing"
    sc("REGISTRY-RESULT-UNCITED", ["registry.results_cite_evidence"], "A local result cites evidence that does not exist.",
       [edit(("engine-profile-registry", "engine-profiles.fake-overlay"), bad_result)])

    def ev(eid, check, subject, gate, synthetic, prereg=None, checks=None, verdicts=None):
        if checks is None:
            gate_checks = PROFILES[subject]["gates"]["smoke"]["checks"] if check == "smoke" else []
            checks = [{"check": c, "result": "pass", "verdict_id": "vd_hymn" if c == "owner_not_garbled" else None, "measured": []}
                      for c in gate_checks]
        if verdicts is None:
            verdicts = sorted({c["verdict_id"] for c in checks if c["verdict_id"]} | ({"vd_hymn"} if check.startswith("listening") else set()))
        return {"kind": "evidence", "schemaVersion": SV, "id": eid, "check": check, "subject": {"subject_type": "profile", "subject_id": subject},
                "profile_revision": R(subject), "host_class": "mlx/m5pro", "gate_id": gate, "result": "pass", "measured": [],
                "checks": checks, "synthetic": synthetic, "attachments": [], "prereg_sha256": prereg,
                "verdict_ids": verdicts, "recorded_at": "2026-10-09T12:00:00Z"}
    sc("EVIDENCE-SYNTHETIC-SMOKE", ["evidence.gates"], "NeutralVoice output is offered as ACE's smoke evidence; that gate forbids synthetic records.",
       [ev("ev_bad_smoke", "smoke", "ace-2b-turbo-mlx", "smoke.ace-2b-turbo-mlx", True)])
    sc("EVIDENCE-SYNTHETIC-BENCHMARK", ["evidence.gates"], "A synthetic smoke record is aimed at ACE's benchmark gate.",
       [ev("ev_bad_bench", "smoke", "ace-2b-sft-mlx", "benchmark.ace-2b-sft-mlx", True)])
    sc("EVIDENCE-UNKNOWN-PREREG", ["evidence.gates"], "A preregistered listening record cites a preregistration that was never committed.",
       [ev("ev_bad_prereg", "listening-preregistered", "ace-2b-sft-mlx", None, False, prereg=H("never-committed"))])
    sc("EVIDENCE-WRONG-KIND-PREREG", ["evidence.gates"],
       "A melody content hash is not a preregistration, even though it is a known record hash.",
       [ev("ev_wrong_kind_prereg", "listening-preregistered", "ace-2b-sft-mlx", None, False,
           prereg=get("melody-spec", "mel_hymn", 1)["content_sha256"])])
    sc("EVIDENCE-BENCHMARK-CONCLUSION-UNSUPPORTED", ["evidence.gates"],
       "A known preregistration and an existing owner verdict do not prove a concluded benchmark result.",
       [ev("ev_benchmark_unbound", "benchmark", "ace-2b-sft-mlx", "benchmark.ace-2b-sft-mlx", False,
           prereg=get("prereg", "pr_smoke")["prereg_sha256"],
           checks=[{"check": "preregistered_listening", "result": "pass", "verdict_id": "vd_hymn", "measured": []}])])
    for check, pid in (("benchmark", "ace-2b-sft-mlx"), ("hum-benchmark", "analysis-transcribe-pyin-hmm")):
        for result in ("pass", "fail"):
            record = ev("ev_unsupported_" + check + "_" + result, check, pid, "benchmark." + pid, False,
                        prereg=get("prereg", "pr_smoke")["prereg_sha256"])
            record["result"] = result
            sc("EVIDENCE-UNSUPPORTED-" + check.upper() + "-" + result.upper(), ["evidence.gates"],
               "An unsupported concluded " + check + " cannot be admitted as either a pass or failure.", [record])
        pending = ev("ev_pending_" + check, check, pid, "benchmark." + pid, False,
                     prereg=get("prereg", "pr_smoke")["prereg_sha256"])
        pending["result"] = "inconclusive"
        sc("EVIDENCE-INCONCLUSIVE-" + check.upper() + "-OK", [],
           "An inconclusive " + check + " records no conclusion and changes no status.", [pending])
    sc("EVIDENCE-MIXED-PROFILE-LISTENING-OK", [],
       "A listening record may cite the existing mixed-profile audition; ordinary listening is not a benchmark conclusion.",
       [ev("ev_mixed_listening", "listening-preregistered", "fake-route-a", None, False,
           prereg=get("prereg", "pr_smoke")["prereg_sha256"], verdicts=["vd_hymn"])])
    unlabelled = edit(("generation-request", "gr_hymn"),
                      lambda d: d.update(labels=[x for x in d["labels"] if x != "unbenchmarked routes"]))
    claims = [ev("ev_claim_" + p["profile_id"], "benchmark", p["profile_id"], None, False,
                 prereg=get("prereg", "pr_smoke")["prereg_sha256"]) for p in unlabelled["plan"]]
    sc("REQUEST-UNSUPPORTED-BENCHMARK-LABEL", ["evidence.gates", "request.plan_consistent"],
       "Unsupported benchmark records cannot remove the unbenchmarked route label, including records without a gate.",
       [unlabelled, *claims])
    ace_checks = PROFILES["ace-2b-sft-mlx"]["gates"]["smoke"]["checks"]
    sc("EVIDENCE-SMOKE-CHECK-MISSING", ["evidence.gates"],
       "A passing real smoke record for ACE lists no owner_not_garbled check, so Jon never listened (the gate declares it).",
       [ev("ev_smoke_no_ear", "smoke", "ace-2b-sft-mlx", "smoke.ace-2b-sft-mlx", False,
           checks=[{"check": c, "result": "pass", "verdict_id": None, "measured": []} for c in ace_checks if c != "owner_not_garbled"])])
    sc("EVIDENCE-SMOKE-FOREIGN-VERDICT", ["evidence.gates"],
       "ACE's owner_not_garbled check cites a verdict on FakeEngine candidates, not on this revision's smoke candidates.",
       [ev("ev_smoke_foreign", "smoke", "ace-2b-sft-mlx", "smoke.ace-2b-sft-mlx", False)])
    # --- imports (owner-attested, uses by source, lanes inherited by DAW bounces)
    bounce = H("daw-bounce")
    ex_hymn = get("export-manifest", "ex_hymn")
    a_bounce = artifact(bounce, "imported_mix", None, "2026-10-09T13:00:00Z", audio=wav(48000, 2, 30), retention="irreplaceable",
                        chain=[c["component_id"] for c in ex_hymn["license_chain"]], uses=["listen", "loudness_measure", "dsp_finish", "conditioning"],
                        import_terms="it_bounce", import_lanes=["individual", "research"])
    it_bounce = {"kind": "import-terms", "schemaVersion": SV, "id": "it_bounce", "artifact_sha256": bounce, "source_service": "daw_bounce",
                 "plan": None, "account_holder": None, "terms_url": None, "terms_date": None, "rights_assignment": None,
                 "license_grant": None, "contains_studio_exports": [{"export_id": "ex_hymn", "closure_sha256": ex_hymn["closure_sha256"]}],
                 "contains_third_party_or_suno": False, "detected_marks": [{"mark": "studio_export_tag", "export_id": "ex_hymn"}],
                 "base_allowed_uses": ["listen", "loudness_measure", "dsp_finish", "conditioning"], "eligible_lanes": ["individual", "research"],
                 "provenance_marks_preserved": True, "act": owner("attest_import", "2026-10-09T13:00:00Z"), "imported_at": "2026-10-09T13:00:00Z"}
    sc("IMPORT-BOUNCE-LANES-DECLARED", ["use.import_terms"],
       "A DAW bounce's lanes are computed from the studio exports it contains, never declared: this bounce of the hymn export "
       "(eligible in all three lanes) claims a different set. The same check refuses a bounce of an individual-only export that claims llc.",
       [a_bounce, it_bounce])
    forged = copy.deepcopy(it_bounce)
    forged["contains_studio_exports"][0]["closure_sha256"] = H("forged-closure")
    sc("IMPORT-BOUNCE-FORGED-EXPORT", ["use.import_terms"],
       "A DAW bounce names a studio export with a closure hash that export does not have, so its lanes cannot be inherited.",
       [a_bounce, forged])

    def suno_as_bounce(d):
        d.update(source_service="daw_bounce", plan=None, account_holder=None, contains_third_party_or_suno=False)
    sc("IMPORT-SUNO-AS-BOUNCE", ["license.chain_complete", "use.import_terms"],
       "A Suno download is declared as Jon's own DAW bounce; its embedded Suno mark gives it away, and its license chain still names Suno.",
       [edit(("import-terms", "it_suno"), suno_as_bounce, rehash_it=False)])

    def suno_llc(d):
        d.update(eligible_lanes=["individual", "llc", "research"])
    sc("IMPORT-SUNO-LLC-NO-LICENSE", ["lane.artifact_eligible", "use.import_terms"],
       "A Suno output from Jon's own account claims llc eligibility with no written license to the LLC.",
       [edit(("import-terms", "it_suno"), suno_llc, rehash_it=False)])
    sc("RELEASE-CLEAR-WRONG", ["release.manifest_blockers"], "The hymn export is releasable (individual lane, no blockers) but says it is not.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(release_clear=False))])
    sc("RELEASE-BLOCKER-UNCOVERED", ["release.manifest_blockers"],
       "The export lists a blocker its closure does not have, and claims an acceptance covers it that does not exist.",
       [edit(("export-manifest", "ex_hymn"), lambda d: d.update(release_blockers=[{"component_id": "neutralvoice", "class": "unverified",
                                                                                  "covered_by": "la_missing"}]))])
    sc("CANONICAL-FLOAT", ["canonical.integers_only"], "A job's intent stores a float instead of a decimal string.",
       [edit(("job", "job_ca"), lambda d: d["params"]["intent"].update(audio_cover_strength=0.9))])
    return out


def build_invalid_records(docs: list[dict], L: dict) -> list[dict]:
    from studio_ref.world import identity
    by = {identity(d): d for d in docs}
    real_profiles = copy.deepcopy(REAL_PROFILES)
    real_components = {"kind": "component-register", "schemaVersion": SV, "register_id": "components.case", "overlay": False,
                       "generated_from": REGISTER["generated_from"],
                       "components": [copy.deepcopy(next(c for c in REGISTER["components"] if c["id"] == "yue2-3b"))]}
    lanes_doc = json.loads((ROOT / "contracts/registry/lanes.v1.json").read_text(encoding="utf-8"))
    tiers_doc = json.loads((ROOT / "contracts/registry/compute-tiers.v1.json").read_text(encoding="utf-8"))
    caps_doc = json.loads((ROOT / "contracts/registry/capabilities.v1.json").read_text(encoding="utf-8"))
    product = json.loads((ROOT / "contracts/product.json").read_text(encoding="utf-8"))
    out = []

    def ir(iid, base, mutate, rule_text, error, description):
        rec = copy.deepcopy(base)
        mutate(rec)
        out.append({"kind": "fixture.invalid-record", "schemaVersion": SV, "id": "IR-" + iid, "record_kind": base["kind"],
                    "rule": rule_text, "description": description, "error_contains": error, "record": rec})

    def g(*key):
        return by[key]

    A = lambda label: g("artifact", L[label])  # noqa: E731
    ir("PROFILE-STATUS-STORED", real_profiles, lambda d: d["profiles"][0].update(status="smoke-passed"),
       "ADR-0027: status is computed, never stored", "$.profiles[0].status", "A stored status field on an engine profile.")
    ir("CLAIM-MEASURED-LOCAL", real_profiles, lambda d: d["profiles"][0]["claims_published"][0].update(label="MEASURED-LOCAL"),
       "ADR-0001: claims_published never holds MEASURED-LOCAL", "$.profiles[0].claims_published[0].label", "A vendor claim relabelled as measured.")
    ir("PROFILE-FAKE-NOT-TEST-ONLY", real_profiles, lambda d: d["profiles"][0].update(engine="fake"),
       "T-15: fakes are test_only", "$.profiles[0].engine", "A fake engine outside a test_only profile.")
    ir("MELODY-PPQ", g("melody-spec", "mel_hymn", 1), lambda d: d.update(ppq=480), "ADR-0033: 960 PPQ", "$.ppq", "A 480 PPQ MelodySpec.")
    ir("MELODY-PITCH", g("melody-spec", "mel_hymn", 1), lambda d: d["notes"][0].update(pitch=128), "MIDI pitch 0-127",
       "$.notes[0].pitch", "A pitch outside MIDI range.")
    ir("MELODY-TEMPO-NOT-INTEGER", g("melody-spec", "mel_hymn", 1), lambda d: d["tempo_map"]["tempo"][0].update(us_per_quarter="500000"),
       "ADR-0033: integer microseconds per quarter", "$.tempo_map.tempo[0].us_per_quarter", "Tempo as a string.")
    ir("MELODY-CONFIDENCE-MISSING", g("melody-spec", "mel_hymn", 1), lambda d: d["notes"][0].update(confidence=None),
       "Transcribed notes carry a confidence", "$.notes[0].confidence", "A transcribed note without confidence.")
    ir("MELODY-CONFIDENCE-FLOAT", g("melody-spec", "mel_hymn", 1), lambda d: d["notes"][0].update(confidence=0.9),
       "Integers only: confidence is a decimal string", "$.notes[0].confidence", "Confidence as a float.")
    ir("MELODY-HUM-WITHOUT-TRANSCRIPTION", g("melody-spec", "mel_hymn", 1), lambda d: d["source"].update(transcription=None),
       "A hum seed is transcribed first", "$.source.transcription", "A hum seed with no transcription record.")
    ir("ARTIFACT-NO-ELIGIBLE-LANES", A("cand_a"), lambda d: d["provenance"].pop("eligible_lanes"),
       "ADR-0009: complete provenance", "missing required property 'eligible_lanes'", "Provenance without eligible lanes.")
    ir("ARTIFACT-LANE-UNKNOWN", A("cand_a"), lambda d: d["provenance"].update(operator_lane="company"),
       "Lanes are individual, llc, research", "$.provenance.operator_lane", "An unknown lane.")
    ir("ARTIFACT-GENERATED-NO-ENGINE", A("cand_a"), lambda d: d["provenance"].update(engine=None),
       "A generated mix records its engine", "$.provenance.engine", "A generated mix without an engine block.")
    ir("ARTIFACT-CAPTURE-MISSING", A("hum"), lambda d: d["provenance"].update(capture=None),
       "A human recording records how it was captured", "$.provenance.capture", "A capture without capture facts.")
    ir("ARTIFACT-TIMINGS-VENDOR", A("cand_a"), lambda d: d["provenance"]["timings"].update(label="VENDOR"),
       "ADR-0026: timings are SDK-measured", "$.provenance.timings", "Engine-reported timings.")
    ir("ARTIFACT-PREVIEW-NO-PARENT", A("preview_a"), lambda d: d["provenance"].update(parents=[]),
       "A preview converts a candidate", "$.provenance.parents", "A preview with no parent.")
    ir("JOB-FAILED-NO-ERROR", g("job", "job_ca"), lambda d: d.update(state="failed", outputs=[]), "A failed job carries a typed error",
       "$.error", "A failed job without an error.")
    ir("JOB-STEP-INDEX-ONLY", g("job", "job_ca"), lambda d: d["steps"][0].pop("total"), "Steps carry index and total together",
       "'index' requires 'total'", "A step with an index but no total.")
    ir("JOB-STEP-PERCENT", g("job", "job_ca"), lambda d: d["steps"][0].update(percent=50), "No invented percentages",
       "$.steps[0].percent", "A step with a percentage.")
    ir("JOB-BURST-NO-APPROVAL", g("job", "job_cb"), lambda d: d.update(approval_id=None), "ADR-0030: burst work needs an approval",
       "$.approval_id", "A burst job running without an approval.")
    ir("JOB-BURST-AUTO-RETRY", g("job", "job_cb"), lambda d: d.update(retry={"of_job_id": "job_old", "automatic": True}),
       "ADR-0030: no automatic paid retry", "$.retry", "An automatic retry of a paid job.")
    ir("JOB-PARTIAL-OUTPUT", g("job", "job_ca"), lambda d: d.update(state="generating"), "No partial result is ever visible",
       "$.outputs", "A running job that already shows outputs.")
    ir("CANDIDATE-SYNTHETIC-UNBADGED", g("candidate", "cand_a"), lambda d: d.update(badges=["unbenchmarked route"]),
       "Synthetic output always reads 'Synthetic test output'", "$.badges", "A synthetic candidate without its badge.")
    ir("CANDIDATE-DIAGNOSTIC-RANKS", g("candidate", "cand_a"),
       lambda d: d.update(diagnostics=[{"scorer": "laion-clap", "metric": "clap", "value": "0.31", "label": "MEASURED-LOCAL", "use": "ranking"}]),
       "ADR-0005: diagnostics never rank", "$.diagnostics[0].use", "A diagnostic used for ranking.")
    ir("CANDIDATE-NO-ROUTE", g("candidate", "cand_a"), lambda d: d.update(route=None), "Every candidate from a request records its route",
       "$.route", "A request candidate without a route.")
    ir("CANDIDATE-BLIND-WITHHOLDS-LESS", g("candidate", "cand_a"), lambda d: d.update(withheld_during_blind=["route"]),
       "Nothing leaks before the reveal", "$.withheld_during_blind", "A candidate that withholds only its route.")
    ir("SONG-INSTRUMENTAL-WITH-LYRICS", g("song-spec", "song_hymn", 1), lambda d: d["controls"]["vocal_mode"].update(requested="instrumental"),
       "ADR-0018: conflicts resolved before submission", "$.approved_lyrics", "Instrumental mode with approved lyrics.")
    ir("SONG-LYRICS-FROM-ASR", g("song-spec", "song_hymn", 1), lambda d: d["approved_lyrics"].update(source="asr"),
       "ASR never overwrites approved lyrics", "$.approved_lyrics", "Approved lyrics sourced from ASR.")
    ir("SONG-LANGUAGE-NOT-BCP47", g("song-spec", "song_hymn", 1), lambda d: d["approved_lyrics"].update(language="English"),
       "Lyrics carry a BCP-47 language", "$.approved_lyrics", "A language name instead of a tag.")
    ir("SONG-LARGER-N-UNPRICED", g("song-spec", "song_hymn", 1), lambda d: d.update(candidate_count=4),
       "ADR-0005: a larger n is an explicit, priced choice", "$.larger_n_budget", "Four candidates with no budget.")
    # --- minor version 1.1.0 (T02c): the assembled form and SongForm chord symbols, accepted only from 1.1.0
    from studio_ref.vector_cases.songform import hymn_assembled
    asm11 = hymn_assembled(g("melody-spec", "mel_hymn", 2), g("song-spec", "song_hymn", 1), {
        "melody_id": "mel_hymn_asm", "rev": 1, "base_rev": None, "tempo_map_rev": 1, "created_at": "2026-10-09T10:09:00Z"})

    def chords(version, **mark):
        return lambda d: (d.update(schemaVersion=version),
                          d["form"]["sections"][0].update(chord_symbols=[{"offset_ticks": 0, "symbol": "C"} | mark]))
    ir("MELODY-FORM-BEFORE-1-1", asm11, lambda d: d.update(schemaVersion="1.0.0"), "Minor versions are additive: form is new in 1.1.0",
       "$.schemaVersion", "A 1.0.0 MelodySpec carrying the 1.1.0 assembled form.")
    ir("MELODY-ASSEMBLED-WITHOUT-FORM", asm11, lambda d: d.pop("form"), "A 1.1 assembled MelodySpec states its duration and sections",
       "missing required property 'form'", "A 1.1.0 assembled MelodySpec without its form.")
    ir("MELODY-FORM-ON-SOURCE", g("melody-spec", "mel_hymn", 2), lambda d: d.update(schemaVersion="1.1.0", form=copy.deepcopy(asm11["form"])),
       "Only an assembled MelodySpec carries a form", "$.spec_kind", "A source melody carrying an assembled form.")
    ir("MELODY-FORM-UNKNOWN-PROPERTY", asm11, lambda d: d["form"]["sections"][0].update(bars=8),
       "Closed objects reject unknown properties", "$.form.sections[0].bars", "A form section with a property no schema defines.")
    ir("SONG-CHORDS-BEFORE-1-1", g("song-spec", "song_hymn", 1), chords("1.0.0"), "Minor versions are additive: chord symbols are new in 1.1.0",
       "$.schemaVersion", "A 1.0.0 SongSpec carrying chord symbols.")
    ir("SONG-CHORD-UNKNOWN-PROPERTY", g("song-spec", "song_hymn", 1), chords("1.1.0", beat=1), "Closed objects reject unknown properties",
       "$.form.sections[0].chord_symbols[0].beat", "A chord symbol with a property no schema defines.")
    ir("SONG-CHORD-SYMBOL-MALFORMED", g("song-spec", "song_hymn", 1), chords("1.1.0", symbol='C"maj'),
       "Chord symbols are plain ASCII chord names", "$.form.sections[0].chord_symbols[0].symbol", "A chord symbol carrying a quote.")
    ir("REFERENCE-STANDARD-NOT-LISTENING-ONLY", g("reference", "ref_worship"), lambda d: d["permission"].update(listening_only=False),
       "O-08: reference standards are listening-only", "$.permission.listening_only", "A reference standard usable as input.")
    ir("REFERENCE-FROM-SUNO", g("reference", "ref_worship"), lambda d: d.update(source="suno"), "ADR-0021: Suno output is never a reference",
       "$.source", "A reference sourced from Suno.")
    ir("AUDITION-GAIN-POSITIVE", g("audition", "aud_hymn"), lambda d: d["gains"][1].update(gain_db="1.20"),
       "Level matching is attenuation-only", "$.gains[1].gain_db", "A positive gain.")
    ir("AUDITION-RESIDUAL", g("audition", "aud_hymn"), lambda d: d.update(residual_mismatch_lu="0.20"),
       "Residual mismatch at most 0.10 LU", "$.residual_mismatch_lu", "A 0.20 LU residual.")
    ir("AUDITION-PRODUCT-ANCHOR", g("audition", "aud_hymn"),
       lambda d: d.update(anchors=[{"label": "C", "reference_id": "ref_worship", "acknowledged_recognizable": True}]),
       "A reference standard is never a product arm", "$.anchors", "A product audition with an anchor.")
    ir("AUDITION-PREVIEW-RATE", g("audition", "aud_hymn"), lambda d: d["preview"].update(sample_rate=44100),
       "Previews share 48 kHz / 24-bit", "$.preview.sample_rate", "A 44.1 kHz preview.")
    ir("AUDITION-EVAL-NO-PREREG", g("audition", "aud_eval"), lambda d: d.update(prereg_sha256=None),
       "Eval sessions are preregistered", "$.prereg_sha256", "An eval session without a preregistration.")
    ir("AUDITION-ARM-LEAKS-ROUTE", g("audition", "aud_hymn"), lambda d: d["arms"][0].update(route="R1"),
       "Arms expose only the blind view", "$.arms[0].route", "An arm that names its route.")
    ir("VERDICT-BY-AUTOMATION", g("verdict", "vd_hymn"), lambda d: d["act"].update(scope="automation"),
       "ADR-0031: a verdict is an owner act", "$.act", "A verdict recorded with an automation token.")
    ir("EXPORT-CONVERTED-VOCAL", g("export-manifest", "ex_hymn"), lambda d: d.update(converted_vocal=True),
       "O-07: no voice conversion in v1", "$.converted_vocal", "A converted vocal in a v1 export.")
    ir("EXPORT-LOUDNESS-NO-STANDARD", g("export-manifest", "ex_hymn"), lambda d: d["loudness"].pop("standard"),
       "ADR-0019: loudness names its standard", "missing required property 'standard'", "A loudness report without its standard.")
    ir("EXPORT-DISCLOSURE-NO-REASON", g("export-manifest", "ex_hymn"), lambda d: d["ai_disclosure"].update(reasons=[]),
       "Disclosure carries its reasons", "$.ai_disclosure.reasons", "Required disclosure with no reasons.")
    ir("PRODUCT-CONTACT", product, lambda d: d.update(publicContactText="contact the founder"),
       "IDC Rule 07: only the public role address", "$.publicContactText", "Any other contact text.")
    ir("APPROVAL-AUTOMATION", g("approval", "ap_hymn"), lambda d: d["act"].update(scope="automation"),
       "ADR-0031: approvals are owner acts", "$.act", "An approval by an automation token.")
    ir("APPROVAL-REUSABLE", g("approval", "ap_hymn"), lambda d: d.update(single_use=False),
       "ADR-0030: single-use approval", "$.single_use", "A reusable approval.")
    ir("QUOTE-FAKE-NOT-SYNTHETIC", g("quote", "q_hymn"), lambda d: d["terms"].update(synthetic_test=False),
       "FakeBurstProvider output is synthetic", "$.terms.synthetic_test", "A fake-provider quote presented as real.")
    ir("QUOTE-REFUSED-NO-REASON", g("quote", "q_hymn"), lambda d: d.update(status="refused"),
       "A refusal names its reason", "$.refusal_reason", "A refused quote without a reason.")
    ir("QUOTE-LANE-CHECK-FAIL", g("quote", "q_hymn"), lambda d: d["terms"]["lane_check"].update(result="fail"),
       "ADR-0029 point 7: no quote for a forbidden lane", "$.terms.lane_check.result", "A quote that failed its lane check.")
    ir("BURST-RUN-TAG", g("burst-run", "br_hymn"), lambda d: d.update(pod_tag="untagged"),
       "The reaper finds pods by tag", "$.pod_tag", "An untagged pod.")
    ir("BURST-RUN-SETTLED-UNCONFIRMED", g("burst-run", "br_hymn"), lambda d: d.update(termination_confirmed=False),
       "Termination is confirmed before settlement", "$.termination_confirmed", "Settled without a confirmed termination.")
    ir("LEDGER-CAP-CHANGE-NO-ACT", g("ledger-entry", 1), lambda d: d.update(entry_type="cap_change", run_id=None),
       "Raising the cap is an owner act", "$.act", "A cap change without an owner act.")
    ir("COMPUTE-NO-PER-RUN-APPROVAL", g("compute-profile", "cp_tier4"), lambda d: d["burst"].update(per_run_approval=False),
       "O-09: every paid run needs Jon's yes", "$.burst.per_run_approval", "Burst without per-run approval.")
    ir("COMPUTE-AUTO-PAID-RETRY", g("compute-profile", "cp_tier4"), lambda d: d["burst"].update(automatic_paid_retry=True),
       "ADR-0030: no automatic paid retry", "$.burst.automatic_paid_retry", "Automatic paid retries enabled.")
    ir("COMPUTE-TIER-5", g("compute-profile", "cp_tier4"), lambda d: d.update(tier=5), "O-02: tiers 1-4", "$.tier", "A fifth tier.")
    ir("COMPUTE-UNAVAILABLE-NO-REMEDY", g("compute-profile", "cp_tier4"), lambda d: d["placements"][0].update(placement="unavailable"),
       "Unavailable(reason, remedy)", "$.placements[0].remedy", "An unavailable placement with no remedy.")
    ir("HARDWARE-VRAM-FLOAT", g("hardware-snapshot", "hw_mac"),
       lambda d: d["accelerators"].append({"vendor": "nvidia", "name": "RTX 4090", "vram_bytes": 25757220864.5, "unified_memory": False,
                                           "compute_capability": "8.9", "driver_version": "570.86", "cuda_runtime": "12.8",
                                           "metal_recommended_max_working_set_bytes": None}),
       "Sizes are integer bytes", "$.accelerators[1].vram_bytes", "Fractional bytes.")
    ir("EVIDENCE-BENCHMARK-SYNTHETIC", g("evidence", "ev_fra_smoke"),
       lambda d: d.update(check="benchmark", gate_id="benchmark.fake-route-a", prereg_sha256=H("prereg")),
       "Synthetic evidence never meets a benchmark gate", "$.synthetic", "A synthetic benchmark record.")
    ir("EVIDENCE-BENCHMARK-NO-PREREG", g("evidence", "ev_fra_smoke"), lambda d: d.update(check="benchmark", synthetic=False),
       "Benchmark records need a preregistration", "$.prereg_sha256", "A benchmark record without a preregistration.")
    ir("EVIDENCE-MEASURED-VENDOR", g("evidence", "ev_fra_smoke"), lambda d: d["measured"][0].update(label="VENDOR"),
       "Evidence measurements are MEASURED-LOCAL", "$.measured[0].label", "A vendor figure inside evidence.")
    def smoke_no_ear(d):
        d.update(check="smoke", gate_id="smoke.fake-route-a",
                 checks=[{"check": "owner_not_garbled", "result": "pass", "verdict_id": None, "measured": []}])
    ir("EVIDENCE-SMOKE-NO-OWNER-VERDICT", g("evidence", "ev_fra_smoke"), smoke_no_ear,
       "An owner_not_garbled check is answered only by Jon's verdict", "$.checks[0].verdict_id",
       "A smoke record that claims 'not garbled' passed without naming the owner verdict that answered it.")
    ir("EVIDENCE-LISTENING-NO-VERDICT", g("evidence", "ev_listen_hymn"), lambda d: d.update(verdict_ids=[]),
       "Listening evidence cites owner verdicts", "$.verdict_ids", "Listening evidence without a verdict.")
    ir("TASK-STATUS-PERCENT", g("task-status", "job_ca"), lambda d: d.update(percent=40), "No invented percentages", "$.percent",
       "A percentage in a worker status.")
    ir("TASK-STATUS-READY-NO-TIMINGS", g("task-status", "job_ca"), lambda d: d.update(timings=None), "SDK-measured timings on ready",
       "$.timings", "A ready status without timings.")
    ir("REFUSAL-CODE", g("refusal", "job_nc_llc"), lambda d: d.update(code="out_of_memory"), "ADR-0026 refusal codes", "$.code",
       "An undeclared refusal code.")
    ir("TASK-REQUEST-PATH", g("task-request", "job_ca"), lambda d: d["inputs"][0].update(path="/tmp/guide.wav"),
       "Assets move by sha256, never by path", "$.inputs[0].path", "An input passed by path.")
    ir("WORKER-PROTOCOL-2", g("worker-describe", "wkr_fake"), lambda d: d.update(protocol_version=2), "Worker protocol v1",
       "$.protocol_version", "An unknown protocol version.")
    ir("WORKER-HEALTH-BUSY-NO-RESIDENT", g("worker-health", "wkr_fake"), lambda d: d.update(state="busy"),
       "A busy worker names its resident profile", "$.resident_profile", "Busy with no resident profile.")
    ir("COMPONENT-NC-IN-PROCESS", real_components, lambda d: d["components"][0].update(process_boundary_required=False),
       "ADR-0011 rule 4: NC runs behind a process boundary", "$.components[0].process_boundary_required", "NC weights in-process.")
    ir("COMPONENT-NC-IN-LLC", real_components, lambda d: d["components"][0].update(allowed_lanes=["individual", "llc", "research"]),
       "ADR-0011: NC never in llc", "$.components[0].allowed_lanes", "NC weights allowed in llc.")
    ir("LANE-POLICY-ANALYZED-BY-PROPAGATES", lanes_doc,
       lambda d: d["propagation"].update(propagating_edges=["derived_from", "converted_from", "analyzed_by"]),
       "ADR-0029: analyzed_by never propagates", "$.propagation.propagating_edges", "Analysis edges carrying lanes.")
    ir("TIERS-THREE", tiers_doc, lambda d: d["tiers"].pop(), "O-02: four tiers", "$.tiers", "Only three tiers.")
    ir("CAPABILITY-SYNTHETIC", caps_doc, lambda d: d["capabilities"][0]["gate"].update(synthetic_allowed=True),
       "Playback is proven on real hosts", "$.capabilities[0].gate.synthetic_allowed", "A playback gate met by synthetic evidence.")
    ir("EDIT-ACCEPTED-UNCHECKED", g("edit-operation", "eo_hymn"),
       lambda d: d.update(state="accepted", accepted_candidate_id="cand_x", result_keeper_id="kp_x"),
       "ADR-0017: accepted edits pass the preservation check", "$.preservation", "An accepted edit without a preservation check.")
    ir("EDIT-WHOLE-SONG", g("edit-operation", "eo_hymn"), lambda d: d.update(whole_song_rerender=True),
       "A whole-song re-render is never a local edit", "$.whole_song_rerender", "A re-render labelled a local edit.")
    ir("IMPORT-SUNO-CONDITIONING", g("import-terms", "it_suno"),
       lambda d: d.update(base_allowed_uses=["listen", "loudness_measure", "dsp_finish", "conditioning"]),
       "ADR-0036: Suno base uses", "$.base_allowed_uses[3]", "A Suno import granted conditioning by its terms.")
    ir("IMPORT-NOT-ATTESTED", g("import-terms", "it_ref"), lambda d: d.pop("act"), "Every import is an owner act (attest_import)",
       "missing required property 'act'", "An import recorded without Jon's attestation (an automation token cannot import).")
    ir("IMPORT-PURCHASE-CONDITIONING", g("import-terms", "it_ref"),
       lambda d: d.update(base_allowed_uses=["listen", "loudness_measure", "eval_anchor", "conditioning"]),
       "An owned purchase is listening, measurement and evaluation anchor only", "$.base_allowed_uses[3]",
       "A purchased commercial recording granted conditioning.")
    ir("IMPORT-SUNO-FREE-PLAN", g("import-terms", "it_suno"), lambda d: d.update(plan="free"),
       "Free-plan Suno output is not commercially usable, so it is not importable", "$.plan", "A free-plan Suno import.")
    ir("IMPORT-BOUNCE-WITH-SUNO", g("import-terms", "it_ref"),
       lambda d: d.update(source_service="daw_bounce", base_allowed_uses=["listen"], contains_third_party_or_suno=True),
       "A bounce containing third-party or Suno audio is imported as suno or licensed", "$.contains_third_party_or_suno",
       "A DAW bounce that admits containing Suno audio.")
    ir("LICENSE-YUE2-HF-ONLY", g("license-acceptance", "la_yue2"), lambda d: d.update(documents=d["documents"][:1]),
       "YuE2's acceptance archives the GitHub MODEL_LICENSE permission beside the Hugging Face license", "$.documents",
       "A YuE2 acceptance that records only the Hugging Face CC BY-NC copy, which lacks the individual-creator permission.")
    ir("RISK-AUDITION-ARM", {"kind": "risk-acceptance", "schemaVersion": SV, "id": "ra_x", "risk": "suno_further_use", "subject_sha256": L["suno"],
                             "uses_added": ["conditioning"], "statement": "fixture", "act": owner("accept_risk", "2026-10-09T12:00:00Z")},
       lambda d: d.update(uses_added=["audition_arm"]), "O-08: a risk acceptance never makes a Suno import an audition arm",
       "$.uses_added[0]", "A risk acceptance that would put a Suno import in the harness.")
    ir("RISK-TRAINING", {"kind": "risk-acceptance", "schemaVersion": SV, "id": "ra_x", "risk": "suno_further_use", "subject_sha256": L["suno"],
                         "uses_added": ["conditioning"], "statement": "fixture", "act": owner("accept_risk", "2026-10-09T12:00:00Z")},
       lambda d: d.update(uses_added=["training"]), "v1 has no training", "$.uses_added[0]", "A risk acceptance for training.")
    ir("STORE-VOLUME-NAME", g("store",), lambda d: d["volume"].update(name="MYSONGS"), "ADR-0035: neutral volume name", "$.volume.name",
       "The product name on disk.")
    ir("EVAL-SET-ELEVEN", g("eval-set", "es_smoke"), lambda d: d.update(brief_ids=d["brief_ids"][:11]), "The smoke set has 12 briefs",
       "$.brief_ids", "An eleven-brief smoke set.")
    ir("EVAL-BRIEF-CASE", g("eval-brief", "brief_smoke_01"), lambda d: d.update(case="vibes"), "The 12 smoke cases (ADR-0010)", "$.case",
       "A smoke brief outside the 12 cases.")
    ir("PREREG-NO-THRESHOLD", g("prereg", "pr_smoke"), lambda d: d["body"].update(thresholds=[]), "Thresholds are fixed at preregistration",
       "$.body.thresholds", "A preregistration with no thresholds.")
    ir("KEEPER-REV2-NO-SUPERSEDES", g("keeper", "kp_hymn"), lambda d: d.update(keeper_rev=2), "A later keeper revision supersedes one",
       "$.supersedes_keeper_id", "A second keeper revision superseding nothing.")
    ir("REQUEST-ONE-CANDIDATE", g("generation-request", "gr_hymn"), lambda d: d.update(plan=d["plan"][:1]), "Two candidates per request",
       "$.plan", "A single-candidate plan.")
    ir("SIDECAR-INCOMPLETE", g("provenance-sidecar", L["hum"]), lambda d: d["artifact"].pop("provenance"),
       "Sidecars carry complete provenance", "$.artifact", "A sidecar without provenance.")
    ir("EVENT-STEP-MISSING", g("event", 3), lambda d: d.update(type="job.step"), "Step events carry the step", "$.data",
       "A step event without its step.")
    ir("CORRECTION-OP", g("correction-log", "mel_hymn"), lambda d: d["entries"][0]["ops"][0].update(op="regenerate"),
       "Corrections are piano-roll edits", "$.entries[0].ops[0].op", "A generative op logged as a correction.")
    ir("PROJECT-LANE-CHANGE-WRONG-ACT", g("project", "prj_hymn"),
       lambda d: d.update(lane_changes=[{"from": "individual", "to": "research", "act": owner("approve_quote", "2026-10-09T12:00:00Z")}]),
       "Changing a lane is its own owner act", "$.lane_changes[0].act", "A lane change recorded as a quote approval.")
    ir("TIMELINE-MIDI-WITH-AUDIO-FIELDS", g("timeline", "tl_hymn"), lambda d: d["tracks"][1]["clips"][0].update(source_rate=44100),
       "MIDI clips live in ticks", "$.tracks[1].clips[0]", "A MIDI clip with an audio source rate.")
    ir("SESSION-SWITCH-INCOMPLETE", g("session", "ses_1"),
       lambda d: d.update(switches=[{"at": "2026-10-09T12:00:00Z", "from_compute_profile_id": "cp_tier4", "to_compute_profile_id": "cp_tier1"}]),
       "A switch logs re-planned jobs and re-quoted approvals", "missing required property 'replanned_job_ids'", "An unlogged switch.")
    return out


# ======================================================================================================================
# Golden vectors (expected values derived by hand; see each case's derivation)
# ======================================================================================================================

def build_vectors() -> dict[str, dict]:
    from studio_ref.vector_discovery import discover
    vectors = {}
    for kind, module in discover(ROOT).items():
        doc = module.build(PROFILES)
        if not isinstance(doc, dict) or doc.get("kind") != kind:
            raise ValueError(f"{kind}: producer kind mismatch")
        if not isinstance(doc.get("cases"), list) or not doc["cases"]:
            raise ValueError(f"{kind}: producer must supply nonempty cases")
        vectors[kind.removeprefix("fixture.") + ".json"] = doc
    return vectors


# ======================================================================================================================

def kind_dir(doc: dict) -> str:
    return doc["kind"]


def file_name(doc: dict) -> str:
    from studio_ref.world import identity
    key = identity(doc)[1:]
    parts = [str(k)[:16] if isinstance(k, str) and len(str(k)) == 64 else str(k) for k in key]
    return ("-".join(parts) or doc["kind"]) + ".json"


def plan_files() -> dict[Path, bytes]:
    docs, assertions, labels = build_world()
    files: dict[Path, bytes] = {
        FIX / "registry" / "engine-profiles.fake-overlay.json": dump(OVERLAY_PROFILES),
        FIX / "registry" / "components.fake-overlay.json": dump(OVERLAY_COMPONENTS),
        FIX / "world" / "assertions.json": dump(assertions),
    }
    for d in docs:
        path = FIX / "world" / kind_dir(d) / file_name(d)
        if path in files:
            raise SystemExit(f"duplicate fixture path {path}")
        files[path] = dump(d)
    shipped = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "contracts/registry").glob("*.json"))]
    shipped.append(json.loads((ROOT / "contracts/product.json").read_text(encoding="utf-8")))
    world_docs = docs + [OVERLAY_PROFILES, OVERLAY_COMPONENTS] + shipped
    for s in build_scenarios(world_docs, labels):
        files[FIX / "scenarios" / (s["id"][3:].lower() + ".json")] = dump(s)
    for r in build_invalid_records(docs, labels):
        files[FIX / "invalid" / (r["id"][3:].lower() + ".json")] = dump(r)
    for name, doc in build_vectors().items():
        files[FIX / "vectors" / name] = dump(doc)
    return files


def main(argv: list[str]) -> int:
    try:
        files = plan_files()
    except (ValueError, OSError, ImportError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    existing = {p for p in FIX.rglob("*.json") if "legacy" not in p.relative_to(FIX).parts}
    if "--check" in argv:
        stale = sorted(str(p.relative_to(ROOT)) for p, data in files.items() if not p.exists() or p.read_bytes() != data)
        extra = sorted(str(p.relative_to(ROOT)) for p in existing - set(files))
        for s in stale:
            print(f"stale: {s}")
        for e in extra:
            print(f"not generated: {e}")
        return 1 if stale or extra else 0
    for p in existing - set(files):
        p.unlink()
    for p, data in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    print(f"wrote {len(files)} fixture files under {FIX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
