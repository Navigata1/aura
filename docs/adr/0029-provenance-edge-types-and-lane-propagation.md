# Lane and license obligations flow only along audio-ancestry edges, never along analysis edges, and are enforced at seven points

Status: accepted (2026-10-09) with the v1 architecture. It implements O-06 and ADR-0011, and resolves tension T-02.

Demucs, allowed only in the individual and research lanes, is the first internal separator for measuring adherence.
If analysis passed its lane to whatever it measured, every ACE keeper measured with Demucs would become
individual-only.

**Decision.**

- Parent edges are typed: **`derived_from`** (the audio came from that audio), **`converted_from`** (the same audio at
  another rate or in another format) and **`analyzed_by`** (a measurement read it).
- An artifact's `eligible_lanes` is the intersection of the allowed lanes of every component in its license chain with
  the `eligible_lanes` of its `derived_from` and `converted_from` parents. **`analyzed_by` never propagates.** The
  license chain and AI-disclosure obligations likewise come from audio ancestry only.
- Analysis jobs are still admitted in the project's lane, so Demucs cannot run at all in an LLC project. There,
  adherence reads "unmeasured (no LLC separator yet)".
- **Seven enforcement points**, each with a negative test:
  1. **Project lane**, an owner act: a lane change re-checks every artifact in the project.
  2. **Admission** at `Conductor.submit`.
  3. **Worker refuse-before-load.**
  4. **The store's write path.**
  5. **Export**, over the closure.
  6. **Evaluation preregistration**: LLC briefs never name YuE2, Demucs or a non-commercial scorer.
  7. **Burst egress**: a quote shows the lane check, and a quote for an LLC project's YuE2 job is never created.
- The same points enforce **use policy**: a `listening_only` reference is never engine input, and a Suno import's
  allowed uses are fixed (ADR-0036).

**Why.** Without typed edges, either analysis leaks a lane into keepers, or analysis must escape the lane check.
This design does neither.

## Consequences

An LLC export of an ACE keeper that an individual-only separator analyzed is allowed. An LLC export of any closure
containing non-commercial audio is refused. In CI, `fake-nc` and `fake-separate` stand in for the real non-commercial
components.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Records carry lanes too: a MelodySpec drafted by a lane-restricted transcriber (SwiftF0 or Basic Pitch) carries that transcriber's eligible lanes and license chain, every revision built on it inherits them, and the lane change, branching and job admission check them (rule `lane.record_eligible`). Imports carry lanes from their owner-attested terms: a DAW bounce inherits the eligible lanes and license chains of the studio exports it contains (rule `use.import_terms`). Exports list their closure's release blockers (rule `release.manifest_blockers`).

**Reverse if:** a license is found to bind analysis outputs themselves, for example terms that forbid commercial use of
a model's measurements. `analyzed_by` would then carry that component's lanes.

Evidence: [architecture.md](../spec/architecture.md) §1, §5 (`artifact/1`), §10, §13.2, §13.4 (T-02), §11 (P1-8).
[RECONCILIATION.md](../research/RECONCILIATION.md) §4.3; §6 D-06, D-11.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-06.
