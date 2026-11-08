"""SongForm assembly hand-derived golden cases (T02c) and the public reference evaluator.

Inputs are hypothetical MelodySpec and SongSpec revisions. Every expected tick, tempo and meter segment, section repeat
and refusal is written out by hand below, with each case's derivation; nothing here calls the assembly under test.
content_sha256 is the canonical self-hash (ADR-0028) of the hand-written record. HYMN_* mirrors the fixture world's
hymn, so its scenarios can hold a 1.1.0 assembled record built from the same hand-derived values.
"""
import copy

from studio_ref import songform, timemodel
from studio_ref.canonical import self_hash
from studio_ref.fixture_support import SV, H

KIND = "fixture.songform"
V11, PRJ, AT, RATE = "1.1.0", "prj_case", "2026-11-07T12:00:00Z", 48000
OUT = {"melody_id": "mel_case_asm", "rev": 1, "base_rev": None, "tempo_map_rev": 1, "created_at": "2026-11-07T12:05:00Z"}
Q120, Q100 = 500000, 600000


def _hashed(doc):
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


def _tempo_map(rev, tempo, meter):
    return {"rev": rev, "tempo": [{"tick": t, "us_per_quarter": u} for t, u in tempo],
            "meter": [{"tick": t, "numerator": n, "denominator": d} for t, n, d in meter]}


def melody(notes, phrases, tempo=((0, Q120),), meter=((0, 4, 4),), transcription=None, quantize=None):
    """A source revision: notes are (start, duration, pitch, velocity), phrases (id, name, start, end)."""
    hum = transcription is not None
    return _hashed({
        "kind": "melody-spec", "schemaVersion": SV, "melody_id": "mel_case", "rev": 1, "base_rev": None, "project_id": PRJ,
        "created_at": AT, "spec_kind": "melody", "ppq": 960, "tempo_map": _tempo_map(1, tempo, meter),
        "key": {"tonic": "C", "mode": "major"},
        "notes": [{"id": f"n{i}", "start_tick": s, "duration_ticks": d, "pitch": p, "velocity": v,
                   "confidence": "0.80" if hum else None, "origin": "transcribed" if hum else "midi_file"}
                  for i, (s, d, p, v) in enumerate(notes, 1)],
        "phrases": [{"id": i, "name": n, "start_tick": s, "end_tick": e} for i, n, s, e in phrases],
        "source": {"seed_kind": "hum" if hum else "midi_file", "capture_sha256": H("songform-capture"),
                   "transcription": transcription, "assembled_from": None},
        "quantize": quantize, "content_sha256": ""})


def song(source, sections, version=SV):
    """sections are (id, name, section_kind, phrase_ids, bars, repeats), optionally followed by chord symbols."""
    def tracked(value):
        return {"requested": value, "support": [], "observed": []}
    keys = ("id", "name", "section_kind", "phrase_ids", "bars", "repeats", "chord_symbols")
    return _hashed({
        "kind": "song-spec", "schemaVersion": version, "song_id": "song_case", "rev": 1, "base_rev": None, "project_id": PRJ,
        "created_at": AT, "melody": {"melody_id": source["melody_id"], "rev": source["rev"], "tempo_map_rev": source["tempo_map"]["rev"]},
        "approved_lyrics": {"text": "[verse]\nLa la la", "language": "en", "source": "written", "approved_at": AT},
        "asr_transcripts": [], "controls": {"style": tracked("plain test song"), "exclude_styles": tracked([]),
                                            "vocal_mode": tracked("vocal"), "duration_s": tracked(60)},
        "form": {"sections": [dict(zip(keys, s)) for s in sections]}, "references": [], "candidate_count": 2,
        "larger_n_budget": None, "render_routes": {"mode": "auto", "routes": []},
        "validation": {"conflicts": [], "unsupported_by_profile": []}, "content_sha256": ""})


