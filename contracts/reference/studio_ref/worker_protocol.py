"""Worker protocol v1 reference (ADR-0026, architecture.md §9.2, contracts/README.md "Worker protocol").

`profile_revision` is the registry's pin-hash over the pins a worker describes. Stdlib only.
"""
from __future__ import annotations

import re

from studio_ref.canonical import canon_bytes, sha256_hex


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
