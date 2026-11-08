# T03 spec review: PR #129 (license verification of the v1-core plumbing, issue #16)

- Reviewed head: `abb682610056653bda9ae7932f021ada1437346d` (`ticket/03-license-verification`, one commit)
- Integration base: `7cb7bbdfb7dc041832301f015bd25543ce6835f3`. This is the current `integration` tip and the merge-base; both were rechecked at 2026-11-08T02:23:04Z.
- Diff: `git diff 7cb7bbdfb7dc041832301f015bd25543ce6835f3...abb682610056653bda9ae7932f021ada1437346d`
- Reviewer: independent. I did not write this change and edited none of it.
- **Verdict: pass.** All four acceptance criteria are met. The fourth needed this review's reviewer line, posted as PR comment [6716123075](https://github.com/Navigata1/aura/pull/129#issuecomment-6716123075). There are no blocking findings. The spec-side non-blocking findings are NB-1, NB-3, NB-4, NB-5, NB-7, NB-8, NB-9, NB-11 and NB-13; NB numbers are shared with `T03-standards-review.md`.

## Spec sources

- Issue #16. Its body matches `docs/spec/tickets.json` T03 (what_to_build, the 4 acceptance criteria) word for word, and it has no comments.
- The T03 ticket's `notes` and `owned_areas`.
- `docs/spec/aura-v1-spec.md`, "Unverified capabilities and the tickets that gate them" (line 1480 onward).
- `contracts/registry/lanes.v1.json`.
- For the waveform-playlist consequence: T77 (`timeline`), ADR-0013 and issue #97.

## Acceptance criteria

### AC1: met

> "Each listed component has a row with license, pinned version or revision, primary-source URL, allowed lanes,
> process-boundary flag and verification status; the component register regenerates byte-identically and the gate
> passes."

Every component T03 names has a row at head (`T03-review-rowdiff.txt`):

