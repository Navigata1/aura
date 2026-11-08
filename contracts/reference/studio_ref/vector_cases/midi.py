"""MIDI round-trip vectors. Every expected byte, chunk length and MelodySpec field is written out by hand from the SMF
1.0 layout (the derivation says how); nothing here calls the reference to build an expectation."""
from studio_ref import midi
from studio_ref.fixture_support import SV, H

KIND = "fixture.midi"
T120 = [{"tick": 0, "us_per_quarter": 500000}]
M44 = [{"tick": 0, "numerator": 4, "denominator": 4}]

# MThd: length 6, format 1, two tracks, 960 PPQ; MTrk 0, 19 bytes: 4/4 (nn 4, dd 2, cc 24, bb 8), 500000 us, End of
# Track; MTrk 1, 13 bytes: note-on C4 velocity 100, delta 960 (87 40), note-off with release velocity 64, End of Track.
ONE_NOTE = ("4d546864" "00000006" "0001" "0002" "03c0"
            "4d54726b" "00000013" "00ff5804" "04021808" "00ff5103" "07a120" "00ff2f00"
            "4d54726b" "0000000d" "00903c64" "8740803c40" "00ff2f00")
FORMAT0 = "4d546864" "00000006" "0000" "0001" "03c0"  # MThd, length 6, format 0, one SMF track, 960 PPQ


def note(start, duration, pitch, velocity):
    return {"start_tick": start, "duration_ticks": duration, "pitch": pitch, "velocity": velocity}


def melody(tempo, meter, *notes):
    return {"tempo_map": {"tempo": tempo, "meter": meter}, "notes": list(notes)}


def read(mel, end_tick, markers=(), not_carried=()):
    return {"melody": mel, "markers": list(markers), "end_tick": end_tick, "not_carried": list(not_carried)}


def refuse_read(name, smf_hex, code, smf_track, tick, why):
    return {"name": name, "derivation": why, "op": "refuse_read", "smf_hex": smf_hex,
            "refusal": {"code": code, "smf_track": smf_track, "tick": tick}}


