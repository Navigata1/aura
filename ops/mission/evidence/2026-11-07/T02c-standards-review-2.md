# T02c standards review 2: PR #131 at cd85ce8 (SongForm assembly, issue #80, part of T02 #15)

- **Head:** `cd85ce80580c82df6222f2c7d7df7a5b4eea4b89`
- **Base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8`. This is the `integration` tip after T03 #129, verified on GitHub, and equals `git merge-base integration cd85ce8`.
- **Diff (the whole patch, reviewed fresh):**
  - Command: `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...cd85ce80580c82df6222f2c7d7df7a5b4eea4b89`.
  - Size: 30 files, +15192 / −23.
  - SHA-256 of the diff text: `f8f1073599a48731221a10b5357b3e4a52cc45e5e8c86d2af86d8d6c8124ab27`.
  - `git patch-id --stable`: **`09e0de2b8daedab41b949dc7c1fcad06cce90cc0`**.
- **The fix alone:** `git diff 1af6154 cd85ce8`: 13 files, SHA-256 `c42a29f3…440f` (T02c-review2-21-patch-ids.txt).
- **Commits:**
  - `9d6e471` and `969886b`: reviewed in round 1.
  - `1af6154`: a merge of `dee28e2`. It is a pure integration merge: `git diff dee28e2...1af6154` keeps the round-1 patch-id `7f9d4bf5…`, and the merge's own diff equals 7cb7bbd→dee28e2.
  - `cd85ce8`: "refuse tempo changes anywhere in a phrase's bars and pin the review gaps".
- **Reviewer:** independent. I never edited the implementation. Disposable copies are under `/Volumes/STUDIO/scratch/review-T02c-cd85ce8/`:
  - `head` and `base` are clones;
  - `mut-*` and `mut2-*` are tracked-file copies;
  - the round-1 trees (`/Volumes/STUDIO/scratch/review-T02c-969886b/`) are reused for comparison.
  - Both clones were left clean.
- **Method:** the two-pass `code-review` skill, as in round 1. This round re-ran every one of my own probes and mutants on the new head and added a differential and an exhaustive check. Scripts are in `T02c-review2-probes/`, and logs and sums in `T02c-review2-SHA256SUMS`.

**Verdict: pass.** There is no blocking finding: B1 is fixed, and I verified the fix independently. There are 9 non-blocking findings.

## B1 from round 1: fixed and verified

The change, in `songform.py:52-56`: `_shape` computes `bars` first and refuses any meter or tempo change strictly inside `(anchor, anchor + bars × bar)`. That is every bar the phrase occupies, leading and trailing rest included, exactly as `contracts/README.md` (Tempo and meter; Refusals) says.

| Check | Result |
|---|---|
| My B1 probe re-run (T02c-review2-07) | A1 (change at 6720) and A2 (change at 5760, the mid-bar end) now refuse `tempo_conflict`. A3 and the pickup case B are unchanged. **0 README/reference disagreements.** |
| New refusal vectors | "tempo change after a phrase's last note, inside its last bar" and "tempo change where a phrase ends mid-bar". Reverting the tempo range (my mutant) fails both (T02c-review2-10). |
| Comparison with my round-1 candidate fix (T02c-review2-08, -08b) | Over 4031 inputs (4000 seeded, 31 committed vector inputs), the head and my round-1 candidate-fix tree give **byte-identical outcome files** (SHA-256 `2fea0d7e…`). |
| What B1 was | Round-1 head 969886b and the tempo-range-reverted mutant also give byte-identical outcomes (`c5a3a510…`). They differ from the head on exactly 202 inputs, and every one of those has a tempo change in a placed phrase's trailing rest. |

## The implementer's meter claim, scrutinized

The claim, from the commit, the PR body and the vector derivation, is that a meter change after a phrase's last note but inside its last bar "is off a bar line and raises the typed `meter_change_inside_bar`". The coordinator paraphrased it as: the case cannot occur for any map passing `bar_segments`, and appears only as the input-error vector.

**Proof.**
- Let the phrase start in meter segment S, with bar length b. Then `anchor` is S's last bar line at or before the start, and `bars_end = anchor + ⌈(end − anchor)/b⌉·b`.
- A map that passes `bar_segments` puts the first change after `anchor` on a bar line of S, so at `anchor + k·b` with k ≥ 1.
- If that change lies before `bars_end`, then k ≤ bars − 1, and therefore `anchor + k·b < end`.
- Hence a valid map can put a meter change in `[end, bars_end)` only after an earlier change inside `(anchor, end)`. That earlier change already refuses `meter_conflict` under either range.
- A phrase that keeps one meter up to its end can meet a trailing-rest meter change only off a bar line. `bar_segments` then raises `meter_change_inside_bar` before any section is placed, which is the `{"invalid": "meter_change_inside_bar"}` vector.

**Evidence** (T02c-review2-09, -08, -10):
- An exhaustive search over **3,050,104** (valid 3-segment map, phrase) pairs finds no trailing-rest meter change without an earlier in-span change.
- So do the 75 seeded pairs that have one.
- Reverting only the meter range is an **equivalent mutant**: 0 of 4031 outcomes change, and `validate.py -v` passes.

**Verdict on the claim:** correct in effect. No verdict depends on the meter range, so the meter half of the fix is behaviour-neutral, kept for symmetry with the README. "Cannot occur for any valid map" is slightly too strong: 68 seeded inputs place an on-bar meter change in a trailing rest, but only after an in-span change. This is a wording note (non-blocking 2).

## Verified (no finding)

- **Local gate** (T02c-review2-02, after the preflight T02c-review2-00): passes at cd85ce8 with `--base dee28e2`:
  - the contract gate (59 rules);
  - 56 pytest tests and 16 subtests;
  - vitest (2 packages) and the node test;
  - the build;
  - the policy scan (634 tracked files, 0 violations);
  - licences.
- **`validate.py -v`** (T02c-review2-03):
  - 31 `fixture.songform` and 43 `fixture.meter` vectors;
  - 100 invalid records;
  - 100 failing and 9 valid scenarios, with 59 rules exercised;
  - 332 files valid and 419 files linted;
  - 2 byte-identical regenerations.
- **Hosted CI** at cd85ce8: `checks / foundation` passes on ubuntu, macos and windows-latest (run 42440113505, attempt 1; T02c-review2-18).
- **Fixture bytes against the new base** (T02c-review2-04): all 310 files at dee28e2 are identical at cd85ce8, 16 are added (all `A`), and `vectors/tempo.json` is unchanged.
- **One typed `TimeModelError`** (`timemodel.py:20-27`) replaces `MeterError`, with codes `tempo_segments_invalid`, `meter_segments_invalid`, `meter_change_inside_bar` and `beat_outside_bar`.
  - It subclasses `ValueError`, so existing `except ValueError` callers still work.
  - Bad arguments (a negative tick or frame, a bar or beat below 1) stay plain `ValueError`s, documented as outside the vectors' domain.
  - `tempo_segments` is now the one shared check, used by `_section_phrases`, `seconds_at_tick` and `frames_to_ticks`. The round-1 duplicate is gone.
  - The songform `{"invalid": code}` vectors pin all three source codes, and the fixture schema closes that enum (T02c-review2-06).
  - My mutants R1 (no tempo check), R2 (refuse instead of raise) and R3 (renamed code) are killed, and so is P3 (a planted wrong invalid code) (T02c-review2-10).
- **The newly pinned rules, checked with my own mutants** (T02c-review2-10). Each is killed:
  - floor instead of ceil for `bars`, by the shared-bar vector and both trailing-tempo vectors;
  - L3 (capture not compared), by the new `lane-record-assembled-capture-swapped`;
  - F1 (the all-instrumental fallback using the last tempo and meter segments), by "a form with no phrase takes the source's tick-0 tempo and meter";
  - L1 and L2, as before;
  - MV1 (accept beat n+1);
  - MV3 (denominators 1 and 2 bar-measured as quarters) and MV4 (16 and 32 as eighths), both killed **only** by the new mixed map, which shows it adds coverage;
  - P1 (a planted mixed-meter expectation, regenerated through the case module) and P2 (a planted shared-bar onset in the JSON).
- **Refusal families on my own inputs** (T02c-review2-06): all 12 refusal codes fire with their documented ids. All three `TimeModelError` meter codes fire. A mid-bar source meter and a non-increasing source tempo both raise rather than refuse.
- **Oracles are hand-written.** The builders still never call `songform` or `timemodel`. My own derivations match all 7 assembled vectors, including the 3 new ones and the committed preparation-note case (T02c-review2-05), and all 16 new meter vectors (T02c-review2-13).
- **Schemas** (T02c-review2-14): 20 of 20 checks still pass, so the 1.1.0 changes remain additive, gated and closed.
- **Lane inheritance** (T02c-review2-15):
  - All 7 lane-record scenarios fire exactly their findings.
  - The new capture-swapped scenario reports "capture_sha256 is not inherited from mel_hymn rev 2". It names the venture's stored MIDI capture, so `melody.wellformed` stays quiet and only the inheritance check fires.
  - The scenario hymn still equals `assemble()` of the scenario world's source.
- **The `melody.wellformed` tightening** (T02c-review2-16) is vacuous at dee28e2 too: none of the base's 19 tempo maps has more than one meter segment.
- **Hard rules** (T02c-review2-19):
  - All files are under `contracts/` or `tests/contracts/`.
  - No contact address (the only URLs are `$schema`), product name, private path, audio or weights.
  - All four commits use the noreply identity and carry the Co-Authored-By trailer.
  - No runtime Score, ABC or MIDI code.
- **GLOSSARY** (T02c-review2-19):
  - "grid" and "layout" are gone from prose and names (`_layout` → `_place`).
  - `_plan` → `_section_phrases`, and `lineage` → `source_melody_id`.
  - No _Avoid_ word remains in the added hand-written lines, and nothing in `contracts`, `tests` or `scripts` still refers to `MeterError`, `_segments`, `_plan` or `_layout`.
- **Round-1 non-blocking items closed:**
  - 1: the layout rule is pinned.
  - 2: capture inheritance, the fallback and the tempo raise path are pinned.
  - 3: consumers.
  - 4: meter breadth and the `ValueError` documentation.
  - 5: documentation drift (scope string, the T02a paragraph, the §4.6 note).
  - 6: `ADDED` now excludes 1.0.x.
  - 8: the GLOSSARY nits and the duplicated tempo check.

## Non-blocking

1. **Two raise paths are still unpinned** (T02c-review2-10 R4, T02c-review2-11 R5, T02c-review2-12).
   - **R4:** deleting the up-front `bar_segments` call in `_section_phrases` passes the gate.
   - **R5:** moving both up-front checks after the identity and duplicate refusals also passes.
   - **Witnesses:**
     - Under R4, an all-instrumental form over an off-bar meter map **assembles**.
     - Under R4 or R5, an off-bar map with a SongSpec naming another revision refuses `song_melody_mismatch` instead of raising.
   - **Why the gate misses them:** the codes are pinned, but each `{"invalid": …}` vector places a phrase, and `position()` re-validates the map.
   - **What stays unpinned:** the README's "a source the time model cannot measure … is an input error, not a refusal", both for a form with no phrase and for its precedence over earlier refusals.
   - **Suggestion:** add `{"invalid": "meter_change_inside_bar"}` for an all-instrumental form over an off-bar map, and one vector that pairs an unmeasurable source with a SongSpec mismatch.
   - **Risk:** low, because `melody.wellformed` already rejects such a stored record.
2. **Meter-claim wording.** It is correct as "a phrase that keeps one meter through its end can meet a trailing meter change only off a bar line". It is too strong as "cannot occur for any valid map" (see above).
3. **Rounding.** All 7 assembled `end_frame` values are exact, so half-up rounding is exercised only by `tempo.json`. No `fixture.tempo` vector pins `tempo_segments_invalid` through `ticks_to_frames`; only assembly does.
4. **README newline.** `contracts/README.md` lost its trailing newline: the head ends with `.`, while the base ended with `\n`. The lint does not flag it.
5. **Still open from round 1:**
   - the rule tightenings also apply to 1.0.0 records (disclosed, and vacuous);
   - the manifest depends on annotations;
   - smells: `rules.py:1051` re-derives the bar-line rule, the test helpers are duplicated, `HYMN_*` restates the world hymn (re-verified equal), and tuples stand in for types.
6. **Pre-existing, outside the diff.** `lane.record_eligible` never compares a transcription's `license_chain` with its transcriber's. A Basic Pitch transcription carrying pYIN's chain still yields 0 findings (T02c-review2-17).
7. **Size** (T02c-review2-20):
   - 823 added lines of hand-written Python (720 non-blank): reference 268, vector data 436, generator 57, tests 62.
   - Plus 212 schema, 34 manifest and 102 README lines. The fix alone is about 150 hand-written lines.
   - This is over the ~400 aim, but it did not impair review.
8. **Merge order, updated for #128 (9742d88) and #130 (8361db1).** Both are now on dee28e2.

   **With #130.** #130 already carries #131's `fields` mechanism:
   - `MANIFEST_KEYS` = {version, scope, consumers, fields, records, pending}, with `fields` required;
   - version 2 and scope "vector-kinds and record fields";
   - an `added_fields()` with the old regex `added in 1\.[0-9]+\.[0-9]+`;
   - `fields: {}`;
   - `{**consumers, **fields}` validated through `check_tickets(known_tickets)`, plus `check_records`.

   #131 checks version 1 and scope "vector-kinds and added fields". Whichever of #130 and #131 lands second must:
   - keep #130's discovery structure;
   - use one agreed scope string (for example "vector-kinds, record fields and added fields") in `consumers.json`, in discovery and in both README paragraphs;
   - adopt #131's `ADDED` regex `added in 1\.[1-9][0-9]*\.[0-9]+`;
   - set `fields` to #131's two entries;
   - make `consumers` the union of binding, songform, meter, and midi once #128 lands, each list unchanged;
   - keep `records` and `pending` as in #130 (melody-spec and song-spec stay pending);
   - keep both test files. #131's subtests match "missing", "orphan" and "unknown consumer ticket slug", and #130's "duplicate or unknown consumer ticket slug" contains the last;
   - keep both `generate_fixtures.py` hooks, regenerate, and prove byte identity plus `validate.py -v` again.

   **With #128.** #128's `_check_order` (`midi.py:74-80`) calls `timemodel._segments`. #131 renames that function to the public `timemodel.tempo_segments`, which raises `TimeModelError("tempo_segments_invalid")`. Whichever of #128 and #131 lands second must:
   - switch that call, or the second branch fails with `AttributeError`. Its `except ValueError` still catches `TimeModelError`.
   - update #128's README:163 reference;
   - keep the "MIDI round trip (T02d)", "SongForm assembly (T02c)" and "Evidence-binding inputs (T02b)" README sections;
   - merge the "Not covered yet" line: #131 reflowed it, and #128 drops "the MIDI round trip";
   - add `consumers["fixture.midi"]`.

   #128 already refuses an off-bar time signature (`MidiRefusal meter_change_inside_bar`), which closes the round-1 merge item. Its `_off_bar_line` duplicates the bar-line rule and could reuse `bar_segments` (optional). #131's PR body still lists that refusal as needed; that line is now stale.

9. **Evidence hygiene in the implementer's folder.**
   - The implementer's round-2 sums (`SHA256SUMS-fixes`) all verify.
   - The round-1 `SHA256SUMS` no longer does: `probes.py` was overwritten in place at 20:45. The round-1 line expects `8f6039c3…`, and the file is now `93739fd3…`, the hash listed in `SHA256SUMS-fixes`.
   - The round-1 probe script is therefore no longer on disk, although its logs (`06-`, `09-mutation-probes.log`) are.
   - Suggestion: version evidence files (for example `probes-fixes.py`) rather than overwrite them.
   - Nothing of mine depends on that file.

## The base moved during this review

`integration` advanced from dee28e2 to `0e02d72` when #127 (S01, public-build decision and expansion trials) merged at 2026-11-08T03:03Z, so #131 is `BEHIND` again.
- #127 shares no file with #131.
- It grows `docs/spec/tickets.json` from 105 to 108 tickets, and every slug #131's manifest uses still exists.
- Neither #128 nor #130 has landed: `consumers.json` on integration is still version 1 with scope "vector-kinds".
- I made a local trial merge of 0e02d72 into cd85ce8 (never pushed, noreply identity). It keeps the reviewed patch-id `09e0de2b8daedab41b949dc7c1fcad06cce90cc0`, and passes the full gate (635 files, 0 policy violations, 56 pytest tests and 16 subtests) and `validate.py -v` (31 songform and 43 meter vectors, byte-identical regenerations) (T02c-review2-22, -22b).
- Under the merger rule, this review carries over to an updated head while its patch-id stays `09e0de2b…`.

## Evidence (SHA-256; all files in T02c-review2-SHA256SUMS)

```
a75289c4ff8f72717afcbc7bcd76e7e07237addce9b66a67d03828d8c44e87a8  T02c-review2-00-preflight.log
63345ce94d08eecc525d163c449bd0c0b5c1ff55ee90b1ebeb1bf7e8fde98aa3  T02c-review2-01-install.log
a55fab3529159eca6ce0d6fdd85679ff8c6382a4e51d36091889901b880cec83  T02c-review2-02-local-gate.log
813235653562add717c475ced96127b31a25147965b255fcb2b802f0b265c447  T02c-review2-03-validate-v-head.log
3977145244e309f4c344c67b9e8b95401cad060addca9939151fd5fa61ecef4b  T02c-review2-04-fixture-bytes.json
3920032442be3882dde5567f70aa3e0b715361755d16ae818056bf6f44eeb26f  T02c-review2-05-hand-derived.log
99b6f9a1e4a028da2c85046747651c2ada6c1dc925e7fba1002783f4eb54ae5b  T02c-review2-06-refusals.log
87846fac481b7b6376ac50e2840754f60558c822253864153d18995ae9c9ae4d  T02c-review2-07-tempo-inside-bars.log
67ab4a4da89d9540e97ea989876bbe4da9f75bf751b2c0fc32e5acc0fb003fdb  T02c-review2-08-differential.log
68836f351cde2186f1950fadf2c3aa29b41fa2dc84a787cc980f2e685bbedefd  T02c-review2-08b-differential-inputs-and-outcomes.sha256
e9c72bb1b9119743c1d509400b93d217997a52cf4c5d5e5e9d03dd55c9421d4c  T02c-review2-09-meter-claim.log
05d544b6143ed34482d2a0ae6d590d3ce260c6e6f5710dcc3ae34f69173b3b0f  T02c-review2-10-mutants.log
04e8bb1c115b37c93e8c16c5a228ac9f61bcdf50aa323025a5b95a5a3c697d71  T02c-review2-10-mutants.json
a701411f3e6c1c1987df5288270d5154b8e134e099de5a68dec2d1c975539b00  T02c-review2-11-validate-mutant-R5.log
3882f449fdb3b8cb0261d3313994903928a35913bcec9e481649cec739c87da3  T02c-review2-12-precedence-witness.log
a6c0b1f2640f33327017df817402d9fc015a7f77a953d46447f11f80b4d2bcbe  T02c-review2-13-meter-mixed.log
2c8dca433418ddc36ef0bb5cf0c3462e6890fa96d97124767c50847b8bea2034  T02c-review2-14-schema-versions.log
d20de2d87326191ecb1fb061121534adc9d1d7002aeeb86401ae1ccc1b35afaa  T02c-review2-15-lane-scenarios.log
3650838e02ee71563330d4007777fdf3076fddfeccdd0b103ca93b5b4cc5b577  T02c-review2-16-meter-tightening-base-dee28e2.log
67d64e68f15684550ff228298ecdc948b4323b3b57553a2ebb6628748e5f4fd0  T02c-review2-17-source-chain-preexisting.log
1b7710d4580ff62b5649a1acc714fdc31940dace1a5a6471fd09fe4aad6cf51b  T02c-review2-18-hosted-checks.txt
ba770d1bb12d52a98dfc127db5bdefb1819ab8ae79194b48930fd6f40cb3a674  T02c-review2-19-scope-policy-glossary.log
70779c1ec4e30aa86f4cc1defd7ba0a918b6826a5f6b8df0a5047b8f97dbf5ac  T02c-review2-20-size.txt
4b56befed5301d73de4b09a5e06758ea0774258d1e096587810359a4808c9cbd  T02c-review2-21-patch-ids.txt
e35255929d68bac23be94db1c870c84b59c5d6291c0d9e786915b025ee8d67fa  T02c-review2-22-trial-merge-0e02d72.log
813235653562add717c475ced96127b31a25147965b255fcb2b802f0b265c447  T02c-review2-22b-trial-merge-0e02d72-validate.log
```

Two logs have identical sums, and this is expected: 03 and 22b both hold the same all-pass `validate.py -v` output followed by "validate exit=0".

The 13.8 MB differential input file stays in scratch (`/Volumes/STUDIO/scratch/review-T02c-cd85ce8/fuzz-inputs.json`, SHA-256 `74c49155…799a`). `T02c-review2-probes/fuzz_inputs.py` (seed 131) regenerates it byte-identically from the head (T02c-review2-08b).

All evidence is synthetic software evidence (CI on fakes). Nothing was rendered, played or listened to.
