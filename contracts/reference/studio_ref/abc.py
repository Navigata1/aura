"""MelodySpec to YuE2 ABC emission (ADR-0004; RECONCILIATION D-04, GAP-02): the reference for Score.to_abc.

to_abc(melody, song, cot=None) writes an assembled melody-spec 1.1 record, with the SongSpec revision it was assembled
from, as YuE2's native two-voice ABC. It returns {"abc": {text, cot, lyrics, syllable_plan}} or {"ineligible":
{"reasons": [...]}}; an input outside the contract raises AbcInputError. The grammar is the bounded native dialect that
skills/yue2-music/scripts/abc_tools.py parses at YuE commit 1647252d68b70cbead046ffd3f7caf036dde47ee (git blob 88b66e5,
byte-identical at yue2-music-v1.2.0). Pure, deterministic and integer-only at 960 PPQ: every note start and end is
re-quantized to the 1/32 grid by the one rounding function (ADR-0033), and nothing is truncated, retimed or respelled
without a typed reason. Rules, scan order and codes: contracts/README.md, "YuE2 ABC emission (T02e)".
"""

from __future__ import annotations

from fractions import Fraction
import re

from .timemodel import PPQ, bar_segments, bar_ticks, round_half_up, seconds_at_tick

UNIT = PPQ // 8  # one 1/32 note, the L:1/32 unit: 120 ticks
MAX_SECONDS = 360  # "about 6 minutes" (ADR-0004; the abc-emission ticket) as exact seconds
US_PER_MINUTE = 60_000_000
LANGUAGES = ("en", "zh")
PIECES = (48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1)  # the dialect's duration multipliers, largest first
LETTERS = "CDEFGAB"
NATURAL = dict(zip(LETTERS, (0, 2, 4, 5, 7, 9, 11)))
SIGNS = {-1: "_", 0: "=", 1: "^", 2: "^^"}  # a double sharp only for G#, D# and A# minor's raised seventh
MAJOR = ("Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#")  # 7 flats to 7 sharps
MINOR = ("Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#")
ROOT = "[A-G](?:bb|##|b|#)?"
QUALITIES = ("", "m", "dim", "aug", "7", "maj7", "m7", "dim7", "m7b5", "sus4", "sus2", "6", "m6", "7sus4", "m(maj7)")
CHORD = re.compile(f"{ROOT}(?:{'|'.join(map(re.escape, QUALITIES))})(?:/{ROOT})?")
HAN = "\u3400-\u4dbf\u4e00-\u9fff"  # CJK Extension A and Unified Ideographs
SYLLABLE = re.compile(f"[{HAN}]|(?:(?![{HAN}])[\\w'\u2019])+")
TAG = re.compile(r"\s*\[([^\[\]]+)\]\s*")
VOICES = ('V: Vocal clef=treble name="Vocal Melody" snm="Vocal"', 'V: Ins clef=treble name="Ins Melody" snm="Inst."')


