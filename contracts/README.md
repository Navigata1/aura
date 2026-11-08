# Contracts (`contracts/`)

The language-neutral source of truth (architecture.md §2, §5, §6.3; the JOVRA `spec/` pattern). The control service,
the TypeScript client, the stdlib worker SDK and the eval harness share these contracts, not code. A rule change lands
here first, as a schema, rule and fixture change, and only then in code. Contracts change only through contract tickets.

```
contracts/
  product.json         the one rename constant and the public contact text (O-10, ADR-0035, ADR-0037)
  schemas/             JSON Schema 2020-12; every record has kind + schemaVersion; no $id, relative $refs only
  registry/            components.v1.json (generated), engine-profiles.v1.json, capabilities.v1.json, lanes.v1.json,
                       compute-tiers.v1.json
  reference/           studio_ref/: stdlib reference implementations; generate_fixtures.py (deterministic bytes)
  fixtures/            registry/ (fake-* test overlays), world/, scenarios/, invalid/, vectors/
scripts/spec/validate.py          the contract gate (stdlib only); non-zero exit on any failure
scripts/spec/jsonschema_subset.py refuses every keyword it does not implement
scripts/registry/sync.py          evidence-register.json + register_overlay.json -> components.v1.json
```

Run from the repo root (Python 3.11+, nothing to install):

```
python3 scripts/registry/sync.py                  # regenerate the component register
python3 contracts/reference/generate_fixtures.py  # regenerate contracts/fixtures (same bytes every run)
python3 scripts/spec/validate.py                  # the gate; -v for detail, --rules to list the reference rules
```

## What the gate proves

1. Schemas use only implemented keywords and every `$ref` resolves; the checker's own self-tests show it rejects
   known-bad values keyword by keyword.
2. Every file validates against the schema its `kind` names; no file holds a float (integers only, ADR-0028).
3. `components.v1.json` and every fixture regenerate byte-identically.
4. The **world** (two projects, individual and llc, from capture to export, with the shipped registries and the fake
   overlays) breaks none of the 59 cross-file reference rules, and the hand-derived lane and closure assertions hold.
5. Every **scenario** (world + overlay) triggers exactly the rules it names, and every rule is triggered by at least one
   scenario, so none is vacuous. Lane cases include a YuE2 artifact forced into an llc project (`lane.store_write`),
   a YuE2 job submitted in llc (`lane.admission`), a lane change refused, analysis edges that must not propagate,
   an llc quote that must never exist, a RoFormer separation in llc before its training-data review, an unverified
   license claiming llc, a melody drafted by an individual-only transcriber read by an llc job (`lane.record_eligible`),
   a DAW bounce whose lanes are declared rather than inherited, a Suno file declared as a DAW bounce, a smoke pass
   without Jon's verdict, and a keeper after a tie (valid) or after 'neither' (refused).
6. Every **invalid record** is rejected by its schema at the named location (status stored on a profile, MEASURED-LOCAL
   in `claims_published`, a positive audition gain, a Suno reference, a percentage in a step, an import nobody
   attested, a risk acceptance that would make a Suno import an audition arm, a YuE2 license acceptance without its
   GitHub permission document, and so on).
7. **Vectors**: tick<->frame (960 PPQ, integer tempo, one half-up rounding), the status fold, `recommend()`, ledger
   arithmetic and audition gains and commitments match hand-derived values exactly.
8. `docs/evidence/` (a hash-checked export of the store: evidence plus the verdicts and preregistrations it cites)
   validates by kind and breaks no reference rule, so a hand-committed passing record cannot become a status; then the
   computed status of the shipped registry from it (none yet: every profile and capability is `declared`), plus the
   Rule-07 lint (no bare address in Markdown prose) and the product-name lint.

