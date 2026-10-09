"""Canonical JSON and hashing (ADR-0028): UTF-8, sorted keys, no insignificant whitespace, integers only.

Non-integer quantities are decimal strings, so Python and TypeScript hash identically without float formatting.
"""

from __future__ import annotations

import hashlib
import json
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def canon_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_of(value) -> str:
    return sha256_hex(canon_bytes(value))


def self_hash(record: dict, field: str) -> str:
    """The hash a record stores about itself: sha256 of its canonical JSON without that field."""
    return sha_of({k: v for k, v in record.items() if k != field})


def float_paths(value, path: str = "$") -> list[str]:
    """Every location holding a JSON number that is not an integer (canonical.integers_only)."""
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, float):
        return [path]
    if isinstance(value, dict):
        out = []
        for key in sorted(value):
            out += float_paths(value[key], f"{path}.{key}")
        return out
    if isinstance(value, list):
        out = []
        for i, item in enumerate(value):
            out += float_paths(item, f"{path}[{i}]")
        return out
    return []


def dec(text: str) -> Decimal:
    return Decimal(text)


def usd_text(amount: Decimal) -> str:
    return str(amount.quantize(CENT, rounding=ROUND_HALF_UP))


def ceil_cents(amount: Decimal) -> Decimal:
    """Round up to the cent: a ceiling must never understate (ADR-0030)."""
    return amount.quantize(CENT, rounding=ROUND_CEILING)
