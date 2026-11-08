"""SongForm assembly (ADR-0032; GLOSSARY: SongForm, Phrase, Assembled melody): the reference for Score.assemble.

assemble(melody, song, output) lays the phrases of the MelodySpec revision a SongSpec names along its SongForm and
returns {"assembled": a melody-spec 1.1.0 record with its form} or {"refused": a typed refusal}; a source the time
model cannot measure raises TimeModelError. Pure, deterministic and integer-only at 960 PPQ, in the TimeModel's bars
and beats (ADR-0033): every bar length is exact, so nothing rounds. Nothing is truncated, stretched, retimed or chosen
by first match. Semantics, scan order and refusal codes: contracts/README.md, "SongForm assembly (T02c)".
"""

from __future__ import annotations

import copy

from .canonical import self_hash
from .timemodel import PPQ, bar_segments, bar_ticks, position, tempo_segments, tick_at

SCHEMA_VERSION = "1.1.0"


class Refused(Exception):
    def __init__(self, code: str, section_id=None, phrase_id=None, note_id=None):
        super().__init__(code)
        self.refusal = {"code": code, "section_id": section_id, "phrase_id": phrase_id, "note_id": note_id}


def assemble(melody: dict, song: dict, output: dict) -> dict:
    """output names the new record: melody_id, rev, base_rev, tempo_map_rev and created_at (its project is the source's)."""
    try:
        return {"assembled": _assemble(melody, song, output)}
    except Refused as refused:
        return {"refused": refused.refusal}


def _at(segments: list[dict], tick: int) -> dict:
    return [s for s in segments if s["tick"] <= tick][-1]


def _changes_inside(segments: list[dict], start: int, end: int) -> bool:
    return any(start < s["tick"] < end for s in segments)


