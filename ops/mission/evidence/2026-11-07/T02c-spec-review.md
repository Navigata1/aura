# T02c spec review: PR #131 (SongForm assembly, issue #80, part of T02 #15)

- **Head:** `969886ba03761bae2f2fae543eb6815960b9fc98`
- **Base:** `7cb7bbdfb7dc041832301f015bd25543ce6835f3`. This is the current `integration` tip, and equals `git merge-base integration 969886b`.
- **Diff:**
  - Command: `git diff 7cb7bbdfb7dc041832301f015bd25543ce6835f3...969886ba03761bae2f2fae543eb6815960b9fc98`.
  - Size: 29 files, +12094 / −13.
  - SHA-256 of the diff text: `c7da2bcb…946e`.
  - `git patch-id --stable`: `7f9d4bf57616be55f303aa980ee58d70682f90b4`.
- **Commits:** `9d6e471` (feat: reference, form, meter vectors) and `969886b` (test: OS-neutral assertion).
- **Reviewer:** independent, with disposable copies under `/Volumes/STUDIO/scratch/review-T02c-969886b/`.
- **Method:** `.claude/skills/code-review/SKILL.md`, run as two independent passes. This file is the Spec axis. Every claim below was re-checked with my own probes (`T02c-review-probes/`, logs in `T02c-review-SHA256SUMS`).

Spec sources:
- Issue #80: its body and checklist. It has no comments.
- The lead's addendum: wave-2 gap #7 (`/Volumes/STUDIO/evidence/explore/wave2-notes.md:98`), "meter-segment vectors for T04's TimeModel TypeScript twin … Add it as a new family; `tempo.json` bytes must not change".
- T02 (`contract-completion`) in `docs/spec/tickets.json`.
- The consumer tickets: T04 `contracts-codegen`, T27 `piano-roll`, T28 `song-spec`, T29 `guide`, T56 `abc-emission` and T57 `chord-symbols`. I also checked T25 `midi-in-out`, T48 `ace-routes` and T77 `timeline`.
- `/Volumes/STUDIO/evidence/T02-preparation-2026-11-06.md`.
- ADR-0029, ADR-0032 and ADR-0033, and architecture §4.6 and §5.

**Verdict: pass.** Every acceptance criterion in issue #80, and every T02 acceptance condition this slice owns, is satisfied.

One "What to build" requirement is only partially met: "Unsupported mappings refuse with typed reasons: … conflicting tempo … Never silently truncate, stretch". The cause is the defect recorded as **blocking B1** in the standards review. A tempo change after a phrase's last note, inside its last bar, is assembled and dropped instead of refused. It is counted once, there, and it blocks the merge.

## Issue #80 acceptance criteria

1. **Vectors equal hand-derived values, including an instrumental intro and outro, a repeated phrase, a tempo change and a pickup. A seeded wrong expected value fails `validate.py -v`. Satisfied.**
   - I derived four assembled vectors by hand from their inputs and the README semantics, and typed the values into a probe without calling the implementation. End frames were computed with exact fractions, not with `timemodel`. All four equal both the committed fixture and a fresh reference run, and the lineage (transcription, capture) is copied (T02c-review-05-hand-derived.log).

     | Vector | What it covers | My derivation (ticks at 960 PPQ; frames at 48 kHz) |
     |---|---|---|
     | intro, pickup, two phrases in one repeat, outro | instrumental intro **and** outro; **pickup** on beat 4; half-note triplet | ph1 `[2880, 7680)` anchors at bar line 0 and needs ceil(7680/3840) = 2 bars. ph2 `[7680, 11520)` needs 1 bar. The verse `[3840, 19200)` shifts both by +3840: onsets 6720, 7200, 7680, 8640, 9600 \| 11520, 12800, 14080. The outro is `[19200, 26880)`. end 26880 = 28 quarters × 0.5 s = 14 s = **672000** |
     | world hymn: repeated chorus and a tempo change | **repeated phrase** with a **tempo change** | The verse is 8 bars `[0, 30720)` at 500000 µs. The chorus repeats twice: ph2 (bar line 3840, 600000 µs) moves +26880 and +57600, giving onsets 30720, 32640 and 61440, 63360. The tempo changes at 30720. 16 s + 64 q × 0.6 s = 54.4 s = **2611200** |
     | sections change meter: 4/4, 3/4, 6/8 | intro and outro; **repeated phrase across a meter change** | intro `[0, 3840)`; verse ph1 +3840. waltz (3/4, 2880-tick bars) ph2 +7680 at `[11520, 17280)`. jig (6/8) ph3 +10560 and +13440. outro `[23040, 25920)`. Meter segments at 0 (4/4), 11520 (3/4) and 17280 (6/8). 27 q × 0.5 s = **648000** |
     | reordered phrases carry their meter and tempo | reorder, repeat, tempo and meter change | ph2 (3/4, 600000 µs) moves −3840 then +1920. The bridge continues 3/4. The march places ph1 at +14400, where both tempo and meter change. end 22080: 15 q × 0.6 s + 8 q × 0.5 s = 13 s = **624000** |

   - The preparation doc's first case reproduces through the reference: onsets 3840, 4800, 7680 and 8640, end 11520 (same log). It is not committed as a vector (non-blocking 4).
   - The seeded wrong value fails the gate three ways:
     - the PR's own test (case-module onset 6720→6721, through both CLIs);
     - my plant of the pickup's expected onset 6720→6721 directly in `vectors/songform.json`, which fails with "reference gives … fixture expects …" and a regeneration mismatch (T02c-review-08a);
     - my plant of a `fixture.meter` expectation (bar 5 beat 3, 16320→16321) regenerated through the case module, which fails the vector check alone (T02c-review-08b).

