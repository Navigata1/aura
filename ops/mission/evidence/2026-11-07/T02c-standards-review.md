# T02c standards review: PR #131 (SongForm assembly, issue #80, part of T02 #15)

- **Head:** `969886ba03761bae2f2fae543eb6815960b9fc98`
- **Base:** `7cb7bbdfb7dc041832301f015bd25543ce6835f3`. This is the current `integration` tip, fetched 2026-11-07, and equals `git merge-base integration 969886b`.
- **Diff:**
  - Command: `git diff 7cb7bbdfb7dc041832301f015bd25543ce6835f3...969886ba03761bae2f2fae543eb6815960b9fc98`.
  - Size: 29 files, +12094 / −13.
  - SHA-256 of the diff text: `c7da2bcbf344ce97ab8c57d2f613e5fa9356f80b5af64a4cbb564983e99e946e`.
  - `git patch-id --stable`: `7f9d4bf57616be55f303aa980ee58d70682f90b4` (T02c-review-15-patch-id.txt). The merger compares it under the updated merger rule.
- **Commits:**
  - `9d6e471` feat(contracts): SongForm assembly reference, explicit form and meter vectors (T02c)
  - `969886b` test(contracts): match the seeded-onset failure without OS path separators
- **Reviewer:** independent. I never edited the implementation. My disposable copies are under `/Volumes/STUDIO/scratch/review-T02c-969886b/`:
  - `head` and `base` are clones of the bare repository.
  - `mut-*` are tracked-file copies used for mutations.
  - Both clones were left clean at their SHAs.
- **Method:** `.claude/skills/code-review/SKILL.md` from the integration tree, run as two independent passes.
  - A Standards sub-agent and a Spec sub-agent each received the diff and the source documents, but not my hypotheses.
  - I then re-verified every finding with my own probes.
  - The probe scripts are in `T02c-review-probes/`. The logs and SHA-256 sums are listed at the end and in `T02c-review-SHA256SUMS`.

**Verdict: block.** There is one blocking finding (B1) and eleven non-blocking ones.

Standards sources:
- `CLAUDE.md`: hard rules 1–14 and the parallel-work rules.
- `GLOSSARY.md`.
- `contracts/README.md`, including the PR's own section "SongForm assembly (T02c)".
- ADR-0029, ADR-0032 and ADR-0033.
- `docs/spec/architecture.md` §4.6, §5 and §6.3.
- `/Volumes/STUDIO/evidence/protocol/AGENT-PROTOCOL.md`.
- The skill's Fowler smell baseline. Smells are always judgement calls.

## Blocking

### B1. The reference assembles a tempo change that its own README contract says it refuses

The PR's README section is the normative text for every consumer, including the TypeScript twin and the T28 runtime. It says:
- `contracts/README.md:160`: "A placed phrase occupies every bar its span touches, counted from the bar line at or before its start".
- `:168`: "Each placed phrase has one tempo and one meter over its bars in the source".
- The refusal list at `:191-192`: "`meter_conflict` and `tempo_conflict` (a change inside its bars)".
- `:153`: "refuse, never truncate, stretch, retime or pick".

The reference does not check the same range. `songform.py:51-54` refuses only for a change strictly inside `(anchor, end)`, that is, from the phrase's bar line to its last tick. It does not check to the end of the last bar the phrase occupies.

My probe (T02c-review-07-tempo-inside-bars.log) uses a phrase `ph1 [0, 5760)` in 4/4. It occupies bars `[0, 7680)`.

| Case | Source tempo change | README says | Reference does |
|---|---|---|---|
| A1 | at 6720, in the second bar after the last note | refuse `tempo_conflict` | **assembles**. The tempo map becomes `[(0, 500000)]`: the change is dropped, and those bars play in 4.0 s instead of the source's 4.1 s. |
| A2 | at 5760, exactly at the phrase end, mid-bar | refuse | **assembles**: 4.0 s instead of 4.2 s. |
| A3 | at 4800, inside the span | refuse | refuses |
| B | pickup `[2880, 7680)`, change at 1920 in the leading rest of its first bar | refuse | refuses |