def assembled(source, song_doc, notes, tempo, meter, repeats, end, output=OUT):
    """The hand-derived result: literal notes, tempo, meter and repeats (section id, name, kind, repeat, start, end,
    [(phrase id, start, end)]); identity from output, lineage, key and quantize copied from the source as contracted."""
    src = source["source"]
    return _hashed({
        "kind": "melody-spec", "schemaVersion": V11, "melody_id": output["melody_id"], "rev": output["rev"],
        "base_rev": output["base_rev"], "project_id": source["project_id"], "created_at": output["created_at"],
        "spec_kind": "assembled", "ppq": 960, "tempo_map": _tempo_map(output["tempo_map_rev"], tempo, meter),
        "key": copy.deepcopy(source["key"]),
        "notes": [{"id": f"n{i}", "start_tick": s, "duration_ticks": d, "pitch": p, "velocity": v, "confidence": None,
                   "origin": "assembled"} for i, (s, d, p, v) in enumerate(notes, 1)],
        "phrases": [],
        "source": {"seed_kind": "assembled", "capture_sha256": src["capture_sha256"],
                   "transcription": copy.deepcopy(src["transcription"]),
                   "assembled_from": {"melody": copy.deepcopy(song_doc["melody"]),
                                      "song": {"song_id": song_doc["song_id"], "rev": song_doc["rev"]}}},
        "quantize": copy.deepcopy(source["quantize"]),
        "form": {"end_tick": end, "sections": [
            {"section_id": i, "name": n, "section_kind": k, "repeat": r, "start_tick": s, "end_tick": e,
             "phrases": [{"phrase_id": p, "start_tick": ps, "end_tick": pe} for p, ps, pe in placed]}
            for i, n, k, r, s, e, placed in repeats]},
        "content_sha256": ""})


HYMN_NOTES_IN = [(0, 960, 60, 90), (960, 960, 63, 90), (1920, 1920, 64, 90), (3840, 1920, 65, 90), (5760, 1920, 67, 90)]
HYMN_PHRASES = [("ph1", "opening line", 0, 3840), ("ph2", "answer line", 3840, 7680)]
HYMN_FORM = [("s1", "verse", "vocal", ["ph1"], 8, 1), ("s2", "chorus", "vocal", ["ph2"], 8, 2)]
HYMN_NOTES = [(0, 960, 60, 90), (960, 960, 63, 90), (1920, 1920, 64, 90), (30720, 1920, 65, 90), (32640, 1920, 67, 90),
              (61440, 1920, 65, 90), (63360, 1920, 67, 90)]
HYMN_REPEATS = [("s1", "verse", "vocal", 1, 0, 30720, [("ph1", 0, 3840)]),
                ("s2", "chorus", "vocal", 1, 30720, 61440, [("ph2", 30720, 34560)]),
                ("s2", "chorus", "vocal", 2, 61440, 92160, [("ph2", 61440, 65280)])]


def hymn_assembled(source, song_doc, output):
    """The world hymn's form over a revision with the hymn's notes, phrases and tempo map, derived by hand."""
    return assembled(source, song_doc, HYMN_NOTES, [(0, Q120), (30720, Q100)], [(0, 4, 4)], HYMN_REPEATS, 92160, output)


def _ok(name, why, melody_doc, song_doc, out, frame):
    return {"name": name, "derivation": why, "melody": melody_doc, "song": song_doc, "output": OUT, "sample_rate": RATE,
            "expected": {"assembled": out, "end_frame": frame}}


def _no(name, why, melody_doc, song_doc, code, section=None, phrase=None, note=None):
    return {"name": name, "derivation": why, "melody": melody_doc, "song": song_doc, "output": OUT, "sample_rate": RATE,
            "expected": {"refused": {"code": code, "section_id": section, "phrase_id": phrase, "note_id": note}}}


def _invalid(name, why, melody_doc, song_doc, code):
    return {"name": name, "derivation": why, "melody": melody_doc, "song": song_doc, "output": OUT, "sample_rate": RATE,
            "expected": {"invalid": code}}


def _instrumental(s):
    s["controls"]["vocal_mode"]["requested"] = "instrumental"
    s["approved_lyrics"] = None