2. **A refusal vector for every listed unsupported mapping. Satisfied** (with B1 noted). The committed vectors cover all 12 refusal codes:

   | Listed mapping | Committed vector |
   |---|---|
   | missing phrase | "missing phrase" |
   | duplicate phrase id | "duplicate phrase id" (the first match is never picked) |
   | overflow | "phrases overflow their bars" |
   | zero-length phrase | "zero-length phrase" |
   | note crossing a phrase edge | "note crosses a phrase end" and "… start" |
   | conflicting tempo | "tempo change inside a phrase" and "phrases of one section disagree on tempo" |
   | conflicting meter | "meter change inside a phrase" and "phrases of one section disagree on meter" |

   They also cover: source not a melody, SongSpec mismatch (rev and project), duplicate section, section-kind mismatch (both directions) and misplaced chord symbols (beyond the repeat, out of order).

   My own one-per-family mutations, which differ from the vectors, all refuse with the documented code and ids, and the three `MeterError` codes fire (T02c-review-06-refusals.log). The gap is B1: the tempo check stops at the phrase's end tick rather than at its last bar line (T02c-review-07).

3. **Lane and license-chain inheritance proven through the world/reference gate, with a negative case. Satisfied.**
   - `SC-LANE-RECORD-ASSEMBLED-INDIVIDUAL-OK` is valid.
   - `…-READ-IN-LLC` and `…-LEGACY-ASSEMBLED-READ-IN-LLC` fire "lanes ['individual', 'research'] exclude llc".
   - `…-LINEAGE-DROPPED` and `…-CHAIN-LAUNDERED` fire "transcription is not inherited from mel_hymn rev 2" (T02c-review-10).
   - Removing the `assembled_from` recursion or the exact-inheritance check fails the gate (T02c-review-11, mutants L1 and L2).
   - The scenario's assembled hymn equals `assemble()` of the scenario world's Basic Pitch source.

4. **Pre-existing fixture bytes unchanged; a 1.0.0 record still validates after the minor bump; an unknown property in a closed object fails. Satisfied.**
   - Bytes: 310 of 310 base fixture files are identical and 15 are added (T02c-review-04).
   - 1.0.0 records: all world 1.0.0 melody and song records validate, the frozen 1.0.0 assembled records without a form included.
   - Unknown properties are rejected in `form`, in `form.sections[].phrases[]` and in a chord symbol (T02c-review-12, and the 7 new invalid records).

