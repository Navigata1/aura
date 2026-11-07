# C01 validation — October 29, 2026

Scope: unsupported benchmark-conclusion containment and typed preregistration lookup. No real model, hardware listening, owner verdict, paid run or per-OS playback validation occurred.

- Implementer: four failing-before/passing-after regression cycles.
- Current local contract gate: 49 schemas, 316 valid-by-kind records, 94 negative scenarios, 8 valid scenarios, 26 status vectors; 59 rules pass.
- Registry regeneration: byte-identical. Ticket graph: 105 tickets passes.
- Independent reviewer: 288 status combinations and 16 admission combinations pass, including both benchmark kinds, pass/fail/inconclusive outcomes, synthetic variants, wrong/absent gates, host/revision scope and preserved smoke behavior. Typed MelodySpec/SongSpec substitution negatives and legitimate mixed-profile/inconclusive positives pass. No new standards/spec defect found within the bounded scope.
- Root independently reran the contract, registry and ticket gates successfully on the local worktree.

**Known inherited clean-checkout blocker:** the baseline ignores `contracts/fixtures/world/store/store.json`; local generation masks its absence from Git. A clean deliverable copy fails one fixture-regeneration check. T01 #2 fixes the ignore rule and tracks the generated fixture. C01 #3 remains blocked by T01 and must rerun from the updated integration base and hosted CI before merge. Local green is not a clean-checkout or CI pass.

Full benchmark functionality remains unavailable. C02 #4 must implement the result binding described in the adjacent contract-fix document before promotion or concluded failure is accepted. No merge or completed capability is claimed here.

Detailed logs and reviewed-file hashes are retained on the studio volume under `evidence/C01/`, including `independent-review.md`, `reviewer-probes.log`, `deliverable-tree-gate.log` and `root-gates.txt`. They are local execution evidence, not store evidence records.

## November 6 integration update

The foundation is merged at `e421699890e80c5fffcc3f36659b3ba4e1587db2`; this branch now includes that actual integration base. The ignored-store-fixture blocker described above is historical. Fresh clean-tree, full software gate, hosted CI and separate independent review are required on this updated branch before merge. P01 email privacy was rechecked enabled; the repository stays private under the revised CI-and-review merge policy.

Fresh full local gate on the updated branch passes (November 6): clean tracked contracts, registry, ticket graph, 37 Python tests, two Vitest tests, two Node tests, production build, policy and actual runtime-license inventory. Log: `/Volumes/STUDIO/evidence/C01/nov06-full-gate.log`. Hosted CI and independent review remain the pre-merge checks. Foundation integration run `42341504038` passed all three hosted operating systems; it is a push run, not scheduled-nightly evidence.
