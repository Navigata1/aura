"""MelodySpec <-> Standard MIDI File, the reference mapping (ADR-0033; contracts/README.md, 'MIDI round trip').

Standard library only. to_smf writes the canonical file; from_smf reads one back.
"""

from __future__ import annotations

import re

PPQ = 960
SECTION_NAME = re.compile(rb"[a-z][a-z0-9-]{0,31}")  # a SongForm section name (song-spec, timeline/1 markers)
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


# ----- write --------------------------------------------------------------------------------------------------------

def _varlen(value: int) -> bytes:
    out = [value & 0x7F]
    while value > 0x7F:
        value >>= 7
        out.append(0x80 | value & 0x7F)
    return bytes(reversed(out))


def _chunk(events: list[tuple[int, bytes]]) -> bytes:
    body, now = bytearray(), 0
    for tick, data in events:
        if tick - now > MAX_DELTA:
            raise MidiRefusal("tick_not_representable", None, tick)
        body += _varlen(tick - now) + data
        now = tick
    body += b"\x00\xff\x2f\x00"
    return b"MTrk" + len(body).to_bytes(4, "big") + bytes(body)


def _ordered(segments: list[dict]) -> list[dict]:
    """Tempo and meter start at tick 0 and strictly increase (melody.wellformed); otherwise the map is ambiguous."""
    for i, segment in enumerate(segments):
        if (segment["tick"] != 0) if i == 0 else (segment["tick"] <= segments[i - 1]["tick"]):
            raise MidiRefusal("tempo_map_ambiguous", None, segment["tick"])
    return segments


def to_smf(melody: dict, markers: list[dict] = ()) -> bytes:
    """Format 1, 960 PPQ: a conductor track (per tick: meter, tempo, section markers) and the notes on MIDI channel 1.
    Takes any dict with a MelodySpec's tempo_map and notes (a whole record included) and the section markers."""
    tm = melody["tempo_map"]
    conductor = [(m["tick"], 0, bytes([0xFF, 0x58, 4, m["numerator"], m["denominator"].bit_length() - 1,
                                       96 // m["denominator"], 8])) for m in _ordered(tm["meter"])]
    conductor += [(t["tick"], 1, b"\xff\x51\x03" + t["us_per_quarter"].to_bytes(3, "big")) for t in _ordered(tm["tempo"])]
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
    head = b"MThd" + (6).to_bytes(4, "big") + (1).to_bytes(2, "big") + (2).to_bytes(2, "big") + PPQ.to_bytes(2, "big")
    return head + _chunk([(t, d) for t, _, d in conductor]) + _chunk([(t, d) for t, _, _, d in events])


# ----- read ---------------------------------------------------------------------------------------------------------

class _Cursor:
    def __init__(self, data: bytes, smf_track: int | None = None):
        self.data, self.pos, self.smf_track = data, 0, smf_track

    def take(self, n: int) -> bytes:
        if self.pos + n > len(self.data):
            raise MidiRefusal("malformed_smf", self.smf_track)
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
        raise MidiRefusal("malformed_smf", self.smf_track)


def _events(body: bytes, smf_track: int) -> list[tuple[int, str, bytes]]:
    """One MTrk chunk as (tick in the file's division, event, data): event is the status byte in hex, or ff + type."""
    cur, tick, running, out = _Cursor(body, smf_track), 0, None, []
    while True:
        tick += cur.varlen()
        first = cur.take(1)[0]
        if first == 0xFF:
            kind, data = cur.take(1)[0], cur.take(cur.varlen())
            running = None  # meta and SysEx events cancel running status (SMF 1.0)
            if kind == 0x2F:
                if data or cur.pos != len(body):
                    raise MidiRefusal("malformed_smf", smf_track)
                return out
            out.append((tick, f"ff{kind:02x}", data))
        elif first in (0xF0, 0xF7):
            cur.take(cur.varlen())
            running = None
            out.append((tick, f"{first:02x}", b""))
        elif first > 0xF0 or (first < 0x80 and running is None):  # a system message, or data with no status
            raise MidiRefusal("malformed_smf", smf_track)
        else:
            if first >= 0x80:
                running, data = first, b""
            else:
                data = bytes([first])  # running status: the previous channel status applies
            data += cur.take((1 if running >> 4 in (0xC, 0xD) else 2) - len(data))
            if max(data) >= 0x80:
                raise MidiRefusal("malformed_smf", smf_track)
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


def _carry(tracks: list, division: int) -> dict:
    tempo, meter, notes, markers, not_carried = {}, {}, [], [], []
    melody_channel, pending = None, {}  # the (track, channel) that holds the melody; sounding pitch -> note-on
    for smf_track, events in enumerate(tracks):
        for source_tick, event, data in events:
            tick, rest = divmod(source_tick * PPQ, division)  # exact, or refused: never rounded
            if rest:
                raise MidiRefusal("tick_not_representable", smf_track, source_tick)
            if len(data) != META_LENGTH.get(event, len(data)):
                raise MidiRefusal("malformed_smf", smf_track)
            if event == "ff51":
                if not int.from_bytes(data, "big"):
                    raise MidiRefusal("tempo_outside_model", smf_track, source_tick)
                _put(tempo, tick, int.from_bytes(data, "big"), smf_track, source_tick)
            elif event == "ff58":
                if not 1 <= data[0] <= 32 or data[1] > 5:
                    raise MidiRefusal("meter_outside_model", smf_track, source_tick)
                _put(meter, tick, (data[0], 1 << data[1]), smf_track, source_tick)
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
                notes.append({"start_tick": start, "duration_ticks": tick - start, "pitch": data[0], "velocity": velocity})
            else:  # listed, never silently dropped; the capture keeps the original bytes
                not_carried.append({"smf_track": smf_track, "tick": tick, "event": event})
        if pending:
            raise MidiRefusal("unterminated_note", smf_track, min(source for _, _, source in pending.values()))
    tempo.setdefault(0, 500000)  # SMF 1.0: 120 BPM and 4/4 until the first tempo and time signature
    meter.setdefault(0, (4, 4))
    notes.sort(key=lambda n: (n["start_tick"], n["pitch"]))
    markers.sort(key=lambda m: m["tick"])
    tempo_map = {"tempo": [{"tick": t, "us_per_quarter": us} for t, us in sorted(tempo.items())],
                 "meter": [{"tick": t, "numerator": n, "denominator": d} for t, (n, d) in sorted(meter.items())]}
    return {"melody": {"tempo_map": tempo_map, "notes": notes}, "markers": markers, "not_carried": not_carried}
