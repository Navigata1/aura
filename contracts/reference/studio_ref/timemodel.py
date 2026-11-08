"""The one time model (ADR-0033): 960 PPQ, tempo as integer microseconds per quarter note, and ONE half-up rounding
of an exact rational at the very end of each conversion. Tempo segments are [{tick, us_per_quarter}] sorted by tick,
the first at tick 0. Meter segments [{tick, numerator, denominator}] count bars and beats from 1 and change only on a
bar line. The TypeScript twin in contracts-ts must reproduce contracts/fixtures/vectors/tempo.json and meter.json.
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


class MeterError(ValueError):
    """A meter map or bar position the time model cannot represent; code names the reason."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def bar_ticks(numerator: int, denominator: int, ppq: int = PPQ) -> int:
    """One bar of numerator/denominator in ticks: exact at 960 PPQ for every allowed denominator (1 to 32)."""
    return numerator * 4 * ppq // denominator


def bar_segments(meter: list[dict], ppq: int = PPQ) -> list[tuple[int, int, int, int]]:
    """Meter segments as (tick, first bar, numerator, denominator). They start at tick 0, strictly increase and change
    only on a bar line of the meter before them, so bars (and beats, one denominator note each) count on from 1."""
    out: list[tuple[int, int, int, int]] = []
    for seg in meter:
        tick, numerator, denominator = seg["tick"], seg["numerator"], seg["denominator"]
        if (not out and tick != 0) or (out and tick <= out[-1][0]):
            raise MeterError("meter_segments_invalid")
        if out:
            start, bar, prev_numerator, prev_denominator = out[-1]
            bars, inside = divmod(tick - start, bar_ticks(prev_numerator, prev_denominator, ppq))
            if inside:
                raise MeterError("meter_change_inside_bar")
            out.append((tick, bar + bars, numerator, denominator))
        else:
            out.append((0, 1, numerator, denominator))
    return out


def position(tick: int, meter: list[dict], ppq: int = PPQ) -> dict:
    """The 1-based bar and beat holding tick, and the ticks into that beat."""
    if tick < 0:
        raise ValueError("tick must be >= 0")
    start, first, numerator, denominator = [s for s in bar_segments(meter, ppq) if s[0] <= tick][-1]
    bars, into = divmod(tick - start, bar_ticks(numerator, denominator, ppq))
    beat, offset = divmod(into, 4 * ppq // denominator)
    return {"bar": first + bars, "beat": beat + 1, "offset": offset}


def tick_at(bar: int, beat: int, meter: list[dict], ppq: int = PPQ) -> int:
    """The first tick of a 1-based bar and beat."""
    if bar < 1 or beat < 1:
        raise ValueError("bars and beats count from 1")
    start, first, numerator, denominator = [s for s in bar_segments(meter, ppq) if s[1] <= bar][-1]
    if beat > numerator:
        raise MeterError("beat_outside_bar")
    return start + (bar - first) * bar_ticks(numerator, denominator, ppq) + (beat - 1) * (4 * ppq // denominator)


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
