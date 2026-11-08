# T03 standards review: PR #129 (license verification of the v1-core plumbing)

- Reviewed head: `abb682610056653bda9ae7932f021ada1437346d` (`ticket/03-license-verification`, one commit)
- Integration base: `7cb7bbdfb7dc041832301f015bd25543ce6835f3`. This is the current `integration` tip and the merge-base; both were rechecked at 2026-11-08T02:23:04Z (`T03-review-final-refs.log`).
- Diff: `git diff 7cb7bbdfb7dc041832301f015bd25543ce6835f3...abb682610056653bda9ae7932f021ada1437346d` (11 files, +3356/-110)
- Reviewer: independent. I did not write this change and edited none of it.
- **Verdict: pass.** There are no blocking findings. This file covers the standards-side non-blocking findings NB-1 to NB-7, NB-10 and NB-12, plus one note for the lead (NB-14). NB numbers are shared with `T03-spec-review.md`.

## Method

- **Review method:** `.claude/skills/code-review/SKILL.md` as it stands at `7cb7bbd`. The Standards and Spec passes ran as separate sub-agents, and neither brief contained my own conclusions. I kept each finding only after reproducing it in the code or with a probe.
- **Disposable copies:** `/Volumes/STUDIO/scratch/review-T03-abb6826/`.
  - Clones: `repo` at the head and `base` at the base.
  - Each probe got a fresh `git archive` copy.
  - No worktree was registered, nothing touched the internal disk, and no `sudo` was used.
- **Standards sources:**
  - CLAUDE.md hard rules 1-14 and the parallel-work rules.
  - `GLOSSARY.md`.
  - ADR-0011, ADR-0013, ADR-0029, ADR-0035.
  - `contracts/README.md`, `docs/DEVELOPING.md`.
  - The CONFLICT AVOIDANCE notes in `docs/spec/tickets.json`.
  - `/Volumes/STUDIO/evidence/protocol/AGENT-PROTOCOL.md`.
  - The skill's smell baseline.

## Gate reruns on the head

| Check | Result | Log |
|---|---|---|
| Disk preflight (3 GiB estimate), `uv sync --frozen`, `pnpm install --frozen-lockfile` | each exit 0 | `T03-review-install.log` |
| `uv run --frozen python scripts/ci/run.py --base 7cb7bbd…` | `Foundation gate passed`, exit 0 (below) | `T03-review-local-gate.log` |
| `validate.py -v`, `sync.py --check`, `generate_fixtures.py --check`, `pytest -v tests/foundation/test_open_source_readiness.py` | each exit 0; 8 passed | `T03-review-contract-checks-head.log` |
| Hosted CI on `abb6826`, run 42435568374 | ubuntu (job 128593552772), macos (job 128593552750) and windows (job 128593552484) all `success` | `T03-review-ci-checks.log` |

What the local gate covered:
- the validator: `PASSED: 0 failure(s), 59 reference rules`;
- `sync.py --check` (byte-identical) and `tickets.py --check`;
- pytest: 54 passed, 12 subtests;
- vitest and the build;
- the policy scan: 612 files, 0 violations;
- the control and web license inventory.

Per-OS pytest counts in CI: macOS 54 passed; ubuntu 53 passed and 1 skipped; windows 52 passed and 2 skipped. The base collects 46 tests and the head 54, so the 8 new tests make up the difference. The new file has no skip markers.

## Planted-violation probes (`T03-review-probe-*.log`)

