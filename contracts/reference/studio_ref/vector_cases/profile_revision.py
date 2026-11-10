"""profile_revision hand-derived golden cases (T02w): the pin-hash a registry status is keyed by.

Every preimage below is written out by hand as the canonical JSON (ADR-0028: UTF-8, keys sorted, no whitespace) of the
object {code_commit, env, sdk_version, weights_manifest_sha256}, with env exactly as describe reports it and a profile
without weights giving null. The expected hex is sha256 of that hand-written text, never of the reference's output.
"""
import hashlib

from studio_ref import worker_protocol
from studio_ref.fixture_support import SV

KIND = "fixture.profile-revision"
LOCK = "f66d3cea03d102df6b8139947fb3b0c09f8a387a58fd6b4e78a63a6796dbfe54"  # the world's wkr_fake lock
WEIGHTS = "1111111111111111111111111111111111111111111111111111111111111111"
DIGEST = "sha256:2222222222222222222222222222222222222222222222222222222222222222"
FULL = "0000000aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def build(profiles):
    def ok(name, why, commit, env, sdk, weights, preimage):
        return {"name": name, "derivation": why,
                "input": {"code_commit": commit, "env": env, "sdk_version": sdk, "weights_manifest_sha256": weights},
                "expected": {"preimage": preimage,
                             "profile_revision": hashlib.sha256(preimage.encode("utf-8")).hexdigest()}}

    def bad(name, why, code, commit="0000000", env=None, sdk="0.1.0", weights=None):
        return {"name": name, "derivation": why,
                "input": {"code_commit": commit, "env": {"lock_sha256": LOCK} if env is None else env,
                          "sdk_version": sdk, "weights_manifest_sha256": weights}, "expected": {"invalid": code}}
    return {"kind": KIND, "schemaVersion": SV, "cases": [
        ok("fake worker, no weights", "wkr_fake's pins; a profile without weights hashes null, never an empty string.",
           "0000000", {"lock_sha256": LOCK}, "0.1.0", None,
           '{"code_commit":"0000000","env":{"lock_sha256":"' + LOCK + '"},"sdk_version":"0.1.0","weights_manifest_sha256":null}'),
        ok("weights manifest pinned", "The same pins with a weights manifest: the hex goes in as a lowercase string.",
           "0000000", {"lock_sha256": LOCK}, "0.1.0", WEIGHTS,
           '{"code_commit":"0000000","env":{"lock_sha256":"' + LOCK + '"},"sdk_version":"0.1.0","weights_manifest_sha256":"'
           + WEIGHTS + '"}'),
        ok("image digest environment", "A burst image: env is the image_digest object, prefix included.",
           "0000000", {"image_digest": DIGEST}, "0.1.0", WEIGHTS,
           '{"code_commit":"0000000","env":{"image_digest":"' + DIGEST + '"},"sdk_version":"0.1.0","weights_manifest_sha256":"'
           + WEIGHTS + '"}'),
        ok("full commit is another revision", "The commit is hashed exactly as described: a 40-digit commit whose first 7 "
           "digits match the short one is a different revision, so a worker must describe one form consistently.",
           FULL, {"lock_sha256": LOCK}, "0.1.0", None,
           '{"code_commit":"' + FULL + '","env":{"lock_sha256":"' + LOCK + '"},"sdk_version":"0.1.0","weights_manifest_sha256":null}'),
        ok("SDK bump is another revision", "Only sdk_version changes from the first case.",
           "0000000", {"lock_sha256": LOCK}, "0.2.0", None,
           '{"code_commit":"0000000","env":{"lock_sha256":"' + LOCK + '"},"sdk_version":"0.2.0","weights_manifest_sha256":null}'),
        bad("uppercase commit", "Commits are lowercase hex, 7 to 40 digits.", "code_commit_invalid", commit="0000000A"),
        bad("both environments", "env is exactly one of lock_sha256 or image_digest.", "env_invalid",
            env={"lock_sha256": LOCK, "image_digest": DIGEST}),
        bad("digest without prefix", "An image digest carries its sha256: prefix.", "env_invalid", env={"image_digest": DIGEST[7:]}),
        bad("two-part SDK version", "SDK versions are major.minor.patch.", "sdk_version_invalid", sdk="0.1"),
        bad("empty weights manifest", "No weights is null; an empty string is refused.", "weights_manifest_invalid", weights=""),
    ]}


def evaluate(case, world):
    given = case["input"]
    describe = {"code_commit": given["code_commit"], "env": given["env"], "sdk_version": given["sdk_version"],
                "profiles": [{"profile_id": "probe", "weights_manifest_sha256": given["weights_manifest_sha256"]}]}
    try:
        preimage = worker_protocol.revision_preimage(given["code_commit"], given["env"], given["sdk_version"],
                                                     given["weights_manifest_sha256"])
        got = {"preimage": preimage.decode("utf-8"), "profile_revision": worker_protocol.profile_revision(describe, "probe")}
    except worker_protocol.ProtocolError as error:
        got = {"invalid": error.code}
    return got, case["expected"]