The check covers the leading rest of a first bar but not the trailing rest of a last bar. That asymmetry suggests the gap is unintended.

The committed vectors cannot tell the two behaviours apart:
- The README-consistent patch (T02c-review-09b-candidate-fix.diff) checks `(anchor, anchor + bars × bar)`.
- It passes all 23 songform vectors and the full `validate.py -v` (T02c-review-09b-validate-candidate-fix.log).
- It turns A1 and A2 into `tempo_conflict` refusals (T02c-review-09b-tempo-bars-on-fix.log).

So a twin or runtime written from the README would refuse where this reference assembles, and the gate would never notice. That is the drift the language-neutral reference exists to prevent (ADR-0033, "two runtimes that round differently would drift apart").

The PR body's claim "Every unsupported mapping refuses with a typed reason; nothing is truncated, stretched, retimed …" is not yet true.

Meter is not affected:
- Meter changes land only on bar lines (`_plan` → `bar_segments`).
- Every interior bar line of a phrase's bars lies before the phrase's end.

**Fix (recommended).**
- In `_shape`, refuse any tempo change (and, for symmetry, any meter change) inside the phrase's whole bars.
- Add a refusal vector, for example "tempo change after a phrase's last note, inside its last bar".

**Alternative.** Reword the README to "inside its span" and pin the dropped change with an assembled vector. This contradicts "never … retime", so it is the weaker choice.

## Verified (no finding)

- **Local gate** (T02c-review-02-local-gate.log): passes at 969886b with `--base 7cb7bbd`:
  - the clean tracked-copy contract gate (59 rules, components regenerate byte-identically);
  - 48 pytest tests and 16 subtests;
  - vitest (2 packages) and the node test;
  - the build;
  - the policy scan (628 tracked files, 0 violations);
  - runtime licences.
  - The disk preflight ran first (T02c-review-00-preflight.log). Everything was installed into the clone on STUDIO.
- **`validate.py -v`** (T02c-review-03-validate-v-head.log):
  - 23 `fixture.songform` and 27 `fixture.meter` vectors;
  - 100 invalid records rejected for the named reason;
  - 99 failing and 9 valid scenarios, with 59 rules exercised;
  - 331 files valid by kind;
  - 2 byte-identical regenerations.
- **Hosted CI** at the head: `checks / foundation` passes on ubuntu, macos and windows-latest (run 42436131651, attempt 1).
  - The earlier windows-only failure at 9d6e471 (run 42435931964, attempt 1) was not retried.
  - 969886b changes only the assertion, and makes it stricter: it now also matches the case name and "reference gives". No test was weakened.
- **Fixture bytes** (T02c-review-04-fixture-bytes.json):
  - All 310 base files under `contracts/fixtures` have identical SHA-256 sums at the head: 0 changed and 0 missing.
  - The 15 added files all show as `A` in the diff.
  - `vectors/tempo.json` is unchanged.
- **Oracles are hand-written.**
  - `vector_cases/songform.py` and `meter.py` `build()` contain literal values and never call `songform` or `timemodel`.
  - My four independent hand derivations match the fixture (spec review; T02c-review-05-hand-derived.log).
  - A planted wrong onset in `vectors/songform.json` fails the gate (T02c-review-08a: vector mismatch plus regeneration mismatch).
  - So does a wrong `fixture.meter` expectation planted in the case module and regenerated (T02c-review-08b: only the vector check fails).
- **Tests go through the seams.** `tests/contracts/test_songform.py` drives the shipped `generate_fixtures.py` and `validate.py` CLIs on tracked copies. Nothing mocks an internal collaborator.
- **Fail-closed apart from B1.**
  - Every refusal code fires as documented on my own mutations, which differ from the vectors (T02c-review-06-refusals.log).
  - A mid-bar source meter raises `MeterError meter_change_inside_bar` instead of assembling.
  - The validator treats a raising evaluator as a failure.
