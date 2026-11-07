# Owner merge-policy amendment — November 6, 2026

Owner instruction in the current task:

> Keep the repo private and revise the merge policy to require green CI and independent review. Recheck the email setting, then merge eligible PRs into integration and keep building from Claude’s plan.

## Integration merge policy

The repository remains private. Ticket PRs may be squash-merged into `integration` when all applicable checks pass on the current head and a separate reviewer has reviewed that head against its current integration base, with no unresolved blocking findings. Recheck both head and base immediately before merge; changed code or base invalidates the corresponding review and requires fresh checks. The merge must match the reviewed head. Do not enable auto-merge or merge red, pending, absent or skipped required checks.

This replaces the requirement for GitHub-enforced private-branch protection, which the account plan previously rejected with HTTP 403. Enforcement is procedural, not a claim that server-side protection exists. A verified GitHub noreply identity is required for every commit and the squash author. Only Jon release-merges `integration` into `main`; the default branch and repository visibility do not change.

Code integration and full ticket acceptance remain distinct. The first integration push can only be validated after the foundation merge. The configured scheduled workflow will not run until present on the default branch; retain that acceptance evidence as pending rather than calling a PR run a nightly run. No main release is authorized to resolve this sequencing dependency.

## Email-setting recheck

On November 6 the GitHub settings URL redirected to sign-in. The current checkbox values are UNVERIFIED; the October 29 observation is historical, not current confirmation. The owner was asked to sign in for the requested recheck. No account setting was changed. P01 remains open until both privacy settings are verified enabled. Implementation interpretation of the revised code-merge rule (not a claim that the owner waived or completed P01): this outstanding account task does not imply that CI or independent review may be skipped, nor may it be reported complete. Existing commit-identity gates and explicit noreply squash authors remain mandatory.

All storage, license, owner-verdict, paid-run and release boundaries remain in force. This amendment authorizes no model downloads, paid jobs or fabricated owner evidence.