| Probe | What was planted (fresh tracked copy each) | Result |
|---|---|---|
| R0 red before | the head's test file on the base tree | **8 errors** (no readiness register); the test is real |
| G1 | delete `components.v1.json` and both readiness files, then run `sync.py` | all three regenerate byte-identically (`c40e402c…`, `bc41306b…`, `a079f3bd…`); `--check` exit 0 |
| F1 | the two invalid fixtures reverted to base bytes | `generate_fixtures --check` exit 1 (`stale:` both); `validate.py` exit 1 (`fixture differs from generate_fixtures.py output`). The generator rewrites only those two files, to exactly the head bytes |
| P1 | `yue2-3b` dropped from the committed readiness JSON | `sync.py --check` exit 1: `yue2-3b: release blocker ['non_commercial_weights'] is missing…`; pytest 3 failed |
| P2 | `lucide` added to `release_blockers.copyleft`, readiness left stale | `--check` exit 1, naming `lucide`; pytest 2 failed |
| P3 | `audio-decoder` label changed from the spec text, every output regenerated | sync, the fixtures and `validate` pass; **the test fails** (`'Hums arrive as WAV or M4A' != 'Hums arrive as WAV only'`) |
| P4 | `mido` confirmed with `primary_sources: []` | `sync.py --check` exit 1: `mido: status 'confirmed' cites no primary source` |
| P5 | `mp3-encoder` widened to individual | exit 1: `open_rows.mp3-encoder: an open row stays unverified, research-only and release-blocking` |
| P6 | `license_verification` sets `songecho` to confirmed and adds no new source | **accepted**: status `confirmed`, still in the `unverified` class, research-only (NB-4) |
| P7 | `mido` given `code_license` `GPL-3.0-only` and no class | **accepted**: boundary true, lanes unchanged, absent from the readiness register, `--check` exit 0 (NB-5) |
| P8 | the product name in an open-row label | it reaches the readiness JSON, but `validate.py` exit 1: `register_overlay.json: names the product outside a product record (ADR-0035)`; fail-closed at the source |

## CLAUDE.md rule 4 (lanes) and rule 5 (licensing doctrine)

- **Lanes.**
  - Every row in the `unverified` class is research-only, at head and at base. This is enforced by `registry.lane_policy_consistent`, and for open rows also by the new refusal (P5). See `T03-review-consistency-head.txt`.
  - `mido` and `mir-eval` widen to all lanes only together with leaving the class, and both have commit-pinned sources.
  - YuE2, Demucs and demucs-mlx are individual and research, with the boundary flag set.
  - SwiftF0, Basic Pitch and Kim Mel-Band-RoFormer are individual and research (llc forbids their classes in `lanes.v1.json`).
  - The open rows are research-only.
- **Allowlist.** `scripts/ci/check.py` allows MIT, BSD-2/3, Apache-2.0, ISC, 0BSD, PSF/Python-2.0, CC0-1.0 and OFL-1.1, and denies `L?GPL|AGPL|CC-BY-NC|CC-BY-SA|SSPL|BUSL`.
  - No T03 row places a denied license in the control service or the web bundle.
  - waveform-data (LGPL-3.0) would be refused if it were bundled. The waveform-playlist row now carries `copyleft`, `process_boundary_required: true`, and a `redistribution_blocker` saying so.
  - axe-core is MPL-2.0, which is not on the allowlist. Its row and `verdict_condition` keep it development-only.
  - Fonts (OFL-1.1), Lucide (ISC), wavesurfer (BSD-3-Clause) and Signalsmith (MIT) are on the allowlist.
  - The bundle inventory covers JavaScript chunks only, so font files rely on the register row. This predates the PR.
- **No weights, audio or binaries.** `git diff --numstat` shows 11 text files. SwiftF0's bundled `swift_f0/model.onnx` was checked through git tree metadata only (blob `3619f9a…`, 135,090 bytes) and not downloaded. No `license-acceptance/1` record and no owner act appear.
- **Rule 11 / ADR-0037.** The 3,356 added lines contain no address, `mailto` or home path.
- **Rule 12 / ADR-0035.** No product name in the added lines; see P8.
- **Legal readings.** They are labelled at document level, plus 8 rows in-row (NB-1).

## The register stays generated

`sync.py` regenerates `components.v1.json` and the new open-source-readiness register (`.json` and `.md`) byte-identically (G1, `sync.py --check`, and the `clean_contracts.py` tracked-file copy in CI). The readiness register's `generated_from` is the committed register's SHA-256, `c40e402c…`. None of T01's 26 stack rows changed.

## Fixture bytes: what the contract says