def _shared():
    """ph1 ends mid-bar at 5760 and ph2 starts there: the two phrases share the source's second 4/4 bar."""
    return melody([(0, 1920, 60, 90), (1920, 1920, 62, 90), (3840, 1920, 64, 90), (5760, 1920, 65, 90)],
                  [("ph1", "long line", 0, 5760), ("ph2", "tag", 5760, 7680)])


def _changed(doc, change):
    doc = copy.deepcopy(doc)
    change(doc)
    return _hashed(doc)


def _section(index, **change):
    return lambda s: s["form"]["sections"][index].update(change)


PICK_FORM = [("s1", "intro", "instrumental", [], 1, 1), ("s2", "verse", "vocal", ["ph1", "ph2"], 4, 1),
             ("s3", "outro", "instrumental", [], 2, 1)]


def _pickup():
    """The intro, pickup and outro source, its SongSpec and its hand-derived result; the refusal cases change it."""
    pick = melody([(2880, 480, 67, 90), (3360, 480, 67, 80), (3840, 960, 69, 100), (4800, 960, 67, 90), (5760, 1920, 72, 90),
                   (7680, 1280, 71, 90), (8960, 1280, 69, 90), (10240, 1280, 67, 90)],
                  [("ph1", "pickup line", 2880, 7680), ("ph2", "triplet answer", 7680, 11520)])
    pick_song = song(pick, PICK_FORM)
    return pick, pick_song, assembled(
        pick, pick_song, [(6720, 480, 67, 90), (7200, 480, 67, 80), (7680, 960, 69, 100), (8640, 960, 67, 90),
                          (9600, 1920, 72, 90), (11520, 1280, 71, 90), (12800, 1280, 69, 90), (14080, 1280, 67, 90)],
        [(0, Q120)], [(0, 4, 4)],
        [("s1", "intro", "instrumental", 1, 0, 3840, []),
         ("s2", "verse", "vocal", 1, 3840, 19200, [("ph1", 6720, 11520), ("ph2", 11520, 15360)]),
         ("s3", "outro", "instrumental", 1, 19200, 26880, [])], 26880)


def _chords(pick, *marks):
    return song(pick, [PICK_FORM[0], PICK_FORM[1] + ([{"offset_ticks": o, "symbol": c} for o, c in marks],), PICK_FORM[2]], V11)


