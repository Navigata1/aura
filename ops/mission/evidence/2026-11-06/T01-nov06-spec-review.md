# Independent Spec review — November 6, 2026

Reviewed head: `85160f75260f4e587c324bff69a20a5d5a880984`.
Base: `79cd9aff1ee239bd0422e684b4e8d58b73bb7c0f` (`integration`).
Diff: `git diff 79cd9aff1ee239bd0422e684b4e8d58b73bb7c0f...85160f75260f4e587c324bff69a20a5d5a880984`.
Worktree clean before/after validation. Reviewer made no repository edits.

## Spec

No blocking implementation finding in the foundation scope. Inspected T01 acceptance criteria, workspace pins, six Python package scaffolds, product-constant CLI and file discovery, web placeholder, CI workflows, policy tests, runtime/bundle license closure, storage/env/worktree helpers and the owner amendments. The store fixture and registry snapshot changes are the explicitly documented reconciliation of contradictory untouched-contract and registry-regeneration requirements. No legacy-schema behavior or real engine was added.

The November 6 amendment keeps visibility private, requires green exact-head CI plus independent current-base review, uses noreply squash authors and leaves main owner-release-only. It correctly identifies unavailable server-side protection as procedural enforcement. The separate account task remains unverified and open; treating it separately from code integration is labelled an implementation interpretation rather than a completed or waived owner action.

Outstanding acceptance, not concealed by this review:
- P01 still needs current verification of both account email settings; the observed sign-in redirect is not verification.
- T01 acceptance says “the push-run id and the first nightly run id.” First integration push evidence is necessarily post-merge; the actual scheduled-nightly run remains pending until the workflow reaches owner-controlled default main. Do not close full T01 acceptance or call a PR run nightly evidence.
- The product is a scaffold. No music generation, real playback, model licensing, owner listening, paid run or three-machine acoustic acceptance is established.

Independent local validation: `uv run --frozen python scripts/ci/run.py --base 79cd9aff1ee239bd0422e684b4e8d58b73bb7c0f` exited 0 after physical-volume preflight. Tracked contract copy, registry/tickets, 37 Python tests, two Vitest and two Node tests, build, commit-aware policy and runtime license gates passed. Current-head hosted CI must independently pass before merge.

Disposition: no blocking Spec code findings; eligible for integration only after current-head CI and Standards review pass. Full ticket acceptance remains open for the evidence above. This review is invalidated by a changed head/base.

Log: `nov06-spec-gate.log`.
Log SHA-256: `441b6731baec7090edac6f9b9928486b0a0ff2b8708b8b6eaf67357f8944d65b`.