def _shape(melody: dict, phrase: dict, section_id: str) -> dict:
    """The bars one phrase occupies (from the bar line at or before its start, rounded up to whole bars), its one tempo
    and meter over all of those bars, trailing rest included, and its notes."""
    pid, start, end = phrase["id"], phrase["start_tick"], phrase["end_tick"]
    if end <= start:
        raise Refused("empty_phrase", section_id, pid)
    tempo_map = melody["tempo_map"]
    meter = _at(tempo_map["meter"], start)
    bar = bar_ticks(meter["numerator"], meter["denominator"])
    anchor = tick_at(position(start, tempo_map["meter"])["bar"], 1, tempo_map["meter"])
    bars = -(-(end - anchor) // bar)
    if _changes_inside(tempo_map["meter"], anchor, anchor + bars * bar):
        raise Refused("meter_conflict", section_id, pid)
    if _changes_inside(tempo_map["tempo"], anchor, anchor + bars * bar):
        raise Refused("tempo_conflict", section_id, pid)
    notes = []
    for note in melody["notes"]:
        note_end = note["start_tick"] + note["duration_ticks"]
        if note["start_tick"] < end and note_end > start:
            if note["start_tick"] < start or note_end > end:
                raise Refused("note_crosses_phrase_edge", section_id, pid, note["id"])
            notes.append(note)
    return {"phrase": phrase, "anchor": anchor, "bars": bars,
            "notes": sorted(notes, key=lambda n: (n["start_tick"], n["pitch"])),
            "time": (_at(tempo_map["tempo"], anchor)["us_per_quarter"], meter["numerator"], meter["denominator"])}


def _section_phrases(melody: dict, song: dict) -> list[tuple[dict, list[dict]]]:
    """Each SongForm section with the shapes of the phrases it places, after every refusal check but chord placement."""
    tempo_segments(melody["tempo_map"]["tempo"])  # TimeModelError unless the tempo map starts at 0 and increases
    bar_segments(melody["tempo_map"]["meter"])  # TimeModelError unless meter changes land on bar lines
    if melody["spec_kind"] != "melody":
        raise Refused("source_not_melody")
    named = {"melody_id": melody["melody_id"], "rev": melody["rev"], "tempo_map_rev": melody["tempo_map"]["rev"]}
    if song["melody"] != named or song["project_id"] != melody["project_id"]:
        raise Refused("song_melody_mismatch")
    sections, seen = song["form"]["sections"], set()
    for section in sections:
        if section["id"] in seen:
            raise Refused("duplicate_section", section["id"])
        seen.add(section["id"])
    phrases = {}
    for phrase in melody["phrases"]:
        if phrase["id"] in phrases:
            raise Refused("duplicate_phrase", None, phrase["id"])
        phrases[phrase["id"]] = phrase
    plan = []
    for section in sections:
        sid = section["id"]
        if (section["section_kind"] == "instrumental") == bool(section["phrase_ids"]):
            raise Refused("section_kind_mismatch", sid)
        shapes = []
        for pid in section["phrase_ids"]:
            if pid not in phrases:
                raise Refused("missing_phrase", sid, pid)
            shapes.append(_shape(melody, phrases[pid], sid))
        for shape in shapes[1:]:
            if shape["time"][1:] != shapes[0]["time"][1:]:
                raise Refused("meter_conflict", sid, shape["phrase"]["id"])
            if shape["time"][0] != shapes[0]["time"][0]:
                raise Refused("tempo_conflict", sid, shape["phrase"]["id"])
        used = 0
        for shape in shapes:
            used += shape["bars"]
            if used > section["bars"]:
                raise Refused("phrase_overflow", sid, shape["phrase"]["id"])
        plan.append((section, shapes))
    return plan


def _place(melody: dict, plan: list[tuple[dict, list[dict]]]):
    """Tempo and meter segments, notes and section repeats, placed from tick 0; returns them with the end tick."""
    meter0 = melody["tempo_map"]["meter"][0]
    first = next((shapes[0]["time"] for _, shapes in plan if shapes), None)
    time = first or (melody["tempo_map"]["tempo"][0]["us_per_quarter"], meter0["numerator"], meter0["denominator"])
    tempo, meter, notes, repeats, cursor = [], [], [], [], 0
    for section, shapes in plan:
        time = shapes[0]["time"] if shapes else time
        us, numerator, denominator = time
        if not tempo or tempo[-1]["us_per_quarter"] != us:
            tempo.append({"tick": cursor, "us_per_quarter": us})
        if not meter or (meter[-1]["numerator"], meter[-1]["denominator"]) != (numerator, denominator):
            meter.append({"tick": cursor, "numerator": numerator, "denominator": denominator})
        bar = bar_ticks(numerator, denominator)
        length = section["bars"] * bar
        offsets = [c["offset_ticks"] for c in section.get("chord_symbols", [])]
        if any(b <= a for a, b in zip(offsets, offsets[1:])) or any(o >= length for o in offsets):
            raise Refused("chord_symbol_misplaced", section["id"])
        for repeat in range(1, section["repeats"] + 1):
            slot, placed = cursor, []
            for shape in shapes:
                shift, phrase = slot - shape["anchor"], shape["phrase"]
                placed.append({"phrase_id": phrase["id"], "start_tick": phrase["start_tick"] + shift,
                               "end_tick": phrase["end_tick"] + shift})
                notes += [{"id": f"n{len(notes) + i}", "start_tick": n["start_tick"] + shift, "duration_ticks": n["duration_ticks"],
                           "pitch": n["pitch"], "velocity": n["velocity"], "confidence": None, "origin": "assembled"}
                          for i, n in enumerate(shape["notes"], 1)]
                slot += shape["bars"] * bar
            repeats.append({"section_id": section["id"], "name": section["name"], "section_kind": section["section_kind"],
                            "repeat": repeat, "start_tick": cursor, "end_tick": cursor + length, "phrases": placed})
            cursor += length
    return tempo, meter, notes, repeats, cursor


def _assemble(melody: dict, song: dict, output: dict) -> dict:
    tempo, meter, notes, repeats, end = _place(melody, _section_phrases(melody, song))
    source = melody["source"]
    record = {
        "kind": "melody-spec", "schemaVersion": SCHEMA_VERSION, "melody_id": output["melody_id"], "rev": output["rev"],
        "base_rev": output["base_rev"], "project_id": melody["project_id"], "created_at": output["created_at"],
        "spec_kind": "assembled", "ppq": PPQ, "tempo_map": {"rev": output["tempo_map_rev"], "tempo": tempo, "meter": meter},
        "key": copy.deepcopy(melody["key"]), "notes": notes, "phrases": [],
        "source": {"seed_kind": "assembled", "capture_sha256": source["capture_sha256"],
                   "transcription": copy.deepcopy(source["transcription"]),
                   "assembled_from": {"melody": copy.deepcopy(song["melody"]),
                                      "song": {"song_id": song["song_id"], "rev": song["rev"]}}},
        "quantize": copy.deepcopy(melody["quantize"]), "form": {"end_tick": end, "sections": repeats}, "content_sha256": ""}
    record["content_sha256"] = self_hash(record, "content_sha256")
    return record
