"""MelodySpec <-> Standard MIDI File, the reference mapping (ADR-0033; contracts/README.md, 'MIDI round trip').

Standard library only. to_smf writes the canonical file; from_smf reads one back. Content the mapping cannot represent
raises a typed MidiRefusal; writer input outside the melody-spec and timeline/1 schemas raises MidiInputError.
"""

from __future__ import annotations

import re

from . import timemodel

SECTION_NAME = re.compile(rb"[a-z][a-z0-9-]{0,31}")  # a SongForm section name (song-spec, timeline/1 markers)
DENOMINATORS = (1, 2, 4, 8, 16, 32)  # melody-spec meter denominators
RELEASE_VELOCITY = 64  # written on every note-off; not read back
META_LENGTH = {"ff51": 3, "ff58": 4}  # tempo and time signature data lengths (SMF 1.0)
MAX_DELTA = 0x0FFFFFFF  # the largest four-byte delta time


class MidiRefusal(ValueError):
    """Content the mapping cannot represent. code is one of the fixture-midi refusal codes."""

    def __init__(self, code: str, smf_track: int | None = None, tick: int | None = None):
        super().__init__(f"{code} (smf_track {smf_track}, tick {tick})")
        self.code, self.smf_track, self.tick = code, smf_track, tick

    def as_dict(self) -> dict:
        return {"code": self.code, "smf_track": self.smf_track, "tick": self.tick}


class MidiInputError(ValueError):
    """Writer input outside the melody-spec and timeline/1 schemas, refused before a byte is written."""


# ----- write --------------------------------------------------------------------------------------------------------

def _varlen(value: int) -> bytes:
    out = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        out.append(0x80 | value & 0x7F)
    return bytes(reversed(out))


def _chunk(events: list[tuple[int, bytes]], end: int = 0) -> bytes:
    """One MTrk chunk. Its End of Track comes at end, or at its last event when that is later."""
    body, now = bytearray(), 0
    for tick, data in events + [(max(end, events[-1][0] if events else 0), b"\xff\x2f\x00")]:
        if tick - now > MAX_DELTA:
            raise MidiRefusal("tick_not_representable", None, tick)
        body += _varlen(tick - now) + data
        now = tick
    return b"MTrk" + len(body).to_bytes(4, "big") + bytes(body)


def _within(value, low: int, high: int | None = None) -> bool:
    return type(value) is int and low <= value and (high is None or value <= high)


def _check_input(melody: dict, markers, end_tick) -> None:
    """The schemas' own field rules, so that invalid input fails loudly instead of being written corrupted."""
    tm = melody["tempo_map"]
    bad = [s for s in tm["tempo"] if not (_within(s["tick"], 0) and _within(s["us_per_quarter"], 1, 0xFFFFFF))]
    bad += [s for s in tm["meter"] if not (_within(s["tick"], 0) and _within(s["numerator"], 1, 32)
                                           and _within(s["denominator"], 1, 32) and s["denominator"] in DENOMINATORS)]
    bad += [n for n in melody["notes"] if not (_within(n["start_tick"], 0) and _within(n["duration_ticks"], 1)
                                               and _within(n["pitch"], 0, 127) and _within(n["velocity"], 1, 127))]
    bad += [m for m in markers if not (_within(m["tick"], 0) and isinstance(m["name"], str)
                                       and SECTION_NAME.fullmatch(m["name"].encode()))]
    if bad or not (tm["tempo"] and tm["meter"]) or not (end_tick is None or _within(end_tick, 0)):
        raise MidiInputError(f"outside the melody-spec or timeline/1 schema: {bad[:1] or end_tick}")


def _check_order(segments: list[dict]) -> None:
    """The time model's one ordering rule (ADR-0033): segments start at tick 0 and strictly increase. It judges the list
    as a whole, so the refusal names no tick."""
    try:
        timemodel._segments([{"tick": segment["tick"], "us_per_quarter": 1} for segment in segments])
    except ValueError:
        raise MidiRefusal("tempo_map_ambiguous") from None


