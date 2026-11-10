"""Worker protocol v1 reference (ADR-0026, architecture.md §9.2, contracts/README.md "Worker protocol").

`Worker.handle` gives the HTTP status, record body and asset content a conforming worker answers, from its describe,
its health and the jobs and assets it holds. It never loads or runs anything, so no job here passes queued: the worker
SDK and conformance (T10) cover running, outputs and timings. `profile_revision` is the registry's pin-hash.
Stdlib only.
"""
from __future__ import annotations

import re

from studio_ref.canonical import canon_bytes, sha256_hex

TYPED = re.compile(r"1\.[1-9][0-9]*\.[0-9]+")  # requests carry typed params from 1.1.0
TERMINAL = {"ready", "failed", "cancelled"}
REFUSAL_DETAIL = {  # advisory text; the contract is the status, the kind and the code
    "unsupported_task": "the profile is not described or does not declare this task",
    "lane_forbidden": "the profile's components do not allow this operator lane",
    "over_limit": "the request exceeds the profile's declared limits",
    "language_unsupported": "the profile does not declare this lyric language",
    "weights_missing": "the profile's pinned weights are not present",
}
ROUTES = [  # the complete list (architecture §9.2): anything else, any other method included, is 404
    ({"GET"}, r"/v1/describe", "describe"), ({"GET"}, r"/v1/health", "health"),
    ({"PUT", "HEAD", "GET"}, r"/v1/assets/(?P<sha>[0-9a-f]{64})", "asset"), ({"POST"}, r"/v1/jobs", "submit"),
    ({"GET"}, r"/v1/jobs/(?P<job>[^/]+)", "status"), ({"GET"}, r"/v1/jobs/(?P<job>[^/]+)/events", "status"),
    ({"GET"}, r"/v1/jobs/(?P<job>[^/]+)/outputs/(?P<role>[^/]+)", "output"),
    ({"POST"}, r"/v1/jobs/(?P<job>[^/]+)/cancel", "cancel"), ({"POST"}, r"/v1/unload", "unload"),
]


