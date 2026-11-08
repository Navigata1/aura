"""Meter hand-derived golden cases (T02c) and the public TimeModel evaluator (ADR-0033).

FORM is the assembled meter map of the SongForm case "sections change meter: 4/4, 3/4, 6/8": 4/4 from tick 0, 3/4 from
11520 and 6/8 from 17280. MIXED covers the other denominators: 2/2 from 0, 1/1 from 7680, 7/16 from 11520 and 5/32 from
14880. A bar of n/d lasts n x 3840 / d ticks at 960 PPQ, a beat is one d-note (3840 / d ticks, so 6/8 counts six
480-tick beats and 5/32 five 120-tick beats) and bars and beats count from 1 across every change. Every expected position is
written out by hand; the TypeScript twin must reproduce them, errors included.
"""
from studio_ref import timemodel
from studio_ref.fixture_support import SV

KIND = "fixture.meter"


def _meter(*segments):
    return [{"tick": t, "numerator": n, "denominator": d} for t, n, d in segments]


FORM = _meter((0, 4, 4), (11520, 3, 4), (17280, 6, 8))
MIXED = _meter((0, 2, 2), (7680, 1, 1), (11520, 7, 16), (14880, 5, 32))


def build(profiles):
    def at(tick, bar, beat, offset, why, meter=FORM, label=""):
        return {"name": f"{label}tick {tick}", "derivation": why, "op": "position", "meter": meter, "input": {"tick": tick},
                "expected": {"bar": bar, "beat": beat, "offset": offset}}

    def start(bar, beat, tick, why, meter=FORM, label=""):
        return {"name": f"{label}bar {bar} beat {beat}", "derivation": why, "op": "tick", "meter": meter,
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
        at(1920, 1, 2, 0, "2/2 counts half-note beats of 1920 ticks: 1920 is beat 2 of bar 1.", MIXED, "mixed: "),
        at(5759, 2, 1, 1919, "A 2/2 bar lasts 3840 ticks: bar 2 is [3840, 7680) and 5759 is 1919 into its first beat.",
           MIXED, "mixed: "),
        at(7680, 3, 1, 0, "The 1/1 change at 7680, after two 2/2 bars, is the downbeat of bar 3.", MIXED, "mixed: "),
        at(11519, 3, 1, 3839, "A 1/1 bar is one 3840-tick beat: 11519 is 3839 into bar 3.", MIXED, "mixed: "),
        at(11520, 4, 1, 0, "The 7/16 change at 11520 is the downbeat of bar 4.", MIXED, "mixed: "),
        at(13199, 4, 7, 239, "A 7/16 bar lasts 7 x 240 = 1680 ticks: 13199 - 11520 = 1679 = 6 beats + 239.", MIXED, "mixed: "),
        at(13200, 5, 1, 0, "Bar 5 starts one 1680-tick bar after the 7/16 change.", MIXED, "mixed: "),
        at(14880, 6, 1, 0, "The 5/32 change at 11520 + 2 x 1680 = 14880 is the downbeat of bar 6.", MIXED, "mixed: "),
        at(15000, 6, 2, 0, "5/32 counts 120-tick beats: 15000 is beat 2 of bar 6.", MIXED, "mixed: "),
        at(16079, 7, 5, 119, "A 5/32 bar lasts 600 ticks: 16079 - 14880 = 1199 = 1 bar + 4 beats + 119.", MIXED, "mixed: "),
        start(2, 2, 5760, "Bar 2 of 2/2 starts at 3840; its second half-note beat is 1920 later.", MIXED, "mixed: "),
        start(3, 1, 7680, "Bar 3, the 1/1 bar, starts at the change.", MIXED, "mixed: "),
        start(5, 7, 14640, "Bar 5 starts at 13200; beat 7 of 7/16 is 6 x 240 later.", MIXED, "mixed: "),
        start(7, 5, 15960, "Bar 7 starts at 14880 + 600 = 15480; beat 5 of 5/32 is 4 x 120 later.", MIXED, "mixed: "),
        invalid("a 1/1 bar has no beat 2", "Bar 3 is in 1/1: one whole-note beat.", "tick", MIXED, "beat_outside_bar",
                bar=3, beat=2),
        invalid("a 5/32 bar has no beat 6", "Bar 6 is in 5/32: five 120-tick beats.", "tick", MIXED, "beat_outside_bar",
                bar=6, beat=6),
    ]}


def evaluate(case, world):
    try:
        if case["op"] == "position":
            got = timemodel.position(case["input"]["tick"], case["meter"])
        else:
            got = {"tick": timemodel.tick_at(case["input"]["bar"], case["input"]["beat"], case["meter"])}
    except timemodel.TimeModelError as error:
        got = {"invalid": error.code}
    return got, case["expected"]
