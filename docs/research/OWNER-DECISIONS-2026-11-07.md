# Owner build-in-public decision — November 7, 2026

Owner instruction in the current task:

> Keep the repo private unless we can build in public and keep ci free- then make it back private again when its at production level but for the build a public build doesnt worry me as much , especially since after i use it a while i may go with an open core / source strategy anyways, so require green three-OS CI and independent review, and merge eligible work into integration.

In the same request Jon asked to "finish building this end to end after considering the continuation report that lays
out more impactful options…" (his words as relayed by the lead; issue #126 turns them into plan changes). This record
amends O-01's private-repository wording for the build phase and amends the November 6 merge policy as described below. Every other owner decision and owner-act gate stays in force, and `main` remains
Jon's release-only branch. Nothing here accepts a license, gives a verdict, approves a paid run or authorizes a download.

## Repository visibility

- `Navigata1/aura` became public on 2026-11-07, so hosted CI stays free during the build. It returns to private at
  production level, and when that is remains Jon's call.
- The lead agent (Claude) made the repository public and created the rulesets and Actions settings below on 2026-11-07,
  on Jon's explicit instruction above and after the publication audit.
- Public visibility is not a license grant. Q5 (AURA's code license) stays owner-pending, no license file is added, and
  the default remains all rights reserved. Jon's remark that he may later choose an open-core or open-source strategy is
  an intention, not a decision.
- No other agent changes visibility, rulesets, Actions settings, label policy or account settings, and any further
  change to them needs Jon's instruction.

## The publication audit

Before the repository went public, the lead audited it on 2026-11-07. The audit scanned every commit diff on every branch
for credentials in common token formats, for personal addresses and for committed media, and checked every commit's
author and committer identity. It then scanned every issue and PR body, comment and review the same way.

Result: no credential matched a common token format, and no personal address or committed media turned up. Every commit
identity is a GitHub noreply identity. The only third-party addresses are two public licensing contacts quoted from
YuE's README inside `docs/research/sources/`, quoted source material that the contact lint exempts. Issues, PRs, comments
and reviews were clean.

## What may enter the public repository

From 2026-11-07 the repository and everything around it is public. What may never appear there is stated once, in
`CLAUDE.md` hard rule 10, and every other document points to it. The policy scan (`scripts/ci/check.py`) enforces part of
the rule on every pull request: tracked files, the PR diff and commit metadata. It has no rule for private paths yet,
and the lead tracks that follow-up. Six quoted archives under `docs/research/sources/` still contain an absolute home
path and stay verbatim until then. Issue and PR text, comments, reviews and CI log output are covered by procedure
only, so whoever posts them checks them first.

## Merge policy

Enforced by GitHub. These rulesets were read back on 2026-11-07; both are active with no bypass actors:

| Ruleset | What it enforces |
|---|---|
| `integration: PR-only, green three-OS CI, up to date` | Changes only through a pull request, squash merge only. Required status checks `checks / foundation (ubuntu-latest)`, `checks / foundation (macos-latest)` and `checks / foundation (windows-latest)` from the GitHub Actions app (integration id 15368), with the branch up to date (strict). Review threads resolved, stale reviews dismissed on push, no force-push, no deletion. |
| `main: owner release only via PR, green three-OS CI` | Changes only through a pull request, with the same three required checks. Review threads resolved, no force-push, no deletion. |

Actions settings require SHA-pinned actions (`sha_pinning_required=true`), require approval for fork workflows from all
external contributors (`all_external_contributors`), and keep the default workflow token read-only.

For what the rulesets cover, this supersedes the November 6 note that enforcement was procedural only. Three things are
still enforced by procedure, not by GitHub:

- **Independent review.** The rulesets require no approving review, so the merger checks the review first. A separate
  reviewer reviews the exact head against its current integration base, with no unresolved blocking finding.
- **Owner-only release on `main`.** The ruleset requires a PR and green checks. Agents never merge to `main`, and only
  Jon release-merges `integration` into it.
- **No auto-merge.**

**Review binding** (the lead's addendum). Because the `integration` ruleset requires branches to be up to date, merging
one PR forces the others to update. An independent review is bound to the PR's patch, identified by
`git diff <merge-base>...<head> | git patch-id --stable`. A branch may be updated only by merging the current
`integration` tip, with the patch-id unchanged: a clean merge with no conflict-resolution edits. Then the existing
Standards and Spec reviews still apply. Fresh green three-OS CI on the new head is still required, and the lead records
the old and new patch-ids in the merge record. Any change to the patch, whether new commits or conflict edits, needs a
fresh independent review of the new head. This relaxes one November 6 clause, that a changed base invalidates the
review, for clean integration-only updates. The reviewed patch must still equal the merged patch, and fresh green
three-OS CI on the new head is required. It is the lead's procedural rule under Jon's merge policy, and Jon can change
it.

Unchanged: every commit and squash author is a verified GitHub noreply identity. A merge needs green checks on the
current head, never red, pending, absent or skipped ones. `main` advances only by Jon's release merge.

## Expansion items folded into the plan

The five items come from the continuation report's "New evidence worth implementing" table and its model-refresh
appendix (2026-10-29). Each primary source was re-read on 2026-11-07 at the revision cited. Upstream figures are VENDOR.
Nothing was installed, downloaded, rendered or listened to. The plan changes are in `docs/spec/tickets.json`, with user
stories 414–422 in group 21 of the spec.

### 1. Lock advisory check (amends T44, T46, T93)

- [GHSA-4prv-5hj7-c2xr](https://github.com/huggingface/diffusers/security/advisories/GHSA-4prv-5hj7-c2xr), published
  2026-10-27, is rated high (CVSS 3.1 score 7.0). It affects the pip package `diffusers`, versions `<= 0.42.0`, patched in
  `0.42.1`. A component library name in a model repository's own config reaches Python's import machinery on
  `from_pretrained()`, even with `trust_remote_code=False`. The precondition is a model directory importable from a
  `sys.path` root, and the advisory notes that `PYTHONSAFEPATH=1` blocks it.
- The fix shipped in [v0.42.1](https://github.com/huggingface/diffusers/releases/tag/v0.42.1), commit
  `2a1433913c7044f34fa4767dd84b28bba0bb0ecf` (2026-10-27). It was still the latest release on 2026-11-07. Three earlier
  Diffusers advisories from May 2026 (GHSA-98h9-4798-4q5v, GHSA-7wx4-6vff-v64p, GHSA-j7w6-vpvq-j3gm) have ranges inside
  0.42.0 and earlier, so a 0.42.1 floor covers them too.
- It reaches AURA's planned workers three ways:
  - ACE-Step 1.5 at the pinned commit requires `diffusers>=0.37.0`
    ([pyproject.toml](https://github.com/ace-step/ACE-Step-1.5/blob/ca1e85fe9430179831e6bc6be790c332190a3866/pyproject.toml)).
  - MiniMax Music 3 runs in Diffusers 0.42.1 as a modular pipeline
    ([docs](https://github.com/huggingface/diffusers/blob/v0.42.1/docs/source/en/api/pipelines/minimax_music3.md)), which is
    one of the advisory's entry points.
  - ACE's alternate decoders load through `diffusers.AutoencoderOobleck`.
- Plan changes:
  - **T44.** The environment step checks each lock against the recorded advisories and fails before anything is
    created or fetched. It records the versions of every package an advisory names. CI applies the same advisories to
    every committed worker lock. This is an amendment because every environment built on Jon's machines descends from
    T44, and a new ticket at the end of the list could not precede them. The CI-built images (YuE2 in T58, the
    challengers in T93) do not descend from T44. They are covered by T93's own floor test, T44's lock scan once it lands,
    and YuE2 declaring no diffusers dependency.
  - **T46 and T93.** Their locks constrain diffusers to 0.42.1 or later.
- No engine environment exists yet, so there is nothing to upgrade today.

### 2. YuE2's exact source revision and separate code, weights and VAE license pins (amends T58, T61, T44)

- **One version label, two code licenses.**
  - On main at `1647252d68b70cbead046ffd3f7caf036dde47ee` (2026-10-06), the
    [LICENSE](https://github.com/multimodal-art-projection/YuE/blob/1647252d68b70cbead046ffd3f7caf036dde47ee/LICENSE)
    is Apache-2.0 (sha256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`), and
    [pyproject.toml](https://github.com/multimodal-art-projection/YuE/blob/1647252d68b70cbead046ffd3f7caf036dde47ee/pyproject.toml)
    declares version 0.1.6 under Apache-2.0.
  - At the `yue2-v0.1.6` tag (commit `9c6c4b349be978b06a9d0d958471a07a6cdeff4d`, 2026-09-09), the
    [LICENSE](https://github.com/multimodal-art-projection/YuE/blob/yue2-v0.1.6/LICENSE) puts the first-party source code,
    agent skill and documentation under CC BY-NC 4.0 (sha256
    `2549dd4f0ee9a6df7e0877915b359bd96d0da624c11ff6fb59650b44e7ba9b6c`). Its pyproject also declares version 0.1.6, under
    `CC-BY-NC-4.0`.
- **Weights terms.** The
  [MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/1647252d68b70cbead046ffd3f7caf036dde47ee/MODEL_LICENSE)
  at `1647252d` (sha256 `c7a0e99360555513ff56815b5dbbc8f0b27a3ad762ceaeeab6838baea9743b3a`) puts the YuE2-3B, YuE2-Vae and
  YuE2-Vae-legacy weights under CC BY-NC 4.0. It adds the 2026-09-16 individual-creator permission, which excludes
  companies' commercial use of the weights.
- **Weights revisions.** Both repositories were still at these heads on 2026-11-07, and both cards say `cc-by-nc-4.0`:
  - [m-a-p/YuE2-3B](https://huggingface.co/m-a-p/YuE2-3B/tree/8f24312f187763b9854adeec87e437e2b03bbff1) at
    `8f24312f187763b9854adeec87e437e2b03bbff1` (2026-10-06).
  - [m-a-p/YuE2-Vae](https://huggingface.co/m-a-p/YuE2-Vae/tree/152733a19ad43aa67e367f9b5503ef8075bb5126) at
    `152733a19ad43aa67e367f9b5503ef8075bb5126` (2026-09-29).
  - The LICENSE file is byte-identical at both pins (sha256
    `060985741d20e70613b4c189c7de106cabd3fb2109fbbfb6d705c9d619417dd0`). It is the CC BY-NC 4.0 weights license without
    the individual-creator permission, which is why the MODEL_LICENSE is archived as a separate document.
- **New since October 29.** Main has advanced 39 commits to `1116bea76032bee5668e5f097294d082fa0b84f0` (2026-11-01). Its
  LICENSE and MODEL_LICENSE are byte-identical to those at `1647252d`, and its pyproject now pins a separate torch
  version on darwin. That commit is not adopted here: a pin moves only after its own license check. Its Metal install
  path is VENDOR until a parity record exists (the worker-hosts rule).
- **Plan changes.**
  - **T58** pins the exact commit, never a label or tag. It keeps the four documents pinned separately and pins both
    weights repositories. It corrects the YuE2 register row by contract-fix PR, so it now also waits for T03. The
    engine-profile contract pins one weights repository per profile today, so the YuE2-Vae pin needs a contract-fix PR.
  - **T61**'s acceptance archives the four documents. T61 now also waits for T44, whose O7 and license-acceptance record it
    already used without an edge.
  - **T44**'s YuE2 sentence names the four documents. ADR-0002 and the architecture's licensing line said two documents;
    both now carry a dated note (see "ADRs and docs reconciled" below).

### 3. Transcription trial cases, with GAME and SheetSage2 as pinned research-only candidates (new T106)

- **GAME.** Commit
  [`eb08841f74d1368d8f03086eac3d5b1a2bf2d436`](https://github.com/openvpi/GAME/commit/eb08841f74d1368d8f03086eac3d5b1a2bf2d436)
  (2026-10-21, "Fix dur2bd failure on CUDA when N=1") stops a single duration from breaking the CUDA ONNX boundary
  reduction. Commit
  [`69ba01ded0ddda5495e51ba373685f1be1a67ea2`](https://github.com/openvpi/GAME/commit/69ba01ded0ddda5495e51ba373685f1be1a67ea2)
  (2026-10-24, "Fix barrier survival") keeps preset boundaries through local-extrema decoding, and is still the head. The
  code is MIT ([README](https://github.com/openvpi/GAME/blob/69ba01ded0ddda5495e51ba373685f1be1a67ea2/README.md)). The
  model files are CC BY-NC-SA 4.0 ([v1.0.0 release notes](https://github.com/openvpi/GAME/releases/tag/v1.0.0)), and
  the latest release with ONNX models is [v1.0.3](https://github.com/openvpi/GAME/releases/tag/v1.0.3) (2026-03-09).
- **Which GAME the trial runs.** The review of PR #127 found that both fixes change functions traced into the exported
  graphs: `format_boundaries` into `dur2bd.onnx`, and `decode_soft_boundaries` (with preset barriers) into
  `segmenter.onnx`. The v1.0.3 ONNX assets were uploaded on 2026-03-09, before both fixes, and no later release exists,
  so those graphs run the pre-fix boundary code. The 2026-10-21 fix concerns CUDA ONNX Runtime only; the 2026-10-24 fix
  applies on every runtime. The repository also ships no ONNX inference pipeline. T106 therefore runs GAME's own PyTorch
  inference (`infer.py`) at `69ba01de`, with the GAME-1.0 PyTorch checkpoints from v1.0.0. Lightning picks the
  accelerator, which the worker records, and upstream tests only CUDA.
- **GAME asset digests** (GitHub release metadata, sha256):
  - v1.0.0: `GAME-1.0-small.zip` (46,886,125 bytes) `3d3e1ac0a83234b2a163a3d43043455d15670765eaa25ef6285c399da1ccc576`,
    the trial's pin; `GAME-1.0-medium.zip` `8c5b3e531e2905b935e664e2f533921cd637243770fab5282413bdb5051ca60c`;
    `GAME-1.0-large.zip` `f45eac9fbb92b82fe67c00f29efad52954469897eb64e5bd5924a43dc5deb9b6`.
  - v1.0.3 (not used): `GAME-1.0.3-small-onnx.zip`
    `00ba0c64115b6b874d9ea4afd3e6cf822abda2a04e52569233b0a044fd40e4e8`; `GAME-1.0.3-medium-onnx.zip`
    `5b7a21e64c6310efac399f5d12838fffa70565be162436b5a4a65f290721e7d8`; `GAME-1.0.3-large-onnx.zip`
    `8a5480539fe7d995800dc0efe149b83a1cd4f4e4a36aa2a1f7665f1765dcac08`.
- **GAME's consent clause.** Its README disclaimer forbids anyone to use the repository's functionality to generate
  someone's singing or speech without that person's consent. It belongs in GAME's register row.
- **SheetSage2.** [m-a-p/SheetSage2](https://huggingface.co/m-a-p/SheetSage2/commit/b83c3d79a6d98bcffaf8f9ed112c90aa887887bc)
  at `b83c3d79a6d98bcffaf8f9ed112c90aa887887bc` (2026-10-12, "Fix local loading of chord spelling module") is still the
  head. Its `model.safetensors` LFS sha256 is `b235f68091a5f5b644000f2b5acb57d1e70432aca2b34ab1b9cf27236e1f4274`,
  identical at the predecessor `32c7c7473e7b59e1ed36bd8a8fefbd11ae8d468a`. The card says `cc-by-nc-4.0`, and its
  [LICENSE](https://huggingface.co/m-a-p/SheetSage2/blob/b83c3d79a6d98bcffaf8f9ed112c90aa887887bc/LICENSE) file is
  headed as the MERT2 weight license.
- These are code fixes: they neither show better accuracy nor clear a licensing restriction. Both components stay
  research-only, as the spec's Out of Scope already says for SheetSage2.
- **T106** adds four hard hum kinds: a one-note phrase, adjacent fixed word boundaries, a long melisma, and a noisy vocal
  standing in for a separated one. It adds the two research-only workers, Jon's license acceptances and a preregistered
  research-lane scoring run with his blind correction passes. Its blockers are T45 (the analysis worker on the Mac,
  pYIN with HMM included) and T53. Scoring a real separated vocal needs the separator on the Mac (T51, with the adapter
  from T49) and is a follow-up outside T106.

### 4. Alternate-decoder fidelity trial (new T107)

- **ACE's decoder contract.** ACE's
  [ALT_VAE.md](https://github.com/ace-step/ACE-Step-1.5/blob/ca1e85fe9430179831e6bc6be790c332190a3866/docs/en/ALT_VAE.md)
  at `ca1e85fe9430179831e6bc6be790c332190a3866` (sha256
  `261a01fcdfaf48cf4bc7c2804192a47d3bb25b1d399e6882a8825746ea0686b3`) says the architecture stays
  `AutoencoderOobleck`, and that a compatible `config.json` plus `diffusion_pytorch_model.safetensors` is a drop-in
  replacement. Its registry ships ScragVAE, whose weights are fetched on first use from Hugging Face with a ModelScope
  fallback. The MLX path follows automatically, and the integration is inference-only. ACE main was still at that commit on
  2026-11-07.
- **ScragVAE.**
  [scragnog/Ace-Step-1.5-ScragVAE](https://huggingface.co/scragnog/Ace-Step-1.5-ScragVAE/blob/0547ba36ff72b94ca3db3fa9194a59899ca37e5c/README.md)
  at `0547ba36ff72b94ca3db3fa9194a59899ca37e5c` (2026-04-19) is still the head.
  - Its card metadata says `license: mit`. Its base is `ACE-Step/ace-step-v1.5-1d-vae-stable-audio-format`, whose card is
    MIT, at `3a962ef9486db134e94a7b96b355e9876aa17c89`.
  - It was trained with the encoder frozen and only the decoder fine-tuned.
  - The repository has no LICENSE file, and the card names no training data.
- **T107** does the rights review first. It then decodes the same saved latents through the official decoder and
  ScragVAE. The latents are a content-addressed artifact in the research project's store, with an artifact origin that a
  contract-fix PR adds. Jon auditions each pair as two blind, level-matched candidates, marking problem intervals with
  notes that name the problem. The trial runs in the research lane only, and diagnostics never select. Its blockers are
  T32 (keepers for the round trip, and through it the audition), T36 and T47.

### 5. Magenta RealTime 2 as a Mac instrument and accompaniment worker trial (new T108, instrument role)

- **Official introduction.** The [introduction](https://magenta.withgoogle.com/magenta-realtime-2), dated 2026-06-04,
  says the engine is controlled by MIDI and audio as well as text. It runs on Apple Silicon through a C++ inference engine
  powered by MLX, with about 200 ms control latency. It gives base's real-time threshold as "MacBook M3 Pro (or higher)"
  or "M2 Max (or higher)". All of these are VENDOR figures.
- **Code.**
  [magenta/magenta-realtime](https://github.com/magenta/magenta-realtime/tree/694a545e4ba0b88bf1150137b129582166d3e07f)
  at `694a545e4ba0b88bf1150137b129582166d3e07f` (2026-07-30) is still the head, under Apache-2.0.
  - Its [README](https://github.com/magenta/magenta-realtime/blob/694a545e4ba0b88bf1150137b129582166d3e07f/README.md)
    says base requires a Pro Max chip for real time, yet marks the M4 Pro as real-time. It lists no M5 Pro.
  - It downloads models by default to `Magenta/magenta-rt-v2/` in the user's Documents folder, which is on the internal disk, unless
    `MAGENTA_HOME` points elsewhere ([paths.py](https://github.com/magenta/magenta-realtime/blob/694a545e4ba0b88bf1150137b129582166d3e07f/magenta_rt/paths.py)).
  - Two runtimes ship: the Python library (`magenta-rt` with its `mlx` extra, streaming through `MagentaRT2Sampler`) and
    the C++ `RealtimeRunner` that the bundled apps use. The vendor's real-time table and its 200 ms figure describe the
    C++ runner.
- **Weights.**
  [google/magenta-realtime-2](https://huggingface.co/google/magenta-realtime-2/blob/010aa0dcb0dfd27b24f0ad07b4dad63e8f9521cc/README.md)
  at `010aa0dcb0dfd27b24f0ad07b4dad63e8f9521cc` (2026-06-04) carries the card license `cc-by-4.0`.
  - The card says the code is Apache 2.0 and adds responsible-use terms.
  - It reports training on about 71k hours of mostly instrumental stock music, with a 230M small and a 2.4B base
    checkpoint, and 48 kHz stereo output.
  - It is not a lyric engine.
- **Not in scope.** The community audio.cpp runtime added MRT2 support on 2026-10-28
  ([`3d426f48edba228a79c67b21b34773b2d761d755`](https://github.com/0xShug0/audio.cpp/commit/3d426f48edba228a79c67b21b34773b2d761d755)).
  It is a separate component with its own pins and stays outside the trial.
- **T108** adds register rows and a research-lane playable-instrument worker on the official Python MLX runtime, with
  `MAGENTA_HOME` on the studio volume. Jon accepts the terms. A smoke gate whose latency checks are committed before
  measurement runs on `mlx/m5pro`, small checkpoint first, with base only after small passes, followed by Jon's "not
  garbled" check. Its figures describe the Python path, so a miss does not falsify the vendor's C++ claim.
  Accompaniment is neither defined nor tested and needs its own ticket. It adds no Studio control, and Create a new
  part stays v2. Its blocker is T52.

## ADRs and docs reconciled

The following were contradicted by these changes. Each now carries a dated note or a precise edit, and none is
rewritten:

- **ADR-0002 and `architecture.md`.** YuE2's acceptance archives four pinned documents, not two. `license-acceptance/1`
  already allows this.
- **ADR-0011.** It said the code license would be chosen before the repository went public. The repository became
  public on 2026-11-07 on Jon's instruction with no license grant, so the code stays all rights reserved and Q5 stays
  owner-pending.
- **ADR-0024, the spec, `architecture.md` and `docs/DEVELOPING.md`.** These said macOS and Windows run only on
  integration and nightly builds. Since PR #12 (2026-11-06), every pull request runs all three OSes, and the
  `integration` ruleset requires them. Story 363 and the per-OS prose are updated.
- **`docs/DEVELOPING.md`.** Its repository-workflow paragraph said to keep the repository private and to enforce the
  checks procedurally. It now points to this record. Its environment example no longer names a home directory.
- **`docs/agents/issue-tracker.md`.** Its ticket workflow said the merge closes the issue. GitHub acts on closing
  keywords only for merges into the default branch, so the merger closes the issue with a comment linking the merge.

## Evidence

The source texts and API reads behind this record are kept outside the repository with SHA-256 sums, under
`/Volumes/STUDIO/evidence/S01/`: license files, ALT_VAE.md, the advisory and the rulesets.