def _assembled_cases(profiles, pick, pick_song, pick_out):
    bp = profiles["transcribe-basic-pitch"]
    hymn = melody(HYMN_NOTES_IN, HYMN_PHRASES, tempo=((0, Q120), (3840, Q100)), transcription={
        "method": "basic-pitch", "profile_id": bp["id"], "job_id": "job_case_tr", "eligible_lanes": bp["allowed_lanes"],
        "license_chain": bp["license_record"], "note": "unverified on real hums"})
    hymn_song = song(hymn, HYMN_FORM)
    waltz = melody([(0, 1920, 60, 90), (1920, 1920, 64, 90), (3840, 960, 67, 90), (4800, 1920, 65, 90)],
                   [("ph1", "four", 0, 3840), ("ph2", "three", 3840, 6720)], tempo=((0, Q120), (3840, Q100)),
                   meter=((0, 4, 4), (3840, 3, 4)), quantize={"grid_ticks": 240})
    waltz_song = song(waltz, [("s1", "waltz", "vocal", ["ph2"], 2, 2), ("s2", "bridge", "instrumental", [], 1, 1),
                              ("s3", "march", "vocal", ["ph1"], 1, 1), ("s4", "outro", "instrumental", [], 1, 1)])
    waltz_out = assembled(waltz, waltz_song, [(0, 960, 67, 90), (960, 1920, 65, 90), (5760, 960, 67, 90), (6720, 1920, 65, 90),
                                              (14400, 1920, 60, 90), (16320, 1920, 64, 90)], [(0, Q100), (14400, Q120)],
                          [(0, 3, 4), (14400, 4, 4)],
                          [("s1", "waltz", "vocal", 1, 0, 5760, [("ph2", 0, 2880)]),
                           ("s1", "waltz", "vocal", 2, 5760, 11520, [("ph2", 5760, 8640)]),
                           ("s2", "bridge", "instrumental", 1, 11520, 14400, []),
                           ("s3", "march", "vocal", 1, 14400, 18240, [("ph1", 14400, 18240)]),
                           ("s4", "outro", "instrumental", 1, 18240, 22080, [])], 22080)
    journey = melody([(0, 1920, 60, 90), (1920, 1920, 62, 90), (3840, 960, 64, 90), (4800, 1920, 65, 90), (6720, 1440, 67, 90),
                      (8160, 1440, 69, 90)], [("ph1", "common", 0, 3840), ("ph2", "waltz", 3840, 6720), ("ph3", "jig", 6720, 9600)],
                     meter=((0, 4, 4), (3840, 3, 4), (6720, 6, 8)))
    journey_song = song(journey, [("s1", "intro", "instrumental", [], 1, 1), ("s2", "verse", "vocal", ["ph1"], 2, 1),
                                  ("s3", "waltz", "vocal", ["ph2"], 2, 1), ("s4", "jig", "vocal", ["ph3"], 1, 2),
                                  ("s5", "outro", "instrumental", [], 1, 1)])
    journey_out = assembled(journey, journey_song, [(3840, 1920, 60, 90), (5760, 1920, 62, 90), (11520, 960, 64, 90),
                                                    (12480, 1920, 65, 90), (17280, 1440, 67, 90), (18720, 1440, 69, 90),
                                                    (20160, 1440, 67, 90), (21600, 1440, 69, 90)],
                            [(0, Q120)], [(0, 4, 4), (11520, 3, 4), (17280, 6, 8)],
                            [("s1", "intro", "instrumental", 1, 0, 3840, []),
                             ("s2", "verse", "vocal", 1, 3840, 11520, [("ph1", 3840, 7680)]),
                             ("s3", "waltz", "vocal", 1, 11520, 17280, [("ph2", 11520, 14400)]),
                             ("s4", "jig", "vocal", 1, 17280, 20160, [("ph3", 17280, 20160)]),
                             ("s4", "jig", "vocal", 2, 20160, 23040, [("ph3", 20160, 23040)]),
                             ("s5", "outro", "instrumental", 1, 23040, 25920, [])], 25920)
    seed = melody([(0, 960, 60, 100), (960, 960, 62, 80)], [("ph1", "seed", 0, 3840)])
    seed_song = song(seed, [("s1", "intro", "instrumental", [], 1, 1), ("s2", "verse", "vocal", ["ph1"], 1, 2)])
    seed_out = assembled(seed, seed_song, [(3840, 960, 60, 100), (4800, 960, 62, 80), (7680, 960, 60, 100), (8640, 960, 62, 80)],
                         [(0, Q120)], [(0, 4, 4)],
                         [("s1", "intro", "instrumental", 1, 0, 3840, []), ("s2", "verse", "vocal", 1, 3840, 7680, [("ph1", 3840, 7680)]),
                          ("s2", "verse", "vocal", 2, 7680, 11520, [("ph1", 7680, 11520)])], 11520)
    shared = _shared()
    shared_song = song(shared, [("s1", "verse", "vocal", ["ph1", "ph2"], 3, 1)])
    shared_out = assembled(shared, shared_song, [(0, 1920, 60, 90), (1920, 1920, 62, 90), (3840, 1920, 64, 90), (9600, 1920, 65, 90)],
                           [(0, Q120)], [(0, 4, 4)], [("s1", "verse", "vocal", 1, 0, 11520, [("ph1", 0, 5760), ("ph2", 9600, 11520)])],
                           11520)
    bed_song = _changed(song(waltz, [("s1", "intro", "instrumental", [], 2, 1), ("s2", "outro", "instrumental", [], 1, 1)]),
                        _instrumental)
    bed_out = assembled(waltz, bed_song, [], [(0, Q120)], [(0, 4, 4)], [("s1", "intro", "instrumental", 1, 0, 7680, []),
                                                                        ("s2", "outro", "instrumental", 1, 7680, 11520, [])], 11520)
    return [
        _ok("world hymn: repeated chorus and a tempo change", "The 8-bar verse [0, 30720) places ph1 at its own ticks (1 bar, "
            "then 7 bars of rest). The chorus repeats twice, [30720, 61440) and [61440, 92160), placing ph2 (bar line 3840, "
            "100 BPM in the source) at +26880 and +57600, so the tempo changes at 30720. The Basic Pitch transcription "
            "(individual and research) and the capture are carried unchanged. 30720 ticks at 0.5 s per quarter = 16 s, "
            "plus 61440 at 0.6 s = 38.4 s; 54.4 s = 2611200 frames.", hymn, hymn_song,
            hymn_assembled(hymn, hymn_song, OUT), 2611200),
        _ok("intro, pickup, two phrases in one repeat, outro", "The intro is one empty 4/4 bar [0, 3840) at the verse's tempo. "
            "ph1 starts on beat 4 (2880), so it fills the bars from its bar line 0: ceil(7680 / 3840) = 2; ph2 fills 1. In "
            "the 4-bar verse [3840, 19200) both move by +3840: the pickup stays on beat 4 (6720), its downbeat lands on the "
            "bar line 7680, ph2's half-note triplet keeps its 1280-tick notes (11520, 12800, 14080) in bar 3 and bar 4 is "
            "rest. The 2-bar outro [19200, 26880) ends 11520 ticks after the last note. 26880 ticks = 28 quarters x 0.5 s "
            "= 14 s = 672000 frames.", pick, pick_song, pick_out, 672000),
        _ok("reordered phrases carry their meter and tempo", "ph2 (3/4, 100 BPM) plays first: its bar line is its start "
            "3840, so it moves by -3840 in repeat 1 [0, 5760) and by +1920 in repeat 2 [5760, 11520), each 2 bars of 2880 "
            "with the second bar rest. The bridge places no phrase and continues 3/4 at 100 BPM [11520, 14400). The march "
            "places ph1 at +14400, where tempo and meter change; the outro continues 4/4 at 120 [18240, 22080). Quantize "
            "240 is copied. 14400 ticks at 0.6 s per quarter = 9 s, plus 7680 at 0.5 s = 4 s: 624000 frames.",
            waltz, waltz_song, waltz_out, 624000),
        _ok("sections change meter: 4/4, 3/4, 6/8", "The intro takes the verse's 4/4 [0, 3840). The 2-bar verse [3840, 11520) "
            "places ph1 at +3840; the 2-bar 3/4 waltz (2880-tick bars) [11520, 17280) places ph2 (bar line 3840) at +7680; "
            "the 6/8 jig (six 480-tick beats, 2880-tick bars) repeats [17280, 20160) and [20160, 23040), placing ph3 (bar "
            "line 6720) at +10560 and +13440; the outro continues 6/8 [23040, 25920). Meter segments start at 11520 and "
            "17280, the map fixture.meter walks. 25920 ticks at 0.5 s per quarter = 13.5 s = 648000 frames.",
            journey, journey_song, journey_out, 648000),
        _ok("chord symbols leave the assembled melody unchanged", "song-spec 1.1.0 chord symbols at 0, 3840, 7680 and 11520 "
            "increase and lie inside the verse's 15360-tick repeat. Assembly reads, but does not copy, them (ABC emission "
            "reads them from the SongSpec by section id), so the result is the pickup case's.",
            pick, _chords(pick, (0, "G"), (3840, "C"), (7680, "D7"), (11520, "G/B")), pick_out, 672000),
        _ok("preparation case: one instrumental bar, then a phrase twice", "The T02 preparation note's first case: ph1 "
            "[0, 3840) with notes at 0 and 960. The 1-bar intro [0, 3840) is empty; the 1-bar verse repeats at [3840, 7680) "
            "and [7680, 11520), so the note pairs start at 3840/4800 and 7680/8640, and the form reaches 11520 although "
            "its last note ends at 9600. 12 quarters x 0.5 s = 6 s = 288000 frames.", seed, seed_song, seed_out, 288000),
        _ok("two phrases that share a source bar take separate bars", "ph1 [0, 5760) touches 2 bars: ceil(5760 / 3840) "
            "= 2, slots 1-2. ph2 [5760, 7680) starts in the source's second bar, so its bar line is 3840 and it fills 1 "
            "bar; in the 3-bar verse it takes slot 3 [7680, 11520) and moves by 7680 - 3840 = +3840, so its note lands at "
            "9600, not 5760. 11520 ticks = 6 s = 288000 frames.", shared, shared_song, shared_out, 288000),
        _ok("a form with no phrase takes the source's tick-0 tempo and meter", "No section places a phrase (an "
            "instrumental SongSpec), so every section takes the source's tick-0 values, 4/4 at 120 BPM, and not its "
            "later 3/4 at 100 BPM: a 2-bar intro [0, 7680) and a 1-bar outro [7680, 11520), with no notes. 288000 frames.",
            waltz, bed_song, bed_out, 288000),
    ]