| Row | License as recorded | Pin | Lanes | Boundary | Status |
|---|---|---|---|---|---|
| `mido` | MIT | 1.3.3, commit 7313549 | all | false | unverified → confirmed |
| `librosa-pyin` | ISC | 1.0.0, 3e4ff7b | all | false | confirmed |
| `pyloudnorm` | MIT | 0.2.0, b8d67bf | all | false | corrected (kept) |
| `mir-eval` | MIT | 0.8.2, 8db0b38 | all | false | unverified → confirmed |
| `axe-core` (new) | MPL-2.0, development only | 4.14.0, e797173 and 2375f7f | all | false | confirmed |
| `newsreader` (new) | OFL-1.1, no Reserved Font Name | google/fonts 8b0a1d0 | all | false | confirmed |
| `ibm-plex-sans` / `ibm-plex-mono` (new) | OFL-1.1, Reserved Font Name "Plex" | 1.1.0 at 1da12f0 / 2.5.0 at 2f9ba1b | all | false | confirmed |
| `bravura-text` (new) | OFL-1.1, Reserved Font Name "Bravura" | 1.482, 37b1943 | all | false | confirmed |
| `lucide` (new) | ISC (Feather-derived icons MIT) | 1.70.0, b826f0c | all | false | confirmed |
| `yue-abc-tools` (new) | Apache-2.0 | yue2-music-v1.2.0, 72272f9 (file SHA-256 recorded) | all | false | confirmed |
| `swiftf0` | MIT; bundled ONNX trained on CC BY-NC-SA 4.0 data | 0.3.0, d1ba77f | individual, research | false | confirmed |
| `basic-pitch` | Apache-2.0 + NOTICE; five training datasets with terms | 0.4.0, 9991303 | individual, research | false | confirmed |
| `demucs-4.1.0` | code MIT; weights research and personal only (author, #327 #384 #508) | 4.1.0, 6a604bb; HF revisions | individual, research | true | corrected (kept) |
| `demucs-mlx` | code MIT; converted weights keep the author's restriction | 1.6.1, 9950c7d; HF 35ecb1a | individual, research | true | corrected (kept) |
| `wavesurfer-core` | BSD-3-Clause | 8.0.5, b0ce881 | all | false | confirmed |
| `waveform-playlist` | MIT, but requires waveform-data ^4.5.2 (LGPL-3.0) | @waveform-playlist/browser 16.0.1, f1739ab | all | true | confirmed → corrected |
| `signalsmith-stretch` | MIT, with Signalsmith Linear 0.6.4 MIT | 1.4.0, a670068 (web build 1.3.2) | all | false | confirmed |

- **Where the pin lives.** The component schema has no version field. The pin therefore lives in:
  - every row's `notes` ("version X (tag T, commit C)");
  - a commit-pinned raw URL in every row's `primary_sources`;
  - the `name` of most of the new rows and of waveform-playlist.
- **Manifest cross-check.** Every pinned URL in these rows is in `plumbing-sources-2026-11-07.json` (74 sources) with a SHA-256.
- **Regeneration and gate.** The register regenerates byte-identically (probe G1, `sync.py --check`), and the gate passes locally and on hosted CI on three operating systems (run 42435568374).
- **Evidence in the PR.**
  - The register diff is the PR's `components.v1.json` change.
  - The PR body gives the gate output in summary; the full logs are in `/Volumes/STUDIO/evidence/T03/`.

### AC2: met

> "Each still-open row names its blocking gate and the capability label shown until it closes (for example 'Hums arrive
> as WAV only'). Evidence: the open-rows table in the PR body, cross-checked against the spec's 'Unverified capabilities'
> table."

| Spec table row | Spec gating ticket | Register row | Gate written into `verdict_condition` | Label (spec "Until then", exact) |
|---|---|---|---|---|
| m4a/AAC decoder license (ffmpeg build, PyAV) | `codec-checks` | `audio-decoder` | T102 codec-checks | Hums arrive as WAV only |
| An MP3 encoder | `codec-checks` | `mp3-encoder` (new) | T102 codec-checks | Export bundles carry WAV and MIDI only |
| G2P or phonemizer license (lyric error rate) | `lyric-per`, `lyric-per-on-mac` | `g2p-phonemizer` | T72 lyric-per, then T73 lyric-per-on-mac | No lyric-error badge |
| MIDI synth and soundfont licenses | `midi-synth-eval` | `midi-synth-soundfont` | T101 midi-synth-eval | No instrument rendering; NeutralVoice is the only guide |
| Lyric word alignment on singing | `lyric-alignment` | `lyric-aligner` (new) | T84 lyric-alignment | No line or word replace |

- The ticket ids match the slugs in `tickets.json`: T102 = codec-checks, T72 = lyric-per, T73 = lyric-per-on-mac, T101 = midi-synth-eval, T84 = lyric-alignment.
- The PR body's open-rows table and the readiness register show the same gates and labels.
- Each open row is `unverified`, research-only and a release blocker. `sync.py` refuses an open row widened to individual (probe P5).
- The test pins each label to the spec text (probe P3).

### AC3: met

> "The open-source-readiness register is generated from the rows and lists YuE2, Demucs, SwiftF0's data caveat and the
> unverified training data of Kim Mel-Band-RoFormer and Basic Pitch as release blockers; a test fails when a row marked
> release-blocking is missing from it."

- **Generation.** `docs/research/licenses/open-source-readiness.{json,md}` are generated by `sync.py` from the component register. Their `generated_from` is the committed register's SHA-256, `c40e402c…`. They list 65 release blockers out of 160 components, including the 5 open rows.
- **The named blockers** are all listed:
  - `yue2-3b` (`non_commercial_weights`);
  - `demucs-4.1.0` and `demucs-mlx` (`non_commercial_by_author`);
  - `swiftf0` (`permissive_label_nc_data`);
  - `melband-roformer-kim` and `basic-pitch` (`unverified_training_data`).
- **The test is real.**
  - It is red before the change: 8 errors on the base tree (probe R0).
  - It fails when YuE2 is dropped from the committed register (P1: `yue2-3b: release blocker ['non_commercial_weights'] is missing…`).
  - It fails when a newly classed row is left unlisted (P2, naming `lucide`).
  - It runs in hosted CI: the 8 new tests account for the jump from 46 to 54 collected tests.

### AC4: met with this review

> "No row moves from UNVERIFIED without a cited primary source; a reviewer spot-checks three rows by hand. Evidence: the
> reviewer line with the three URLs in the PR."

- **Rows leaving UNVERIFIED.** The only two are `mido` and `mir-eval`. Each cites a commit-pinned LICENSE and the PyPI metadata for the same version.
- **New confirmed rows** all cite commit-pinned sources.
- **Refusal.** `sync.py` refuses a confirmed row that cites no source (P4).
- **Reviewer line.** Posted once as comment 6716123075, covering mir-eval, mido, waveform-playlist→waveform-data, SwiftF0 (LICENSE and the training-data caveat) and Demucs. No GitHub review was submitted.
- **Limit.** The machine check only requires that some source is present (NB-4).

## Primary-source spot-checks (by hand)

Every file was fetched by its raw URL and again through the GitHub contents API, into its own empty directory. The bytes were identical and the git blob id matched the manifest. I read each text. Logs: `T03-review-spotcheck-fetch.log`, `T03-review-spotcheck-readings.log`, `T03-review-spotcheck-results.json`.

| Component | Pinned source | Bytes | SHA-256 | Text read | Tag → commit | Corroboration |
|---|---|---|---|---|---|---|
| mir-eval | `mir-evaluation/mir_eval@8db0b38…/LICENSE.txt` | 1079 | `220f461a…c069` matches | MIT | 0.8.2 → 8db0b38 | PyPI 0.8.2 declares MIT |
| mido | `mido/mido@7313549…/LICENSE` | 1078 | `bd038e5a…eb1c` matches | MIT | 1.3.3 → 7313549 (annotated tag) | PyPI 1.3.3 declares MIT |
| waveform-playlist | `naomiaro/waveform-playlist@f1739ab…/LICENSE.md` | 1072 | `cf78dfc2…e355` matches | MIT | release tag `transport-engine-improvements` (2026-10-28) → f1739ab | a release commit |
| waveform-playlist | `…@f1739ab…/packages/browser/package.json` | 2730 | `8368ab54…0e68` matches | `@waveform-playlist/browser` 16.0.1, `waveform-data: ^4.5.2` | same | npm 16.0.1 also depends on `waveform-data ^4.5.2` |
| waveform-data | `bbc/waveform-data.js@de3b1c3…/LICENSE` | 7421 | `88813443…a9ee` matches | GNU LGPL v3 (29 June 2007) | v4.5.2 → de3b1c3 | npm 4.5.2 is `LGPL-3.0`, `gitHead` de3b1c3; it is the latest release, so `^4.5.2` admits only LGPL-3.0 today |
| swiftf0 | `lars76/swift-f0@d1ba77f…/LICENSE` | 1076 | `5f4711c7…8c18` matches | MIT | v0.3.0 → d1ba77f (annotated tag) | PyPI 0.3.0 `license_expression: MIT`; the git tree holds `swift_f0/model.onnx` (blob `3619f9a…`, 135,090 bytes; metadata only, not downloaded) |
| swiftf0 (data caveat) | `lars76/swift-f0-training@a3095d2…/README.md` | 6430 | `3633675c…6f10` matches | "CC BY-NC-SA 4.0, research use" | main@a3095d2 | HF dataset card `lars1234/pitch-benchmark@e98642f`: 5722 bytes, `cb67633f…60cc` matches, `license: cc-by-nc-sa-4.0` |
| demucs-4.1.0 | `adefossez/demucs@6a604bb…/LICENSE` | 1087 | `cf9b1782…8173` matches | MIT (Meta) | v4.1.0 → 6a604bb | author comment #327 (adefossez): 100 bytes, `6c270699…` matches, "The model weights are not covered by the MIT license, and are provided only for scientific purposes." |

The registry metadata I fetched also hashes identically to the manifest entries: npm `@waveform-playlist/browser` 16.0.1 `db512c75…`, npm `waveform-data` 4.5.2 `63c11ec9…`, PyPI `mido` `e53e9bd1…`, `mir_eval` `23a8b97b…` and `swift-f0` `55652bcb…`.

I did not check by hand Basic Pitch's dataset terms, the demucs-mlx card, the fonts, axe-core, Lucide, `abc_tools.py`, Signalsmith, librosa, pyloudnorm or wavesurfer. For those I rely on the manifest hashes and on the implementer's evidence sums, all 149 of which verify. All readings here are interpretations, not legal advice.

## The rest of what_to_build

- **"Each row states the lanes it allows and whether it must sit behind the process boundary".** Every row states both. The flags of `librosa-pyin` and of the open rows read `false` against their own notes (NB-7).
- **"a row stays research-only while it carries an UNVERIFIED blocker".** This holds for all 8 rows in the class (`T03-review-consistency-head.txt`). The converse (an `unverified` status implies the class) is not enforced: 7 rows predating the PR break it (NB-11).
- **"generated from the same rows and lists every release blocker".** It lists every row with a release-blocker class. Completeness depends on the overlay's classification (NB-5, NB-7).
- **"SwiftF0's package and bundled ONNX (keeping its training-data caveat)".** Verified above; the caveat stands until T54.
- **"Basic Pitch with every dataset it was trained on and that dataset's terms".**
  - Recorded in the row's notes and in verification finding 5: GuitarSet CC BY 4.0, MAESTRO CC BY-NC-SA 4.0, Slakh2100 redux CC BY 4.0, iKala academic-only, and the MedleyDB pitch subset CC BY-NC-SA 4.0.
  - The row keeps `unverified_training_data` for T54. Its `redistribution_blocker` still reads "None" (NB-8).
- **"Demucs 4.1.0 and demucs-mlx weights terms".** Recorded. demucs-mlx keeps the author's restriction although its Hugging Face card tags the weights MIT.
- **"Every legal reading is labelled an interpretation, not legal advice".** Met at document level, and in-row on 8 rows (NB-1).
- **Obligations of rows that engine profiles copy.**
  - Basic Pitch's `apache_notice`, and `attribution` on the MIT, BSD and ISC rows, are deferred to a contract-fix PR.
  - The deferral is recorded in the repo (verification notes, "Still open").
  - See NB-9.

## The waveform-playlist consequence (T77 and ADR-0013)

- **The finding holds** (spot-check above). `@waveform-playlist/browser` 16.0.1 requires waveform-data ^4.5.2, and that package is LGPL-3.0. CLAUDE.md rule 5 and the bundle allowlist deny LGPL in the web bundle.
- **It is recorded where T77's implementer will see it.**
  1. **Issue #97 (T77).** A comment dated 2026-11-08T01:47:34Z states the finding and points to ADR-0013's other option, a timeline of our own. Protocol step 3 has every implementer read the issue with its comments.
  2. **The register row.** Its `verdict_condition` reads: "Evaluated against the studio's own timeline (T77) only with waveform-data kept out of the web bundle". Its `redistribution_blocker` states the LGPL consequence. T77's acceptance scores "license", and that criterion leads to this row.
  3. **The readiness register.** It lists waveform-playlist under `copyleft`.
  4. **The verification notes**, finding 1.
  5. **The PR body.**
  6. **CI's bundle license inventory** would refuse waveform-data if T77 bundled it.
- **Not updated.** ADR-0013 line 17 and spec line 1246 still say "evaluate waveform-playlist v16 (MIT)", and the PR body names T77 but not ADR-0013 (NB-3).
- **Answer:** yes, the consequence is recorded where T77's implementer will see it. The ADR and spec wording is a follow-up.

## Scope

- **Inside T03's owned areas:**
  - the overlay's non-stack rows (none of T01's 26 stack rows changed, and `codegen-tools` stays with T01 and T04);
  - the generated `components.v1.json`;
  - `docs/research/licenses` (the notes and the manifest);
  - the generated readiness register.
