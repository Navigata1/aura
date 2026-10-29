# T01 independent review — local preparation accepted

Date: October 29, 2026. Baseline: integration `79cd9aff1ee239bd0422e684b4e8d58b73bb7c0f`. Reviewed the current external worktree against that baseline, including staged and working contents. No application/source edits by this reviewer. Review artifacts remain outside the repository.

## Standards

No open code correctness findings remain in the reviewed foundation scope. The implementation corrected the substantive issues found during review:

- Storage preflight now requires APFS ownership and a recognized external physical bus; internal, nested-image, missing-protocol and unknown-protocol hosts refuse. Cache/temp symlink escapes and inherited `UV_PROJECT_ENVIRONMENT` refuse before exports or directory creation.
- Control-runtime license traversal preserves requested extras, revisits expanded requirements, and checks installed versions and disallowed license metadata. An independent synthetic installed-metadata counterexample originally passed while hiding an LGPL extra; it now refuses and names the denied dependency. See `review-extra-reproduction.txt` and `review-extra-after-fix.txt`.
- Web inventory now follows emitted modules rather than production dependency declarations. A dev-only bundled package is included. Generated Vite/Rolldown runtimes resolve to installed package licenses; unresolved modules refuse. Chunk hashes and emitted-JavaScript coverage bind the inventory to the build.
- Neutral naming checks cover lowercase identifiers/formats while retaining a narrow documentation-filename exception. GitHub Actions use immutable revisions and checkout does not persist credentials.

The final real Mac preflight and synthetic refusal tests pass. These checks are preparation guards, not T19 storage durability qualification or a complete supply-chain/security audit.

## Spec

Independent full gate passed after the final physical-bus correction. Evidence: `independent-final-all-files-gate.log`.

- Fresh tracked-file contract copy: 49 schemas, 306 valid records, 59 reference rules; registry regeneration and 105-ticket DAG pass. Required previously ignored store fixture is now tracked. Registry-derived snapshot changes are documented as T01's bounded regeneration reconciliation; legacy fixtures are unchanged.
- 36 Python tests plus four physical-host subtests; two Vitest tests; one Node bundle-inventory test; actual TypeScript/Vite build.
- Policy scan: 558 tracked files, zero violations. Installed/bundled runtime inventory: five web packages, all permitted; control currently has no third-party runtime dependencies.
- Product constant and file-discovered command/doctor sections work. The rendered web page explicitly remains a foundation placeholder.

T01 is not complete: Navigata1 privacy confirmation, enforceable required checks (GitHub returned plan-related HTTP403), hosted Linux/macOS/Windows runs, and actual nightly evidence remain open. Nightly definition is not a scheduled run; only the owner may advance default `main`. The final CLAUDE cold-start amendment now names Extreme SSD and prioritizes October 29's decision.

Disposition: suitable for a draft PR after the parent runs commit-aware checks. No merge, release, music-quality, playback, real-engine, owner-listening or paid-run approval is conferred. No open code findings; external/spec evidence gates remain incomplete.
