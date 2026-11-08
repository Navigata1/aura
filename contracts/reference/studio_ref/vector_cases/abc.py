"""YuE2 ABC emission hand-derived golden cases (T02e) and the public reference evaluator.

Inputs are hypothetical assembled MelodySpec revisions and the SongSpec revisions they were assembled from, built with
the SongForm cases' helpers; the pickup case's source, SongSpec and assembled record, and the hymn's, are reused as they
are. Every expected ABC line, lyrics string, syllable-plan row and reason is written out by hand below, with each case's
derivation; nothing here calls the emitter under test. The grammar is abc_tools.py's at YuE commit 1647252d
(contracts/README.md, "YuE2 ABC emission"). L:1/32 is 120 ticks, so a 4/4 bar is 32 units.
"""
import copy

from studio_ref import abc
from studio_ref.canonical import self_hash
from studio_ref.fixture_support import SV
from studio_ref.vector_cases import songform as sf

KIND = "fixture.abc"
Q120, Q60 = 500000, 1000000
VOICES = 'V: Vocal clef=treble name="Vocal Melody" snm="Vocal"\nV: Ins clef=treble name="Ins Melody" snm="Inst."\n'


def _changed(doc, change):
    doc = copy.deepcopy(doc)
    change(doc)
    doc["content_sha256"] = self_hash(doc, "content_sha256")
    return doc


def _lyrics(song_doc, text, language="en"):
    return _changed(song_doc, lambda s: s["approved_lyrics"].update(text=text, language=language))


def _text(meter, bpm, key, body):
    """The fixed native header written out (X:1, a blank T:, M:, L:1/32, Q:, both voices, K:), then the groups."""
    return f"X:1\nT:\nM:{meter}\nL:1/32\nQ:1/4={bpm}\n{VOICES}K:{key}\n{body}"


def _plan(section, *rows):
    """Plan rows of repeat 1: (line, syllable, (note id, pitch, start, end) or None); line and syllable None on a note
    no syllable reaches."""
    return [{"section_id": section, "repeat": 1, "line": line, "syllable": text, "note_id": note and note[0],
             "pitch": note and note[1], "start_tick": note and note[2], "end_tick": note and note[3]}
            for line, text, note in rows]


def _why(code, section=None, note=None, tick=None):
    return {"code": code, "section_id": section, "note_id": note, "tick": tick}


def _ok(name, why, melody, song_doc, cot, text, used, lyrics, plan):
    return {"name": name, "derivation": why, "melody": melody, "song": song_doc, "cot": cot,
            "expected": {"abc": {"text": text, "cot": used, "lyrics": lyrics, "syllable_plan": plan}}}


def _no(name, why, melody, song_doc, *reasons, cot=None):
    return {"name": name, "derivation": why, "melody": melody, "song": song_doc, "cot": cot,
            "expected": {"ineligible": {"reasons": list(reasons)}}}


def _invalid(name, why, melody, song_doc, code):
    return {"name": name, "derivation": why, "melody": melody, "song": song_doc, "cot": None, "expected": {"invalid": code}}


def _line(notes, key, lyric, bars, name="verse"):
    """One vocal section over one phrase from tick 0, 4/4 at 120 BPM: assembled, the notes stay in place."""
    src = _changed(sf.melody(notes, [("ph1", "line", 0, bars * 3840)]), lambda m: m["key"].update(key))
    song_doc = _lyrics(sf.song(src, [("s1", name, "vocal", ["ph1"], bars, 1)]), lyric)
    return sf.assembled(src, song_doc, notes, [(0, Q120)], [(0, 4, 4)],
                        [("s1", name, "vocal", 1, 0, bars * 3840, [("ph1", 0, bars * 3840)])], bars * 3840), song_doc


