"""Tempo hand-derived golden cases and public reference evaluator."""
from studio_ref import timemodel
from studio_ref.fixture_support import SV

KIND = "fixture.tempo"

def build(profiles):
    T120 = [{"tick": 0, "us_per_quarter": 500000}]
    TCHG = [{"tick": 0, "us_per_quarter": 500000}, {"tick": 3840, "us_per_quarter": 600000}]
    T125 = [{"tick": 0, "us_per_quarter": 480000}]

    def tc(name, op, tempo, rate, inp, exp, why):
        return {"name": name, "derivation": why, "op": op, "tempo": tempo, "sample_rate": rate, "input": inp, "expected": exp}
    tempo = {"kind": "fixture.tempo", "schemaVersion": SV, "cases": [
        tc("zero", "ticks_to_frames", T120, 48000, 0, 0, "0 ticks is 0 s."),
        tc("one beat at 120 BPM, 48 kHz", "ticks_to_frames", T120, 48000, 960, 24000, "960 ticks = 1 quarter = 0.5 s; 0.5 x 48000 = 24000."),
        tc("one tick at 120 BPM, 48 kHz", "ticks_to_frames", T120, 48000, 1, 25, "0.5 s / 960 x 48000 = 25 exactly."),
        tc("two bars at 120 BPM", "ticks_to_frames", T120, 48000, 7680, 192000, "8 quarters x 0.5 s = 4 s = 192000 frames."),
        tc("one tick at 44.1 kHz rounds up", "ticks_to_frames", T120, 44100, 1, 23, "22050 / 960 = 22.96875, rounded half-up to 23."),
        tc("exact half rounds up", "ticks_to_frames", T120, 44100, 16, 368, "16 x 22.96875 = 367.5, half-up gives 368."),
        tc("one beat at 44.1 kHz", "ticks_to_frames", T120, 44100, 960, 22050, "0.5 s x 44100."),
        tc("at the tempo change", "ticks_to_frames", TCHG, 48000, 3840, 96000, "4 quarters at 0.5 s = 2 s = 96000."),
        tc("after the tempo change", "ticks_to_frames", TCHG, 48000, 4800, 124800,
           "96000 + 960 ticks at 0.6 s per quarter = 0.6 s x 48000 = 28800; 124800."),
        tc("frames to ticks, one beat", "frames_to_ticks", T120, 48000, 24000, 960, "Inverse of the beat case."),
        tc("frames to ticks, below half", "frames_to_ticks", T120, 48000, 12, 0, "12 / 25 = 0.48 ticks, rounds to 0."),
        tc("frames to ticks, above half", "frames_to_ticks", T120, 48000, 13, 1, "13 / 25 = 0.52 ticks, rounds to 1."),
        tc("frames to ticks, exact half at 125 BPM", "frames_to_ticks", T125, 48000, 12, 1,
           "480000 us per quarter: 960e6 / (480000 x 48000) = 1/24 tick per frame; 12 frames = 0.5, half-up 1."),
        tc("frames to ticks, 1.5 at 125 BPM", "frames_to_ticks", T125, 48000, 36, 2, "36 / 24 = 1.5, half-up 2."),
        tc("frames to ticks at the change", "frames_to_ticks", TCHG, 48000, 96000, 3840, "Inverse of the change boundary."),
        tc("frames to ticks after the change", "frames_to_ticks", TCHG, 48000, 110400, 4320,
           "14400 frames past 96000 = 0.3 s; at 0.6 s per quarter that is 480 ticks; 3840 + 480."),
        tc("frames to ticks round trip", "frames_to_ticks", TCHG, 48000, 124800, 4800, "Inverse of the after-change case."),
    ]}
    return tempo

def evaluate(case, world):
    fn = timemodel.ticks_to_frames if case["op"] == "ticks_to_frames" else timemodel.frames_to_ticks
    return fn(case["input"], case["tempo"], case["sample_rate"]), case["expected"]
