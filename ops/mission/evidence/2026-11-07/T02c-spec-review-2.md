# T02c spec review 2: PR #131 at cd85ce8 (SongForm assembly, issue #80, part of T02 #15)

- **Head:** `cd85ce80580c82df6222f2c7d7df7a5b4eea4b89`
- **Base:** `dee28e2fd2b7a79ca2773e639a4a714af5c356b8`. This is the `integration` tip after T03 #129, and equals `git merge-base integration cd85ce8`.
- **Diff (the whole patch, fresh):**
  - Command: `git diff dee28e2fd2b7a79ca2773e639a4a714af5c356b8...cd85ce80580c82df6222f2c7d7df7a5b4eea4b89`.
  - Size: 30 files, +15192 / −23.
  - SHA-256 of the diff text: `f8f10735…ab27`.
  - `git patch-id --stable`: `09e0de2b8daedab41b949dc7c1fcad06cce90cc0`.
- **The fix alone:** `git diff 1af6154 cd85ce8`.
- **Commits:** `9d6e471`, `969886b`, `1af6154` (a pure merge of dee28e2 that keeps the round-1 patch-id `7f9d4bf5…`) and `cd85ce8` (the fix).
- **Reviewer:** independent, with disposable copies under `/Volumes/STUDIO/scratch/review-T02c-cd85ce8/`. My probes are in `T02c-review2-probes/`, and the logs in `T02c-review2-SHA256SUMS`.

Spec sources (unchanged from round 1):
- Issue #80. It still has no comments.
- The lead's addendum (wave-2 gap #7: meter-segment vectors for T04's twin).
- T02 in `docs/spec/tickets.json`.
- The consumer tickets T04, T25, T27, T28, T29, T48, T56, T57 and T77.
- The preparation note, ADR-0029, ADR-0032, ADR-0033, and architecture §4.6 and §5.

**Verdict: pass.**
- Every acceptance criterion in issue #80, and every T02 acceptance condition this slice owns, is satisfied at cd85ce8.
- The one "What to build" requirement that round 1 found partially met is now met. That requirement is "Unsupported mappings refuse with typed reasons: … conflicting tempo … Never silently truncate, stretch".

## Issue #80 acceptance criteria

1. **Vectors equal hand-derived values, including an instrumental intro and outro, a repeated phrase, a tempo change and a pickup. A seeded wrong expected value fails `validate.py -v`. Satisfied.**
   - My own derivations match all 7 assembled vectors (T02c-review2-05):

     | Vector | My derivation |
     |---|---|
     | the 4 from round 1 | unchanged: 672000, 2611200, 648000 and 624000 frames |
     | **preparation case**, now committed | onsets 3840, 4800, 7680, 8640; end 11520; 288000 frames |
     | **shared bar** | ph1 `[0, 5760)` needs ⌈5760/3840⌉ = 2 bars. ph2 `[5760, 7680)` anchors at 3840 and takes slot 3 (shift +3840), so its note moves from 5760 to **9600**. One 3-bar section; end 11520 |
     | **no phrase** | the waltz source's tick-0 values: 4/4 at 500000 µs, not its later 3/4 at 600000 µs. Sections `[0, 7680)` and `[7680, 11520)`, no notes, 288000 frames |

   - The preparation-note case (onsets 3840/4800/7680/8640, end 11520) is now a committed vector. That closes round-1 non-blocking 4.
   - The seeded wrong value fails in three ways:
     - the PR's own test;
     - my planted shared-bar onset in the JSON (9600→5760), and my planted invalid code (T02c-review2-10, P2 and P3);
     - my planted mixed-meter expectation, regenerated through the case module (P1). Only the vector check fails.

2. **A refusal vector for every listed unsupported mapping. Satisfied, now including B1's case.**
   - All 12 refusal codes are covered.
   - "Conflicting tempo" now also covers "tempo change after a phrase's last note, inside its last bar" and "tempo change where a phrase ends mid-bar".
   - The round-1 B1 probe re-run shows no README/reference disagreement (T02c-review2-07).
   - Over 4031 inputs, the head's outcomes are byte-identical to my independent round-1 candidate fix (T02c-review2-08).
   - My own one-per-family mutations all refuse as documented (T02c-review2-06).
   - **Meter conflict:** a meter change in a phrase's trailing rest is either off a bar line, which raises `meter_change_inside_bar` and is pinned as `{"invalid": "meter_change_inside_bar"}`, or comes after an in-span change that already refuses. I proved this and confirmed it exhaustively over 3,050,104 pairs (T02c-review2-09). Nothing is retimed.

3. **Lane and license-chain inheritance through the world/reference gate, with negative cases. Satisfied, with one more negative case.**
   - `lane-record-assembled-capture-swapped` reports "capture_sha256 is not inherited". Lineage-dropped, chain-laundered, read-in-llc and legacy-read-in-llc still fire, and individual-ok is valid (T02c-review2-15).
   - My mutants L1, L2 and L3 are killed (T02c-review2-10).

4. **Pre-existing fixture bytes unchanged; a 1.0.0 record still validates; an unknown property in a closed object fails. Satisfied.**
   - Bytes: 310 of 310 dee28e2 fixtures are identical and 16 are added (T02c-review2-04).
   - Schemas: 20 of 20 checks pass (T02c-review2-14).