def _long(us, outro):
    """A one-bar verse (a C4 whole note) and an instrumental outro of the given bars, 4/4 at one tempo. The lyrics end
    with a placeholder [outro] tag, a block with no syllable, which binds nothing."""
    src = sf.melody([(0, 3840, 60, 90)], [("ph1", "long", 0, 3840)], tempo=((0, us),))
    song_doc = _lyrics(sf.song(src, [("s1", "verse", "vocal", ["ph1"], 1, 1), ("s2", "outro", "instrumental", [], outro, 1)]),
                       "[verse]\nLa la\n[outro]")
    end = (1 + outro) * 3840
    return sf.assembled(src, song_doc, [(0, 3840, 60, 90)], [(0, us)], [(0, 4, 4)],
                        [("s1", "verse", "vocal", 1, 0, 3840, [("ph1", 0, 3840)]),
                         ("s2", "outro", "instrumental", 1, 3840, end, [])], end), song_doc


PICK_BODY = ("% intro\nV: Vocal\nZ|\nV: Ins\nZ|\n"
             "% verse\nV: Vocal\nz24G4G4|A8G8c16|B8-B3A8-A2G8-G3|Z|\nV: Ins\nZ4|\n"
             "% outro\nV: Vocal\nZ2|\nV: Ins\nZ2|\n")
CHORD_BODY = ("% intro\nV: Vocal\nZ|\nV: Ins\nZ|\n"
              '% verse\nV: Vocal\n"G"z16"Em"z8G4G4|"C"A8G8c8-"Am"c8|"D7"B8-B3A8-A2G8-G3|"G/B"z32|\nV: Ins\nZ4|\n'
              "% outro\nV: Vocal\nZ2|\nV: Ins\nZ2|\n")
PICK_LYRICS = "[intro]\n\n[verse]\nLa la la\n\n[outro]"
PICK_PLAN = _plan("s2", (1, "La", ("n1", 67, 6720, 7200)), (1, "la", ("n2", 67, 7200, 7680)), (1, "la", ("n3", 69, 7680, 8640)),
                  (None, None, ("n4", 67, 8640, 9600)), (None, None, ("n5", 72, 9600, 11520)),
                  (None, None, ("n6", 71, 11520, 12840)), (None, None, ("n7", 69, 12840, 14040)),
                  (None, None, ("n8", 67, 14040, 15360)))


