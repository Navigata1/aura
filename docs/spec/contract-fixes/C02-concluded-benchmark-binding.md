# C02 — bind concluded benchmarks before enabling promotion

Issue #4, open. This file registers the contract-fix ticket id so `contracts/consumers.json` can name C02 as a
consumer; it adds no scope. The acceptance is issue #4 and the follow-on criteria in
[C01-benchmark-conclusions.md](C01-benchmark-conclusions.md) ("Required follow-on contract before benchmark promotion
returns"). The sequence is in [T02-continuation-sequencing.md](../T02-continuation-sequencing.md) (step 3).

C02 consumes the T02b inputs (issue #77): `benchmark-prereg/1`, `benchmark-membership/1`, `evidence-binding/1` and the
`fixture.binding` vectors of `contracts/reference/studio_ref/binding.py`. Those only report whether inputs bind.
Until C02 lands, `evidence.gates` refuses concluded benchmark and hum-benchmark records, the status fold ignores them,
and nothing is concluded, promoted or demoted (C01).
