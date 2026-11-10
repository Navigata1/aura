"""Worker protocol v1 golden transcripts (T02w): every expected status, body and content is written out by hand.

The rules they pin (contracts/README.md, "Worker protocol"): auth is checked before routing (401, even for an
undeclared route); any method and path outside architecture §9.2's list is 404; a schema-invalid or pre-1.1 submit, or
one that repeats an input role, is 400; a refusal is 422 before any asset moves; an admitted submit is 202 with a
task-status in awaiting_inputs, or queued when every input is already present; a resubmit of the same job_id is 202 when
identical and 409 when not; a PUT is 403 unless an admitted, unfinished job lists the hash, then 413 above the declared
length, 400 for any other length or hash mismatch and 204 once stored; HEAD is 200 or 404.
"""
import json
from pathlib import Path

from studio_ref import worker_protocol
from studio_ref.fixture_support import H

KIND = "fixture.worker-transcript"
V11 = "1.1.0"
SOURCE, MELODY, OTHER, NC_SOURCE = H("transcript-source"), H("transcript-melody"), H("transcript-other"), H("transcript-nc")
LIMITS = {"channels": 2, "instrumental_only": False, "lyric_languages": ["en"], "max_duration_s": 600, "sample_rate": 44100}
OPEN = {"channels": None, "instrumental_only": False, "lyric_languages": None, "max_duration_s": None, "sample_rate": None}
ALL, NC = ["individual", "llc", "research"], ["individual", "research"]


def _profile(pid, tasks, lanes, limits=LIMITS, present=True):
    return {"profile_id": pid, "tasks": tasks, "limits": limits, "lanes": lanes, "weights_present": present,
            "weights_manifest_sha256": None}


def _worker(wid, profiles, resident=None):
    describe = {"kind": "worker-describe", "schemaVersion": "1.0.0", "protocol_version": 1, "sdk_version": "0.1.0",
                "worker_id": wid, "host": {"os": "darwin", "arch": "arm64", "backend": "fake", "device": "fake-device",
                                           "memory_bytes": 51539607552, "free_disk_bytes": 966367641600, "nvidia": None,
                                           "metal": None},
                "env": {"lock_sha256": H("transcript-lock")}, "code_commit": "0000000", "profiles": profiles}
    health = {"kind": "worker-health", "schemaVersion": "1.0.0", "worker_id": wid, "state": "idle", "resident_profile": resident,
              "mem": {"rss_bytes": 67108864, "device_bytes": None}}
    return {"describe": describe, "health": health}


def _job(jid, task, profile, lane="individual", inputs=(), version=V11, seed=1, **params):
    return {"kind": "task-request", "schemaVersion": version, "job_id": jid, "profile_id": profile, "task": task,
            "lane": lane, "inputs": [{"role": r, "sha256": s, "media_type": m, "bytes": b} for r, s, m, b in inputs],
            "params": params, "seed": seed, "deadline_s": 600}


def _status(jid, state):
    return {"kind": "task-status", "schemaVersion": V11, "job_id": jid, "state": state, "steps": [], "outputs": [],
            "params_actual": None, "timings": None, "error": None}


def _refused(jid, code):
    return {"kind": "refusal", "schemaVersion": "1.0.0", "job_id": jid, "code": code,
            "detail": worker_protocol.REFUSAL_DETAIL[code], "loaded_nothing": True}


def x(why, method, path, status, *, body=None, content=None, reply=None, reply_content=None, authorized=True):
    return {"why": why, "request": {"method": method, "path": path, "authorized": authorized, "body": body, "content": content},
            "response": {"status": status, "body": reply, "content": reply_content}}


def _cover(jid, profile="fake-route-a", lane="individual", source=SOURCE, **params):
    params = {"duration_s": 30, "channels": 2, "lyrics_language": None, **params}
    return _job(jid, "cover", profile, lane, [("source", source, "audio/wav", 1024)], **params)


