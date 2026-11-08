# C02 — bind concluded benchmarks before enabling promotion

Issue #4, open. This file registers the contract-fix ticket id so `contracts/consumers.json` can name C02 as a
consumer; it adds no scope. The acceptance is issue #4 and the follow-on criteria in
[C01-benchmark-conclusions.md](C01-benchmark-conclusions.md) ("Required follow-on contract before benchmark promotion
returns"). The sequence is in [T02-continuation-sequencing.md](../T02-continuation-sequencing.md) (step 3).

C02 consumes the T02b inputs (issue #77): `benchmark-prereg/1`, `benchmark-membership/1`, `evidence-binding/1` and the
`fixture.binding` vectors of `contracts/reference/studio_ref/binding.py`. Those only report whether inputs bind.
Until C02 lands, `evidence.gates` refuses concluded benchmark and hum-benchmark records, the status fold ignores them,
and nothing is concluded, promoted or demoted (C01).

## C02 to-do recorded by the T02b review (2026-11-07)

These come from the independent review of PR #130 (P-N1, P-N2, P-N6, S-N2). T02b leaves them to C02.

- **Resolve the evidence record (P-N1).** `binding_findings` never reads `evidence_id`, so the valid bindings name
  `ev_bench_ace` and `ev_hum_pyin`, which do not exist. Resolve it and check its `check` and `gate_id`, subject,
  profile revision, host class, `prereg_sha256` and `synthetic: false` against the binding.
- **Commit order beyond the listed jobs (P-N2).** Commit order covers only the jobs the membership lists, so a
  candidate from an unlisted job queued before the commit binds cleanly. Bind each candidate to its arm's job, and tie
  each hum MelodySpec to its transcription job (`melody-spec` `source.transcription.job_id`). The hum vectors hold no
  `melody-spec` records yet.
- **Refusals still missing (P-N6):**
  - a threshold on a metric the protocol does not declare;
  - a membership case listed twice;
  - world-level brief existence and lane checks for `benchmark-prereg` (`lane.eval` covers `prereg/1` only; T02b checks
    a case's brief by content hash and lane, inside `binding_findings` only);
  - synthetic hums;
  - verdict uniqueness across cases.
- **The whole set.** Require all 48 briefs of the benchmark set for `benchmark-48`. The benchmark-48 goldens hold one
  brief and will change.
- **The conclusion.** Evaluate quota, coverage, repeat pairs and thresholds deterministically (unknown metrics fail
  closed), apply the hum decision rule per lane, wire typed resolution into `evidence.gates` and registry admission, and
  only then conclude, promote or demote.
- **GLOSSARY gap (S-N2), for `/domain-modeling`.** "Subject", "membership" and "evidence binding" have no GLOSSARY
  entries. A binding's `subject` (`profile_id`, `profile_revision`, `host_class`) has a different shape from
  `evidence/1`'s `subject` (`subject_type`, `subject_id`, with revision and host class beside it).
