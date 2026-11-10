# S01 spec review 2: PR #127 (fresh review after the fix commit)

- **PR:** Navigata1/aura #127 (issue #126)
- **Reviewed head:** `4773eb58ac94232cebb36b454bec1ba08dcdd101`
- **Integration base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8` (the current `integration` tip and the merge-base)
- **Diff command:** `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...4773eb58ac94232cebb36b454bec1ba08dcdd101`
- **Patch-id:** `2ebf2204099a60e345c91805051c3c3dfa7ce1a5`
- **Hosted checks:** all three passed in run 42439174344.
- **Merge integrity.** The merge of `dee28e2` is a clean automatic merge that carries no change into the PR's patch (probe-R01; details in `S01-standards-review-2.md`).
- **Spec sources:**
  - Issue #126 (no comments).
  - The coordinator's re-review request.
  - The continuation report's own lines on Magenta RealTime 2, read locally and quoted below only as far as needed.
- **Method.** As before: an independent Spec pass whose output served as leads, then my own verification against primary sources (the GitHub REST API, the Hugging Face API and the release metadata). Probes and sources are in `S01-review-2-probes/` and `S01-review-2-sources/`.

## Verdict: pass (no blocking spec finding)

B1 is resolved, and no factual error remains in a pinned revision, license reading or repository fact. Eleven non-blocking findings follow (R2-N1 to R2-N5 in the standards file, R2-N6 to R2-N11 here). A twelfth entry, R2-C1, is a correction to my first review.

## B1: resolved

The coordinator asked me to check B1 against the release myself. Probe-R09 and the re-fetched `game-release-v1.0.0.json` show:

- **The pin is right.** The v1.0.0 release (2026-03-07, "These are GAME 1.0 pretrained models", "The model files apply CC BY-NC-SA 4.0") contains an asset named **`GAME-1.0-small.zip`**:
  - **46,886,125 bytes**;
  - digest **`sha256:3d3e1ac0a83234b2a163a3d43043455d15670765eaa25ef6285c399da1ccc576`**;
  - uploaded 2026-03-07T06:36:28Z.

  T106 and record L172–174 state exactly this. The medium and large digests and all three v1.0.3 digests in the record also match.
- **The ticket and record say the ONNX graphs predate both fixes.**
  - T106: "The v1.0.3 ONNX graphs are not used: they were traced on 2026-03-09, before both fixes, and the repository ships no ONNX inference pipeline."
  - Record L164–170 explains which functions are traced into `dur2bd.onnx` and `segmenter.onnx`.
  - The spec's UNVERIFIED row says "GAME's released ONNX graphs predate both, so the trial runs its PyTorch path".
- **The new claims about upstream are correct** (at `69ba01de`):
  - README L274: "We don't provide implementation of ONNX model inference pipeline in this repository".
  - `inference/api.py` builds a `lightning.pytorch.Trainer` with no `accelerator`, so Lightning's automatic choice applies, which matches "Lightning picks the accelerator".
  - README L26: "tested under … CUDA 12.9", which matches "upstream tests only CUDA".
  - The README directs users to the release models for `infer.py -m`.
  - The 10-21 fix changes nothing in PyTorch for a single duration, because reducing an empty axis is fine there. So "concerns CUDA ONNX Runtime only" is accurate.
- **The new criterion can fail.** It checks for a PyTorch run at the pin with the v1.0.0 checkpoint, the accelerator recorded, and a test that fails if the weights pin names an ONNX asset. It names its evidence.

The residual risks from switching to the PyTorch path are in R2-N10. None of them blocks.

## Issue #126 checklist at this head

| Item | Status |
|---|---|
| 1. Decision record: instruction, public on 2026-11-07, rulesets, SHA pinning and fork approval, audit, other decisions stay | Satisfied. Settings are re-read and unchanged (probe-R09). The record now says who acted (L16–17) and quotes the expansion request as relayed (L7–8). |
| 2. CLAUDE.md read-first and issue-tracker.md | Satisfied. Both point to November 7 and to rule 10. |
| 3a. Lock advisory gate | Satisfied, unchanged. The T44 justification is reworded (N13). |
| 3b. YuE2 exact revision and separate pins | Satisfied. The HF LICENSE hash `060985741d20…7dd0` is in the record and matches my first-review copies and the implementer's independent copies at both pins. |
| 3c. Transcription trial with GAME and SheetSage2 pinned | Satisfied (B1 resolved). The "separated noisy vocal" case is still an honest stand-in (R2-N9). |
| 3d. Alternate-decoder trial | Satisfied. Latents are a content-addressed store artifact with `derived_from` edges, and a contract-fix adds their origin; the current `origin` enum has none. Blockers are T32, T36 and T47. |
| 3e. Magenta RealTime 2 trial | Satisfied for the instrument role. Accompaniment is narrowed out (R2-N6), and some wording is inconsistent (R2-N7, R2-N8). |
| AC: tickets.py with every story covered | Satisfied (probe-R02, and mutation N4 for story 421). |
| AC: validate.py, and no contract change | Satisfied. 0 failures; 0 paths under `contracts/`, `scripts/registry/` or `docs/research/licenses/` in the PR diff. |
| AC: primary sources with pinned revisions | Satisfied. Every upstream head is unchanged at re-review time: ACE `ca1e85fe`, YuE main `1116bea7`, GAME `69ba01de`, magenta-realtime `694a545e`, the HF YuE2-3B, YuE2-Vae, SheetSage2, ScragVAE and MRT2 pins, and Diffusers latest v0.42.1. There is still no GAME release after October 1 (probe-R09). |
| AC: PR body lists new tickets, blockers and owner gates | Satisfied. The new blocker issue numbers T45 #58, T53 #66, T32 #45, T36 #49, T47 #60 and T52 #65 all match GitHub (probe-R07). |

**Edges** (probe-R07, probe-R08):
- T106 is blocked by T45 and T53. T19 and T44 are reachable through T45 (whose blockers are T19, T36 and T44), so removing them is correct transitive reduction.
- T107 is blocked by T32, T36 and T47. T31 is reachable through T32 (whose blockers are T09 and T31).
- Neither ticket has a redundant blocker, and re-adding T19 or T31 is rejected by the checker.
- No existing ticket's depth moved, and the weighted critical path is still 49.
- The edges are genuine. T45 is the Mac install of `analysis-transcribe-pyin-hmm`, and T32 supplies the keepers for the round trip.

## Status of the first review's spec findings

| ID | Status | What remains |
|---|---|---|
| B1 | **Resolved** | See above. |
| N9 T45 edge | **Resolved** | None. |
| N10 keeper edge and latents | **Resolved** | None. |
| N11 separated vocal | **Partly resolved** | The needed tickets are named (T51, T49), but there is no follow-up ticket or open item (R2-N9). |
| N12 accompaniment and vendor path | **Partly resolved** | The vendor-path and M5 Pro wording are fixed. Accompaniment is deferred (R2-N6), and story 422's benefit clause is inconsistent (R2-N7). |
| N13 T44 justification | **Resolved** | Now "environments built on Jon's machines", and the CI-built images' coverage is stated. |
| N14 digests and consent clause | **Resolved** | The GAME release notes also name training data (R2-N10). |
| N15 closing #126 | **Resolved** | The issue-tracker step is corrected, and the PR body says the merger closes #126 by hand. |

## Non-blocking findings (round 2)

**R2-N6. Accompaniment is narrowed out of item 5 without being listed as open.**
- Issue #126 asks for "a Mac instrument **and** accompaniment worker trial". T108 and story 421 are now instrument-only.
- The source report supports choosing one: "Evaluate it as a future playable instrument **or** accompaniment worker after the first v1 flow". The narrowing is therefore defensible, and the T52 edge matches the report's "after the first v1 flow".
- Three gaps remain:
  - The PR body's "Unverified / still open" does not list it.
  - The record (L248) says accompaniment "needs its own ticket", while T108's notes say "needs its own ticket if the instrument trial passes".
  - The record's §5 heading still says "instrument and accompaniment".
- **Fix.** Make the record and T108 agree, and list the narrowing as open so the lead can accept it explicitly.

**R2-N7. T108's benefit wording does not match what it measures.**
- **Story 422 contradicts itself.** It measures "on the official Python MLX runtime, not the C++ runner the vendor's figures describe", yet keeps "so that a vendor's real-time claim becomes a measured fact or an honest failure". T108 itself says "a miss here does not falsify the vendor's claim".
- **The UNVERIFIED row (L1542) is ambiguous.** It reads "VENDOR only, for the C++ runner" and names `magenta-realtime-trial` as its gate. The trial can settle real-time play on the M5 Pro for AURA's path, but the row should name that path.
- **The runtime entry point is loosely named.** T108 says it streams "through `MagentaRT2Sampler`". At `694a545e` the entry points are `MagentaRT2System` and `MagentaRT2SystemMlxfn`, the CLI's default `.mlxfn` path; the sampler is a component inside the former. Name the entry class the worker uses, because the two systems are different compute paths.

**R2-N8. T108's control-latency measurement must fit the fixed worker protocol.**
- ADR-0026 fixes the worker route list ("Anything else returns 404") and rejected WebSocket.
- T108 measures "the control latency from a MIDI change to the first changed output frame". That is compatible only if the change is scripted inside the job's submitted MIDI input.
- **Fix.** Say so in T108, or name ADR-0026 if a live control route is intended. T108 already plans contract-fix PRs for the MIDI input and the latency checks.

**R2-N9. The separated-vocal case is still a stand-in.** T106 and story 417 use "a noisy vocal standing in for a separated one". The record names what a real case needs (T51 and T49) but creates no follow-up ticket, story or open item for it. Either list it under "Unverified / still open", or add a note to the spec's GAME and SheetSage2 UNVERIFIED row.

**R2-N10. Residual risks from the PyTorch path.**
- **Checkpoint compatibility.** That the March GAME-1.0 checkpoint loads at `69ba01de` is implied by the README. Loading is `strict=True`, so a key change from April's backbone clean-ups would fail loudly, and T106's new criterion would catch it. It is not proven, so keep it named as a risk.
- **Pickle loading.** GAME loads the checkpoint with `torch.load` (a pickle). The worker should keep torch's `weights_only` default and the sha256 pin.
- **Training data.** The v1.0.0 notes name GAME's training data: about 32 h of private labelled singing data, plus DEMAND, MUSAN, MIR-1K, MusicNet, MUSDB18-HQ, a private instrument set and MB-RIRs. That belongs in GAME's register row next to the consent clause.

**R2-N11. Unchanged from the first review: the `main` ruleset row's omissions.**
- The record's `main` row still leaves out that `main` dismisses stale reviews, allows merge or squash, and does not require up-to-date branches (strict is false).
- Issue #126 says both rulesets enforce up-to-date branches. The record is right not to claim that for `main`, but it should say so.

**R2-C1. A correction to my first review.** My first review said three-OS checks had run on every PR "since #6". That was imprecise. In #6, pr.yml ran three OSes only for the `ticket/01-foundation` branch, and #12 (`fdd588c`, 2026-11-06) made every PR three-OS. The PR's "since PR #12" is correct (probe-R10).

## Leads from the independent Spec pass

Adopted:
- Accompaniment (R2-N6).
- The separated vocal (R2-N9).
- The six archives (standards R2-N2).
- The binding contradictions (standards R2-N1).
- T65 and spec L1309 (standards R2-N3).
- Story 422 and the UNVERIFIED row (R2-N7).
- `main` strict (R2-N11).

Rejected:
- **"T108 → T52 orders work rather than encoding a dependency."** The source report says "after the first v1 flow" and "after the existing v1 flow works", and T52 also carries T19, T44 and T45, which T108 needs.
- **"The trial can never close the UNVERIFIED row."** Rejected in part. The row's capability is real-time play on the M5 Pro, which T108 measures for AURA's path. Only the wording needs fixing (R2-N7).
