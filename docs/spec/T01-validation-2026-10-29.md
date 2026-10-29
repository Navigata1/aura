# T01 foundation validation — October 29, 2026

This is a buildable scaffold and guarded development environment, not a music-generation application. The control API, audio playback, model workers and quality evaluation remain future tickets.

## Local software evidence

The complete local gate (`uv run --frozen python scripts/ci/run.py --files-only`) passes from the dedicated external volume with pinned Node 22.22.3 and managed Python 3.12.13. Independent review reran it after storage and license-graph corrections.

- Fresh tracked-file copy: 49 schemas, 306 valid-by-kind records, 59 reference rules; registry regeneration and 105-ticket DAG pass. The previously ignored required store fixture is now tracked.
- 37 Python tests plus 4 subtests, 2 Vitest tests and 2 Node bundled-module provenance tests pass.
- Web production build passes. The emitted module inventory is bound to chunk hashes and checks five third-party package entries. Control currently has no third-party runtime dependencies; future additions are traversed including requested extras.
- Policy scanner passes on the delivered tracked tree and emitted bundle. Planted negatives cover the declared contact/commit, secrets, licensing, product naming, weights and audio rules. This is bounded rule coverage, not a claim that all possible secrets or attacks are detected.
- Guard negatives cover a missing mount, low space, internal/nested/unknown backing, cache symlink escape, inherited workspace override and unverified bundle/runtime dependency metadata.
- Source research checked 25 pinned upstream license sources. React, TypeScript and libsndfile source hashes were independently re-fetched. Source licensing and installed distribution checks are distinct.

Detailed local logs live on STUDIO under `evidence/T01/` and `evidence/T01-root-final-local-gate.log`. Independent review found no open code correctness defect within T01's scaffold scope after the fixes. Commit-aware checks and hosted runs must be recorded against their exact commit, separately from these preparation results.

## Explicit acceptance still pending

1. P01: read-only browser inspection found Keep email private enabled but Block command line pushes exposing email disabled. The owner must enable the latter. No personal address is retained in repo evidence.
2. GitHub refused private integration branch protection with HTTP 403. Required-check enforcement is unavailable under the current account plan. No repository visibility, subscription or default-branch change was made.
3. Hosted checks are separate from the local result. The foundation PR runs the same reusable gate on Linux, macOS and Windows to obtain initial OS evidence before integration has its workflows; later ticket PRs retain the planned Linux fast gate. CI config alone is not a passing run.
4. GitHub scheduled workflows run from default main. Main remains owner-release-only. A configured nightly schedule or a manual equivalent is not an observed scheduled run; first scheduled-run evidence follows an owner release unless the owner revises the acceptance sequence.

No real hardware engine test, owner listening verdict, paid GPU run, real per-OS playback, or model-license acceptance occurred. The interim STUDIO volume holds only reproducible development data until T18/T19 qualify storage for irreplaceable data. T01 stays open until its remaining acceptance conditions are satisfied or explicitly revised.

## Bounded specification reconciliations

The required stack-license registry update necessarily changes two generated invalid-record snapshots; no schema or reference semantics change in T01. A missing generated store fixture is added with a narrow ignore exception. The old literal product name in a ticket diagnostic is replaced with neutral wording. The separate C01 contract PR contains the benchmark correction. See the stack-verification note for the exact fixture paths and source checks.

The foundation is a broad pre-specified ticket; most diff volume is generated registry, locks and operational documentation. It remains one issue/branch/PR into integration, with review organized around storage, package/CLI, policy checks, license inventory and CI boundaries. Later feature work follows the ticket DAG.

## First hosted Windows correction

Run 40955793946 passed Linux and macOS but exposed native backslashes in Windows registry provenance. `scripts/registry/sync.py` now serializes relative provenance paths with `as_posix()`. A public-generator Windows-path regression failed before and passes after; Mac-generated registry bytes remain unchanged. Independent review approved the narrow fix. Hosted Windows must rerun beyond that formerly failing stage; it is not passed by the local regression alone.

The next Windows run progressed beyond registry validation and exposed shell-boundary test failures. Tests now choose Git-for-Windows Bash explicitly and use the managed interpreter with portable quoting. A separately reproduced Windows path-separator mismatch in bundle ownership is corrected through normalized path comparison, with a public bundle-inventory regression. Independent targeted review passed; actual Windows CI still determines hosted readiness.
