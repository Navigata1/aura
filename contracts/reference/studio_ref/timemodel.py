"""The one time model (ADR-0033): 960 PPQ, tempo as integer microseconds per quarter note, and ONE half-up rounding
of an exact rational at the very end of each conversion. Tempo segments are [{tick, us_per_quarter}] sorted by tick,
the first at tick 0. The TypeScript twin in contracts-ts must reproduce contracts/fixtures/vectors/tempo.json.
"""

from __future__ import annotations

from fractions import Fraction

PPQ = 960
US_PER_SECOND = 1_000_000


def round_half_up(value: Fraction) -> int:
    """The single rounding function. Half-way values round toward +infinity (value >= 0 in practice)."""
    return (value.numerator * 2 + value.denominator) // (value.denominator * 2)


def _segments(tempo: list[dict]) -> list[tuple[int, int]]:
    segs = [(seg["tick"], seg["us_per_quarter"]) for seg in tempo]
    if not segs or segs[0][0] != 0 or any(b[0] <= a[0] for a, b in zip(segs, segs[1:])):
        raise ValueError("tempo segments must start at tick 0 and strictly increase")
    return segs


def seconds_at_tick(tick: int, tempo: list[dict], ppq: int = PPQ) -> Fraction:
    total = Fraction(0)
    segs = _segments(tempo)
    for i, (start, us) in enumerate(segs):
        end = segs[i + 1][0] if i + 1 < len(segs) else None
        if tick <= start:
            break
        span = (min(tick, end) if end is not None else tick) - start
        total += Fraction(span * us, ppq * US_PER_SECOND)
    return total


def ticks_to_frames(tick: int, tempo: list[dict], sample_rate: int, ppq: int = PPQ) -> int:
    if tick < 0:
        raise ValueError("tick must be >= 0")
    return round_half_up(seconds_at_tick(tick, tempo, ppq) * sample_rate)


def frames_to_ticks(frame: int, tempo: list[dict], sample_rate: int, ppq: int = PPQ) -> int:
    if frame < 0:
        raise ValueError("frame must be >= 0")
    target = Fraction(frame, sample_rate)
    segs = _segments(tempo)
    start_seconds = Fraction(0)
    for i, (start, us) in enumerate(segs):
        end = segs[i + 1][0] if i + 1 < len(segs) else None
        seg_seconds = None if end is None else Fraction((end - start) * us, ppq * US_PER_SECOND)
        if seg_seconds is None or target < start_seconds + seg_seconds:
            ticks = start + (target - start_seconds) * ppq * US_PER_SECOND / us
            return round_half_up(Fraction(ticks))
        start_seconds += seg_seconds
    raise AssertionError("unreachable")