def build(profiles):
    fake = _worker("wkr_fake", [_profile("fake-route-a", ["cover", "text_to_song"], ALL), _profile("fake-nc", ["cover"], NC),
                                _profile("fake-route-b", ["cover"], ALL, {**LIMITS, "channels": 1}, present=False)],
                   resident="fake-route-a")

    def sung(jid, profile="fake-route-a", task="cover", **params):
        job = _cover(jid, profile, **{"lyrics_language": "fr", **params}) if task == "cover" else \
            _job(jid, task, profile, duration_s=30, channels=2, **params)
        job["inputs"].append({"role": "lyrics", "sha256": OTHER, "media_type": "text/plain", "bytes": 64})
        return job
    twice = _cover("job_two")
    twice["inputs"].append(dict(twice["inputs"][0]))
    legacy = _cover("job_old")
    legacy["schemaVersion"] = "1.0.0"
    moved = _cover("job_ca")
    moved["seed"] = 2
    a = SOURCE
    fake_case = {"name": "fake worker: submit first, then assets", "derivation": "FakeEngine's generate tasks on the "
                 "protocol: auth, routing, admission and refusal before any byte moves, assets by hash, idempotent submit, "
                 "cancel and unload.", "worker": fake, "exchanges": [
        x("No bearer token: 401.", "GET", "/v1/describe", 401, authorized=False),
        x("Auth comes before routing, so an unauthenticated probe learns no route.", "GET", "/v1/nope", 401, authorized=False),
        x("An undeclared path is 404.", "GET", "/v1/nope", 404),
        x("A declared path with an undeclared method is 404, not 405.", "POST", "/v1/describe", 404),
        x("Describe.", "GET", "/v1/describe", 200, reply=fake["describe"]),
        x("Health.", "GET", "/v1/health", 200, reply=fake["health"]),
        x("Submit first: no admitted job lists this hash yet.", "PUT", f"/v1/assets/{a}", 403, content={"sha256": a, "bytes": 1024}),
        x("Admitted: 202 awaiting_inputs, its source not yet present.", "POST", "/v1/jobs", 202, body=_cover("job_ca"),
          reply=_status("job_ca", "awaiting_inputs")),
        x("An identical resubmit is idempotent.", "POST", "/v1/jobs", 202, body=_cover("job_ca"), reply=_status("job_ca", "awaiting_inputs")),
        x("The same job_id with another body is a conflict.", "POST", "/v1/jobs", 409, body=moved),
        x("HEAD before the PUT.", "HEAD", f"/v1/assets/{a}", 404),
        x("An asset path is a lowercase sha256, or no route.", "PUT", "/v1/assets/not-a-hash", 404, content={"sha256": a, "bytes": 1024}),
        x("Bytes whose hash is not the path's.", "PUT", f"/v1/assets/{a}", 400, content={"sha256": OTHER, "bytes": 1024}),
        x("More bytes than the request declared.", "PUT", f"/v1/assets/{a}", 413, content={"sha256": a, "bytes": 2048}),
        x("The length is checked before the hash: the worker stops reading at the declared length.", "PUT", f"/v1/assets/{a}",
          413, content={"sha256": OTHER, "bytes": 2048}),
        x("A PUT with no bytes.", "PUT", f"/v1/assets/{a}", 400),
        x("Fewer bytes than declared.", "PUT", f"/v1/assets/{a}", 400, content={"sha256": a, "bytes": 512}),
        x("The listed asset is stored.", "PUT", f"/v1/assets/{a}", 204, content={"sha256": a, "bytes": 1024}),
        x("Every input present: the job is queued.", "GET", "/v1/jobs/job_ca", 200, reply=_status("job_ca", "queued")),
        x("HEAD after the PUT.", "HEAD", f"/v1/assets/{a}", 200),
        x("GET returns the stored asset.", "GET", f"/v1/assets/{a}", 200, reply_content={"sha256": a, "bytes": 1024}),
        x("No output before ready.", "GET", "/v1/jobs/job_ca/outputs/mix", 404),
        x("A non-commercial profile in llc is refused before load.", "POST", "/v1/jobs", 422,
          body=_cover("job_nc", "fake-nc", "llc", NC_SOURCE), reply=_refused("job_nc", "lane_forbidden")),
        x("A refused request never receives a byte.", "PUT", f"/v1/assets/{NC_SOURCE}", 403, content={"sha256": NC_SOURCE, "bytes": 1024}),
        x("A refused job is not known.", "GET", "/v1/jobs/job_nc", 404),
        x("An undeclared task.", "POST", "/v1/jobs", 422, body=_job("job_t", "text_to_song", "fake-nc", duration_s=30, channels=2,
                                                                     lyrics_language=None), reply=_refused("job_t", "unsupported_task")),
        x("Above max_duration_s (600).", "POST", "/v1/jobs", 422, body=_cover("job_long", duration_s=601), reply=_refused("job_long", "over_limit")),
        x("A lyric language the profile does not declare.", "POST", "/v1/jobs", 422, body=sung("job_fr"),
          reply=_refused("job_fr", "language_unsupported")),
        x("Weights not present.", "POST", "/v1/jobs", 422, body=_cover("job_b", "fake-route-b", channels=1),
          reply=_refused("job_b", "weights_missing")),
        x("Order: the task before the lane.", "POST", "/v1/jobs", 422, body=_job("job_o1", "text_to_song", "fake-nc", "llc",
          duration_s=30, channels=2, lyrics_language=None), reply=_refused("job_o1", "unsupported_task")),
        x("Order: the lane before the limits.", "POST", "/v1/jobs", 422, body=_cover("job_o2", "fake-nc", "llc", duration_s=601),
          reply=_refused("job_o2", "lane_forbidden")),
        x("Order: duration before language.", "POST", "/v1/jobs", 422, body=sung("job_o3", duration_s=601),
          reply=_refused("job_o3", "over_limit")),
        x("Channels above the profile's 1, before missing weights.", "POST", "/v1/jobs", 422, body=_cover("job_o4", "fake-route-b"),
          reply=_refused("job_o4", "over_limit")),
        x("Order: language before weights.", "POST", "/v1/jobs", 422, body=sung("job_o5", "fake-route-b", channels=1),
          reply=_refused("job_o5", "language_unsupported")),
        x("An unknown param is schema-invalid.", "POST", "/v1/jobs", 400, body=_cover("job_u", guidance="7")),
        x("A 1.0.0 request has untyped params.", "POST", "/v1/jobs", 400, body=legacy),
        x("Input roles are unique.", "POST", "/v1/jobs", 400, body=twice),
        x("Faults belong to fake profiles only.", "POST", "/v1/jobs", 400, body=_cover("job_f", "ace-2b-turbo-mlx", faults={"silence": True})),
        x("No inputs to wait for: queued at once.", "POST", "/v1/jobs", 202, body=_job("job_t2s", "text_to_song", "fake-route-a",
          duration_s=30, channels=2, lyrics_language=None, faults={"silence": True}), reply=_status("job_t2s", "queued")),
        x("Cancel.", "POST", "/v1/jobs/job_ca/cancel", 200, reply=_status("job_ca", "cancelled")),
        x("A cancelled job lists no hash any more.", "PUT", f"/v1/assets/{a}", 403, content={"sha256": a, "bytes": 1024}),
        x("Events mirror the status.", "GET", "/v1/jobs/job_ca/events", 200, reply=_status("job_ca", "cancelled")),
        x("Cancel of an unknown job.", "POST", "/v1/jobs/job_zz/cancel", 404),
        x("Unload frees the resident model.", "POST", "/v1/unload", 200, reply={**fake["health"], "resident_profile": None}),
    ]}
    guide_worker = _worker("wkr_analysis", [_profile("analysis-guide-neutralvoice", ["guide"], ALL, OPEN)])
    melody = [("melody", MELODY, "application/json", 2048)]
    guide_case = {"name": "analysis worker: the guide task", "derivation": "A guide renders one assembled MelodySpec, sent "
                  "as canonical JSON in role melody, at a declared sample rate.", "worker": guide_worker, "exchanges": [
        x("Admitted.", "POST", "/v1/jobs", 202, body=_job("job_gd", "guide", "analysis-guide-neutralvoice", inputs=melody,
          sample_rate=48000, vowel="a"), reply=_status("job_gd", "awaiting_inputs")),
        x("The melody arrives.", "PUT", f"/v1/assets/{MELODY}", 204, content={"sha256": MELODY, "bytes": 2048}),
        x("Queued.", "GET", "/v1/jobs/job_gd", 200, reply=_status("job_gd", "queued")),
        x("A guide takes no audio.", "POST", "/v1/jobs", 400, body=_job("job_g2", "guide", "analysis-guide-neutralvoice",
          inputs=[("source", SOURCE, "audio/wav", 1024)], sample_rate=48000)),
        x("sample_rate is required.", "POST", "/v1/jobs", 400, body=_job("job_g3", "guide", "analysis-guide-neutralvoice", inputs=melody)),
    ]}
    open_worker = _worker("wkr_tailnet", [_profile("heartmula-3b-cuda", ["text_to_song"], NC, OPEN)])
    open_case = {"name": "a profile that declares no lyric languages", "derivation": "README decision 7: lyric languages "
                 "left undeclared refuse every sung request until a smoke run declares one; instrumental requests run.",
                 "worker": open_worker, "exchanges": [
        x("Sung.", "POST", "/v1/jobs", 422, body=sung("job_hm", "heartmula-3b-cuda", "text_to_song", lyrics_language="en"),
          reply=_refused("job_hm", "language_unsupported")),
        x("Instrumental, with no inputs to wait for.", "POST", "/v1/jobs", 202, body=_job("job_hi", "text_to_song",
          "heartmula-3b-cuda", duration_s=30, channels=2, lyrics_language=None), reply=_status("job_hi", "queued")),
    ]}
    return {"kind": KIND, "schemaVersion": "1.0.0", "cases": [fake_case, guide_case, open_case]}


def _validator():
    import importlib.util
    path = Path(__file__).resolve().parents[4] / "scripts/spec/jsonschema_subset.py"
    spec = importlib.util.spec_from_file_location("jsonschema_subset", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schemas = module.SchemaSet(path.parents[2] / "contracts/schemas")
    return lambda record, kind: schemas.validate(record, f"{kind}.schema.json")


def evaluate(case, world):
    worker = worker_protocol.Worker(case["worker"]["describe"], case["worker"]["health"], _validator())
    got = [worker.handle(json.loads(json.dumps(step["request"]))) for step in case["exchanges"]]
    return got, [step["response"] for step in case["exchanges"]]