5. **`contracts/consumers.json` maps the new kinds and fields to their real consuming tickets** (song intent, the guide, ABC emission). **Satisfied for the named tickets.**
   - `fixture.songform` → contract-completion, song-spec, guide, abc-emission.
   - `fixture.meter` → contract-completion, contracts-codegen, song-spec, guide, piano-roll.
   - The `form` field → song-spec, guide, abc-emission, midi-in-out, export, ace-routes and timeline (each with contract-completion).
   - The `chord_symbols` field → chord-symbols and abc-emission (with contract-completion).
   - All slugs exist. Discovery fails in both directions (PR test subtests: field without consumer, orphan, unknown slug, newly annotated field).
   - Its accuracy can be improved (non-blocking 1).

6. **Lead's addendum: meter-segment vectors for T04's TimeModel twin. Satisfied.**
   - `fixture.meter` holds 27 hand-derived cases: 15 `position`, 7 `tick` and 5 typed errors (`beat_outside_bar` ×2, `meter_change_inside_bar`, `meter_segments_invalid` ×2).
   - They cover bar and beat boundaries across 4/4 → 3/4 → 6/8 at 960 PPQ, including the last meter running past the form.
   - I re-derived every position and tick by hand and they match.
   - It is a new family, `tempo.json` is byte-unchanged, and T04 (`contracts-codegen`) and T27 (`piano-roll`) are consumers.
   - Its breadth is limited (non-blocking 3).

## "What to build" in issue #80

- **Explicit full-form duration and section boundaries, additive; intros and outros never dropped; names survive. Met.**
  - melody-spec 1.1.0 `form.end_tick` holds the duration, and `form.sections` lists every repeat with its id, name, kind, span and placed phrases.
  - In the pickup case the outro ends 11520 ticks after the last note.
  - A 1.0 assembled record has no form, and the README tells consumers to refuse it.
- **Integer ticks at 960 PPQ and one rounding function; tempo and meter semantics explicit when phrases reorder or repeat. Met.**
  - The waltz and journey cases cover reorder and repeat.
  - Each vector states `end_frame` through `ticks_to_frames`, but every value is exact (non-blocking 5).
- **Source lanes and license chain inherited, exercised through the world/reference gate. Met** (criterion 3).
- **Unsupported mappings refuse with typed reasons; never silently truncate, stretch or pick the first match. Partially met:** see standards B1.
- **Optional chord-symbol field by minor version. Met.**
  - song-spec 1.1.0 `chord_symbols` is a non-empty list of `{offset_ticks, symbol}`, accepted only from 1.1.
  - Assembly checks placement and does not copy the symbols.
  - There is one assembled vector and two refusal vectors, plus 3 invalid records.

**Out of scope, and nothing claimed beyond the slice. Met.**
- All 29 files are under `contracts/` or `tests/contracts/`. There is no runtime Score, UI, ABC or MIDI code (T02c-review-14).
- The PR's "Unverified / still open" list is honest, with one exception: the claim that every unsupported mapping refuses (B1).

## T02 (`contract-completion`) original acceptance: what this slice owns

