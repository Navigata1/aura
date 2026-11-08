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
   arithmetic, audition gains and commitments, and the evidence-binding input findings match hand-derived values exactly.
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

SongForm assembly, MelodySpec -> YuE2 ABC emission, the MIDI round trip, `render_mode` stitching, route standing and
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
Every discovered family has a nonempty unique list of actual `docs/spec/tickets.json` ticket slugs, and no orphan
manifest entry is allowed. These slugs name the consuming contract or feature ticket; they do not claim that the future
feature is implemented. Vector kinds have no pending allow-list: missing consumers fail closed. Record kinds and
fields joined the manifest in T02b (below); the rest of the field/enum/declaration consumer inventory remains T02 work.

`tests/contracts/test_vector_discovery.py` exercises the public generator and validator in disposable tracked-file
copies: new-family discovery, unchanged existing bytes, corrupt expectations, duplicate kinds, missing evaluator,
missing/unknown consumer, removed handler, producer-kind mismatch and legacy expectation execution. The production
schemas and existing fixture bytes are unchanged. SongForm, ABC, MIDI and route-standing implementation remain open;
C01 benchmark containment remains in force until C02 establishes result binding.

## Evidence-binding inputs (T02b)

C02 (#4) needs exact inputs to bind concluded benchmark evidence to, not the existence of a hash. Three closed record
kinds hold them. None of them concludes, promotes or demotes anything, and none is read by `evidence.gates` or the status
fold: C01's refusal of concluded `benchmark` and `hum-benchmark` records and its inert fold are unchanged.

- `benchmark-prereg/1`, the typed preregistration. `set` is the benchmark gate's set (`benchmark-48` or
  `hum-benchmark`). It fixes the subjects under test (profile revision and host class), the exact case set (briefs, or
  hums with their MIDI ground truth), one threshold per protocol metric, sessions, hidden repeat pairs and coverage.
  `prereg_sha256` is the record's own canonical hash, and `committed_at` must precede every run it governs. `prereg/1`
  stays the preregistration of smoke-set eval auditions.
- `benchmark-membership/1`: per case, each arm's subject with its runs (jobs) and candidates, or its transcribed
  melodies whose correction logs hold Jon's blind correction; the owner verdict ids each engine case expects.
- `evidence-binding/1`: one evidence record, its subject, its typed preregistration and the membership. It carries no
  validated flag (`IR-EVIDENCE-BINDING-VALIDATED-FLAG`).

`studio_ref/binding.py` is the reference. `resolve_prereg` is typed: only a `benchmark-prereg` of the same set whose own
hash matches resolves, so a MelodySpec, a `prereg/1` or the other set's preregistration never does. `prereg_findings` and
`binding_findings` report missing thresholds, duplicate case ids, hash mismatches, subjects without a gate of that set,
forbidden case lanes (ADR-0029 point 6), unresolved or substituted references, unregistered subjects and cases, runs
queued at or before the commit, and expected verdicts or corrections that do not resolve or were given over synthetic
test output. The `fixture.binding` vectors hold the hand-derived findings for valid mixed-profile engine and hum
preregistrations and bindings, and at least one negative for every finding.

`contracts/consumers.json` (version 2) maps every field of these kinds to real consuming tickets. A ticket is a
`docs/spec/tickets.json` slug or a contract-fix id registered by a `docs/spec/contract-fixes/Cnn-*.md` file, which is
how C02 is named. Every other record kind sits on an explicit `pending` allow-list. An orphan kind or field entry, an
unmapped field, an unknown ticket or a new kind on neither list fails both the generator and the validator.

Still open for C02: wiring typed resolution into `evidence.gates` and registry admission, binding candidates to their
arm's subject and cases to the benchmark set's briefs (all 48 for `benchmark-48`), quota, coverage and threshold
evaluation, and the conclusion itself. Fields of the pending kinds and route standing remain T02 work.