- **Minor versions are additive and gated** (T02c-review-12-schema-versions.log, 20 of 20 checks), using records I built myself:
  - Every 1.0.0 world melody and song record validates, the frozen 1.0.0 assembled hymn without a form included.
  - `form` is accepted only on assembled records claiming 1.1 or later, and is required from 1.1.
  - `chord_symbols` on any section is rejected below 1.1, so `contains` works for section 2 as well as section 0.
  - An empty chord list fails, an empty `form.sections` fails, and unknown properties fail in `form`, in `form.sections[].phrases[]` and in a chord.
- **`melody.wellformed` tightening.** The new rule that a meter changes only on a bar line (`rules.py:1050-1052`) is vacuous for every pre-existing record:
  - None of the 19 tempo maps anywhere under the base `contracts/` tree has more than one meter segment (T02c-review-13-meter-tightening.log).
  - Every pre-existing scenario still fires exactly its named rules.
  - It is consistent with ADR-0033: bar and beat positions across meter segments are well defined, and the same in both twins, only when a segment starts on a bar line. Tick↔frame rounding is untouched.
  - The rule applies to 1.0.0 records too. The PR discloses that, and no existing record is affected.
- **Lane and license-chain inheritance through `assembled_from`** (ADR-0029 amendment, `lane.record_eligible`) is enforced in the world/reference gate:
  - Each `lane-record-*` scenario fires exactly its intended finding (T02c-review-10-lane-scenarios.log): an llc read of the 1.1.0 or the 1.0.0 assembled hymn reports "lanes ['individual', 'research'] exclude llc", and a dropped or laundered transcription reports "transcription is not inherited from mel_hymn rev 2".
  - Mutants are killed: removing the `assembled_from` recursion fails `legacy-assembled-read-in-llc` (L1), and removing the exact-inheritance check fails `lineage-dropped` and `chain-laundered` (L2) (T02c-review-11-*).
  - The scenarios' 1.1.0 assembled hymn equals `assemble()` of the scenario world's Basic Pitch source.
- **Integers only and deterministic.** No float reaches a hashed record. Notes are sorted and note ids are sequential, and nothing depends on dict order.
- **Hard rules** (T02c-review-14-scope-and-policy.log):
  - No secret, contact address (the only URLs are `$schema`), product name, private path, audio or weights in the diff.
  - Every changed file is under `contracts/` or `tests/contracts/`.
  - Commits use the noreply identity and carry the Co-Authored-By trailer.
  - No lane check is skipped; the diff only adds checks.
- **GLOSSARY.** SongForm, Section, Phrase, Assembled melody, MelodySpec, SongSpec, Tempo map and Guide are used as defined. The only naming nits are in N8.

## Non-blocking

1. **The whole-bar layout rule is not pinned.**
   - Rule: `bars` is rounded up, and two phrases never share a bar (`songform.py:62`, README:164).
   - No committed source marks a phrase that ends mid-bar (T02c-review-07, note D).
   - A floor-instead-of-ceil mutant passes the full gate (T02c-review-09a). Its validate log is byte-identical to the head's.
   - Suggestion: add an assembled vector where a phrase ends mid-bar and another follows. For example, `ph1 [0, 5760)` then `ph2 [5760, 7680)` in a 3-bar section gives ph2's note at 9600 and an end of 11520.
2. **The `capture_sha256` half of the new inheritance check is not pinned.** A mutant that compares only `transcription` (`rules.py:927`) passes the gate (T02c-review-11-…-L3). Suggestion: add a scenario with a wrong capture on a 1.1 assembled record.
3. **More paths have no vector:**
   - the all-instrumental fallback (`songform.py:114-115`);
   - the raise paths (`songform.py:68-71`);
   - half-up rounding: all four assembled `end_frame` values are exact, so the songform family never exercises it. `tempo.json` still does.