def _eligible(pick, pick_song, pick_out):
    chords = sf._chords(pick, (0, "G"), (1920, "Em"), (3840, "C"), (6720, "Am"), (7680, "D7"), (11520, "G/B"))
    zh_src = sf.melody([(0, 1920, 60, 90), (1920, 1920, 62, 90), (3840, 960, 64, 90), (4800, 1920, 65, 90)],
                       [("ph1", "four", 0, 3840), ("ph2", "three", 3840, 6720)], meter=((0, 4, 4), (3840, 3, 4)))
    zh_song = _lyrics(sf.song(zh_src, [("s1", "verse", "vocal", ["ph1"], 1, 1), ("s2", "waltz", "vocal", ["ph2"], 1, 1)]),
                      "[verse]\n春\n风\n[waltz]\n吹过", "zh-Hans")
    zh_out = sf.assembled(zh_src, zh_song, [(0, 1920, 60, 90), (1920, 1920, 62, 90), (3840, 960, 64, 90), (4800, 1920, 65, 90)],
                          [(0, Q120)], [(0, 4, 4), (3840, 3, 4)],
                          [("s1", "verse", "vocal", 1, 0, 3840, [("ph1", 0, 3840)]),
                           ("s2", "waltz", "vocal", 1, 3840, 6720, [("ph2", 3840, 6720)])], 6720)
    d_major = _line([(0, 480, 66, 90), (480, 480, 65, 90), (960, 480, 77, 90), (1440, 480, 78, 90), (1920, 960, 73, 90),
                     (2880, 1920, 68, 90), (4800, 960, 67, 90), (5760, 1920, 60, 90)], {"tonic": "D", "mode": "major"},
                    "[Verse 1]\nLa la la la la la la la", 2, "verse-1")
    g_minor = _line([(0, 1080, 67, 90), (1080, 840, 66, 90), (1920, 960, 51, 90), (2880, 960, 85, 90)],
                    {"tonic": "G", "mode": "minor"}, "[verse]\nLa la la la", 1)
    g_sharp_minor = _line([(0, 960, 68, 90), (960, 960, 67, 90), (2520, 1320, 68, 90)], {"tonic": "G#", "mode": "minor"},
                          "[verse]\nLa la la", 1)
    return [
        _ok("pickup, half-note triplet, intro and outro", "120 BPM (500000 us) is Q:1/4=120. The intro bar, the last verse "
            "bar and both outro bars are whole-bar rests: Z, and Z2 for the outro group. Verse bar 1 [3840, 7680): 24 units of "
            "rest pad the pickup (6720 = 3840 + 24 x 120), then two G4 eighths, G4. Bar 2: A8 G8 and the C5 half note, c16. Bar "
            "3 holds the half-note triplet [11520, 15360): its inner edges 12800 and 14080 re-quantize to round_half_up(106.67) "
            "= 107 and round_half_up(117.33) = 117 units (12840 and 14040), so its notes last 11, 10 and 11 units, written "
            "largest piece first and tied: B8-B3 A8-A2 G8-G3. The one verse block binds the one vocal section; its three "
            "syllables take n1-n3 and n4-n8 have none. No chord symbol, so cot is melody.", pick_out, pick_song, None,
            _text("4/4", 120, "C", PICK_BODY), "melody", PICK_LYRICS, PICK_PLAN),
        _ok("zh lyrics over a 4/4 to 3/4 change", "zh-Hans has the primary subtag zh. The verse is one 4/4 bar of C4 and D4 "
            "half notes, C16D16. The waltz turns 3/4 at 3840, so its group carries M:3/4 in both voice blocks; its 24-unit bar "
            "is an E4 quarter and an F4 half, E8F16. Each Han character is one syllable: the verse block's two one-character "
            "lines give lines 1 and 2 to n1 and n2, and the waltz line's two characters go to n3 and n4. The lyrics sent have "
            "one tagged block per section repeat, in form order.", zh_out, zh_song, None,
            _text("4/4", 120, "C", "% verse\nV: Vocal\nC16D16|\nV: Ins\nZ|\n% waltz\nV: Vocal\nM:3/4\nE8F16|\nV: Ins\nM:3/4\nZ|\n"),
            "melody", "[verse]\n春\n风\n\n[waltz]\n吹过",
            _plan("s1", (1, "春", ("n1", 60, 0, 1920)), (2, "风", ("n2", 62, 1920, 3840)))
            + _plan("s2", (1, "吹", ("n3", 64, 3840, 4800)), (1, "过", ("n4", 65, 4800, 6720)))),
        _ok("chord symbols kept for cot='full'", "Chord symbols at offsets 0, 1920, 3840, 6720, 7680 and 11520 of the one "
            "verse repeat [3840, 19200) sound at 3840, 5760, 7680, 10560, 11520 and 15360; cot is not given, so they make it "
            "full. Each is quoted before the token at its onset. Em at 5760 splits the pickup bar's rest into z16 and z8; Am "
            "at 10560 splits the held C5 half note [9600, 11520) with a tie, c8- then c8; the last verse bar is an ordinary "
            "rest z32, never Z, because G/B starts there. Ins carries none. Notes, lyrics and plan are the pickup case's.",
            pick_out, chords, None, _text("4/4", 120, "C", CHORD_BODY), "full", PICK_LYRICS, PICK_PLAN),
        _ok("chord symbols stripped for cot='melody'", "The same SongSpec with cot='melody' asked for: no chord symbol is "
            "written, so the ABC is the pickup case's text exactly.", pick_out, chords, "melody",
            _text("4/4", 120, "C", PICK_BODY), "melody", PICK_LYRICS, PICK_PLAN),
        _ok("D major: key signature, natural and sharp signs, a tie over the bar line", "The tag [Verse 1] names the "
            "section verse-1 (lowercased, a space as a hyphen). K:D sharpens F and C. n1 F#4 is the key's own F, F4. n2 F4 is "
            "a letter the key alters, =F4, and the bar now holds F natural in every octave (the native convention), so n3 F5 "
            "is f4 without a sign and n4 F#5 needs ^f4. n5 C#5 is the key's c8. n6 G#4 [2880, 4800) is outside the key and a "
            "sharp key raises the letter below: ^G8- crosses the bar line at 3840 and its continuation is G8, without a sign. "
            "Bar 2 starts from the key again, which the continuation does not change: n7 G4 is G8 with no sign (the dialect's "
            "own ^F32-|F8F24| case) and n8 C4 is =C16. Eight syllables, eight notes.", *d_major, None,
            _text("4/4", 120, "D", "% verse-1\nV: Vocal\nF4=F4f4^f4c8^G8-|G8G8=C16|\nV: Ins\nZ2|\n"), "melody",
            "[verse-1]\nLa la la la la la la la",
            _plan("s1", (1, "La", ("n1", 66, 0, 480)), (1, "la", ("n2", 65, 480, 960)), (1, "la", ("n3", 77, 960, 1440)),
                  (1, "la", ("n4", 78, 1440, 1920)), (1, "la", ("n5", 73, 1920, 2880)), (1, "la", ("n6", 68, 2880, 4800)),
                  (1, "la", ("n7", 67, 4800, 5760)), (1, "la", ("n8", 60, 5760, 7680)))),
        _ok("G minor: the raised seventh, a flat, octave marks and one-unit pieces", "K:Gm flattens B and E. n1 G4 lasts 9 "
            "units: G8-G, the one-unit piece written without a number. n2 F#4 is G minor's raised seventh, the seventh degree "
            "F raised (not _G), and lasts 7 units: ^F6-F, its tied continuation without a sign. n3 Eb3 is the key's own E an "
            "octave down: E,8. n4 Db6 is neither in the key nor its raised seventh, and a flat key lowers the letter above: "
            "_d'8 (written D6 with one octave mark above d).", *g_minor, None,
            _text("4/4", 120, "Gm", "% verse\nV: Vocal\nG8-G^F6-FE,8_d'8|\nV: Ins\nZ|\n"), "melody", "[verse]\nLa la la la",
            _plan("s1", (1, "La", ("n1", 67, 0, 1080)), (1, "la", ("n2", 66, 1080, 1920)), (1, "la", ("n3", 51, 1920, 2880)),
                  (1, "la", ("n4", 85, 2880, 3840)))),
        _ok("G# minor: the raised seventh is F double sharp", "K:G#m sharpens F, C, G, D and A. n1 G#4 is the key's G, G8. n2 "
            "G4 is the raised seventh, the seventh degree F# raised again: ^^F8. The 5-unit rest [1920, 2520) is z4z, pieces "
            "largest first. n3 G#4 lasts 11 units, G8-G3: the bar's F sign does not touch G.", *g_sharp_minor, None,
            _text("4/4", 120, "G#m", "% verse\nV: Vocal\nG8^^F8z4zG8-G3|\nV: Ins\nZ|\n"), "melody", "[verse]\nLa la la",
            _plan("s1", (1, "La", ("n1", 68, 0, 960)), (1, "la", ("n2", 67, 960, 1920)), (1, "la", ("n3", 68, 2520, 3840)))),
        _ok("exactly six minutes is eligible", "60 BPM (1000000 us) is Q:1/4=60 and a 4/4 bar lasts 4 s. One verse bar (a C4 "
            "whole note, C32) and 89 outro bars make 90 bars = 360 quarters = 360 s, exactly the limit, which is eligible. "
            "The outro's 89 whole-bar rests are 22 groups of Z4 and one Z; only its first group carries the comment. The "
            "placeholder [outro] tag has no syllable and binds nothing; the verse block's two syllables meet one note, so the "
            "second has none.", *_long(Q60, 89), None,
            _text("4/4", 60, "C", "% verse\nV: Vocal\nC32|\nV: Ins\nZ|\n% outro\n" + "V: Vocal\nZ4|\nV: Ins\nZ4|\n" * 22
                  + "V: Vocal\nZ|\nV: Ins\nZ|\n"), "melody", "[verse]\nLa la\n\n[outro]",
            _plan("s1", (1, "La", ("n1", 60, 0, 3840)), (1, "la", None))),
    ]


