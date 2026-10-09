"""Audition level matching and the blind commitment (ADR-0010, GLOSSARY: Level matching, Reveal)."""

from __future__ import annotations

from decimal import Decimal

from .canonical import canon_bytes, sha256_hex

TWO_PLACES = Decimal("0.01")


def gains(loudness: dict[str, str]) -> dict[str, str]:
    """Attenuation only: every arm is lowered to the quietest arm's integrated loudness; none is raised."""
    values = {label: Decimal(v) for label, v in loudness.items()}
    quietest = min(values.values())
    out = {}
    for label in sorted(values):
        gain = (quietest - values[label]).quantize(TWO_PLACES)
        out[label] = "0.00" if gain == 0 else str(gain)
    return out


def commitment(mapping: list[dict], nonce: str) -> str:
    """sha256(canonical_json(mapping sorted by label) + '|' + nonce)."""
    ordered = sorted(({"label": m["label"], "candidate_id": m["candidate_id"]} for m in mapping), key=lambda m: m["label"])
    return sha256_hex(canon_bytes(ordered) + b"|" + nonce.encode("utf-8"))
