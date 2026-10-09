# The Suno boundary is data on the import, enforced at admission, in the audition and at the store

Status: accepted (2026-10-09) with the v1 architecture. It implements ADR-0021 (O-08).

A rule that lives only in prose is a claim. The Suno boundary has to fail a check when it is crossed.

**Decision.** An `imported_mix` whose source service is Suno carries `allowed_uses = [listen, loudness_measure,
dsp_finish]`, plus only what an owner-signed `risk-acceptance/1` record names, which the schema limits to engine,
conditioning, separation, edit or conversion input. Every import is itself an owner act (`attest_import`), its uses fixed
by its source, and ingest detects Suno's embedded marks, forcing source Suno. Enforcement:

- `Registry.admit` checks every input's `allowed_uses` against the task, so a Suno import is refused as cover, repaint,
  extend, conversion or separation input before anything loads;
- `Audition.open` refuses it as an arm, and evaluation preregistration as a reference or anchor, whatever risk
  acceptances exist;
- the store's write path refuses any artifact derived from it by a use it does not allow.

DSP finishing preserves the import's embedded provenance metadata, and the export manifest carries the imported terms
(`import-terms/1`). Risk acceptances are owner acts (ADR-0031).

**Why.** Each enforcement point is a negative test that can fail, which turns ADR-0021 from a policy into evidence.

## Consequences

StudioHarness tests that an imported Suno mix is refused as cover input and as an audition arm (P1-8), and that any
generative operation on a DSP-finished import is refused (P5-6).

**Reverse if:** ADR-0021 changes.

Evidence: [architecture.md](../spec/architecture.md) §4.4 (use policy), §6.1 (Suno boundary tests), §10, §11 (P1-8,
P5-6). [RECONCILIATION.md](../research/RECONCILIATION.md) §2 GAP-07; §6 D-21.