def _ineligible(pick, pick_song, pick_out):
    hymn_src = sf.melody(sf.HYMN_NOTES_IN, sf.HYMN_PHRASES, tempo=((0, sf.Q120), (3840, sf.Q100)))
    hymn_song = sf.song(hymn_src, sf.HYMN_FORM)
    hymn_out = sf.hymn_assembled(hymn_src, hymn_song, sf.OUT)
    bed_song = _changed(sf.song(pick, [("s1", "intro", "instrumental", [], 2, 1), ("s2", "outro", "instrumental", [], 1, 1)]),
                        sf._instrumental)
    bed_out = sf.assembled(pick, bed_song, [], [(0, Q120)], [(0, 4, 4)], [("s1", "intro", "instrumental", 1, 0, 7680, []),
                                                                         ("s2", "outro", "instrumental", 1, 7680, 11520, [])], 11520)

    def pick_changed(change):
        return _changed(pick_out, change)
    return [
        _no("fr lyrics are ineligible", "fr is neither en nor zh; nothing else is wrong.", pick_out,
            _lyrics(pick_song, "[verse]\nLa la la", "fr"), _why("lyrics_language")),
        _no("a 6 min 30 s form is over the limit", "One verse bar and 194 outro bars at 120 BPM: 195 x 3840 ticks = 780 "
            "quarters x 0.5 s = 390 s = 6 min 30 s, over 360 s.", *_long(Q120, 194), _why("length_over_limit")),
        _no("a tempo change is refused, never retimed", "The hymn form changes from 120 to 100 BPM at the chorus (s2, 30720). "
            "The ABC has one integer tempo. The lyrics bind the verse and the chorus.", hymn_out,
            _lyrics(hymn_song, "[verse]\nLa la la\n[chorus]\nLa la"), _why("tempo_change", "s2", None, 30720)),
        _no("a tempo that is not a whole BPM", "60000000 / 461538 = 130.0001 BPM; Q: takes a whole number and rounding would "
            "retime the song.", pick_changed(lambda m: m["tempo_map"].update(tempo=[{"tick": 0, "us_per_quarter": 461538}])),
            pick_song, _why("tempo_not_integer_bpm", "s1", None, 0)),
        _no("an instrumental SongSpec has no lyrics to sing", "Instrumental, so no approved lyrics; its form places no note.",
            bed_out, bed_song, _why("lyrics_missing")),
        _no("a lyric tag naming another section", "The only block is tagged chorus; the one vocal section is the verse, s2 at "
            "3840.", pick_out, _lyrics(pick_song, "[chorus]\nLa la la"), _why("lyrics_unbound", "s2", None, 3840)),
        _no("a lyric block left over", "The verse block binds s2; the bridge block binds no section.", pick_out,
            _lyrics(pick_song, "[verse]\nLa la la\n[bridge]\nLa"), _why("lyrics_unbound")),
        _no("a modal key", "A modal key has no native K: field, and the key is never respelled.",
            pick_changed(lambda m: m["key"].update(mode="modal")), pick_song, _why("key_unrepresentable")),
        _no("a key spelling outside the native table", "D# major (nine sharps) is not among the 15 native major keys; it is "
            "not respelled as Eb.", pick_changed(lambda m: m["key"].update(tonic="D#")), pick_song, _why("key_unrepresentable")),
        _no("two notes sounding at once", "n1 lengthened to 960 ticks sounds until 7680, but n2 starts at 7200; both voices "
            "are monophonic.", pick_changed(lambda m: m["notes"][0].update(duration_ticks=960)), pick_song,
            _why("notes_overlap", "s2", "n2", 7200)),
        _no("a note that vanishes on the 1/32 grid", "n1 [6730, 6770): round_half_up(56.08) = round_half_up(56.42) = 56 units "
            "at both ends.", pick_changed(lambda m: m["notes"][0].update(start_tick=6730, duration_ticks=40)), pick_song,
            _why("note_requantize_collapse", "s2", "n1", 6730)),
        _no("cot='full' without chord symbols", "cot='full' asked for; the SongSpec has no chord symbol.", pick_out, pick_song,
            _why("chords_missing"), cot="full"),
        _no("a chord outside the native vocabulary", "Cmaj9 at the verse's first tick, 3840: maj9 is not a native quality.",
            pick_out, sf._chords(pick, (0, "Cmaj9")), _why("chord_unrepresentable", "s2", None, 3840)),
        _no("a chord off the 1/32 grid", "C at offset 3900 sounds at 7740 = 64.5 units; chord symbols are not re-quantized.",
            pick_out, sf._chords(pick, (0, "G"), (3900, "C")), _why("chord_off_grid", "s2", None, 7740)),
        _no("every reason, in scan order", "fr lyrics, a block for the verse only (the chorus, s2 at 30720, is unbound) and "
            "the hymn's tempo change at 30720: each reason once, in scan order.", hymn_out,
            _lyrics(hymn_song, "[verse]\nLa la la", "fr"), _why("lyrics_language"), _why("lyrics_unbound", "s2", None, 30720),
            _why("tempo_change", "s2", None, 30720)),
    ]


