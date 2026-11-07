"""Stable synthetic fixture labels; these records never constitute owner evidence."""
from studio_ref.canonical import sha256_hex

SV = "1.0.0"

def H(label):
    return sha256_hex(("fixture:" + label).encode("utf-8"))

def R(profile_id):
    return sha256_hex(("fixture-profile-revision:" + profile_id).encode("utf-8"))

def owner(act, when):
    return {"act": act, "scope": "owner-ui", "at": when}
