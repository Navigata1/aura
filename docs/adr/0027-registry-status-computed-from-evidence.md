# Profile status is computed from evidence records per profile revision and host class, and is never stored or promoted by hand

Status: accepted (2026-10-09) with the v1 architecture. It amends D-01, which had a stored status field.

The owner's rule is that nothing is done until a check that could fail has passed. A stored status survives a pin bump,
and a hand-written `promote()` invites claims without evidence.

**Decision.**

- `profile_revision = sha256(code commit + weights manifest + env lock or image digest + SDK version)`.
- Status is a pure fold over evidence records for one `(profile_revision, host_class)`:
  - `declared → installed` needs an install record and a conformance pass at that revision and host class;
  - `installed → smoke-passed` needs the profile's declared smoke gate: a smoke record whose `checks` list every check
    the gate declares, each passing, with `owner_not_garbled` answered by an owner-ui verdict on that revision's own
    smoke candidates;
  - `smoke-passed → benchmarked` needs a preregistered benchmark gate;
  - any later failing record on the same revision and host class gives `disabled`;
  - a pin change is a new revision: with no records at it, it computes to `declared`, and it reaches `installed` only
    after its own install and conformance records.
- `Registry.record(EvidenceRecord)` is the only write. It rejects a record whose gate needs an unknown preregistration
  hash, a listening gate without owner verdicts, synthetic evidence aimed at a benchmark gate, and a smoke record missing
  a declared check or its owner verdict.
- **Synthetic evidence** (from NeutralVoice or FakeEngine) may satisfy a smoke gate only where that gate allows it,
  such as the transcriber's synthetic floor or a `test_only` profile. It never satisfies a benchmark gate.
- **Everyday product verdicts** are `listening-unregistered` evidence. They are shown per route and never change a
  status.
- The product view (`GET /api/v1/registry?audience=product`) omits anything below smoke-passed and never shows a
  published claim as measured. A generation naming an unpromoted profile gets `409 profile_not_promoted` before
  anything loads.
- Evidence records (`evidence/1`) hold the check, subject, revision, host class, result, MEASURED-LOCAL values, a
  synthetic flag, hashed attachments and, where needed, the preregistration hash. The store is the system of record;
  `docs/evidence/` holds hash-checked exports (each record with the canonical JSON of the verdicts and preregistrations
  it cites, never audio), and the contract gate runs every reference rule over them, so a hand-committed passing record
  cannot become a status.

**Why.** Evidence, not claims. This keeps the capability statuses of JOVRA ADR-0004 and makes promotion impossible to
fake.

## Consequences

Evidence takes real work: ACE needs install, conformance, smoke and Jon's "not garbled" check before it appears.
Capability entries (`studio.playback` per OS) use the same fold.

**Reverse if:** nothing foreseen reverses this.

Evidence: [architecture.md](../spec/architecture.md) §4.4, §6.3, §6.4, §13.2, §13.4 (T-03, T-04).
[RECONCILIATION.md](../research/RECONCILIATION.md) §6 D-01, D-10. Pattern: JOVRA ADR-0004.