class ProtocolError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def revision_preimage(code_commit, env, sdk_version, weights_manifest_sha256) -> bytes:
    """The canonical JSON (ADR-0028) of the four pins the spec concatenates: an object, so there is no separator to
    choose, a profile without weights is null and every hash is lowercase hex text."""
    if not isinstance(code_commit, str) or not re.fullmatch(r"[0-9a-f]{7,40}", code_commit):
        raise ProtocolError("code_commit_invalid")
    lock, digest = (env.get("lock_sha256"), env.get("image_digest")) if isinstance(env, dict) else (None, None)
    if not isinstance(env, dict) or len(env) != 1 or not (isinstance(lock, str) and re.fullmatch(r"[0-9a-f]{64}", lock)
                             or isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)):
        raise ProtocolError("env_invalid")
    if not isinstance(sdk_version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", sdk_version):
        raise ProtocolError("sdk_version_invalid")
    if weights_manifest_sha256 is not None and not (isinstance(weights_manifest_sha256, str)
                                                    and re.fullmatch(r"[0-9a-f]{64}", weights_manifest_sha256)):
        raise ProtocolError("weights_manifest_invalid")
    return canon_bytes({"code_commit": code_commit, "env": env, "sdk_version": sdk_version,
                        "weights_manifest_sha256": weights_manifest_sha256})


def profile_revision(describe: dict, profile_id: str) -> str:
    """sha256 hex of the preimage for one described profile; the profile id is not hashed (status is keyed by the
    subject as well as the revision)."""
    profile = next((p for p in describe["profiles"] if p["profile_id"] == profile_id), None)
    if profile is None:
        raise ProtocolError("profile_not_described")
    return sha256_hex(revision_preimage(describe["code_commit"], describe["env"], describe["sdk_version"],
                                        profile["weights_manifest_sha256"]))


def _reply(status, body=None, content=None):
    return {"status": status, "body": body, "content": content}


class Worker:
    """One worker's protocol state. validate(record, kind) returns the schema errors of a record."""

    def __init__(self, describe: dict, health: dict, validate):
        self.describe, self.health, self.validate = describe, health, validate
        self.jobs: dict[str, dict] = {}
        self.assets: dict[str, int] = {}

    def handle(self, request: dict) -> dict:
        if not request["authorized"]:
            return _reply(401)
        for methods, pattern, name in ROUTES:
            match = re.fullmatch(pattern, request["path"])
            if match and request["method"] in methods:
                return getattr(self, "_" + name)(request, **match.groupdict())
        return _reply(404)

    def _status_of(self, job_id):
        return {"kind": "task-status", "schemaVersion": "1.1.0", "job_id": job_id, "state": self.jobs[job_id]["state"],
                "steps": [], "outputs": [], "params_actual": None, "timings": None, "error": None}

    def _describe(self, request):
        return _reply(200, self.describe)

    def _health(self, request):
        return _reply(200, self.health)

    def _unload(self, request):
        return _reply(200, {**self.health, "state": "idle", "resident_profile": None})

    def _submit(self, request):
        body = request["body"]
        if (not isinstance(body, dict) or self.validate(body, "task-request")
                or not TYPED.fullmatch(body["schemaVersion"])):
            return _reply(400)
        roles = [i["role"] for i in body["inputs"]]
        if len(roles) != len(set(roles)):
            return _reply(400)
        held = self.jobs.get(body["job_id"])
        if held is not None:
            return _reply(202, self._status_of(body["job_id"])) if held["request"] == body else _reply(409)
        code = self._refusal(body)
        if code:
            return _reply(422, {"kind": "refusal", "schemaVersion": "1.0.0", "job_id": body["job_id"], "code": code,
                                "detail": REFUSAL_DETAIL[code], "loaded_nothing": True})
        self.jobs[body["job_id"]] = {"request": body, "state": "awaiting_inputs"}
        self._start_ready()
        return _reply(202, self._status_of(body["job_id"]))

    def _refusal(self, body):
        """The refusals a describe decides, in the refusal enum's order; memory, disk and busy are runtime facts."""
        profile = next((p for p in self.describe["profiles"] if p["profile_id"] == body["profile_id"]), None)
        if profile is None or body["task"] not in profile["tasks"]:
            return "unsupported_task"
        if body["lane"] not in profile["lanes"]:
            return "lane_forbidden"
        limits, params = profile["limits"], body["params"]
        for param, limit in (("duration_s", "max_duration_s"), ("channels", "channels")):
            if limits[limit] is not None and params.get(param, 0) > limits[limit]:
                return "over_limit"
        language = params.get("lyrics_language")
        if language is not None and language not in (limits["lyric_languages"] or []):
            return "language_unsupported"
        return None if profile["weights_present"] else "weights_missing"

    def _start_ready(self):
        for job in self.jobs.values():
            if job["state"] == "awaiting_inputs" and all(i["sha256"] in self.assets for i in job["request"]["inputs"]):
                job["state"] = "queued"

    def _asset(self, request, sha):
        if request["method"] != "PUT":
            if sha not in self.assets:
                return _reply(404)
            return _reply(200, content={"sha256": sha, "bytes": self.assets[sha]} if request["method"] == "GET" else None)
        declared = [i["bytes"] for job in self.jobs.values() if job["state"] not in TERMINAL
                    for i in job["request"]["inputs"] if i["sha256"] == sha]
        if not declared:
            return _reply(403)
        content = request["content"]
        if content is None:
            return _reply(400)
        if content["bytes"] > max(declared):
            return _reply(413)
        if content["sha256"] != sha or content["bytes"] not in declared:
            return _reply(400)
        self.assets[sha] = content["bytes"]
        self._start_ready()
        return _reply(204)

    def _status(self, request, job):
        return _reply(200, self._status_of(job)) if job in self.jobs else _reply(404)

    def _output(self, request, job, role):
        return _reply(404)  # outputs exist only once a job is ready, and the reference runs nothing

    def _cancel(self, request, job):
        if job not in self.jobs:
            return _reply(404)
        if self.jobs[job]["state"] not in TERMINAL:
            self.jobs[job]["state"] = "cancelled"
        return _reply(200, self._status_of(job))
