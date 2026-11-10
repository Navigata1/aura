# Owner merge-policy amendment — November 6, 2026

Owner instruction in the current task:

> Keep the repo private and revise the merge policy to require green CI and independent review. Recheck the email setting, then merge eligible PRs into integration and keep building from Claude’s plan.

## Integration merge policy

The repository remains private. Ticket PRs may be squash-merged into `integration` when all applicable checks pass on the current head and a separate reviewer has reviewed that head against its current integration base, with no unresolved blocking findings. Recheck both head and base immediately before merge; changed code or base invalidates the corresponding review and requires fresh checks. The merge must match the reviewed head. Do not enable auto-merge or merge red, pending, absent or skipped required checks.

This replaces the requirement for GitHub-enforced private-branch protection, which the account plan previously rejected with HTTP 403. Enforcement is procedural, not a claim that server-side protection exists. A verified GitHub noreply identity is required for every commit and the squash author. Only Jon release-merges `integration` into `main`; the default branch and repository visibility do not change.

Code integration and full ticket acceptance remain distinct. The first integration push can only be validated after the foundation merge. The configured scheduled workflow will not run until present on the default branch; retain that acceptance evidence as pending rather than calling a PR run a nightly run. No main release is authorized to resolve this sequencing dependency.

## Email-setting recheck

The initial November 6 in-app browser check redirected to sign-in. After the owner reported signing in, the existing Chrome email-settings tab identified Navigata1 and showed both **Keep my email addresses private** and **Block command line pushes that expose my email** checked. No setting was changed by the agent. The privacy prerequisite is now verified; the earlier sign-in interruption is historical. Only setting booleans and account identity are retained in `ops/mission/evidence/github-privacy-2026-11-06.json`.

All storage, license, owner-verdict, paid-run and release boundaries remain in force. This amendment authorizes no model downloads, paid jobs or fabricated owner evidence.
