# Audio is content-addressed and immutable, and every artifact carries complete provenance

Status: accepted (2026-10-09). From D-09, amended by the v1 architecture: SQLite stays the system of record, but every
immutable record and every artifact's provenance is also written as content-addressed JSON, so the database can be
rebuilt (ADR-0028); parent edges are typed (ADR-0029); and the origins `rendered_guide`, `analysis` and `preview` are
added.

All three sources chose SQLite plus files. Release, rights and AI disclosure (MiniMax AUP #11 requires a
"machine-generated" notice) depend on knowing exactly which components made which audio. An honest studio must also be
able to say what each engine actually consumed.

**Decision.**

- **Blobs.** Every blob is stored once, named by its SHA-256, staged on the same volume, fsynced, renamed and made
  read-only. Native-rate originals are always kept, and conversions point to their source.
- **Entities**, each a JSON Schema contract (ADR-0025): `Project` (kind `song`, with `narration` reserved; operator
  lane, default `individual`), `MelodySpec` and `SongSpec` revisions (immutable), `Reference` (hash, role,
  permission), `GenerationRequest`, `Candidate`, `Job`, `Artifact`, `EditOperation` and `Timeline` (v1-studio), and
  `ExportManifest`. `PerformanceSpec` comes later.
- **`Artifact.origin`**: `generated_mix | separated_source | regenerated_part | new_part | human_recording |
  rendered_guide | rendered_midi | tts_render | conversion | imported_mix | analysis | preview`. An `imported_mix`
  carries its source service and terms.
- **Provenance on every artifact**: the producing job, profile revision, weights revision and hash, code commit, env
  lock or image digest, parameters as **intent and actual**, seed, host and host class, compute profile, cold and warm
  timings, typed parents, `operator_lane`, `eligible_lanes`, license chain, `allowed_uses`, retention class and
  `synthetic_test`.
- **`ExportManifest`**: files with hashes, roles, rates and frames; human contributions; the model and license chain;
  lane and eligible lanes; the AI-disclosure flag and its reasons (required whenever any MiniMax output is included);
  `converted_vocal`; imported-source terms; a loudness report naming its standard and meter version; the closure hash;
  `synthetic_test`; and the verification time.
- One versioned project graph holds sections, lyrics, beats, clips, tracks and references. C2PA-style credentials are
  optional and later. There is no forced watermark.

**Why.** All sources agree on SQLite. GPT's provenance model makes rights and disclosure computable. MiniMax AUP #11
requires disclosure. JOVRA ADR-0004 showed the value of provenance on every derived value.

## Consequences

An artifact without complete provenance is refused at the store's write path. Exports are computed from closures, so a
manifest is never assembled by hand.

**Reverse if:** multi-user sharing becomes a goal, which would need a server store.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A14, A29; §2 C50; §5 (GPT 6, Fable 4); §6 D-09.
[evidence-register.json](../research/evidence-register.json) X-12, X-20, X-44.
[feature-inventory.md](../research/feature-inventory.md) I2, J4, J5. [architecture.md](../spec/architecture.md) §4.2,
§5, §13.4 (T-01).