class AbcInputError(ValueError):
    """An input outside the contract; code names it. A tempo or meter map the time model cannot measure raises its own
    TimeModelError, as for assembly."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def to_abc(melody: dict, song: dict, cot: str | None = None) -> dict:
    """cot None takes 'full' when any section carries chord symbols, else 'melody'."""
    form, bars = _checked(melody, song)
    chords = {s["id"]: s.get("chord_symbols", []) for s in song["form"]["sections"]}
    if cot is None:
        cot = "full" if any(chords.values()) else "melody"
    elif cot not in ("melody", "full"):
        raise ValueError("cot must be melody or full")
    notes = sorted(melody["notes"], key=lambda n: (n["start_tick"], n["pitch"]))
    lyrics = song["approved_lyrics"]
    bound, unbound_at = _bind(lyrics["text"], form) if lyrics else (None, None)
    reasons = _reasons(melody, form, notes, chords if cot == "full" else None, lyrics, bound, unbound_at)
    if reasons:
        return {"ineligible": {"reasons": reasons}}
    onsets = {} if cot == "melody" else {r["start_tick"] + c["offset_ticks"]: c["symbol"]
                                         for r in form["sections"] for c in chords[r["section_id"]]}
    return {"abc": {"text": _text(melody, form, bars, notes, onsets), "cot": cot,
                    "lyrics": "\n\n".join("\n".join([f"[{r['name']}]", *bound.get(r["section_id"], [])])
                                          for r in form["sections"]),
                    "syllable_plan": _plan(form, notes, bound)}}


def _checked(melody, song):
    """The form and its bars (start, ticks, meter), after the input checks, in their scan order."""
    if melody["spec_kind"] != "assembled":
        raise AbcInputError("melody_not_assembled")
    form = melody.get("form")
    if form is None:
        raise AbcInputError("form_missing")
    if not _assembled_from(melody, song, form):
        raise AbcInputError("song_mismatch")
    segments, bars, tick = bar_segments(melody["tempo_map"]["meter"]), [], 0
    while tick < form["end_tick"]:
        _, _, numerator, denominator = [s for s in segments if s[0] <= tick][-1]
        bars.append((tick, bar_ticks(numerator, denominator), f"{numerator}/{denominator}"))
        tick += bar_ticks(numerator, denominator)
    if tick != form["end_tick"] or not _tiles(melody, song, form, bars):
        raise AbcInputError("form_inconsistent")
    return form, bars


def _assembled_from(melody, song, form):
    """The SongSpec is the revision this form was assembled from: same identity and project, the same sections and
    repeats, and chord symbols that assembly accepts (strictly increasing, inside one repeat)."""
    sections = song["form"]["sections"]
    lengths = {r["section_id"]: r["end_tick"] - r["start_tick"] for r in form["sections"]}
    offsets = [[c["offset_ticks"] for c in s.get("chord_symbols", [])] for s in sections]
    return (melody["source"]["assembled_from"]["song"] == {"song_id": song["song_id"], "rev": song["rev"]}
            and song["project_id"] == melody["project_id"]
            and [(r["section_id"], r["name"], r["section_kind"], r["repeat"]) for r in form["sections"]]
            == [(s["id"], s["name"], s["section_kind"], r) for s in sections for r in range(1, s["repeats"] + 1)]
            and all(a < b for o in offsets for a, b in zip(o, o[1:]))
            and all(x < lengths[s["id"]] for s, o in zip(sections, offsets) for x in o))


def _tiles(melody, song, form, bars):
    """The repeats tile [0, end_tick) on bar lines, each with its section's bars, and every note lies inside."""
    end = form["end_tick"]
    lines = {bar[0] for bar in bars} | {end}
    edges = [(r["start_tick"], r["end_tick"]) for r in form["sections"]]
    return (edges[0][0] == 0 and edges[-1][1] == end and all(a[1] == b[0] for a, b in zip(edges, edges[1:]))
            and all(start < stop and start in lines and stop in lines for start, stop in edges)
            and [sum(start <= bar[0] < stop for bar in bars) for start, stop in edges]
            == [s["bars"] for s in song["form"]["sections"] for _ in range(s["repeats"])]
            and all(n["start_tick"] + n["duration_ticks"] <= end for n in melody["notes"]))


def _bind(text, form):
    """Lyric lines per vocal section id, or None with the first unbound vocal section's tick (None: a block left over).
    A line that is only [tag] starts a block; blocks without a syllable bind nothing."""
    blocks = []
    for line in text.splitlines():
        tag = TAG.fullmatch(line)
        if tag:
            blocks.append((re.sub(r"\s+", "-", tag.group(1).strip().lower()), []))
        elif line.strip():
            if not blocks:
                blocks.append((None, []))
            blocks[-1][1].append(line.strip())
    blocks = [b for b in blocks if any(SYLLABLE.findall(line) for line in b[1])]
    firsts = [r for r in form["sections"] if r["section_kind"] == "vocal" and r["repeat"] == 1]
    for i, repeat in enumerate(firsts):
        if i >= len(blocks) or blocks[i][0] != repeat["name"]:
            return None, repeat["start_tick"]
    if len(blocks) > len(firsts):
        return None, None
    return {r["section_id"]: blocks[i][1] for i, r in enumerate(firsts)}, None