def _inconsistent(pick, pick_song, pick_out):
    def one_point_zero(m):
        m.update(schemaVersion=SV)
        del m["form"]

    def mid_bar(m):
        m["form"]["sections"][0]["end_tick"] = 1920
        m["form"]["sections"][1]["start_tick"] = 1920

    def ninth(m):
        m["notes"].append({"id": "n9", "start_tick": 26880, "duration_ticks": 960, "pitch": 60, "velocity": 90,
                           "confidence": None, "origin": "assembled"})

    def short_verse(m):
        m["form"]["sections"][1]["end_tick"] = 15360
        m["form"]["sections"][2]["start_tick"] = 15360
    return [
        _invalid("a source melody, not an assembled one", "spec_kind melody.", pick, pick_song, "melody_not_assembled"),
        _invalid("a 1.0 assembled record has no form", "A consumer refuses it rather than infer a form.",
                 _changed(pick_out, one_point_zero), pick_song, "form_missing"),
        _invalid("another SongSpec revision", "The melody was assembled from song_case rev 1; this is rev 2.", pick_out,
                 _changed(pick_song, lambda s: s.update(rev=2, base_rev=1)), "song_mismatch"),
        _invalid("a SongSpec whose sections differ from the form", "This SongSpec repeats the verse twice; the form holds one "
                 "verse repeat.", pick_out, _changed(pick_song, lambda s: s["form"]["sections"][1].update(repeats=2)),
                 "song_mismatch"),
        _invalid("a chord symbol assembly would refuse", "Offset 15360 is outside the 15360-tick verse repeat.", pick_out,
                 sf._chords(pick, (15360, "G")), "song_mismatch"),
        _invalid("repeats that stop before the form's end", "The repeats end at 26880; end_tick says 30720.",
                 _changed(pick_out, lambda m: m["form"].update(end_tick=30720)), pick_song, "form_inconsistent"),
        _invalid("a repeat boundary inside a bar", "The intro ends and the verse starts at 1920, mid-bar in 4/4.",
                 _changed(pick_out, mid_bar), pick_song, "form_inconsistent"),
        _invalid("a note after the form's end", "n9 [26880, 27840) starts where the form ends.", _changed(pick_out, ninth),
                 pick_song, "form_inconsistent"),
        _invalid("repeats whose bars differ from the SongSpec's", "The verse ends and the outro starts at 15360: the repeats "
                 "still tile on bar lines, but hold 3 and 3 bars where the SongSpec says 4 and 2.",
                 _changed(pick_out, short_verse), pick_song, "form_inconsistent"),
    ]


def build(profiles):
    pickup = sf._pickup()
    return {"kind": KIND, "schemaVersion": SV,
            "cases": _eligible(*pickup) + _ineligible(*pickup) + _inconsistent(*pickup)}


def evaluate(case, world):
    try:
        got = abc.to_abc(case["melody"], case["song"], case["cot"])
    except abc.AbcInputError as error:
        got = {"invalid": error.code}
    return got, case["expected"]
