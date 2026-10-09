"""Ledger arithmetic for the monthly cap (O-09, ADR-0030, T-09). All amounts are Decimal from usd strings.

month_to_date = settle amounts + open reserves at their ceilings + fixed lines + reconciliation adjustments, for one
UTC calendar month, counting only entries recorded strictly before `before` when given. A reserve is open until its run
has a settle or a release. Overrun entries mark an excess that the settle amount already contains, so they add nothing.
A reconcile_adjustment books provider charges the ledger never saw (a pod the reaper missed, stopped-pod storage, a
cost revised after settlement, network-volume fees): it adds to month-to-date and, like an overrun, blocks new leases
until Jon acknowledges it. Reconciliation may lower only amounts settled at the ceiling, through a settle entry.
"""

from __future__ import annotations

from decimal import Decimal


def month_to_date(entries: list[dict], month: str, before: str | None = None) -> Decimal:
    seen = [e for e in sorted(entries, key=lambda e: e["seq"]) if before is None or e["at"] < before]
    closed = {e["run_id"] for e in seen if e["entry_type"] in ("settle", "release")}
    total = Decimal("0")
    for e in seen:
        if e["month"] != month:
            continue
        if e["entry_type"] in ("settle", "fixed_line", "reconcile_adjustment"):
            total += Decimal(e["usd"])
        elif e["entry_type"] == "reserve" and e["run_id"] not in closed:
            total += Decimal(e["usd"])
    return total


def cap_allows(mtd: Decimal, ceiling: Decimal, cap: Decimal) -> bool:
    return mtd + ceiling <= cap


def overrun_blocks(entries: list[dict]) -> bool:
    blocked = False
    for e in sorted(entries, key=lambda e: e["seq"]):
        if e["entry_type"] in ("overrun", "reconcile_adjustment"):
            blocked = True
        elif e["entry_type"] == "overrun_acknowledged":
            blocked = False
    return blocked