def _reasons(melody, form, notes, chords, lyrics, bound, unbound_at):
    """Every reason the dialect cannot hold, each code once at its first occurrence, in scan order (chords is None
    under cot='melody', whose chord symbols are never read)."""
    found, tempo = {}, melody["tempo_map"]["tempo"]

    def add(code, tick=None, note=None):
        section = None if tick is None else [r for r in form["sections"] if r["start_tick"] <= tick][-1]["section_id"]
        found.setdefault(code, {"code": code, "section_id": section, "note_id": note, "tick": tick})
    if lyrics is None:
        add("lyrics_missing")
    elif lyrics["language"].split("-")[0] not in LANGUAGES:
        add("lyrics_language")
    if lyrics is not None and bound is None:
        add("lyrics_unbound", unbound_at)
    if seconds_at_tick(form["end_tick"], tempo) > MAX_SECONDS:
        add("length_over_limit")
    if len(tempo) > 1:
        add("tempo_change", tempo[1]["tick"])
    for segment in tempo:
        if US_PER_MINUTE % segment["us_per_quarter"]:
            add("tempo_not_integer_bpm", segment["tick"])
    if _key(melody["key"]) is None:
        add("key_unrepresentable")
    if chords is not None:
        placed = [(r["start_tick"] + c["offset_ticks"], c["symbol"]) for r in form["sections"] for c in chords[r["section_id"]]]
        if not placed:
            add("chords_missing")
        for tick, symbol in placed:
            if not CHORD.fullmatch(symbol):
                add("chord_unrepresentable", tick)
        for tick, _ in placed:
            if tick % UNIT:
                add("chord_off_grid", tick)
    for a, b in zip(notes, notes[1:]):
        if b["start_tick"] < a["start_tick"] + a["duration_ticks"]:
            add("notes_overlap", b["start_tick"], b["id"])
    for note in notes:
        if _q(note["start_tick"]) == _q(note["start_tick"] + note["duration_ticks"]):
            add("note_requantize_collapse", note["start_tick"], note["id"])
    return list(found.values())


def _q(tick):
    """The one re-quantization: the nearest 1/32-note grid line, half up (timemodel.round_half_up)."""
    return round_half_up(Fraction(tick, UNIT)) * UNIT


def _key(key):
    """The K: field, the key signature by letter and the spelling candidates in rank order, or None when the native
    table lacks the key (a modal key, or a spelling such as D# major)."""
    table = {"major": MAJOR, "minor": MINOR}.get(key["mode"], ())
    if key["tonic"] not in table:
        return None
    fifths = table.index(key["tonic"]) - 7
    altered = ("FCGDAEB" if fifths > 0 else "BEADGCF")[:abs(fifths)]
    signature = {letter: (1 if fifths > 0 else -1) if letter in altered else 0 for letter in LETTERS}
    ranked = list(signature.items())  # the key's own letter
    if key["mode"] == "minor":  # a minor key's raised seventh: its seventh degree's letter, one semitone up
        seventh = LETTERS[(LETTERS.index(key["tonic"][0]) + 6) % 7]
        ranked.append((seventh, signature[seventh] + 1))
    ranked += [(letter, 0) for letter in LETTERS]  # a natural sign on a letter the key alters
    ranked += [(letter, 1 if fifths >= 0 else -1) for letter in LETTERS]  # sharp keys (and C, Am) sharpen, flat keys flatten
    return key["tonic"] + ("m" if key["mode"] == "minor" else ""), signature, ranked


def _spell(pitch, ranked):
    """The first candidate that sounds the pitch: its letter, alteration and note name with its octave marks."""
    letter, alteration = next((l, a) for l, a in ranked if (NATURAL[l] + a) % 12 == pitch % 12)
    octave = (pitch - alteration - 60 - NATURAL[letter]) // 12
    return letter, alteration, letter + "," * -octave if octave <= 0 else letter.lower() + "'" * (octave - 1)


def _pieces(units):
    """A length in units as the dialect's multipliers, largest first; 1 is written without a number."""
    out = []
    while units:
        piece = next(p for p in PIECES if p <= units)
        out.append("" if piece == 1 else str(piece))
        units -= piece
    return out