- **Outside them but required by the ticket text:**
  - `scripts/registry/sync.py` and `tests/foundation/test_open_source_readiness.py` ("generated from the same rows", "a test fails when…");
  - two rows of `docs/DEVELOPING.md` documenting `sync.py`'s new output;
  - the two invalid fixtures. Editing them is inherent; see the standards review, "Fixture bytes".
- **Not asked for:** `VERIFIED_FIELDS` admits `verdict`, which no entry uses (NB-12).

## Findings

**Blocking:** none.

**Non-blocking (spec side):**

- **NB-1.** The legal label is in-row on 8 rows. The other rows rely on the document-level labels, which is T01's convention.
- **NB-3.** ADR-0013 line 17 and spec line 1246 keep "(MIT)", and the PR body does not name ADR-0013.
- **NB-4.**
  - AC4's machine check only requires that some `https` source is present (probe P6: `songecho` flipped to confirmed on its arXiv URL).
  - The status/class tie is not enforced.
- **NB-5.** The readiness register's completeness rests on the classes: a GPL `code_license` without `copyleft` is omitted (P7).
- **NB-7.**
  - `librosa-pyin` reads boundary `false` although its note says it stays in a worker.
  - soxr and lameenc (LGPL) have no row or class. T01 classed soundfile, libsndfile and scipy, and this PR classes waveform-playlist, for the same pattern.
  - The open rows read `false` while unverified.