- **Contract text.**
  - `contracts/README.md`, "What the gate proves" item 3: "`components.v1.json` and every fixture regenerate byte-identically". This is met.
  - `docs/DEVELOPING.md`: `generate_fixtures.py` is for "Contract tickets only".
  - `tickets.json` CONFLICT AVOIDANCE (1): contracts change only in T02, then by contract-fix PR.
  - CONFLICT AVOIDANCE (2): "The register overlay is edited by T01 (stack rows), then T03, then by contract-fix PR."
  - CONFLICT AVOIDANCE (8): changes in another ticket's area go through a small fix PR.
  - T02 owns `contracts/fixtures`.
  - The protocol: contract tickets prove that no existing fixture byte changed.
  - Frozen `legacy/` fixtures are never edited (CLAUDE.md).
- **Why the change is inherent.**
  - `contracts/reference/generate_fixtures.py:1247-1249` builds IR-COMPONENT-NC-IN-PROCESS and IR-COMPONENT-NC-IN-LLC from `REGISTER["generated_from"]` plus a copy of the `yue2-3b` row. So these fixtures intentionally embed the overlay hash.
  - The overlay edit that rule (2) assigns to T03 therefore moves exactly these two lines.
  - T03's first criterion ("the gate passes") requires the fixtures to be regenerated in the same PR; a separate fix PR could not pass either side.
  - T01 hit the same literal conflict and recorded it ("Bounded reconciliation of T01 wording", `docs/research/licenses/stack-verification-2026-10-29.md:46-48`, authorized by the lead on 2026-10-29).
- **Evidence.**
  - 308 of 310 fixtures are byte-identical to the base, and no legacy fixture changed.
  - Each changed file differs by one line: the overlay SHA-256, now `73697e89…`. That equals SHA-256 of the head overlay and the head register's `generated_from`.
  - The embedded `yue2-3b` row is unchanged.
  - F1 shows that the gate fails with the base bytes, and that the generator reproduces the head bytes and changes no other file (`T03-review-fixture-bytes.log`, `T03-review-probe-F1-fixture-provenance.log`).
- **Judgement: acceptable.** It is inherent and not a blocker. The lead should record the acceptance at merge as was done for T01; see NB-2 for the standing coupling.

## Code quality and tests

- **Hard violations of a documented standard:** none found.
- **Tests:**
  - They run through the public seams (`readiness_problems`, `build`, `generate_readiness`).
  - They were red before (R0) and are green after.
  - They fail on a missing or unlisted release blocker (P1, P2) and on label drift from the spec (P3).
  - Weaknesses are listed under NB-6.

## Findings

**Blocking:** none.

**Non-blocking:**

- **NB-1. The legal-reading label is mostly document-level.**
  - 8 rows carry "interpretation, not legal advice" in-row: axe-core, the `verdict_condition` of the four font rows (Newsreader, IBM Plex Sans, IBM Plex Mono, Bravura Text), demucs-mlx, waveform-playlist and yue-abc-tools.
  - Other changed rows hold readings without it, for example mido's "None (MIT); retain the copyright and permission notice." and the fonts' `redistribution_blocker`. They rely on these labels:
    - `plumbing-verification-2026-11-07.md` lines 3-4;
    - the readiness register's JSON `description` and MD header;
    - the manifest's `scope`;
    - the overlay's `license_verification.source`, which `sync.py` drops.
  - This matches the T01 convention. At base no row carries the label, and T01's notes carry it once. ADR-0011 also states it once, under Consequences.
  - The register schema has no document-level note field.
  - Suggestion for a contract-fix: have `sync.py` append the label to every row it rewrites from a verification.
- **NB-2. Overlay and fixture coupling (Shotgun Surgery).** Every later overlay edit, including every contract-fix PR, will move the two invalid fixtures. A contract-fix could freeze the IR records' snapshot so they stop tracking the overlay hash.
- **NB-3. The ADR-0013 premise is now stale.**
  - ADR-0013 line 17 and spec line 1246 still read "evaluate waveform-playlist v16 (MIT)".
  - The decision itself (evaluate it against our own timeline) still stands.
  - The PR body names T77 but not ADR-0013.
  - The consequence is recorded where T77's implementer will see it; see the spec review.
- **NB-4. The source refusal checks only that a URL is present** (P6).
  - Any surviving `https://` URL satisfies `_require_sources`. Nothing ties it to a pin or to the hashed manifest.
  - Nothing refuses a row that is not `unverified` but still sits in the `unverified` class. The schema defines that class as "a license not yet checked".
  - Lanes stay safe in that state, because the class keeps the row research-only.
  - Suggestion: require a pinned source listed in the manifest, and refuse a status that disagrees with the class.