def _off_bar_line(meter: list[dict]) -> int | None:
    """The first meter change that is not on a bar line of the meter before it, or None. ADR-0033 counts bars and beats
    across meter segments only from bar lines; a bar of n/d is n x 3840 / d ticks at 960 PPQ, exact for every allowed
    denominator (the rule #131 adds to melody.wellformed)."""
    for before, after in zip(meter, meter[1:]):
        if (after["tick"] - before["tick"]) % (before["numerator"] * 4 * timemodel.PPQ // before["denominator"]):
            return after["tick"]
    return None


def to_smf(melody: dict, markers: list[dict] = (), end_tick: int | None = None) -> bytes:
    """Format 1, 960 PPQ: SMF track 0, the conductor (per tick: meter, tempo, section markers), and SMF track 1, the
    notes on MIDI channel 1. Takes any dict with a MelodySpec's tempo_map and notes (a whole record included), the
    section markers and the file's end: the conductor's End of Track goes at end_tick when that is later than every
    event (an outro keeps its bars); left out, every SMF track ends at its own last event."""
    _check_input(melody, markers, end_tick)
    tm = melody["tempo_map"]
    for segments in (tm["meter"], tm["tempo"]):
        _check_order(segments)
    if (off := _off_bar_line(tm["meter"])) is not None:
        raise MidiRefusal("meter_change_inside_bar", None, off)
    conductor = [(m["tick"], 0, bytes([0xFF, 0x58, 4, m["numerator"], m["denominator"].bit_length() - 1,
                                       96 // m["denominator"], 8])) for m in tm["meter"]]
    conductor += [(t["tick"], 1, b"\xff\x51\x03" + t["us_per_quarter"].to_bytes(3, "big")) for t in tm["tempo"]]
    for marker in markers:
        name = marker["name"].encode("ascii")
        conductor.append((marker["tick"], 2, b"\xff\x06" + _varlen(len(name)) + name))
    conductor.sort(key=lambda e: e[:2])
    notes = sorted(melody["notes"], key=lambda n: (n["start_tick"], n["pitch"]))
    sounding = {}  # pitch -> end tick of its latest note
    for n in notes:
        if sounding.get(n["pitch"], 0) > n["start_tick"]:
            raise MidiRefusal("same_pitch_overlap", None, n["start_tick"])
        sounding[n["pitch"]] = n["start_tick"] + n["duration_ticks"]
    events = [(n["start_tick"], 1, n["pitch"], bytes([0x90, n["pitch"], n["velocity"]])) for n in notes]
    events += [(n["start_tick"] + n["duration_ticks"], 0, n["pitch"], bytes([0x80, n["pitch"], RELEASE_VELOCITY]))
               for n in notes]
    events.sort(key=lambda e: e[:3])
    last = max(tick for tick, *_ in conductor + events)
    if end_tick is not None and end_tick < last:
        raise MidiRefusal("end_before_last_event", None, last)
    end = end_tick if end_tick is not None and end_tick > last else 0
    head = b"MThd" + (6).to_bytes(4, "big") + (1).to_bytes(2, "big") + (2).to_bytes(2, "big")
    head += timemodel.PPQ.to_bytes(2, "big")
    return head + _chunk([(t, d) for t, _, d in conductor], end) + _chunk([(t, d) for t, _, _, d in events])


# ----- read ---------------------------------------------------------------------------------------------------------

class _Cursor:
    """Reads bytes; a short read is malformed at the SMF track and, once the event's delta time is read, its tick."""

    def __init__(self, data: bytes, smf_track: int | None = None):
        self.data, self.pos, self.smf_track, self.tick = data, 0, smf_track, None

    def take(self, n: int) -> bytes:
        if self.pos + n > len(self.data):
            raise MidiRefusal("malformed_smf", self.smf_track, self.tick)
        self.pos += n
        return self.data[self.pos - n:self.pos]

    def number(self, n: int) -> int:
        return int.from_bytes(self.take(n), "big")

    def varlen(self) -> int:
        value = 0
        for _ in range(4):
            byte = self.take(1)[0]
            value = value << 7 | byte & 0x7F
            if byte < 0x80:
                return value
        raise MidiRefusal("malformed_smf", self.smf_track, self.tick)


def _events(body: bytes, smf_track: int) -> tuple[list[tuple[int, str, bytes]], int]:
    """One MTrk chunk as its events, (tick in the file's division, event, data) with event the status byte in hex or ff
    and the meta type, and the tick of its End of Track."""
    cur, tick, running, out = _Cursor(body, smf_track), 0, None, []
    while True:
        cur.tick = None  # a broken delta time places no event
        tick += cur.varlen()
        cur.tick = tick
        first = cur.take(1)[0]
        if first == 0xFF:
            kind, data = cur.take(1)[0], cur.take(cur.varlen())
            running = None  # meta and SysEx events cancel running status (SMF 1.0)
            if kind == 0x2F:
                if data or cur.pos != len(body):
                    raise MidiRefusal("malformed_smf", smf_track, tick)
                return out, tick
            out.append((tick, f"ff{kind:02x}", data))
        elif first in (0xF0, 0xF7):
            cur.take(cur.varlen())
            running = None
            out.append((tick, f"{first:02x}", b""))
        elif first > 0xF0 or (first < 0x80 and running is None):  # a system message, or data with no status
            raise MidiRefusal("malformed_smf", smf_track, tick)
        else:
            if first >= 0x80:
                running, data = first, b""
            else:
                data = bytes([first])  # running status: the previous channel status applies
            data += cur.take((1 if running >> 4 in (0xC, 0xD) else 2) - len(data))
            if max(data) >= 0x80:
                raise MidiRefusal("malformed_smf", smf_track, tick)
            out.append((tick, f"{running:02x}", data))


def from_smf(data: bytes) -> dict:
    """Formats 0 and 1, at any division whose ticks convert exactly to 960 PPQ, back to the MIDI-carried MelodySpec
    fields, the section markers and the events not carried. Anything else raises a typed MidiRefusal."""
    cur = _Cursor(bytes(data))
    if cur.take(4) != b"MThd" or cur.number(4) != 6:
        raise MidiRefusal("malformed_smf")
    fmt, ntrks, division = cur.number(2), cur.number(2), cur.number(2)
    if division & 0x8000:
        raise MidiRefusal("smpte_division")
    if fmt == 2:
        raise MidiRefusal("track_layout_unsupported")
    if fmt > 2 or not ntrks or (fmt == 0 and ntrks != 1) or not division:
        raise MidiRefusal("malformed_smf")
    tracks = []
    for index in range(ntrks):
        cur.smf_track = index
        if cur.take(4) != b"MTrk":
            raise MidiRefusal("malformed_smf", index)
        tracks.append(_events(cur.take(cur.number(4)), index))
    if cur.pos != len(cur.data):
        raise MidiRefusal("malformed_smf")
    return _carry(tracks, division)


def _put(table: dict, tick: int, value, smf_track: int, source_tick: int) -> None:
    """One tempo (or meter) per tick: a repeat of the same value is the same entry, a different one is refused."""
    if table.setdefault(tick, value) != value:
        raise MidiRefusal("tempo_map_ambiguous", smf_track, source_tick)


def _whole(source_tick: int, division: int, smf_track: int) -> int:
    """A tick of the file's division at 960 PPQ: exact, or refused, never rounded."""
    tick, rest = divmod(source_tick * timemodel.PPQ, division)
    if rest:
        raise MidiRefusal("tick_not_representable", smf_track, source_tick)
    return tick


def _file_end(ends: list[tuple[int, int, int]], not_carried: list[dict]) -> tuple[int, list[dict]]:
    """The file's end is its latest End of Track. An earlier one after its own SMF track's last event is a position the
    result would not otherwise hold, so it is listed (ff2f), last among that SMF track's entries."""
    end_tick = max(end for _, _, end in ends)
    inner = [{"smf_track": smf_track, "tick": end, "event": "ff2f"}
             for smf_track, last, end in ends if last < end < end_tick]
    return end_tick, sorted(not_carried + inner, key=lambda entry: entry["smf_track"])


def _melody(tempo: dict, meter: dict, meter_at: dict, notes: list[dict]) -> dict:
    """The MIDI-carried MelodySpec fields. The SMF defaults (120 BPM, 4/4) hold until the first tempo and time
    signature, and a time signature off a bar line of the meter before it is refused where it stands in the file."""
    tempo, meter = {0: 500000, **tempo}, {0: (4, 4), **meter}
    tempo_map = {"tempo": [{"tick": t, "us_per_quarter": us} for t, us in sorted(tempo.items())],
                 "meter": [{"tick": t, "numerator": n, "denominator": d} for t, (n, d) in sorted(meter.items())]}
    if (off := _off_bar_line(tempo_map["meter"])) is not None:
        raise MidiRefusal("meter_change_inside_bar", *meter_at[off])
    return {"tempo_map": tempo_map, "notes": sorted(notes, key=lambda n: (n["start_tick"], n["pitch"]))}


def _carry(tracks: list, division: int) -> dict:
    tempo, meter, meter_at, notes, markers, not_carried, ends = {}, {}, {}, [], [], [], []
    melody_channel, pending = None, {}  # the (SMF track, channel) holding the melody; sounding pitch -> its note-on
    for smf_track, (events, source_end) in enumerate(tracks):
        last = 0
        for source_tick, event, data in events:
            tick = last = _whole(source_tick, division, smf_track)
            if len(data) != META_LENGTH.get(event, len(data)):
                raise MidiRefusal("malformed_smf", smf_track, source_tick)
            if event == "ff51":
                if not int.from_bytes(data, "big"):
                    raise MidiRefusal("tempo_outside_model", smf_track, source_tick)
                _put(tempo, tick, int.from_bytes(data, "big"), smf_track, source_tick)
            elif event == "ff58":
                if not 1 <= data[0] <= 32 or data[1] > 5:
                    raise MidiRefusal("meter_outside_model", smf_track, source_tick)
                _put(meter, tick, (data[0], 1 << data[1]), smf_track, source_tick)
                meter_at.setdefault(tick, (smf_track, source_tick))
            elif event == "ff06" and SECTION_NAME.fullmatch(data):
                markers.append({"name": data.decode("ascii"), "tick": tick})
            elif event[0] == "9" and data[1]:
                if melody_channel not in (None, (smf_track, event[1])):
                    raise MidiRefusal("track_layout_unsupported", smf_track, source_tick)
                if data[0] in pending:
                    raise MidiRefusal("same_pitch_overlap", smf_track, source_tick)
                melody_channel, pending[data[0]] = (smf_track, event[1]), (tick, data[1], source_tick)
            elif event[0] in "89" and (smf_track, event[1]) == melody_channel and data[0] in pending:
                start, velocity, _ = pending.pop(data[0])
                if tick == start:
                    raise MidiRefusal("zero_length_note", smf_track, source_tick)
                notes.append({"start_tick": start, "duration_ticks": tick - start, "pitch": data[0],
                              "velocity": velocity})
            else:  # listed, never silently dropped; the capture keeps the original bytes
                not_carried.append({"smf_track": smf_track, "tick": tick, "event": event})
        ends.append((smf_track, last, _whole(source_end, division, smf_track)))
        if pending:
            raise MidiRefusal("unterminated_note", smf_track, min(source for _, _, source in pending.values()))
    end_tick, not_carried = _file_end(ends, not_carried)
    return {"melody": _melody(tempo, meter, meter_at, notes), "markers": sorted(markers, key=lambda m: m["tick"]),
            "end_tick": end_tick, "not_carried": not_carried}
