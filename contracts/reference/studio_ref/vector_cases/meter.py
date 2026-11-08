"""Meter hand-derived golden cases (T02c) and the public TimeModel evaluator (ADR-0033).

FORM is the assembled meter map of the SongForm case "sections change meter: 4/4, 3/4, 6/8": 4/4 from tick 0, 3/4 from
11520 and 6/8 from 17280. A bar of n/d lasts n x 3840 / d ticks at 960 PPQ, a beat is one d-note (3840 / d ticks, so
6/8 counts six 480-tick beats) and bars and beats count from 1 across every change. Every expected position is
written out by hand; the TypeScript twin must reproduce them, errors included.
"""
from studio_ref import timemodel
from studio_ref.fixture_support import SV

KIND = "fixture.meter"


def _meter(*segments):
    return [{"tick": t, "numerator": n, "denominator": d} for t, n, d in segments]


FORM = _meter((0, 4, 4), (11520, 3, 4), (17280, 6, 8))


def build(profiles):
    def at(tick, bar, beat, offset, why, meter=FORM):
        return {"name": f"tick {tick}", "derivation": why, "op": "position", "meter": meter, "input": {"tick": tick},
                "expected": {"bar": bar, "beat": beat, "offset": offset}}

    def start(bar, beat, tick, why):
        return {"name": f"bar {bar} beat {beat}", "derivation": why, "op": "tick", "meter": FORM,
                "input": {"bar": bar, "beat": beat}, "expected": {"tick": tick}}

    def invalid(name, why, op, meter, code, **given):
        return {"name": name, "derivation": why, "op": op, "meter": meter, "input": given, "expected": {"invalid": code}}
    return {"kind": KIND, "schemaVersion": SV, "cases": [
        at(0, 1, 1, 0, "The first tick is bar 1, beat 1."),
        at(959, 1, 1, 959, "One tick before the second beat: 4/4 beats are quarter notes, 960 ticks."),
        at(960, 1, 2, 0, "The second 960-tick beat of bar 1."),
        at(11519, 3, 4, 959, "4/4 bars last 3840 ticks, so bar 3 is [7680, 11520); 11519 - 7680 = 3839 = 3 beats + 959."),
        at(11520, 4, 1, 0, "The 3/4 change at 11520 is the downbeat of bar 4."),
        at(12480, 4, 2, 0, "3/4 beats are 960 ticks."),
        at(14399, 4, 3, 959, "A 3/4 bar lasts 2880 ticks: bar 4 is [11520, 14400); 2879 = 2 beats + 959."),
        at(14400, 5, 1, 0, "Bar 5 starts one 2880-tick bar after the change."),
        at(17279, 5, 3, 959, "The last tick of bar 5, [14400, 17280)."),
        at(17280, 6, 1, 0, "The 6/8 change at 17280 is the downbeat of bar 6."),
        at(17760, 6, 2, 0, "6/8 counts six eighth-note beats of 480 ticks."),
        at(20159, 6, 6, 479, "A 6/8 bar lasts 6 x 480 = 2880 ticks: 20159 - 17280 = 2879 = 5 beats + 479."),
        at(20160, 7, 1, 0, "Bar 7 starts one 6/8 bar after the change."),
        at(25920, 9, 1, 0, "The form ends 8640 ticks = 3 bars after the 6/8 change, on the downbeat of bar 9."),
        at(30000, 10, 3, 240, "The last meter runs on past the form: 30000 - 17280 = 12720 = 4 bars + 1200 = 2 beats + 240."),
        start(1, 1, 0, "Bar 1, beat 1 is tick 0."),
        start(3, 4, 10560, "Bar 3 starts 2 x 3840 = 7680 ticks in; beat 4 is 3 x 960 later."),
        start(4, 1, 11520, "Bar 4 is the first 3/4 bar, at the change."),
        start(5, 3, 16320, "Bar 5 starts at 11520 + 2880 = 14400; beat 3 is 2 x 960 later."),
        start(6, 1, 17280, "Bar 6 is the first 6/8 bar."),
        start(6, 6, 19680, "Beat 6 of the first 6/8 bar is 5 x 480 = 2400 ticks after 17280."),
        start(9, 1, 25920, "Bar 9 is 3 x 2880 ticks after 17280, where the form ends."),
        invalid("a 3/4 bar has no beat 4", "Bar 4 is in 3/4.", "tick", FORM, "beat_outside_bar", bar=4, beat=4),
        invalid("a 6/8 bar has no beat 7", "Bar 6 is in 6/8.", "tick", FORM, "beat_outside_bar", bar=6, beat=7),
        invalid("meter change inside a bar", "1920 is the middle of a 4/4 bar; a meter changes only on a bar line.",
                "position", _meter((0, 4, 4), (1920, 3, 4)), "meter_change_inside_bar", tick=0),
        invalid("meter map not from tick 0", "The first meter segment starts at 960, not 0.", "position",
                _meter((960, 4, 4)), "meter_segments_invalid", tick=960),
        invalid("meter segments not increasing", "Two segments start at tick 0.", "tick", _meter((0, 4, 4), (0, 3, 4)),
                "meter_segments_invalid", bar=1, beat=1),
    ]}


def evaluate(case, world):
    try:
        if case["op"] == "position":
            got = timemodel.position(case["input"]["tick"], case["meter"])
        else:
            got = {"tick": timemodel.tick_at(case["input"]["bar"], case["input"]["beat"], case["meter"])}
    except timemodel.MeterError as error:
        got = {"invalid": error.code}
    return got, case["expected"]
