"""Audition hand-derived golden cases and public reference evaluator."""
from studio_ref import audition
from studio_ref.fixture_support import SV
import hashlib
from studio_ref.canonical import sha256_hex

KIND = "fixture.audition"

def build(profiles):
    mapping = [{"label": "B", "candidate_id": "cand_a"}, {"label": "A", "candidate_id": "cand_b"}]
    nonce = "00" * 31 + "01"
    preimage = '[{"candidate_id":"cand_b","label":"A"},{"candidate_id":"cand_a","label":"B"}]|' + nonce
    audition_vec = {"kind": "fixture.audition", "schemaVersion": SV, "cases": [
        {"name": "two arms", "derivation": "Quietest is -15.40; A is lowered by 1.20, B untouched.", "op": "gains",
         "loudness": {"A": "-14.20", "B": "-15.40"}, "expected_gains": {"A": "-1.20", "B": "0.00"}},
        {"name": "equal loudness", "derivation": "No arm moves.", "op": "gains", "loudness": {"A": "-14.00", "B": "-14.00"},
         "expected_gains": {"A": "0.00", "B": "0.00"}},
        {"name": "three arms", "derivation": "Quietest -12.55: A -9.00 -> -3.55; C -10.10 -> -2.45.", "op": "gains",
         "loudness": {"A": "-9.00", "B": "-12.55", "C": "-10.10"}, "expected_gains": {"A": "-3.55", "B": "0.00", "C": "-2.45"}},
        {"name": "commitment", "derivation": "Mapping sorted by label, canonical JSON (sorted keys, no spaces), '|', the nonce; hashed with sha256.",
         "op": "commitment", "mapping": mapping, "nonce": nonce, "preimage": preimage,
         "expected_commitment": hashlib.sha256(preimage.encode("utf-8")).hexdigest()},
    ]}
    return audition_vec

def evaluate(case, world):
    if case["op"] == "gains":
        return audition.gains(case["loudness"]), case["expected_gains"]
    if sha256_hex(case["preimage"].encode("utf-8")) != case["expected_commitment"]:
        raise ValueError("the hand-written preimage does not hash to the expected commitment")
    return audition.commitment(case["mapping"], case["nonce"]), case["expected_commitment"]