def build(profiles):
    record = {"kind": "melody-spec", "schemaVersion": SV, "melody_id": "mel_midi", "rev": 2, "base_rev": 1,
              "project_id": "prj_midi", "created_at": "2026-11-07T12:00:00Z", "spec_kind": "melody", "ppq": 960,
              "tempo_map": {"rev": 1, "tempo": T120, "meter": M44}, "key": {"tonic": "A", "mode": "minor"},
              "notes": [{"id": "n7", "start_tick": 0, "duration_ticks": 960, "pitch": 60, "velocity": 100,
                         "confidence": None, "origin": "corrected"}],
              "phrases": [{"id": "ph1", "name": "opening line", "start_tick": 0, "end_tick": 3840}],
              "source": {"seed_kind": "midi_file", "capture_sha256": H("midi capture"), "transcription": None,
                         "assembled_from": None},
              "quantize": {"grid_ticks": 240}, "content_sha256": H("midi record")}
    cases = [
        {"name": "one note at 120 BPM in 4/4", "op": "round_trip", "melody": melody(T120, M44, note(0, 960, 60, 100)),
         "markers": [], "end_tick": 960, "smf_hex": ONE_NOTE, "derivation":
         "Header 4d546864 00000006 0001 0002 03c0: format 1, two SMF tracks, 960 PPQ. Conductor (19 bytes): 00 ff5804 04 02 18 08 "
         "is 4/4 (dd 2 = 2^2; cc 24 = 96/4, one click per quarter; bb 8), 00 ff5103 07a120 is 500000 us, 00 ff2f00. "
         "Melody (13 bytes): 00 90 3c 64 is note-on C4 (60) velocity 100 at 0; 87 40 is delta 960 (7 x 128 + 64); "
         "80 3c 40 is its note-off with release velocity 64; 00 ff2f00. end_tick 960 is that last End of Track."},
        {"name": "a pickup on beat 4 keeps its leading rest", "op": "round_trip",
         "melody": melody(T120, M44, note(2880, 960, 67, 90), note(3840, 1920, 72, 100)), "markers": [], "end_tick": 5760,
         "smf_hex": "4d546864000000060001000203c0" "4d54726b00000013" "00ff580404021808" "00ff510307a120" "00ff2f00"
                    "4d54726b00000017" "964090435a" "8740804340" "00904864" "8f00804840" "00ff2f00", "derivation":
         "Header and conductor as in the one-note case. Melody (23 bytes): the first delta is 2880 (22 x 128 + 64 = 96 40), "
         "so nothing moves to tick 0: 90 43 5a is G4 (67) velocity 90 on beat 4; 87 40 80 43 40 ends it at 3840; at 3840 "
         "the note-off comes before 00 90 48 64, C5 (72) velocity 100 on the downbeat; 8f 00 (15 x 128) 80 48 40 ends it at "
         "5760; 00 ff2f00, so end_tick is 5760."},
        {"name": "eighth-note triplets are exact at 960 PPQ", "op": "round_trip",
         "melody": melody(T120, M44, note(0, 320, 60, 100), note(320, 320, 62, 100), note(640, 320, 64, 100)),
         "markers": [], "end_tick": 960,
         "smf_hex": "4d546864000000060001000203c0" "4d54726b00000013" "00ff580404021808" "00ff510307a120" "00ff2f00"
                    "4d54726b0000001f" "00903c64" "8240803c40" "00903e64" "8240803e40" "00904064" "8240804040" "00ff2f00",
         "derivation":
         "Three eighth-note triplets fill one quarter: 960 / 3 = 320 ticks each, a whole number at 960 PPQ, so nothing "
         "rounds. C4, D4 (3e) and E4 (40), velocity 100, start at 0, 320 and 640; each note-off comes 320 ticks later "
         "(82 40 = 2 x 128 + 64), before the next note-on. Melody 31 bytes; conductor as in the one-note case; end_tick 960."},
        {"name": "tempo and meter change with section markers", "op": "round_trip",
         "melody": melody([{"tick": 0, "us_per_quarter": 500000}, {"tick": 3840, "us_per_quarter": 600000}],
                          [{"tick": 0, "numerator": 4, "denominator": 4}, {"tick": 3840, "numerator": 3, "denominator": 4}],
                          note(0, 1920, 64, 96), note(1920, 1920, 64, 96), note(3840, 2880, 67, 110)),
         "markers": [{"name": "verse", "tick": 0}, {"name": "chorus", "tick": 3840}], "end_tick": 6720,
         "smf_hex": "4d546864000000060001000203c0"
                    "4d54726b00000036" "00ff580404021808" "00ff510307a120" "00ff06057665727365"
                    "9e00ff580403021808" "00ff51030927c0" "00ff060663686f727573" "00ff2f00"
                    "4d54726b0000001f" "00904060" "8f00804040" "00904060" "8f00804040" "0090436e" "9640804340" "00ff2f00",
         "derivation":
         "Conductor (54 bytes), meter then tempo then markers at each tick: at 0, 4/4, 07a120 and ff06 05 'verse' "
         "(76 65 72 73 65); delta 3840 (30 x 128 = 9e 00), then ff5804 03 02 18 08 (3/4, a click per quarter), 600000 us "
         "(0927c0) and ff06 06 'chorus' (63 68 6f 72 75 73). Melody (31 bytes): E4 (64 = 40) velocity 96 (60) at 0 and "
         "again at 1920, the first note-off (8f 00 80 40 40) written before the second note-on, so the touching notes stay "
         "two; G4 (43) velocity 110 (6e) at 3840 for a dotted half, 2880 (96 40); 00 ff2f00 at end_tick 6720."},
        {"name": "an outro after the last note keeps its length", "op": "round_trip",
         "melody": melody(T120, M44, note(0, 3840, 60, 100)),
         "markers": [{"name": "verse", "tick": 0}, {"name": "outro", "tick": 3840}], "end_tick": 7680,
         "smf_hex": "4d546864000000060001000203c0"
                    "4d54726b00000027" "00ff580404021808" "00ff510307a120" "00ff06057665727365" "9e00ff06056f7574726f"
                    "9e00ff2f00" "4d54726b0000000d" "00903c64" "9e00803c40" "00ff2f00", "derivation":
         "end_tick 7680 is later than every event (the outro marker and the note-off, both at 3840), so the conductor's "
         "End of Track goes there: after ff06 05 'outro' (6f 75 74 72 6f) at 3840 (9e 00) comes 9e 00 ff2f00, 3840 more "
         "ticks, and the outro keeps its bar (39 bytes). The melody's SMF track (13 bytes) ends at its note-off. Reading "
         "gives end_tick 7680 back, the latest End of Track."},
        {"name": "a whole MelodySpec record writes only its MIDI fields", "op": "write", "melody": record, "markers": [],
         "end_tick": None, "smf_hex": ONE_NOTE, "derivation":
         "The record's tempo map and its one note equal the one-note case; its ids, revisions, corrected origin, "
         "confidence, key, phrase, quantize layer and source are MelodySpec-only, and a null end_tick ends each SMF track "
         "at its own last event, so the bytes are the one-note bytes."},
        {"name": "format 0 at 480 PPQ with running status and the SMF defaults", "op": "read",
         "smf_hex": "4d546864" "00000006" "0000" "0001" "01e0"
                    "4d54726b" "00000013" "00903c50" "83603c00" "003e50" "83603e00" "00ff2f00",
         "read": read(melody(T120, M44, note(0, 960, 60, 80), note(960, 960, 62, 80)), 1920), "derivation":
         "Format 0, one SMF track, 480 PPQ (01e0), so every tick doubles exactly. 90 3c 50: C4 velocity 80 at 0; 83 60 (480) "
         "3c 00 is running status 90 with velocity 0, a note-off; 00 3e 50 starts D4 (62) at 480; 83 60 3e 00 ends it at "
         "960. No tempo or time signature, so the SMF defaults hold: 500000 us (120 BPM) and 4/4. At 960 PPQ the notes are "
         "0 + 960 and 960 + 960, and End of Track at 960 is end_tick 1920."},
        {"name": "events a MelodySpec does not carry are listed, never dropped", "op": "read",
         "smf_hex": "4d546864000000060001000203c0"
                    "4d54726b0000002e" "00ff03046c656164" "00ff580403021808" "00ff59020000" "00ff060756657273652031"
                    "00ff0605696e74726f" "00ff2f00"
                    "4d54726b00000028" "00f0057e7f0901f7" "00ff580403021808" "00c000" "00b00764" "00803c40" "00903c64"
                    "8740803c40" "00ff2f00",
         "read": read(melody(T120, [{"tick": 0, "numerator": 3, "denominator": 4}], note(0, 960, 60, 100)), 960,
                      [{"name": "intro", "tick": 0}],
                      [{"smf_track": 0, "tick": 0, "event": e} for e in ("ff03", "ff59", "ff06")]
                      + [{"smf_track": 1, "tick": 0, "event": e} for e in ("f0", "c0", "b0", "80")]), "derivation":
         "SMF track 0 (46 bytes): ff03 04 'lead' (a name), 3/4, ff59 02 00 00 (a key signature), ff06 07 'Verse 1' (56 65 "
         "72 73 65 20 31, not a section name), ff06 05 'intro' (69 6e 74 72 6f, a marker). SMF track 1 (40 bytes): SysEx f0 "
         "05 7e 7f 09 01 f7, the same 3/4 (one entry), c0 00, b0 07 64, a note-off 80 3c 40 with nothing sounding, then C4 "
         "velocity 100 from 0 to 960 (87 40), end_tick 960. The note, meter and 'intro' are carried; each other event is "
         "listed by SMF track, tick and status. No tempo: the SMF default."},
        {"name": "an End of Track inside the file is listed, not dropped", "op": "read",
         "smf_hex": "4d546864000000060001000203c0" "4d54726b00000014" "00ff580404021808" "00ff510307a120" "bc00ff2f00"
                    "4d54726b0000000e" "00903c64" "8740803c40" "9640ff2f00",
         "read": read(melody(T120, M44, note(0, 960, 60, 100)), 7680, [], [{"smf_track": 1, "tick": 3840, "event": "ff2f"}]),
         "derivation":
         "SMF track 0 (20 bytes) ends 7680 ticks after its last event (bc 00 ff2f00, 60 x 128), the latest End of Track, so "
         "end_tick is 7680. SMF track 1 (14 bytes) ends at 3840 (96 40 after the note-off at 960): after its own last event "
         "but before the file's end, a position the result does not otherwise hold, so it is listed as ff2f."},
        refuse_read("SMPTE time division", "4d546864" "00000006" "0001" "0001" "e728" "4d54726b" "00000004" "00ff2f00",
                    "smpte_division", None, None,
                    "Division e728 has its top bit set: SMPTE timing (e7 = -25 frames per second, 28 = 40 ticks per frame), "
                    "which has no ticks per quarter note, so no 960 PPQ tempo map exists for it."),
        refuse_read("a tempo of 0 us per quarter", FORMAT0 + "4d54726b" "0000000b" "00ff5103000000" "00ff2f00",
                    "tempo_outside_model", 0, 0,
                    "ff51 03 00 00 00 sets 0 us per quarter; the tempo map holds integers from 1 to 16777215."),
        refuse_read("a 33/4 time signature", FORMAT0 + "4d54726b" "0000000c" "00ff580421021808" "00ff2f00",
                    "meter_outside_model", 0, 0, "nn 21 is 33 beats; a MelodySpec meter has at most 32."),
        refuse_read("a time signature numerator of 0", FORMAT0 + "4d54726b" "0000000c" "00ff580400021808" "00ff2f00",
                    "meter_outside_model", 0, 0, "nn 00 is zero beats in a bar; a MelodySpec meter has at least 1."),
        refuse_read("a 4/64 time signature", FORMAT0 + "4d54726b" "0000000c" "00ff580404061808" "00ff2f00",
                    "meter_outside_model", 0, 0, "dd 06 is a denominator of 2^6 = 64; a MelodySpec meter stops at 32."),
        refuse_read("two different tempos at one tick", FORMAT0 + "4d54726b" "00000012" "00ff510307a120" "00ff51030927c0"
                    "00ff2f00", "tempo_map_ambiguous", 0, 0,
                    "500000 and 600000 us both at tick 0: a tempo map holds one tempo per tick, and taking either would "
                    "silently drop the other."),
        refuse_read("two different time signatures at one tick", FORMAT0 + "4d54726b" "00000014" "00ff580404021808"
                    "00ff580403021808" "00ff2f00", "tempo_map_ambiguous", 0, 0,
                    "4/4 and then 3/4 at tick 0: a meter holds one time signature per tick, so the reader refuses rather "
                    "than keep one."),
        refuse_read("a time signature inside a bar", FORMAT0 + "4d54726b" "00000015" "00ff580404021808" "8f00ff580403021808"
                    "00ff2f00", "meter_change_inside_bar", 0, 1920,
                    "4/4 at 0, then 3/4 at 1920 (8f 00), half a bar: a 4/4 bar is 4 x 3840 / 4 = 3840 ticks, and ADR-0033 "
                    "counts bars and beats across meter segments only from bar lines, so the change must fall on 3840, 7680 "
                    "and so on."),
        refuse_read("a second note-on for a sounding pitch", FORMAT0 + "4d54726b" "00000016" "00903c64" "8360903c64"
                    "8360803c40" "00803c40" "00ff2f00", "same_pitch_overlap", 0, 480,
                    "C4 starts at 0 and again at 480 (83 60) before any note-off, so which note-off ends which note is "
                    "ambiguous."),
        refuse_read("format 2", "4d546864" "00000006" "0002" "0001" "03c0" "4d54726b" "00000004" "00ff2f00",
                    "track_layout_unsupported", None, None,
                    "Format 2 holds independent sequences, each with its own tempo map; the mapping reads one."),
        refuse_read("notes in two SMF tracks", "4d546864000000060001000203c0" "4d54726b0000000d" "00903c64" "8740803c40"
                    "00ff2f00" "4d54726b0000000d" "00903e64" "8740803e40" "00ff2f00", "track_layout_unsupported", 1, 0,
                    "SMF track 0 plays C4 and SMF track 1 plays D4 (3e), both at 0; a MelodySpec is one melody, so a chooser "
                    "must name the SMF track (T25) rather than the reader merging or dropping one."),
        refuse_read("notes on two MIDI channels", FORMAT0 + "4d54726b" "00000015" "00903c64" "00913e64" "8740803c40"
                    "00813e40" "00ff2f00", "track_layout_unsupported", 0, 0,
                    "C4 on channel 1 (90) and D4 on channel 2 (91) in one SMF track; one melody is one channel."),
        refuse_read("a tick that is not a whole 960 PPQ tick", "4d546864" "00000006" "0000" "0001" "0780"
                    "4d54726b" "0000000c" "00903c64" "01803c40" "00ff2f00", "tick_not_representable", 0, 1,
                    "At 1920 PPQ (0780) the note-off at tick 1 is 960 x 1 / 1920 = half a tick; rounding would retime it."),
        refuse_read("an End of Track that is not on a whole 960 PPQ tick", "4d546864" "00000006" "0000" "0001" "0780"
                    "4d54726b" "0000000d" "00903c64" "8f00803c40" "01ff2f00", "tick_not_representable", 0, 1921,
                    "At 1920 PPQ the note-off at 1920 (8f 00) is tick 960, but End of Track at 1921 (01) is 960.5: the end is "
                    "converted exactly like any other event, or refused, never rounded."),
        refuse_read("a zero-length note", FORMAT0 + "4d54726b" "0000000c" "00903c64" "00803c40" "00ff2f00",
                    "zero_length_note", 0, 0, "C4 starts and ends at tick 0; a MelodySpec note lasts at least one tick."),
        refuse_read("a note still sounding at End of Track", FORMAT0 + "4d54726b" "00000009" "00903c64" "8740ff2f00",
                    "unterminated_note", 0, 0,
                    "C4 starts at 0 and the SMF track ends at 960 (87 40 ff 2f 00) with no note-off, so its length is unknown."),
    ]
    end = "4d54726b" "00000004" "00ff2f00"  # an MTrk holding only End of Track
    cases += [refuse_read(name, smf_hex, "malformed_smf", smf_track, tick, why) for name, smf_hex, smf_track, tick, why in [
        ("not a MIDI file header", "52494646" "00000006" "0000" "0001" "03c0" + end, None, None,
         "The file starts 'RIFF', not 'MThd' (4d 54 68 64)."),
        ("a header longer than 6 bytes", "4d546864" "00000008" "0000" "0001" "03c0" "0000" + end, None, None,
         "MThd's length is 8; the mapping reads only the 6-byte SMF 1.0 header rather than skip unknown fields."),
        ("a file with no SMF tracks", "4d546864" "00000006" "0001" "0000" "03c0", None, None,
         "ntrks 0000: there is no SMF track to hold a tempo map or a note."),
        ("a format above 2", "4d546864" "00000006" "0003" "0001" "03c0" + end, None, None,
         "Format 0003 is not defined by SMF 1.0 (0, 1 and 2 are)."),
        ("a division of 0", "4d546864" "00000006" "0000" "0001" "0000" + end, None, None,
         "0 ticks per quarter note cannot place any event."),
        ("format 0 with two SMF tracks", "4d546864" "00000006" "0000" "0002" "03c0" + end + end, None, None,
         "Format 0 has exactly one SMF track."),
        ("a chunk that is not MTrk", FORMAT0 + "4d54726c" "00000004" "00ff2f00", 0, None,
         "The first chunk after the header is 'MTrl'; unknown chunks are refused, not skipped."),
        ("a chunk shorter than its length", FORMAT0 + "4d54726b" "00000008" "00903c64", 0, None,
         "The chunk says 8 bytes but the file ends after 4."),
        ("a track without End of Track", FORMAT0 + "4d54726b" "00000009" "00903c64" "8740803c40", 0, None,
         "The 9 bytes end after the note-off, inside the next delta time; ff 2f 00 never comes."),
        ("data after End of Track", FORMAT0 + "4d54726b" "00000008" "00ff2f00" "00ff2f00", 0, 0,
         "A second event follows the End of Track at tick 0 inside the chunk."),
        ("bytes after the last chunk", FORMAT0 + end + "00", None, None, "One stray byte follows the only chunk."),
        ("a delta time longer than four bytes", FORMAT0 + "4d54726b" "00000009" "8080808000" "00ff2f00", 0, None,
         "80 80 80 80 still has its continuation bit after four bytes, the SMF maximum."),
        ("running status after a meta event", FORMAT0 + "4d54726b" "00000010" "00903c64" "00ff0100" "87403c00"
         "00ff2f00", 0, 960, "ff 01 00 (an empty text event) cancels running status, so the data byte 3c at 960 has no status."),
        ("a status byte where data belongs", FORMAT0 + "4d54726b" "00000008" "00903c90" "00ff2f00", 0, 0,
         "The note-on's velocity byte is 90, a status byte; data bytes are below 80."),
        ("a system message in an SMF track", FORMAT0 + "4d54726b" "00000006" "00f8" "00ff2f00", 0, 0,
         "f8 (timing clock) is a real-time message; a file holds only channel, SysEx and meta events."),
        ("a tempo event of the wrong length", FORMAT0 + "4d54726b" "0000000b" "8740ff510207a1" "00ff2f00", 0, 960,
         "At 960 (87 40), ff 51 must carry 3 bytes; 02 07 a1 carries 2."),
        ("a time signature of the wrong length", FORMAT0 + "4d54726b" "0000000b" "8740ff58020402" "00ff2f00", 0, 960,
         "At 960 (87 40), ff 58 must carry 4 bytes; 02 04 02 carries 2."),
    ]]
    cases += [{"name": name, "derivation": why, "op": "refuse_write", "melody": mel, "markers": [], "end_tick": end_tick,
               "refusal": {"code": code, "smf_track": None, "tick": tick}} for name, mel, end_tick, code, tick, why in [
        ("two overlapping notes of one pitch", melody(T120, M44, note(0, 1920, 60, 100), note(960, 960, 60, 100)), None,
         "same_pitch_overlap", 960, "C4 sounds from 0 to 1920 and again from 960; one channel cannot hold both, and "
         "the first note-off would end the wrong note."),
        ("two tempos at one tick", melody([{"tick": 0, "us_per_quarter": 500000}, {"tick": 0, "us_per_quarter": 600000}],
                                          M44, note(0, 960, 60, 100)), None,
         "tempo_map_ambiguous", None, "The tempo list repeats tick 0, so it does not strictly increase: the time model's "
         "ordering check (melody.wellformed) refuses the list as a whole, so no tick."),
        ("a tempo list that does not start at tick 0", melody([{"tick": 960, "us_per_quarter": 500000}], M44,
                                                              note(0, 960, 60, 100)), None,
         "tempo_map_ambiguous", None, "Written as is, a reader would hear the SMF default 120 BPM before 960, a tempo "
         "the MelodySpec never stated. The time model's ordering check refuses the list as a whole, so no tick."),
        ("a meter that does not start at tick 0", melody(T120, [{"tick": 960, "numerator": 4, "denominator": 4}],
                                                        note(0, 960, 60, 100)), None,
         "tempo_map_ambiguous", None, "Written as is, a reader would hear the SMF default 4/4 before 960, a meter the "
         "MelodySpec never stated. The list as a whole is refused, so no tick."),
        ("a meter change inside a bar", melody(T120, [{"tick": 0, "numerator": 4, "denominator": 4},
                                                       {"tick": 1920, "numerator": 3, "denominator": 4}],
                                                      note(0, 960, 60, 100)), None,
         "meter_change_inside_bar", 1920, "3/4 starts at 1920, half a 3840-tick 4/4 bar; written as is, the file would put "
         "a bar line where the MelodySpec's own bars do not."),
        ("a gap longer than the SMF delta-time maximum", melody(T120, M44, note(268435456, 960, 60, 100)), None,
         "tick_not_representable", 268435456, "The first note-on is 268435456 = 2^28 ticks after 0, one more than the "
         "largest four-byte delta time, 0x0fffffff."),
        ("a file end before the last note-off", melody(T120, M44, note(0, 1920, 60, 100)), 960,
         "end_before_last_event", 1920, "end_tick 960 falls inside the C4 that sounds until 1920, the last event; End of "
         "Track must come last, so the end is refused rather than the note cut or the end moved."),
    ]]
    return {"kind": KIND, "schemaVersion": SV, "cases": cases}


def evaluate(case, world):
    op = case["op"]
    if op.startswith("refuse_"):
        try:
            if op == "refuse_write":
                midi.to_smf(case["melody"], case["markers"], case["end_tick"])
            else:
                midi.from_smf(bytes.fromhex(case["smf_hex"]))
        except midi.MidiRefusal as refusal:
            return refusal.as_dict(), case["refusal"]
        return "no refusal", case["refusal"]
    if op == "read":
        return midi.from_smf(bytes.fromhex(case["smf_hex"])), case["read"]
    written = midi.to_smf(case["melody"], case["markers"], case["end_tick"]).hex()
    if op == "write":
        return written, case["smf_hex"]
    # The canonical file carries everything it was written from, so reading it back lists nothing as not carried.
    return ({"smf_hex": written, "read": midi.from_smf(bytes.fromhex(case["smf_hex"]))},
            {"smf_hex": case["smf_hex"], "read": read(case["melody"], case["end_tick"], case["markers"])})
