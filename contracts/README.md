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

SongForm assembly, MelodySpec -> YuE2 ABC emission, `render_mode` stitching, route standing and
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
This manifest is deliberately scoped to vector kinds: every discovered family has a nonempty unique list of actual
`docs/spec/tickets.json` ticket slugs, and no orphan manifest entry is allowed. These slugs name the consuming contract
or feature ticket; they do not claim that the future feature is implemented. Full field/enum/schema/declaration
consumer inventory remains T02 work. There is no pending allow-list in this slice: missing consumers fail closed.

`tests/contracts/test_vector_discovery.py` exercises the public generator and validator in disposable tracked-file
copies: new-family discovery, unchanged existing bytes, corrupt expectations, duplicate kinds, missing evaluator,
missing/unknown consumer, removed handler, producer-kind mismatch and legacy expectation execution. The production
schemas and existing fixture bytes are unchanged. SongForm, ABC, MIDI and route-standing implementation remain open;
C01 benchmark containment remains in force until C02 establishes result binding.

## MIDI round trip (T02d)

`reference/studio_ref/midi.py` is the stdlib reference for MelodySpec <-> Standard MIDI File (SMF 1.0): the behaviour
`Score.to_midi(melody, form)` and `Score.from_midi(bytes)` (architecture §4.6) must reproduce. `fixture.midi`
(`fixtures/vectors/midi.json`, schema `fixture-midi.schema.json`) holds its hand-derived vectors; expected bytes are
lowercase hex inside the JSON, and no binary file is committed. `to_smf(melody, markers)` writes, `from_smf(bytes)`
reads, and anything the mapping cannot represent raises a typed `MidiRefusal` (`{code, smf_track, tick}`). Nothing is
retimed or rounded, and nothing is dropped silently.

**Written: one canonical file.** Format 1, two tracks, 960 PPQ, no running status. Track 0 (the conductor) holds, at
each tick, the time signature (`FF 58 04 nn dd cc 08`: `dd` is log2 of the denominator, `cc` is 96 / denominator, one
click per beat unit), the tempo (`FF 51 03`, the integer microseconds per quarter) and the section markers (`FF 06`,
the section name), in that order. Track 1 holds the notes on MIDI channel 1 as `90 kk vv` (the note's velocity) and
`80 kk 40`; at one tick note-offs come first, then ascending pitch, so touching notes of one pitch stay two notes.
Each track ends with `FF 2F 00` at its last event. The writer reads only `tempo_map.tempo`, `tempo_map.meter` and each
note's start, duration, pitch and velocity, so a whole `melody-spec` record works; per-field validity is the schema's
job, and the writer refuses only what a schema cannot see.

**Read.** Formats 0 and 1, at any division whose ticks convert exactly (`960 x tick / division` is whole, so a 480 PPQ
file doubles every tick). Running status, a note-on with velocity 0 as a note-off, and tempo, meter and markers in any
track. Until the first tempo or time signature the SMF defaults hold (500000 us, 120 BPM; 4/4). The same tempo or time
signature repeated at one tick, as notation programs write it in every track, is one entry. Notes come back in
(start_tick, pitch) order and markers in tick order, so `from_smf(to_smf(m, k))` gives `m` and `k` back exactly, with
nothing listed as not carried.

**Not carried, and never silently.** MelodySpec-only fields are not written: note ids, confidence and origin, key,
phrases, quantize, source and revisions. On import the MIDI in-and-out ticket assigns ids `n1`, `n2`, ... in that
order, the origin and a null confidence, and keeps the original bytes as the capture. Read but not kept: release
velocity, the time signature's `cc` and `bb`, and the MIDI channel number. Every other event is listed in
`not_carried` as `{smf_track, tick, event}`, where `event` is the status byte in hex or `ff` and the meta type: names,
text, lyrics, cue points, key signatures, a marker whose text is not a section name, program and control changes,
pitch bend, aftertouch, SysEx and a note-off with no note sounding.

**Section markers** use the `timeline/1` marker shape (`{name, tick}`, a SongForm section name) and travel beside the
MelodySpec, as `to_midi(melody, form)` implies. Phrases are not written as markers: a phrase is a span with an end, an
SMF marker is a point, and GLOSSARY keeps phrases apart from sections. Deriving the markers from a SongForm, and
writing the full form's end as the End of Track, wait for the SongForm assembly slice (T02c), which defines section
boundaries and form duration.

| Code | Refused when |
| --- | --- |
| `smpte_division` | the division word counts SMPTE frames (its top bit is set) |
| `tempo_outside_model` | a tempo of 0 us per quarter |
| `meter_outside_model` | a time signature numerator of 0 or above 32, or a denominator above 32 |
| `tempo_map_ambiguous` | two different tempos, or two different time signatures, at one tick; on write, a tempo or meter list that does not start at tick 0 and strictly increase |
| `same_pitch_overlap` | a note-on for a pitch already sounding on the melody's channel; on write, two overlapping notes of one pitch |
| `track_layout_unsupported` | format 2; note-ons in more than one track, or on more than one channel (the importer's chooser names one) |
| `tick_not_representable` | a tick that is not a whole 960 PPQ tick; on write, a gap over the four-byte delta-time maximum, `0x0FFFFFFF` |
| `zero_length_note` | a note-off at its own note-on's tick |
| `unterminated_note` | a note still sounding when its track ends |
| `malformed_smf` | no `MThd` of length 6; format 0 without exactly one track, no tracks, a format above 2 or a division of 0; a chunk that is not `MTrk` (unknown chunks are refused, not skipped), a short chunk, or bytes after the last one; a delta time over four bytes; a data byte with no status (meta and SysEx events cancel running status), a status byte where data belongs, or a system message; a tempo or time signature of the wrong length; a track without End of Track, or anything after it |

On read, a refusal's tick is in the file's own division; a write refusal carries no track. The Studio API's MIDI
route already answers with `Ineligible{reasons}` (architecture §4.1), and a write refusal is such a reason. Not in
this slice: mapping key signatures to the MelodySpec key (they are listed, not mapped), live event lists
(`from_midi_events`) and the track chooser, which belong to the MIDI in-and-out ticket.
