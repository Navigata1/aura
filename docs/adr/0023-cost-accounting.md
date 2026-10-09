# Every job logs its cost and time, and cost is reported per keeper

Status: accepted (2026-10-09). From D-23, extended by O-09 (the burst ledger, ADR-0030).

Per-candidate rental costs are small but uncertain. INFERRED estimates on a 4090 at $1.10/h are about $0.002–0.003 for
ACE and $0.009–0.022 for YuE2 per candidate; MiniMax's $0.03–0.13 is COMMUNITY-derived on different hardware. Cold
starts, model loads and idle seconds are billed, and rental prices are snapshots.

**Decision.**

- Every job records its compute cost (zero for local work, the settled amount for burst), cold and warm wall time as
  measured by the worker SDK (MEASURED-LOCAL by construction), its placement and its host class.
- **Keeper cost** is the reporting denominator: candidates per keeper (re-rolls included), compute cost and listening
  time per keeper.
- Rent before buying. Rental figures carry their snapshot date, and quotes use the live rate (ADR-0030).

**Why.** Per-candidate costs hide the real price of a song, which is every attempt and every minute of listening behind
one keeper (C44; GSV-50, GPT's cost model with accepted output as the denominator).

## Consequences

"Cost per song" is never shown without a keeper denominator. Narration, when it arrives, reports per approved finished
hour.

**Reverse if:** nothing foreseen reverses this.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C44; §4.8; §6 D-23.
[evidence-register.json](../research/evidence-register.json) V-cost-2, V-cost-3, X-24.
[feature-inventory.md](../research/feature-inventory.md) C9, J12.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-09. [architecture.md](../spec/architecture.md) §4.8,
§7.5.