4. **Error types.** `timemodel.position` and `tick_at` raise a bare `ValueError` for tick < 0 or bar or beat < 1 (`timemodel.py:74`, `:84`). `songform._plan` also raises a bare `ValueError` for a bad tempo map (`:70`).
   - These inputs lie outside `fixture-meter`'s schema domain, so no vector can hold them.
   - The README (`:205`) says only that the twin must reproduce the `MeterError` codes.
   - Suggestion: say that these are input errors, not `MeterError`s.
5. **Documentation drift:**
   - README:133 still says the manifest "is deliberately scoped to vector kinds", and `consumers.json` keeps `"scope": "vector-kinds"`, although the manifest now also maps `fields`.
   - architecture §4.6 gives `assemble(melody, form) -> melody`, but the reference is `assemble(melody, song, output)`. T28 should reconcile the two.
6. **The manifest depends on annotations.**
   - `fields` tracks only locations that carry `$comment: "added in 1.x.y"`, so an unannotated minor addition escapes the check.
   - Each 1.1 gate is a hand-written `allOf` (Shotgun Surgery smell).
   - `ADDED` (`vector_discovery.py:7`) also matches "added in 1.0.0".
   - This is adequate for the slice. The full consumer inventory stays T02 work.
7. **Rule tightenings also apply to 1.0.0 records.** They are disclosed and vacuous for existing fixtures (see Verified):
   - the bar-line meter rule;
   - exact inheritance for a non-null 1.0 lineage.
   - One consequence: MIDI import must refuse a time signature off a bar line. See the merge note (N11).
8. **Smells (judgement calls):**
   - **Duplicated Code:**
     - The tempo-map check in `_plan` (`songform.py:68-70`) repeats `melody.wellformed` and `timemodel._segments`.
     - `rules.py:1051` re-derives what `bar_segments` already enforces.
     - `test_songform.py:15-32` copies `setUp` and `run_cli` from `test_vector_discovery.py`.
     - `HYMN_*` restates the world hymn (my probe shows the two are equal today).
   - **Primitive Obsession:**
     - the `time` tuple, read as `[0]` and `[1:]`;
     - the 4-tuple bar segments;
     - the 5-tuple `_layout` return.
   - **GLOSSARY:**
     - "bar grid" (README:155 and the songform docstring) uses the _Avoid_ word "grid" from Tempo map.
     - `_layout` uses "layout", an _Avoid_ word for SongForm.
     - `_plan` can be confused with Score.plan.
     - `lineage` holds a melody id (`rules.py:1066`).
9. **Pre-existing, outside the diff (a follow-up).** `lane.record_eligible` compares a transcription's `eligible_lanes` with its transcriber's but never its `license_chain`.
   - A Basic Pitch transcription carrying pYIN's chain, on both the source and its 1.1.0 assembled copy, yields 0 findings (T02c-review-17-source-chain-preexisting.log).
   - Lanes cannot widen, because they are computed from the profile. Obligations could still be laundered at the source.
10. **Size:**
    - Added lines (T02c-review-16-size.txt): 724 of hand-written Python (627 non-blank), plus 205 schema, 30 manifest and 84 README lines.
    - Python breakdown: reference 259, vector data 350, generator hooks 53, tests 62.
    - The aim is about 400, and the PR states about 711.
    - The excess did not impair review: the reference is compact, and the vector data is literal with written derivations.
    - The meter family, added at the lead's request, would have fit a PR of its own.
