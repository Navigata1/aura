# Paid burst runs: a live-rate quote, Jon's approval per run, a reservation at the ceiling before provisioning, settlement at the ceiling when billing is missing, and a $25 monthly cap

Status: accepted (2026-10-09). Owner decision O-09: a standing cap of $25 a month, every paid run needs Jon's explicit
yes, and every run is logged against the cap before it starts. From the v1 architecture §7.5. RunPod pod rates, proxy
limits, whether an in-container shutdown stops billing, provider spend limits and private-registry pulls are
UNVERIFIED; each is a spike ticket in P3.

In tier 4, YuE2 runs only on rented GPUs. Burst costs can leak through orphan pods, cold starts, billed model loads,
rate drift and retries.

**Decision.** Paid jobs move `queued → awaiting_approval → preparing → …`:

1. **Quote.** A job placed on `burst` gets a quote containing:
   - the **live** provider rate and its timestamp (a dated snapshot only as a labelled fallback);
   - `max_minutes` = boot + weights download + the sum of job estimates + a teardown margin. Each estimate is
     MEASURED-LOCAL history on that GPU class where it exists, and otherwise the VENDOR figure × 3, labelled
     "unmeasured";
   - the **ceiling** = `max_minutes` × the highest rate in the GPU-class fallback list, plus fixed lines;
   - the egress list by hash (for R1: the ABC, the lyrics plan and the job parameters; never Suno audio, never
     reference standards) and the lane check.

   `quote_sha256` covers all of it.
2. **Cap check.** Month-to-date (UTC calendar month, shown in local time) = settled actuals + open reservations at
   their ceilings + fixed monthly lines. If month-to-date plus the ceiling would exceed **$25.00**, the quote is
   refused, with no override in the flow. Raising the cap is an owner act in Settings and is recorded.
3. **Approval**, an owner act in the UI only. The dialog fetches a challenge nonce and shows the provider, GPU class,
   rate and timestamp, job list, ceiling, month-to-date, cap, remainder and egress list. The approval is single-use,
   bound to the quote hash, and expires 15 minutes after the quote. One approval covers one request's burst jobs. Any
   change to the job list, or a tier switch, needs a new quote and a new yes. The CLI, the eval harness, paid
   conformance runs and agents can request quotes but can never approve them.
4. **Reservation before provisioning.** A ledger `reserve` entry at the ceiling is fsynced in the same transaction as
   the cap check.
5. **Provision.** A RunPod secure-cloud pod starts from the pinned yue2 image digest, tagged `studio-burst` plus the run
   id, with a one-run 256-bit bearer token (only its hash is stored), a hard maximum duration, an in-image `shutdown -h`
   deadline, and weights downloaded at boot under the recorded license acceptance. A conformance ping runs before the
   first job.
6. **Run.** The Conductor polls through the provider's HTTPS proxy with short requests.
7. **Settle.** The pod is terminated and termination is confirmed through the provider API. The run settles at the
   provider-reported cost or, when billing is missing, **at the ceiling** (`settled_at_ceiling`); monthly
   reconciliation may lower only an amount settled at the ceiling, and books any invoice charge the ledger never saw (a
   machine the reaper missed, stopped-machine storage, a revised cost, network-volume fees) as a `reconcile_adjustment`
   that counts toward the cap and blocks new leases until Jon acknowledges it. A cost above the reservation writes an `overrun`, which blocks new leases until
   Jon acknowledges it (an owner act).
8. **Reaper**, at startup and every 5 minutes: it terminates any tagged pod without an open run and any run past its
   hard maximum, then settles it.
9. **No automatic paid retry.** A retry needs a new quote and a new approval.

Backstops: the in-image deadline (a second lock until the billing spike proves it), a provider-side spend limit that
Jon sets by hand, and monthly reconciliation against the invoice.

**Why.** O-09. Model loads and idle time are billed (C44), so the only safe accounting is a conservative ceiling
reserved before any spend.

## Considered Options

- **Settling at an INFERRED runtime × a snapshot price.** Rejected: it understates cost (T-07).
- **Approval from any authenticated client, or a terminal y/N prompt.** Rejected: it widens the owner-act surface
  (ADR-0031, T-08).
- **Two burst adapters (RunPod and Vast) at once, or Tailscale inside pods.** Rejected for now: prove one adapter
  first. Vast becomes an adapter only on ledger evidence.
- **A network volume for weights.** Adopted only when measured boot-plus-download time shows it is cheaper (T-13).

## Consequences

Every step runs for $0 against FakeBurstProvider in CI (TB2). Burst runs (`burst-run/1`) and ledger entries
(`ledger-entry/1`) are append-only. A declined run labels the plan "ACE-only: burst declined". Pods use secure cloud
rather than community hosts, because unreleased melody and lyrics leave the machine.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The hard maximum is always computed from boot, weights download, the job estimates and the teardown margin (INFERRED until the YuE2 smoke record supplies measured times), never hard-coded, and the GPU-class fallback list names only classes with a smoke-passed record. Jon keeps the provider's prepaid balance at or below the remaining cap with auto top-up off, the external backstop. The RunPod key sits in a presence-gated keychain item the self-hosted runner's user cannot read.

**Reverse if:** the owner changes the cap or the approval rule. The mechanism stays.

Evidence: [OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-02, O-09.
[architecture.md](../spec/architecture.md) §4.5, §7.5, §7.6, §9.1, §12, §13.4 (T-07, T-08, T-09, T-12, T-13), §11
(TB2, P3). [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C44; §4.8; §6 D-03, D-23.
[evidence-register.json](../research/evidence-register.json) V-cost-2, V-cost-3. Pattern: JOVRA ADR-0019 (quote,
consent, cap, reservation).
