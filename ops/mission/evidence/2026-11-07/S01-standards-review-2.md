# S01 standards review 2: PR #127 (fresh review after the fix commit)

- **PR:** Navigata1/aura #127 (issue #126)
- **Reviewed head:** `4773eb58ac94232cebb36b454bec1ba08dcdd101`
- **Integration base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8`. This is the current `integration` tip and the merge-base, read from GitHub. It is integration after the T03 squash, #129.
- **Diff command:** `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...4773eb58ac94232cebb36b454bec1ba08dcdd101`
  (sha256 of the unredacted diff `bff3b11e70be9c51c0820d194330f69350e636aeccc7be851bae8d7a7ac6bb61`, 11 files, +548 −70). The saved copies `pr127-at-4773eb5-redacted.diff` and `fix-9310e75-redacted.diff` mask the local account name in DEVELOPING.md's removed line. Regenerate the exact diff from git to check the hash.
- **Patch-id:** `2ebf2204099a60e345c91805051c3c3dfa7ce1a5`. It matches the coordinator's figure, so the patch changed from the first review's `3a1896e3…`.
- **Commits:** `7600cc8` and `906f4a8` (reviewed before), the fix commit `9310e75`, and the merge `4773eb5` (parents `9310e75` and `dee28e2`). All four have noreply identities.
- **Hosted checks on this head:** all three `checks / foundation (…)` jobs passed in run 42439174344.
- **Merge integrity** (probe-R01):
  - Integration moved by exactly one commit, T03 (`dee28e2`, parent `7cb7bbd`).
  - The committed merge tree `6b92c98a…` equals `git merge-tree --write-tree 9310e75 dee28e2`. So it is a clean automatic merge with no conflict edits, although T03 and S01 both touched `docs/DEVELOPING.md`.
  - The PR diff against `dee28e2` is byte-identical, index lines aside, to the branch's diff against `7cb7bbd` before the merge. Both have patch-id `2ebf2204…`.
  - **The merge carried no unintended change into the PR.**

**Method.** This is the same as the first review: the integration tree's `code-review` skill, run as two independent passes. Each pass got the diff, the standards sources and no conclusions. Their output served as leads only, and I verified every finding myself in a new disposable copy, `/Volumes/STUDIO/scratch/review-S01-4773eb5/`. My probes are in `/Volumes/STUDIO/evidence/S01/S01-review-2-probes/` and my re-fetched sources in `/Volumes/STUDIO/evidence/S01/S01-review-2-sources/`, both with SHA-256 sums.

## Verdict: pass (no blocking standards finding)

## Checks run

| Check | Result | Evidence |
|---|---|---|
| CLAUDE.md hard rules 1–14 | Rules 1–9 and 11–14 are identical to the base. Rule 10 keeps its base text verbatim. It adds the public-surface sentence, defines a private path, and names itself the single statement of the rule. Nothing is weakened. | probe-R05 |
| ADR edits are dated notes, not rewrites | ADR-0002 (+2), ADR-0011 (+2) and ADR-0024 (+3) have **0 removed lines**. Each addition starts with a dated marker: "Note (2026-11-07, …)", "Status note (2026-11-07, …)" and "Note (2026-11-07):". The decision text is untouched. | probe-R05 |
| Sensitive content in the diff | None in 548 added lines. There are no addresses, absolute home paths, account names, tokens or keys. The two `~/` paths name no account (`~/.config/studio/env.sh`, and the vendor's default folder), so they fit rule 10's new definition. | probe-R06 |
| Home paths in the tree | Six tracked files under `docs/research/sources/` still hold one. DEVELOPING.md is fixed. The record (L40–41) and the PR body acknowledge them. | probe-R06 |
| `tickets.py --check` and `validate.py` on the merged head | Both pass. The checker reports 108 tickets, 26 need Jon, 422/422 stories, reduced edges, depth 19 and path weight 49. `validate.py` reports 0 failures across 59 rules. | probe-R02, R03 |
| The gates can fail on this patch | 8 of 8 mutations behaved as expected. Dropping the new T45 edge fails. Re-adding T19 to T106 or T31 to T107 fails as "redundant … must be transitively reduced". Dropping story 421, leaving tickets.md stale, bumping a golden vector and planting an address all fail. A planted home path passes, matching the record's statement that the scan has no path rule yet. | probe-R08 |
| Full local gate on the merged head | Passes. Contracts have 0 failures, and the registry and open-source-readiness register regenerate byte-identically. The DAG passes, pytest has 54 passed, web tests and build pass, and the policy scan finds 0 violations in 613 files. | probe-R04 |
| Repository settings | Both rulesets are identical to the first read-back: active, no bypass actors. `sha_pinning_required=true`, `all_external_contributors`, a read-only token, and public visibility. | probe-R09 |
| Owner gates | T106, T107 and T108 remain `owner_gate`, `ready-for-human` and `gate:evidence`, with `owner_needs`. The amended tickets are unchanged in gating. | probe-R02 |
| New acceptance criteria | All are failable and name their evidence. The `weights_missing` refusal T108 cites is a defined code (common.schema.json, ADR-0026). | read |
| "Since PR #12" (now in about nine places) | **Correct.** In #6, pr.yml ran three OSes only for the `ticket/01-foundation` branch. #12 (`fdd588c`) made every PR three-OS. `integration.yml` and the nightly run all three. My first review's "since #6" was imprecise. | probe-R10 |

## Status of the first review's standards findings

| ID | Status | What remains |
|---|---|---|
| N1 patch-id wording | **Partly resolved** | See R2-N1. |
| N2 home paths | **Partly resolved** | DEVELOPING.md is fixed and rule 10 defines a private path. Six archives stay, as an acknowledged exception outside rule 10, and the follow-up has no issue (R2-N2). |
| N3 ADRs named | **Resolved**, with residues | Dated notes and the record's "ADRs and docs reconciled" section. The residues are in R2-N3. |
| N4 DEVELOPING L291 | **Resolved** | It now points to November 7 and rule 10. Its first sentence still restates the November 6 base clause (R2-N1). |
| N5 problem labels | **Resolved** | "Problem intervals, each with a note naming the problem" matches GLOSSARY and `verdict.schema.json` (`note`). |
| N6 T108 criteria | **Resolved** | There are now two criteria: the downloader one refuses with `weights_missing`, and the install-order one requires small smoke-passed first. |
| N7 single statement | **Resolved** | Rule 10 is the single statement, and CLAUDE.md, issue-tracker.md and DEVELOPING.md point to it. |
| N8 who acted | **Resolved** | Record L16–17 names the lead agent, acting on Jon's instruction. L7–8 quotes the expansion request as relayed. |

## Non-blocking findings (round 2)

**R2-N1. The review-binding rule is now disclosed as a relaxation, but other sentences still contradict it.**
- **What is fixed.** Record L71–74 and CLAUDE.md L14–19 say it relaxes the November 6 changed-base clause, and the PR body lists Jon's confirmation as an open follow-up.
- **What still contradicts it:**
  - (a) CLAUDE.md names only that clause and says "Every other rule in it stays". But the binding also replaces November 6's "The merge must match the reviewed head" (OWNER-DECISIONS-2026-11-06.md L9) with "the reviewed patch must equal the merged patch".
  - (b) Record L59–60 says "A separate reviewer reviews the exact head against its current integration base".
  - (c) issue-tracker.md L56–57 says "an independent review of that head".
  - (d) DEVELOPING.md L292 says "independent review against the current integration base".
  - (b) to (d) state the November 6 rule that the binding relaxes a few lines later.
- **Why it is non-blocking.** Jon's two quoted instructions ask only for green CI and an independent review. The binding keeps the merged patch identical to the reviewed one and reruns CI. It is disclosed as the lead's rule, the lead specified it, and Jon's confirmation is listed as open.
- **When it would block.** If the lead or Jon treats the November 6 text itself as binding owner wording, this blocks until Jon confirms.
- **Fix.** List both relaxed clauses in CLAUDE.md, and reword (b) to (d) as "the PR's patch (see Review binding)".

**R2-N2. The six-archive exception lives outside rule 10.**
- Rule 10 says it is "the one statement of the rule". But the only statement that six tracked archives keep an absolute home path, "until then", is in the record (L40–41).
- The follow-up is "the lead tracks", with no issue number.
- The repository is public, and each file names the local account.
- **Fix.** Purge them now, which replaces a path, not a quoted claim. Otherwise, add the exception to rule 10 and open the follow-up issue, with a path rule and a planted-violation test.

**R2-N3. Residues from reconciling the ADRs.**
- **T65 still says "on macOS and Windows in the integration and nightly runs".** T65 is the ticket that covers story 363, which this PR updated.
- **Spec L1309, the StudioHarness row of the seam table, still says "macOS and Windows on integration and nightly".**
- **ADR-0002's note says "`license-acceptance/1` already supports this".** That is true for the four documents (the `documents[]` roles). But `weights_source` is a single `$ref` to engine-profile `weightsSource`. So T58's planned contract-fix for a second weights pin must also let the acceptance bind both YuE2 weights repositories. Say so in T58.

**R2-N4. GLOSSARY terms, present since `906f4a8` (I missed these in the first review).**
- **"Vocal" for a hum.** Story 417 (spec L655), T106's what_to_build and record L189–190 call a hum kind "a noisy vocal standing in for a separated one". GLOSSARY **Hum** lists _Avoid_: "vocal". T106's own criteria already say "the noisy hum". Write "a noisy hum standing in for a separated vocal stem".
- **"Residual" in two other senses.** GLOSSARY **Residual** means "the mix minus its stems" (_Avoid_: bleed). The PR uses "residual" for bed left in the stand-in (T106: "a stated residual and noise level") and for the 0.1 LU loudness gap (T107: "the residual loudness mismatch"). GLOSSARY **Level matching** calls the latter "the remaining mismatch".
- **Unlisted terms.** "Bed", "accompaniment", "playable instrument" and "hum kind"/"trial set" are not GLOSSARY terms, and the spec's glossary-gap paragraph (L1568–1573) does not list them. CLAUDE.md: "A missing term is a gap for domain-modeling".

**R2-N5 (a judgement call, Mysterious Name).** Rule 10's heading, "No secrets in the client", no longer describes a rule that now governs every public surface. A heading such as "No secrets in the client or on any public surface" would fit.

## Leads from the independent Standards pass

Adopted:
- The binding contradictions (R2-N1).
- The six archives (R2-N2).
- The weights_source scope (R2-N3).
- The "vocal" and "residual" collisions and the glossary gaps (R2-N4).
- The rule 10 heading (R2-N5).
- The ADR-0026 point, which belongs to the Spec lens (`S01-spec-review-2.md`, R2-N8).

Kept at non-blocking, with the reasoning above:
- "An agent relaxed an owner rule" as a hard violation.

Not adopted:
- "The OWNER-DECISIONS file mixes decision, addendum and research." Issue #126 asked for exactly that record.
- "'Since PR #12' restated in about nine places." It is correct everywhere I checked, so the repetition is only a style point.

## Sensitive-content note for whoever commits this review under `ops/`

This file and `S01-spec-review-2.md` contain no secrets, personal addresses or paths outside `/Volumes/STUDIO`. The six repository files are referred to only by directory. `S01-review-2-sources/` holds raw upstream texts and is evidence only.