- **NB-5. Readiness completeness rests on the overlay's classes** (P7).
  - A GPL or LGPL `code_license` without the `copyleft` class sets the boundary flag but is not a release blocker, so it is missing from the readiness register.
  - In `--check`, `readiness_problems` compares two outputs built from the same rows, so it only adds a named reason to a staleness failure.
  - No current row is affected: only `audio-decoder` matches the copyleft pattern, and it is listed under `unverified`.
  - Suggestion: refuse a copyleft `code_license` without the class.
- **NB-6. Test precision.**
  - `test_no_row_leaves_unverified_without_a_primary_source` and `test_an_open_row_must_stay_unverified` use a bare `assertRaises(SyncError)` without checking the message.
  - The second test plants an open row on `mir-eval`, which breaks all three open-row conditions at once. A mutant that keeps only one of the conditions still passes.
  - No test drives `main(["--check"])`. CI does, through `scripts/ci/clean_contracts.py`, and P1 and P2 show it failing with named rows.
- **NB-7. Process-boundary consistency.**
  - `librosa-pyin` reads `false`, although its own note says its LGPL dependencies (soundfile over libsndfile, and soxr) keep it in a worker.
  - T01 classed soundfile, libsndfile and scipy `copyleft`, and this PR classes waveform-playlist `copyleft`, both for an LGPL piece. Yet soxr (librosa) and lameenc (Demucs) have no row or class.
  - The open rows `mp3-encoder` and `lyric-aligner` are new, and `g2p-phonemizer` and `midi-synth-soundfont` predate the PR. All four read `false`, although likely candidates such as LAME and espeak-ng are copyleft.
  - The rows cannot be adopted while unverified (rule 5), and the PR and the notes defer transitive audits to the adopting tickets.
  - Suggestion: a fail-closed flag for unverified rows, and rows for soxr and lameenc, in the contract-fix.
- **NB-10. CLAUDE.md rule 3.**
  - The `librosa-pyin` note re-commits "Vocadito pitch F1 0.653 (author-run benchmark)", which carries no figure label.
  - This is evidence-register text copied into the overlay's replacement `notes`.
  - The `swiftf0` row labels the same benchmark VENDOR.
- **NB-12. Judgement calls from the smell baseline.**
  - **Mutation.** `_apply_open_rows` mutates rows in place, while `_verified` returns copies. Owner style prefers immutable updates.
  - **Duplicated Code.** `main()` builds the register twice (`generate` plus `generate_readiness`).
  - **Mysterious Name.** `register` means the evidence register in `build()` but the component register in `readiness_problems()`, and the test's `REGISTER` is a different file from `sync.py`'s.
  - **Speculative Generality.** `VERIFIED_FIELDS` admits `verdict`, which is a studio decision, but no entry uses it.
  - **Data Clumps.** `readiness()` re-reads the raw overlay gate and label instead of the neutralised row. P8 shows the lint makes this fail-closed.
  - **Glossary.** The overlay field `gate` holds a ticket reference, whereas GLOSSARY defines Gate as a pass rule on evidence records. The wording comes from T03's own text.
- **NB-14. Note for the lead (not a defect of this PR).**
  - 52 of the 150 files in the implementer's evidence folder contain third-party addresses. They come from registry metadata, the Basic Pitch NOTICE and the OFL-FAQ copies.
  - A checkpoint PR into `ops/mission/evidence/` must not commit `raw/` or `licenses/` wholesale. The policy scan would refuse any address other than the public contact.

## Reconciliation with the sub-agent passes

The Standards sub-agent rated two items HARD; I downgraded both after checking the repo:
- The legal label is NB-1, because of the T01 precedent and the document-level labels.
- The fixture edit is NB-2, because CONFLICT AVOIDANCE (2) gives the overlay to T03, the generator couples the fixtures by construction, and there is the T01 reconciliation.

I reproduced its fail-open claims as P6 and P7 with different rows (songecho rather than vocalparse). Its "latent product-name path" is closed by the existing ADR-0035 lint (P8).