def _bar(start, ticks, spans, onsets, signature, ranked):
    """One bar of the Vocal voice, or None for a whole-bar rest (no note and no chord onset in it). Notes and rests split
    at the bar lines and chord onsets; an accidental is written when the bar's state for its letter differs, and a tied
    continuation repeats its letter without one (abc_tools.py: accidentals hold by letter, across octaves, to the bar)."""
    end = start + ticks
    held = [s for s in spans if s[0] < end and s[1] > start]
    marks = {t: c for t, c in onsets.items() if start <= t < end}
    if not held and not marks:
        return None
    cuts = sorted({start, end, *marks, *(t for a, b, _ in held for t in (a, b) if start < t < end)})
    out, local = [], {}
    for a, b in zip(cuts, cuts[1:]):
        chord = f'"{marks[a]}"' if a in marks else ""
        span = next((s for s in held if s[0] <= a < s[1]), None)
        if span is None:
            out.append(chord + "".join(f"z{p}" for p in _pieces((b - a) // UNIT)))
            continue
        letter, alteration, name = _spell(span[2], ranked)
        sign = ""
        if a == span[0] and local.get(letter, signature[letter]) != alteration:
            sign, local[letter] = SIGNS[alteration], alteration
        out.append(chord + sign + "-".join(name + p for p in _pieces((b - a) // UNIT)) + ("-" if b < span[1] else ""))
    return "".join(out)


def _groups(bars):
    """Bars in groups of at most four, with a new group at every meter change."""
    groups = []
    for bar in bars:
        if groups and len(groups[-1]) < 4 and groups[-1][-1][2] == bar[2]:
            groups[-1].append(bar)
        else:
            groups.append([bar])
    return groups


def _line(bodies):
    """One music line: bars joined by bar lines, each run of whole-bar rests written Z, Z2, Z3 or Z4."""
    out, rests = [], 0
    for body in [*bodies, ""]:
        if body is None:
            rests += 1
            continue
        if rests:
            out.append("Z" if rests == 1 else f"Z{rests}")
            rests = 0
        if body:
            out.append(body)
    return "|".join(out) + "|"


def _text(melody, form, bars, notes, onsets):
    """The fixed header, then per section repeat a % comment and its groups: V: Vocal, then V: Ins (whole-bar rests),
    each with M: when the group's meter changes."""
    field, signature, ranked = _key(melody["key"])
    spans = [(_q(n["start_tick"]), _q(n["start_tick"] + n["duration_ticks"]), n["pitch"]) for n in notes]
    vocal = {start: _bar(start, ticks, spans, onsets, signature, ranked) for start, ticks, _ in bars}
    meter, bpm = bars[0][2], US_PER_MINUTE // melody["tempo_map"]["tempo"][0]["us_per_quarter"]
    lines = ["X:1", "T:", f"M:{meter}", "L:1/32", f"Q:1/4={bpm}", *VOICES, f"K:{field}"]
    for repeat in form["sections"]:
        lines.append(f"% {repeat['name']}")
        for group in _groups([b for b in bars if repeat["start_tick"] <= b[0] < repeat["end_tick"]]):
            change = [f"M:{group[0][2]}"] if group[0][2] != meter else []
            meter = group[0][2]
            lines += ["V: Vocal", *change, _line([vocal[b[0]] for b in group]), "V: Ins", *change, _line([None] * len(group))]
    return "\n".join(lines) + "\n"


def _plan(form, notes, bound):
    """In each vocal repeat, its block's syllables take its notes in onset order, one each, with the re-quantized
    ticks; a note or syllable left without a partner keeps its row, so nothing is dropped."""
    plan = []
    for repeat in form["sections"]:
        if repeat["section_kind"] != "vocal":
            continue
        syllables = [(i, s) for i, line in enumerate(bound[repeat["section_id"]], 1) for s in SYLLABLE.findall(line)]
        mine = [n for n in notes if repeat["start_tick"] <= n["start_tick"] < repeat["end_tick"]]
        for k in range(max(len(syllables), len(mine))):
            line, syllable = syllables[k] if k < len(syllables) else (None, None)
            note = mine[k] if k < len(mine) else None
            plan.append({"section_id": repeat["section_id"], "repeat": repeat["repeat"], "line": line, "syllable": syllable,
                         "note_id": note and note["id"], "pitch": note and note["pitch"],
                         "start_tick": note and _q(note["start_tick"]),
                         "end_tick": note and _q(note["start_tick"] + note["duration_ticks"])})
    return plan
