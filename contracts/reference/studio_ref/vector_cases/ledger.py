"""Ledger hand-derived golden cases and public reference evaluator."""
from studio_ref import ledger
from studio_ref.fixture_support import SV, owner
from decimal import Decimal

KIND = "fixture.ledger"

def build(profiles):
    def le(seq, at, typ, usd, month="2026-10", run="br_x"):
        return {"kind": "ledger-entry", "schemaVersion": SV, "seq": seq, "at": at, "entry_type": typ,
                "run_id": run if typ in ("reserve", "settle", "release", "overrun") else None, "usd": usd, "month": month,
                "note": "vector", "act": owner("acknowledge_overrun", at) if typ == "overrun_acknowledged" else None}

    def lc(name, entries, before, ceiling, mtd, allowed, blocks, why, month="2026-10", cap="25.00"):
        return {"name": name, "derivation": why, "entries": entries, "month": month, "before": before, "ceiling_usd": ceiling,
                "cap_usd": cap, "expected": {"month_to_date_usd": mtd, "allowed": allowed, "overrun_blocks": blocks}}
    ledger_vec = {"kind": "fixture.ledger", "schemaVersion": SV, "cases": [
        lc("empty month", [], None, "0.38", "0.00", True, False, "Nothing spent; 0.00 + 0.38 <= 25.00."),
        lc("open reservation and a fixed line", [le(1, "2026-10-02T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-01T00:00:00Z", "fixed_line", "2.00")],
           None, "0.38", "2.38", True, False, "An open reserve counts at its ceiling: 0.38 + 2.00."),
        lc("settled below the reservation", [le(1, "2026-10-02T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-02T10:20:00Z", "settle", "0.21")],
           None, "0.38", "0.21", True, False, "The settle closes the reserve; only 0.21 counts."),
        lc("released", [le(1, "2026-10-02T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-02T10:01:00Z", "release", "0.00")],
           None, "0.38", "0.00", True, False, "A released reserve counts nothing."),
        lc("month boundary", [le(1, "2026-09-30T23:50:00Z", "settle", "10.00", month="2026-09", run="br_sep"), le(2, "2026-10-01T00:10:00Z", "reserve", "1.00")],
           None, "0.38", "1.00", True, False, "September's settle is not in October (UTC calendar month, T-09)."),
        lc("before a quote", [le(1, "2026-10-02T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-02T11:00:00Z", "fixed_line", "5.00")],
           "2026-10-02T10:30:00Z", "0.38", "0.38", True, False, "Only entries strictly before the quote count."),
        lc("over the cap", [le(1, "2026-10-03T10:00:00Z", "fixed_line", "24.80")], None, "0.38", "24.80", False, False,
           "24.80 + 0.38 = 25.18 > 25.00: refused."),
        lc("exactly at the cap", [le(1, "2026-10-03T10:00:00Z", "fixed_line", "24.62")], None, "0.38", "24.62", True, False,
           "24.62 + 0.38 = 25.00 <= 25.00: allowed."),
        lc("overrun not double counted", [le(1, "2026-10-04T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-04T10:30:00Z", "settle", "0.60"),
                                          le(3, "2026-10-04T10:30:01Z", "overrun", "0.22")],
           None, "0.38", "0.60", True, True, "The settle holds the actual 0.60; the overrun marks the 0.22 excess and blocks leases."),
        lc("overrun acknowledged", [le(1, "2026-10-04T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-04T10:30:00Z", "settle", "0.60"),
                                    le(3, "2026-10-04T10:30:01Z", "overrun", "0.22"), le(4, "2026-10-04T11:00:00Z", "overrun_acknowledged", "0.00")],
           None, "0.38", "0.60", True, False, "Jon's acknowledgement (an owner act) lifts the block."),
        lc("upward reconciliation", [le(1, "2026-10-04T10:00:00Z", "reserve", "0.38"), le(2, "2026-10-04T10:30:00Z", "settle", "0.30"),
                                     le(3, "2026-10-31T09:00:00Z", "reconcile_adjustment", "1.10", run=None)],
           None, "0.38", "1.40", True, True,
           "The invoice shows 1.10 the ledger never booked (an orphan pod's storage): 0.30 + 1.10 = 1.40 counts, and new leases wait for Jon."),
        lc("upward reconciliation acknowledged", [le(1, "2026-10-04T10:30:00Z", "settle", "0.30", run="br_y"),
                                                  le(2, "2026-10-31T09:00:00Z", "reconcile_adjustment", "1.10", run=None),
                                                  le(3, "2026-10-31T09:05:00Z", "overrun_acknowledged", "0.00", run=None)],
           None, "0.38", "1.40", True, False, "Acknowledging lifts the block; the adjustment still counts toward the cap."),
    ]}
    return ledger_vec

def evaluate(case, world):
    mtd = ledger.month_to_date(case["entries"], case["month"], case["before"])
    return {"month_to_date_usd": f"{mtd:.2f}",
            "allowed": ledger.cap_allows(mtd, Decimal(case["ceiling_usd"]), Decimal(case["cap_usd"])),
            "overrun_blocks": ledger.overrun_blocks(case["entries"])}, case["expected"]