- **NB-8.** `basic-pitch` keeps `redistribution_blocker: "None"` despite the NOTICE and three non-commercial or academic-only datasets.
  - Engine profiles copy only `code_license`, `weights_license` and `obligations`, so this field was not tied to any fixture.
  - Mirror swiftf0's wording until T54 decides.
- **NB-9.** The deferred obligations need the contract-fix PR before any export relies on the register's obligations.
- **NB-11.** Seven rows predating the PR have status `unverified` without the `unverified` class: deepfilternet (allowed in individual and llc), melodyspec-abc-converter, muscriptor, neutralvoice, prior-art-studios, stepaudio-3-music and studio-own-code.
  - The state is unchanged from base, and none of these rows is on T03's list.
  - Worth a contract-fix check, because rule 4 keys on license status.
- **NB-13. Housekeeping.**
  - The PR body's author-written "Reviewer spot-check" marks mido and mir-eval "(left UNVERIFIED)", meaning as T01 left them. The independent line is comment 6716123075.
  - The PR body gives no hosted run id; it is 42435568374, green on abb6826.
  - `contracts/README.md` still describes `sync.py`'s output as `components.v1.json` alone; the PR notes this.
  - `docs/research/evidence-register.json` and RECONCILIATION §4 still show mido and mir_eval as UNVERIFIED. The overlay now carries the verification, and T03 does not own the evidence register.