Fixtures are JSON only. Every audio hash in them is a synthetic label; nothing was rendered, measured or listened to.
The world runs on FakeEngine stand-ins (`fake-*`, `test_only`, `synthetic_test: true`); real-engine records appear only
inside scenarios, and vector inputs are hypothetical inputs to pure functions. None of it is evidence.

## Decisions taken where the documents left room

1. **Status is computed, never stored** (ADR-0001, ADR-0027, GLOSSARY "Profile status"): profiles carry no status
   field, and the schema rejects one. "Published" figures live in `claims_published`. With no evidence recorded,
   every seed profile computes to `declared`; nothing is smoke-passed.
2. **Status fold**: a failing record while still `declared` changes nothing; a failing install, conformance or smoke
   record once at `installed` or above gives `disabled`, which is terminal for that revision and host class.
   A smoke record promotes only when its `checks` list every check the gate declares, each passing, with
   `owner_not_garbled` answered by a verdict id (the rule `evidence.gates` checks that the verdict is an owner-ui act on
   that revision's own candidates). A pin change is a new revision at `declared`.
3. **recommend()**: every NVIDIA tier needs compute capability >= 8.0 (BF16); with several reachable hosts the best tier
   wins (a Mac studio host can drive a tailnet CUDA worker); "WSL2 memory under 24 GB" is read as 24 GiB.
4. **Ceiling** rounds up to the cent. **Month-to-date** counts settle amounts, open reserves, fixed lines and
   reconciliation adjustments; a settle or release closes its reserve; overrun entries mark an excess already inside the
   settle amount and add nothing; an overrun or a reconciliation adjustment blocks new leases until acknowledged.
5. **Commitment** = `sha256(canonical_json(mapping sorted by label) + "|" + nonce)`.
6. **Lanes**: in the register, every component allowed in `individual` is also allowed in `research`; SwiftF0 is
   narrowed to individual and research (ADR-0011 rule 6), and the 2026-10-09 design review narrowed Kim
   Mel-Band-RoFormer and Basic Pitch the same way (`unverified_training_data`, forbidden in llc), widened the
   non-commercial scorers to individual and research (O-06), and made every row with an UNVERIFIED license
   research-only (individual and llc now forbid `unverified`). An `analyzed_by` edge is recorded on the analysis
   artifact, pointing at the audio it read. An import's lanes are bounded by its attested terms, and a transcribed
   MelodySpec carries its transcriber's lanes.
7. **Lyric languages**: ACE profiles declare `en` only until a smoke run per language (Q6 default); HeartMuLa and
   MiniMax leave languages undeclared, so vocal requests are refused until their smoke runs.
8. **Register text** copied from the research register uses neutral wording for the product name (ADR-0035), and nine
   supplement rows cover v1-path components the research register lacks (own code, NeutralVoice, and stack libraries
   recorded as license-UNVERIFIED, not assumed).

9. **Design review, 2026-10-09** (architecture.md, "Design review log"): `audition-session/1` became `audition/1`
   (verdicts and reveals carry `audition_id`; an audition may draw on several requests); every import is an owner act
   (`attest_import`) whose uses follow its source; a risk acceptance can add only engine, conditioning, separation, edit
   or conversion input; `license-acceptance/1` records every weights acceptance (YuE2 needs both license documents);
   weights come from a Hugging Face revision, a pinned URL or a file in a pinned package; export manifests carry
   `release_blockers` and `release_clear`; compute tiers use the glossary's placement terms; capabilities define how
   each check is measured, live MIDI is proven by an event-list hash and a played reference phrase, and
   `adherence.real-separator.darwin` gates adherence on real candidates; quotes never carry a lane refusal.

## C01 containment, 2026-10-29

The intended benchmark transition in ADR-0027 is **not implemented**. Its previous reference fold accepted a hash
without proving a concluded result. C01 therefore fails closed: `evidence.gates` refuses **pass and fail** conclusions
for both `benchmark` and `hum-benchmark` with `benchmark conclusion unsupported`, and the pure status fold ignores
both kinds. Neither can promote nor disable a profile. Inconclusive records remain non-promoting; existing
install/conformance/smoke semantics are unchanged. Generation requests retain `unbenchmarked routes` even when an
unsupported benchmark record is present. A preregistration hash now resolves only to a `prereg` record, never to a
MelodySpec or SongSpec hash.

This is containment, **not completion of the benchmark feature**. Mixed-profile listening is still valid; C01 does not
reuse the smoke rule that every candidate must belong to one profile. Existing schemas remain load-compatible and
unsupported conclusions are refused by reference admission. The former status golden claiming that a bare hash
benchmarked an engine was corrected; no frozen legacy fixture changed. See
[the follow-on binding criteria](../docs/spec/contract-fixes/C01-benchmark-conclusions.md), required before T08 relies on
benchmark conclusions and coordinated with T02's route-standing work.

## Not covered yet (needs vectors before code relies on it)

SongForm assembly beyond its bounded T02c semantics (below), MelodySpec -> YuE2 ABC emission,
the MIDI round trip, `render_mode` stitching, route standing and
the plan-rules order, the remaining job kinds and tasks (isolate, dsp-finish, dsp-edit, offline-render, preservation,
per, align, diagnostics, stem-to-midi, a reserved tts), `price-snapshots/`, frozen `legacy/`
fixtures (they freeze at the first release), the TypeScript twin of the tempo vectors and the Pydantic/TS codegen
drift check.


## Golden-vector discovery (T02a)

Each non-underscore Python module under `reference/studio_ref/vector_cases/` declares one `KIND` (`fixture.<slug>`),
`build(profiles)` returning its complete JSON vector record, and `evaluate(case, world)` returning `(actual, expected)`.
Builders contain hand-derived expected values; they never call the implementation under test to construct an oracle.
The generator discovers modules in sorted filename order and writes `fixtures/vectors/<slug>.json`; it rejects
missing callables, duplicate/invalid kinds, mismatched producer kinds and empty cases before writing any fixtures.
The validator discovers schemas by their existing `kind` const/enum and executes the matching evaluator; unknown
vector kinds fail explicitly. Frozen legacy vectors still execute against current reference functions.

A new family needs its module, schema and an entry in `contracts/consumers.json`, with no shared dispatch-list edit.
Its `consumers` map is deliberately scoped to vector kinds: every discovered family has a nonempty unique list of
actual `docs/spec/tickets.json` ticket slugs, and no orphan manifest entry is allowed. T02c adds a `fields` map for
schema locations a minor version adds (see "Minor versions" below), so the manifest's scope reads "vector-kinds and
added fields". These slugs name the consuming contract or feature ticket; they do not claim that the future feature
is implemented. Full field/enum/schema/declaration consumer inventory remains T02 work. There is no pending
allow-list in this slice: missing consumers fail closed.

`tests/contracts/test_vector_discovery.py` exercises the public generator and validator in disposable tracked-file
copies: new-family discovery, unchanged existing bytes, corrupt expectations, duplicate kinds, missing evaluator,
missing/unknown consumer, removed handler, producer-kind mismatch and legacy expectation execution. The production
schemas and existing fixture bytes are unchanged. ABC, MIDI and route-standing implementation remain open
(SongForm: T02c below);
C01 benchmark containment remains in force until C02 establishes result binding.


## SongForm assembly (T02c)

`reference/studio_ref/songform.py` is the language-neutral reference for `Score.assemble` (ADR-0032, architecture
§4.6). `assemble(melody, song, output)` lays the phrases of the MelodySpec revision a SongSpec names along its
SongForm and returns `{"assembled": <melody-spec 1.1.0>}` or `{"refused": {code, section_id, phrase_id, note_id}}`;
`output` names the new record's `melody_id`, `rev`, `base_rev`, `tempo_map_rev` and `created_at`, and its project is
the source's. The vectors (`fixtures/vectors/songform.json`, hand-derived in `vector_cases/songform.py`) fix the
semantics below. The runtime Score module and every consumer (the guide, ABC emission, MIDI export, the timeline,
R2-raw's `assemble-audio`) must honour them and their refusals: refuse, never truncate, stretch, retime or pick.

- **Time.** Integer ticks at 960 PPQ, in the TimeModel's bars and beats (**Meter**, below). A bar of n/d lasts n x
  3840 / d ticks, exact for every allowed denominator, so assembly never rounds; ADR-0033's one half-up rounding
  applies only when a consumer converts ticks to frames (each vector also states its form's end frame at 48 kHz).
- **Sections and repeats.** Sections play in form order from tick 0, each `repeats` times. One repeat lasts `bars`
  bars of the section's meter whether or not its phrases fill it; the bars after its last phrase are rest.
- **Phrases.** A placed phrase occupies every bar its span touches, counted from the bar line at or before its start
  in the source meter and rounded up to whole bars, and moves by a whole number of bars, so every note keeps its place
  in the bar. A phrase that starts mid-bar (a pickup) keeps its offset: its first bar is rest until the pickup, its
  downbeat lands on the next bar line, and it stays inside its own section. The phrases of one repeat take consecutive
  bar slots in `phrase_ids` order; two phrases never share a bar, so a phrase that starts in the bar where the
  previous one ended moves to the next bar line (a vector pins this; T28's default form of one section per phrase
  behaves the same way). A note belongs to a phrase when it lies inside the phrase's span; it keeps its duration,
  pitch and velocity, with `origin` `assembled` and `confidence` null (the confidence stays on the source revision).
  Notes outside every placed phrase are left out with their phrase, as the SongForm chose.
- **Tempo and meter.** Each placed phrase has one tempo and one meter over every bar it occupies in the source, its
  leading and trailing rest included: a change anywhere in those bars, even after its last note, is refused, never
  dropped, because dropping it would retime that bar. A section takes its phrases' tempo and meter; a section that
  places no phrase continues the previous section's, and leading ones take the first phrase-bearing section's (the
  source's tick-0 values if none places a phrase). The assembled tempo map starts a tempo or meter segment at a
  section's first tick only when the value changes, so a reordered or repeated phrase carries its tempo and meter with
  it.
- **Explicit form** (melody-spec 1.1.0, `form`, assembled records only, and required on them from 1.1.0). `end_tick`
  is the full-form duration and `sections` lists every repeat of every section in order (`section_id`, `name`,
  `section_kind`, `repeat`, `start_tick`, `end_tick`, and the phrases it places at their assembled spans). Repeats
  tile [0, `end_tick`); instrumental intros and outros keep their bars; section names survive for the timeline and
  MIDI markers. Consumers read duration and boundaries here and never infer them from the last note; a 1.0 assembled
  record has no form, so a consumer refuses it instead of inferring one. The phrase marks (`phrases`) of an assembled
  record are empty.
- **Lineage.** The assembled record copies its source revision's `capture_sha256`, `transcription` (the transcriber's
  eligible lanes and license chain), `key` and `quantize`; `assembled_from` names the melody and song revisions. Rule
  `lane.record_eligible` requires a 1.1 assembled record to carry its source's capture and transcription exactly, and
  still computes every assembled record's lanes through `assembled_from`, so a 1.0 record whose lineage is by
  reference only cannot widen a lane (scenarios `lane-record-assembled-*`,
  `lane-record-legacy-assembled-read-in-llc`).

**Refusals**, reported in this scan order: `source_not_melody` (the source is itself assembled);
`song_melody_mismatch` (the SongSpec names another revision or tempo-map revision, or lives in another project);
`duplicate_section`; `duplicate_phrase` (the source marks one id twice); then for each section in form order
`section_kind_mismatch` (an instrumental section places a phrase, or a vocal one places none), then for each of its
phrases `missing_phrase`, `empty_phrase` (it ends at or before its start), `meter_conflict` and `tempo_conflict` (a
change inside the bars it occupies, from its first bar line to the end of its last bar), `note_crosses_phrase_edge` (a
note overlaps its span without lying inside it), then `meter_conflict` and `tempo_conflict` (the section's phrases
disagree) and `phrase_overflow` (they need more bars than the section has); finally, per section,
`chord_symbol_misplaced`. A source the time model cannot measure breaks `melody.wellformed` and is an input error, not
a refusal: the reference raises `TimeModelError` with `tempo_segments_invalid` (the tempo map does not start at tick 0
or strictly increase), `meter_segments_invalid` or `meter_change_inside_bar`, and the vectors pin each code
(`{"invalid": code}`). An all-instrumental form takes the source's tick-0 tempo and meter, also pinned.

**Meter** (`timemodel.bar_segments`, `position`, `tick_at`; vectors `fixtures/vectors/meter.json`, hand-derived in
`vector_cases/meter.py`, consumed by the TypeScript TimeModel twin, song intent, the piano roll, ABC emission, the
timeline and MIDI in and out). Bars and beats count from 1 across every meter change, and a beat is one denominator
note (3840 / d ticks), so 6/8 counts six 480-tick beats; a felt dotted-quarter pulse is not modelled. Meter segments
start at tick 0, strictly increase and change only on a bar line of the meter before them (rule `melody.wellformed`,
scenario `melody-meter-inside-bar`); the last meter runs on past the form. `position(tick)` gives `{bar, beat,
offset}` and `tick_at(bar, beat)` the first tick of that beat. An unrepresentable map or beat raises `TimeModelError`
with `meter_segments_invalid`, `meter_change_inside_bar` or `beat_outside_bar` (and `tempo_segments`, behind
tick-to-frame conversion, raises `tempo_segments_invalid`); the twin must reproduce these codes. Arguments outside the
vectors' domain (a negative tick or frame, a bar or beat below 1) are input errors that raise a plain `ValueError`.
The vectors walk the bar and beat boundaries of two maps: the assembled meter map of the SongForm case whose sections
run 4/4, 3/4, 6/8, and 2/2, 1/1, 7/16, 5/32 for the remaining denominators.

**Chord symbols** (song-spec 1.1.0, spec interpretation 2): an optional, non-empty `chord_symbols` list on a SongForm
section, each `{offset_ticks, symbol}` measured from the start of every repeat, strictly increasing and inside one
repeat. Assembly checks their placement but does not copy them; ABC emission reads them from the SongSpec by
`section_id`, keeping them for `cot='full'` and stripping them for `cot='melody'`.

**Minor versions.** A schema location a minor version adds carries `"$comment": "added in 1.x.y"` and is accepted only
on records that claim that minor or later, so every 1.0.0 record still validates and a 1.0.0 record carrying a 1.1
field fails (`fixtures/invalid/*-before-1-1.json`). `consumers.json` `fields` maps every such location to its
consuming tickets; discovery fails on a location without consumers, an orphan entry or an unknown ticket slug.

**Still open.** Tempo or meter changes inside the bars a phrase occupies, an instrumental section that places a phrase
and re-assembling an assembled melody are refused, not supported. A pickup always stays inside its own section (it
never reaches back into the previous one), and two phrases that share a source bar take separate bars; supporting
either otherwise is a later minor version. The world's two 1.0 assembled records predate these semantics (their bytes
are frozen), so no rule yet requires a stored assembled record to equal `assemble()` of its sources; the runtime Score
module, its API refusal type and that consistency check belong to the song-intent ticket, which also reconciles
architecture §4.6's `assemble(melody, form) -> melody` with this reference's `assemble(melody, song, output)` (the
SongSpec supplies the form and names the source revision; `output` names the new record). Fixtures are synthetic:
nothing was rendered or listened to.