def _refused_cases(pick, pick_song, pick_out):
    def crossing(m):
        m["notes"][4]["duration_ticks"] = 2880

    def tempo(change_at):
        return lambda m: m["tempo_map"].update(tempo=[{"tick": 0, "us_per_quarter": Q120},
                                                      {"tick": change_at, "us_per_quarter": Q100}])

    def meter(change_at):
        return lambda m: m["tempo_map"].update(meter=[{"tick": 0, "numerator": 4, "denominator": 4},
                                                      {"tick": change_at, "numerator": 2, "denominator": 4}])
    shared = _shared()
    solo = song(shared, [("s1", "verse", "vocal", ["ph1"], 2, 1)])
    return [
        _no("source already assembled", "Assembly lays out a source melody; an assembled one is never re-assembled.",
            pick_out, pick_song, "source_not_melody"),
        _no("SongSpec names another revision", "The SongSpec places mel_case rev 2; the source is rev 1.", pick,
            _changed(pick_song, lambda s: s["melody"].update(rev=2)), "song_melody_mismatch"),
        _no("SongSpec from another project", "The SongSpec lives in prj_other; the source in prj_case.", pick,
            _changed(pick_song, lambda s: s.update(project_id="prj_other")), "song_melody_mismatch"),
        _no("duplicate section id", "Two sections are s2; neither is chosen.", pick, _changed(pick_song, _section(2, id="s2")),
            "duplicate_section", "s2"),
        _no("duplicate phrase id", "The source marks ph2 twice; the first match is never picked.",
            _changed(pick, lambda m: m["phrases"].append({"id": "ph2", "name": "second answer", "start_tick": 11520,
                                                          "end_tick": 15360})),
            pick_song, "duplicate_phrase", None, "ph2"),
        _no("instrumental section places a phrase", "The intro is instrumental but places ph2.", pick,
            _changed(pick_song, _section(0, phrase_ids=["ph2"])), "section_kind_mismatch", "s1"),
        _no("vocal section places none", "The outro is marked vocal but places no phrase.", pick,
            _changed(pick_song, _section(2, section_kind="vocal")), "section_kind_mismatch", "s3"),
        _no("missing phrase", "The verse places ph9, which the source does not mark.", pick,
            _changed(pick_song, _section(1, phrase_ids=["ph1", "ph9"])), "missing_phrase", "s2", "ph9"),
        _no("zero-length phrase", "ph2 starts and ends at 7680.", _changed(pick, lambda m: m["phrases"][1].update(end_tick=7680)),
            pick_song, "empty_phrase", "s2", "ph2"),
        _no("tempo change inside a phrase", "The source tempo changes at 4800, inside ph1's bars [0, 7680).",
            _changed(pick, tempo(4800)), pick_song, "tempo_conflict", "s2", "ph1"),
        _no("phrases of one section disagree on tempo", "The tempo changes at 7680, ph2's bar line: ph1 is 120 BPM and ph2 "
            "100 BPM in the one verse.", _changed(pick, tempo(7680)), pick_song, "tempo_conflict", "s2", "ph2"),
        _no("meter change inside a phrase", "The source turns 2/4 at the bar line 3840, inside ph1's bars [0, 7680).",
            _changed(pick, meter(3840)), pick_song, "meter_conflict", "s2", "ph1"),
        _no("phrases of one section disagree on meter", "The source turns 2/4 at 7680: ph1 is 4/4 and ph2 2/4 in the one verse.",
            _changed(pick, meter(7680)), pick_song, "meter_conflict", "s2", "ph2"),
        _no("note crosses a phrase end", "n5 [5760, 8640) runs past ph1's end 7680; it is never truncated.",
            _changed(pick, crossing), pick_song, "note_crosses_phrase_edge", "s2", "ph1", "n5"),
        _no("note crosses a phrase start", "With only ph2 placed, n5 [5760, 8640) starts before ph2's start 7680.",
            _changed(pick, crossing), _changed(pick_song, _section(1, phrase_ids=["ph2"])), "note_crosses_phrase_edge",
            "s2", "ph2", "n5"),
        _no("phrases overflow their bars", "ph1 needs 2 bars and ph2 1: 3 bars in a 2-bar verse; nothing is truncated.",
            pick, _changed(pick_song, _section(1, bars=2)), "phrase_overflow", "s2", "ph2"),
        _no("chord symbol beyond its repeat", "The verse repeat is 4 x 3840 = 15360 ticks; a chord at 15360 lies outside it.",
            pick, _chords(pick, (0, "G"), (15360, "D7")), "chord_symbol_misplaced", "s2"),
        _no("chord symbols out of order", "Offsets 3840 then 0 do not increase.", pick, _chords(pick, (3840, "C"), (0, "G")),
            "chord_symbol_misplaced", "s2"),
        _no("tempo change after a phrase's last note, inside its last bar", "ph1 [0, 5760) occupies the bars [0, 7680); "
            "the tempo changes at 6720, after its last note ends at 5760 but inside its last bar, so the bars it occupies "
            "have no single tempo. Dropping the change would retime that bar.", _changed(shared, tempo(6720)), solo,
            "tempo_conflict", "s1", "ph1"),
        _no("tempo change where a phrase ends mid-bar", "The tempo changes at 5760, exactly where ph1 ends and inside "
            "its last bar [3840, 7680).", _changed(shared, tempo(5760)), solo, "tempo_conflict", "s1", "ph1"),
        _invalid("meter change after a phrase's last note, inside its last bar", "The source turns 2/4 at 6720, inside "
                 "ph1's last 4/4 bar after its last note. A meter changes only on a bar line (melody.wellformed), so the "
                 "time model cannot measure the source and raises before any section is placed.",
                 _changed(shared, meter(6720)), solo, "meter_change_inside_bar"),
        _invalid("tempo map not from tick 0", "The source's first tempo segment starts at 960 (melody.wellformed).",
                 _changed(pick, lambda m: m["tempo_map"].update(tempo=[{"tick": 960, "us_per_quarter": Q120}])), pick_song,
                 "tempo_segments_invalid"),
        _invalid("meter segments not increasing", "Two meter segments start at tick 0 (melody.wellformed).",
                 _changed(pick, lambda m: m["tempo_map"].update(meter=[{"tick": 0, "numerator": 4, "denominator": 4},
                                                                       {"tick": 0, "numerator": 3, "denominator": 4}])),
                 pick_song, "meter_segments_invalid"),
    ]


def build(profiles):
    pickup = _pickup()
    return {"kind": KIND, "schemaVersion": SV, "cases": _assembled_cases(profiles, *pickup) + _refused_cases(*pickup)}


def evaluate(case, world):
    try:
        got = songform.assemble(case["melody"], case["song"], case["output"])
    except timemodel.TimeModelError as error:
        return {"invalid": error.code}, case["expected"]
    if "assembled" in got:
        record = got["assembled"]
        got = {"assembled": record, "end_frame": timemodel.ticks_to_frames(
            record["form"]["end_tick"], record["tempo_map"]["tempo"], case["sample_rate"])}
    return got, case["expected"]
