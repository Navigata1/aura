# C01 — contain unsupported benchmark conclusions

Implementation scope, 2026-10-29. This records an implementation limitation of ADR-0027, not a replacement of its
intended status policy. Tests use JSON stand-ins and hypothetical records only; no listening, measurement or owner
act occurred. Root audit findings A-01/A-02/A-03 are the source.

## What C01 establishes

- Evidence preregistration hashes resolve to records whose kind is `prereg`; generic known content hashes do not count.
- Admission refuses concluded `benchmark` and `hum-benchmark` records (both pass and fail) as unsupported. This is not a
  failed benchmark and must never be shown as such. Inconclusive records are allowed but change no status.
- The pure fold ignores both kinds, including callers that supply `known_preregs`. Neither an absent gate nor an
  existing verdict, checks list or preregistration hash can confer a benchmark status or disable a profile.
- The plan's unbenchmarked label remains until supported, validated conclusions exist.
- Ordinary mixed-profile listening remains allowed. Smoke's same-profile constraint is not imposed on comparisons.

All existing schema shapes remain accepted by schema validation. The reference rule is the refusal boundary, not a
silently incompatible schema revision. There are no released frozen fixtures; the incorrect benchmark status golden
changes its expectation. T02's additions-only fixture policy applies to its own work, not this separately reviewed
correctness fix.

## Required follow-on contract before benchmark promotion returns

Create a dedicated contract ticket coordinated with T02 (concluded route standing) and blocking T08's benchmark
admission/promotion path. Do not restore the old transition by checking that a hash or verdict merely exists.

1. Define a closed, immutable concluded-result record and its links to the exact preregistration, set, gate and
   subject profile revisions and host classes. Define engine benchmark and hum benchmark result types explicitly;
   the current eval-set schema covers only smoke and 48-brief engine sets, not the full hum protocol.
2. Resolve and canonical-hash-check the preregistration by kind; validate its declared briefs, asset hashes, pins,
   thresholds, budgets and quota against the result. Reject unknown, ambiguous, duplicated, substituted or unrelated
   references. Prove preregistration committed before rendering, not only before the result timestamp.
3. Bind every result case to its preregistered brief, candidates/corrections, jobs, artifact provenance, exact profile
   revisions and host classes. Legitimate mixed-profile comparisons must pass without crediting another profile or
   host. Suno sources remain outside evaluation.
4. Define deterministic threshold evaluation and quota semantics (sessions, repeat-pair fraction, listening/correction
   coverage, repeat reliability and excluded/unfinished cases). Thresholds are the preregistered values, never values
   supplied after observing output. Unknown metrics fail closed; short quota yields inconclusive, not pass or fail.
5. Resolve each required verdict/correction to its owner act and matching audition/case, enforce uniqueness and
   coverage, and distinguish inconclusive from concluded fail. Mere existence of a verdict is insufficient.
6. Feed the same validated conclusion into registry admission, the pure status fold, route standing and plan labels.
   A supported, concluded failure may disable under ADR-0027; an unsupported/incomplete result cannot. Do not add a
   caller-set `validated: true` field or an untrusted list of evidence ids as a substitute for validation.
7. Add positive goldens for engine and hum benchmark conclusions, including a valid mixed-profile comparison and
   exact host/revision scoping; add independent negatives for each binding, changed threshold, insufficient quota,
   unrelated existing verdict/preregistration, duplicate case/verdict, unknown metric, wrong result, synthetic data,
   missing gate and mutated hash. Demonstrate that replacing pass with unsupported/inconclusive neither promotes nor
   demotes, and that a genuine concluded fail has the documented terminal effect.
8. Reconcile the additive schema version, legacy readers and T02 consumers before codegen or T08 adopts the contract.
   Remove C01's refusal and restore promotion only in the same reviewed change that passes these golden gates.

## Evidence classes

Local contract tests: synthetic/hypothetical JSON only. Hosted CI, real hardware execution, owner listening, paid runs
and real per-OS playback: none in C01. Benchmark capability remains unavailable; acoustic quality remains unmeasured.