5. **`consumers.json` maps the new kinds and fields to their real consuming tickets. Satisfied, and more accurate than in round 1.**
   - `fixture.songform` now also names `ace-routes` (T48: "slices whose boundaries equal the SongForm vector's frames").
   - `fixture.meter` now names contract-completion, contracts-codegen, song-spec, piano-roll, `abc-emission` (T56, full bars), `timeline` (T77, bars and beats) and `midi-in-out` (T25). `guide` was dropped, since T29 uses no bars.
   - The scope reads "vector-kinds and added fields", and every slug is real.

6. **Lead's addendum: meter-segment vectors for T04's TimeModel twin. Satisfied.**
   - There are 43 cases on two maps:
     - 4/4 → 3/4 → 6/8;
     - 2/2 → 1/1 → 7/16 → 5/32, so every allowed denominator (1, 2, 4, 8, 16 and 32) appears.
   - I derived all 16 new cases by hand and they match (T02c-review2-13). For example:
     - tick 13199 → bar 4, beat 7, offset 239 (a 7/16 bar is 1680 ticks, and 1679 = 6 × 240 + 239);
     - tick 16079 → bar 7, beat 5, offset 119 (5/32 bars are 600 ticks: 1199 = 600 + 4 × 120 + 119);
     - bar 7 beat 5 → 15960;
     - a 1/1 bar has no beat 2.
   - Mutants that mis-measure only denominators 1 and 2, or only 16 and 32, are caught only by the new map (T02c-review2-10, MV3 and MV4).
   - `TimeModelError` codes, and the documented `ValueError` input domain, give the twin one error contract.

## "What to build" in issue #80

| Requirement | Status at cd85ce8 |
|---|---|
| Explicit full-form duration and section boundaries, additive; intros and outros never dropped; names survive | Met. Melody-spec 1.1.0 `form` is unchanged from round 1. |
| Integer ticks at 960 PPQ and one rounding function; tempo and meter semantics explicit under reorder and repeat | Met. Every `end_frame` is exact, so half-up rounding is exercised only by `tempo.json` (non-blocking 2). |
| Source lanes and license chain inherited, exercised through the world/reference gate | Met (criterion 3). |
| Unsupported mappings refuse with typed reasons; never silently truncate, stretch or pick the first match | **Met** (B1 fixed). Unmeasurable sources raise a typed `TimeModelError`, pinned per code. The precedence of that raise over earlier refusals, and the case of a form with no phrase, are not pinned (non-blocking 1). |
| Optional chord-symbol field by minor version | Met, unchanged. |

**Out of scope, and nothing claimed beyond the slice. Met.**
- All 30 files are under `contracts/` or `tests/contracts/`, and there is no runtime Score, UI, ABC or MIDI code (T02c-review2-19).
- The PR's "Unverified / still open" list is now accurate on refusals.
- One stale line remains: it still says #128 needs a typed off-bar time-signature refusal, which #128 has since added (9742d88).

## T02 (`contract-completion`) original acceptance: what this slice owns

| T02 acceptance | Status |
|---|---|
| validate.py passes; no existing byte changes (additions only) | Satisfied against dee28e2 |
| SongForm, ABC and MIDI vectors (pickup, triplet, tempo change, zh, fr, 6 min 30 s, instrumental section); a seeded wrong value fails | **SongForm part satisfied**: pickup, triplet, tempo change and instrumental sections. ABC (zh, fr, 6 min 30 s) is T02e #86, and MIDI is T02d #128. Both stay open. |
| A record with every new optional field validates; an unknown property fails; 1.0.0 still validates | Satisfied for this slice's two fields |
| The manifest maps every new field, vector kind and schema to a consumer, and fails on missing, unknown or orphan entries | Satisfied for this slice. The full inventory stays T02. |
| Registry pre-seeding, the plumbing self-test (T02a), route standing (T02f) | Not this slice |

## Non-blocking

1. **Raise precedence and the no-phrase raise are unpinned.**
   - Without the up-front meter check, an all-instrumental form over an off-bar map assembles.
   - With the checks moved after the identity refusals, a SongSpec mismatch refuses instead of raising.
   - Both mutants pass the gate (T02c-review2-10 R4, -11 R5, -12).
   - Add the two vectors named in standards review 2, non-blocking 1.
2. **Rounding.** No songform `end_frame` exercises half-up rounding.
3. **Merge order** with #128 (9742d88) and #130 (8361db1). See standards review 2, non-blocking 8: the scope strings, the `ADDED` regex, `fields`, and #128's call to the renamed `timemodel._segments`.
4. **GLOSSARY** still has no entry for "pickup" or "chord symbol". The PR discloses this, and it is a `domain-modeling` gap.

## The base moved during this review

`integration` advanced to `0e02d72` when #127 (S01) merged, so #131 is `BEHIND`.
- #127 changes `docs/spec/tickets.json`, now 108 tickets, but every consumer slug this slice uses still exists.
- A local trial merge, never pushed, keeps the reviewed patch-id `09e0de2b…` and passes the full gate and `validate.py -v` (T02c-review2-22, -22b).
- No acceptance item above changes on the new tip.

## Evidence

The SHA-256 table is in the standards review 2, and every file is in `T02c-review2-SHA256SUMS`. The spec-specific logs are:
- `T02c-review2-05-hand-derived.log`
- `T02c-review2-06-refusals.log`
- `T02c-review2-07-tempo-inside-bars.log`
- `T02c-review2-08-differential.log`
- `T02c-review2-09-meter-claim.log`
- `T02c-review2-10-mutants.*`
- `T02c-review2-13-meter-mixed.log`
- `T02c-review2-15-lane-scenarios.log`
- `T02c-review2-19-scope-policy-glossary.log`

All of it is synthetic software evidence (CI on fakes). Nothing was rendered, played or listened to, and no musical-quality claim is made.