11. **Merge order with #128 (T02d, head 19985b8) and #130 (T02b, head dd300ff).** Both are based on 7cb7bbd.

    **The manifests and checks:**
    - **This PR** keeps `consumers.json` at `version` 1 and `scope` "vector-kinds", and adds a `fields` map. `added_fields()` checks it in both directions, and discovery accepts keys ⊆ {version, scope, consumers, fields}.
    - **#130** moves the manifest to `version` 2 and `scope` "vector-kinds and record fields". The keys must be exactly {version, scope, consumers, records, pending} (`MANIFEST_KEYS`, compared as a set). It adds `known_tickets()`, which includes C-ids, and `check_records()`.
    - **#128** only adds `consumers["fixture.midi"]`.
    - Each discovery refuses the other's manifest.

    **Whichever of #130 and #131 lands second must do the following in one commit:**
    1. `consumers.json`:
       - `version` 2, with keys {version, scope, consumers, records, pending, fields}, and one agreed scope string checked by discovery.
       - `consumers` is the union (tempo, status, recommend, ledger, audition, binding, songform, meter, and midi once #128 lands), each list unchanged.
       - `records` and `pending` stay exactly as in #130. melody-spec and song-spec stay pending, so their 1.1.0 additions remain covered by `fields`.
       - `fields` stays exactly as in #131.
    2. `vector_discovery.py`:
       - Add `fields` to `MANIFEST_KEYS` as a required key.
       - Keep #130's version and scope check, `known_tickets`, `check_tickets` and `check_records`.
       - Keep #131's `added_fields()` set comparison, with its "missing …, orphan …" message.
       - Validate every `fields` list through `check_tickets(known_tickets)`.
       - When a pending kind later moves into `records`, map its top-level added fields there too.
    3. Keep both PRs' tests. #130 adds record-consumer tests. #131's `test_songform.py` edits `fields` and matches "missing", "orphan" and "unknown consumer ticket slug"; the last also matches #130's "duplicate or unknown consumer ticket slug".
    4. Keep both `generate_fixtures.py` hooks, regenerate, and prove again both the byte identity of every fixture then on integration and `validate.py -v`.

    **Whichever of #128 and #131 lands second must:**
    - keep the "MIDI round trip (T02d)" and "SongForm assembly (T02c)" README sections, plus #130's "Evidence-binding inputs (T02b)";
    - merge the shared "Not covered yet" line: T02c rewrites "SongForm assembly …" and T02d drops "the MIDI round trip".
    - Because #131 makes an off-bar meter change break `melody.wellformed`, add a typed `MidiRefusal` and a refusal vector for a time signature off a bar line. #128's `from_smf` accepts a time signature at any tick (it checks only 1 ≤ nn ≤ 32 and dd ≤ 5). If this is not added, record it as open in #128's README.
    - #128's only meter change (3/4 at 3840) already lands on a bar line.

## The base moved during the review

`integration` advanced from 7cb7bbd to `dee28e2` when #129 (T03, license verification) merged at 2026-11-08T02:29Z, so #131 is now `BEHIND`.
- #129 shares no file with #131.
- I made a local trial merge of dee28e2 into 969886b in a disposable copy. It was never pushed, and its commit uses the noreply identity.
- That merge keeps the reviewed patch-id `7f9d4bf57616be55f303aa980ee58d70682f90b4`, and passes the full local gate (633 files, 0 policy violations, 56 pytest tests and 16 subtests) and `validate.py -v` (23 songform and 27 meter vectors, byte-identical regenerations) (T02c-review-18-trial-merge-dee28e2.log, T02c-review-18b-trial-merge-dee28e2-validate.log).
- Under the merger rule, this review carries over to an updated head only while its patch-id is unchanged. B1's fix will change the patch, so the fix needs a fresh review.

## How the two passes compare with my verification

- **Standards pass:** it rated the tempo-range finding blocking. I reproduced it, added the A2 and B cases, and showed that the fix is invisible to the current vectors, so I keep it blocking. I verified each of its non-blocking points before including it here.
- **Spec pass:** it rated the same defect "low". The two axes are reported separately (see the spec review), and the defect is counted once, here, as B1.

## Evidence (SHA-256; also in T02c-review-SHA256SUMS)

```
7f52dc05b3533ac1b1a8c3616cf7fa65d1f0839d263e98544ea64772f17c5e11  T02c-review-00-preflight.log
4eb924c3372b550bb485f05d926973fb03fa5ae69575cda82ffa1f63fde13457  T02c-review-01-install.log
1e79e56a9bb5affb7a05b2cbf34ea77aee0c7beba91575ef8cbb0188f6bafc63  T02c-review-02-local-gate.log
c5404b10bdd892d8153773c392f0829daa54d72685497435a4e924e658938799  T02c-review-03-validate-v-head.log
e4ac297b411075984ad245e123492e79a63a76cd75fc04277fbc7772f3db3151  T02c-review-04-fixture-bytes.json
12b65f8a6fc377c538981dd2ed28e916c34da176acb74f2fcf674d9548d0e7c7  T02c-review-05-hand-derived.log
16e3dd88eba82164d9ffe6ac9bb9ba75ad065dc24470de7074f2d28990f2b242  T02c-review-06-refusals.log
c18d3abc71af24342cca6f80b255e5a805c2fd08d8e966d865d2c70c38fdc617  T02c-review-07-tempo-inside-bars.log
fd916693851174c25a93dbf0a5cbe84f81a27734b8644f66d9f8c41f1fa76683  T02c-review-08a-validate-planted-onset.log
bc1f7daa03cb9ae022c0a0d12eaf51afa253f227d797f8dd677a2f7a3420b0f5  T02c-review-08b-validate-planted-meter.log
c5404b10bdd892d8153773c392f0829daa54d72685497435a4e924e658938799  T02c-review-09a-validate-mutant-floor-bars.log
46bf9a1bbf7df0c2b14f7748e0faed7e2cbfb5e058efc6b08aa720b39bd22b58  T02c-review-09b-validate-candidate-fix.log
0cefbb7f32cdcbf67312d8c2e93cb8719cb46434f90e0c40d3304e22bb9ab9d0  T02c-review-09b-tempo-bars-on-fix.log
05e9b346af29702ef4536eb939d9dfde3ce0491513251f8794693e8a52576987  T02c-review-10-lane-scenarios.log
632aa9126a41d34d4d3f5028dbfd9ff1fce8d454db75f5e5b4163f5628a85c94  T02c-review-11-validate-mutant-L1-no-assembled-from-recursion.log
cff5504a8c179473d104edc591006a09859e3893824002074388cfeb79d79043  T02c-review-11-validate-mutant-L2-no-exact-inheritance.log
e77ff05cace8e25218e1a2b0c700f56d8ef4b90f6aa9fcabf47b96d9b0206535  T02c-review-11-validate-mutant-L3-no-capture-check.log
76bbe23738a428602b057551c0a3ea874bdf974e481414c667bc80d0f8add7d8  T02c-review-12-schema-versions.log
e329fb61a4550223b5b9285c3b9aa28131a02a8a3efb52131cad1c6bed265146  T02c-review-13-meter-tightening.log
d294bb875705727d8f77ddbd3ad0a28d3b4419e4ab553a41c25cd42a6c50528f  T02c-review-14-scope-and-policy.log
012e9f251e58250a09ac49173d48baa7240d5ccfd861dbac34dda9092696f37c  T02c-review-15-patch-id.txt
739a79bf3c34c2ace17cd7399900c40c3d8a877f63360baad1b952c04f7138e4  T02c-review-16-size.txt
e6f40a219a436b8268556975fecedab432a549cd16e8ae108589f2fb2205c4a0  T02c-review-17-source-chain-preexisting.log
49fba154a0e0dede3334f681cae283b25e3b822c70f45a81ebe9018554a5860d  T02c-review-18-trial-merge-dee28e2.log
46bf9a1bbf7df0c2b14f7748e0faed7e2cbfb5e058efc6b08aa720b39bd22b58  T02c-review-18b-trial-merge-dee28e2-validate.log
```

Three pairs of logs have identical sums, and this is expected:
- 03 and 09a both hold an all-pass `validate.py -v` output followed by "exit=0".
- 09b and 18b both hold an all-pass output followed by "validate exit=0".
- In each case the identical output is the point: the mutant or patch left every vector passing.

The mutation diffs (`T02c-review-08*.diff`, `-09*.diff`, `-11*.diff`), the probe scripts (`T02c-review-probes/`) and the PR body as reviewed (`T02c-review-pr131-body-at-969886b.md`) are covered by `T02c-review-SHA256SUMS`.

All evidence is synthetic software evidence (CI on fakes). Nothing was rendered, played or listened to.