| T02 acceptance | Status for this slice |
|---|---|
| validate.py passes; no existing fixture byte changes (additions only) | Satisfied |
| SongForm, ABC and MIDI vectors equal hand-derived values: pickup, triplet, tempo change, zh and fr lyric cases, a 6 min 30 s form, an instrumental section; a seeded wrong value fails | **SongForm part satisfied**: pickup, triplet (carried exactly as 1280-tick notes), tempo change and instrumental sections. The zh, fr and 6 min 30 s cases are ABC emission (T02e #86), and MIDI is T02d (#128). Both stay open. |
| A record carrying every new optional field validates; an unknown property fails; 1.0.0 still validates | Satisfied for the two fields this slice adds. The remaining v1 fields stay T02. |
| The manifest maps every new field, vector kind and schema to a consumer and fails on a missing, unknown or orphan entry | Satisfied for this slice's two fields and two vector kinds. The full inventory stays T02 (see standards non-blocking 6). |
| Registry pre-seeding, plumbing self-test (T02a), route standing (T02f) | Not this slice. The T02a tests still pass. |

## The Spec pass's findings, with my verification

- **(c) "Shared bar inserts rest", rated medium by the pass.** I reproduced it (T02c-review-07, C1–C3).
  - Phrases that share a source bar take separate bars: with ph1 `[0, 5760)` and ph2 `[5760, 7680)`, ph2's note moves from 5760 to 9600.
  - The source's own 2 bars refuse `phrase_overflow`.
  - T28's default form (one vocal section per phrase) behaves the same way.
  - The README states this rule (`:163-164`, and under "Still open"), and it is deterministic, so it is not silent. **Non-blocking** (2).
- **(c) "Tempo check covers only the span", rated low by the pass.** This is the same defect as standards **B1**. I judge it blocking there, because it contradicts the README's own refusal list and silently drops a source tempo change.
- **(a) Missing or partial:**
  - No vector has a phrase ending mid-bar. Confirmed: the floor mutant survives the gate (standards non-blocking 1).
  - The preparation-doc case is not a vector. Confirmed, though the reference reproduces it.
  - The consumer mapping can be more accurate. Confirmed.
  - Meter coverage is narrow. Confirmed.
  - End frames are all exact. Confirmed.
- **(b) Not asked for:**
  - The `melody.wellformed` bar-line rule is the lead's deliberate tightening. It is vacuous for every pre-existing record (T02c-review-13).
  - The extra refusals (`section_kind_mismatch`, `source_not_melody`, `song_melody_mismatch`, `duplicate_section`, `chord_symbol_misplaced`) are typed and documented, and fail closed.
  - The reference signature differs from architecture §4.6.

## Non-blocking

1. **Consumer accuracy.**
   - `fixture.songform` omits `ace-routes`, yet T48's acceptance reads "assemble-audio produces slices whose boundaries equal the SongForm vector's frames". ace-routes appears only on the `form` field.
   - `fixture.meter` lists `guide`, but T29 has no bar or beat criterion.
   - It omits `abc-emission` (T56, "full bars"), `timeline` (T77, "zooms in bars and beats") and `midi-in-out` (T25, time signatures through the TimeModel).
2. **Shared-bar layout.** The rule is documented but no vector pins it, and the T28 default form inherits a one-bar gap wherever phrases share a bar. Add the C1 case as an assembled vector (it also pins the ceil rule), and note this behaviour for T28.
3. **Meter vector breadth.** There is one valid map, with denominators 4 and 8 only. Consider a second map and denominators 1, 2, 16 and 32 so that T04's twin is held to beat length 3840 / d. Also document the `ValueError` inputs (tick < 0, bar or beat < 1), which lie outside the fixture's schema domain.
4. **The preparation doc's first case** (onsets 3840/4800/7680/8640, end 11520) is not a committed vector.
5. **Rounding.** No songform `end_frame` exercises half-up rounding; `tempo.json` still covers it.
6. **Interface.** `assemble(melody, song, output)` differs from architecture §4.6 `assemble(melody, form) -> melody`. T28 should reconcile them.
7. **GLOSSARY** has no entry for "pickup" or "chord symbol". The PR discloses this, and it is a `domain-modeling` gap.
8. **Merge order with #128 (T02d) and #130 (T02b).** The reconciliation is spelled out in the standards review, non-blocking 11, and in the review JSON:
   - Keep both manifest mechanisms (`records`/`pending` and `fields`) and both checks.
   - Use version 2 with `fields` as a required key.
   - Keep the union of consumers.
   - Keep every README section.
   - Add a typed MIDI refusal for an off-bar time signature.

## The base moved during the review

`integration` moved to `dee28e2` when #129 (T03) merged, so #131 is `BEHIND`.
- A local trial merge, never pushed, keeps the reviewed patch-id `7f9d4bf57616be55f303aa980ee58d70682f90b4`.
- It passes the full gate and `validate.py -v` (T02c-review-18-trial-merge-dee28e2.log, T02c-review-18b-trial-merge-dee28e2-validate.log).
- No acceptance item above changes on the new tip.

## Evidence

See the standards review for the SHA-256 table, and `T02c-review-SHA256SUMS` for every file. The spec-specific logs are:
- `T02c-review-05-hand-derived.log`
- `T02c-review-06-refusals.log`
- `T02c-review-07-tempo-inside-bars.log`
- `T02c-review-08a-*`
- `T02c-review-08b-*`
- `T02c-review-10-lane-scenarios.log`
- `T02c-review-12-schema-versions.log`
- `T02c-review-13-meter-tightening.log`
- `T02c-review-14-scope-and-policy.log`

All of it is synthetic software evidence (CI on fakes). Nothing was rendered, played or listened to, and no musical-quality claim is made.
