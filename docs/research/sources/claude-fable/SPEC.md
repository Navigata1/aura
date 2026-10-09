# suno-personal — Build Spec (v0)

Single-user, self-hosted Suno-style music app. Derived from `VIDEO-ANALYSIS.md`; frame refs (#NNN) point there.

## Non-goals
No accounts, credits, plans, Explore feed, publishing, comments, download caps, or multi-tenant anything. Voice cloning is for the owner's own voice only; keep a consent checkbox + stored reference clip, drop Suno's read-aloud liveness gate (#070).

## Architecture
```
apps/web        Next.js 15 (App Router) + Tailwind + shadcn/ui    — the Suno shell
apps/api        FastAPI + SQLite (SQLModel) + local disk           — library, jobs, files
apps/engine     Python worker: ACE-Step 1.5 (gen/cover/timbre), Demucs (stems), LLM (lyrics)
                queue = SQLite table polled by worker (no Redis for v0)
data/           songs/<id>/{master.wav, master.mp3, stems/*.wav, meta.json}, voices/<id>/ref.wav
```
Web ↔ API over REST + SSE for job progress. Engine may run on the Mac (MPS) or a remote GPU box; the API only needs `ENGINE_URL`. **Decide this with the smoke test in Phase 0 before any UI work.**

## Primitives (everything in the video reduces to these)
| Primitive | Inputs | Output | Engine |
|---|---|---|---|
| `generate` | description, lyrics\|prompt\|instrumental, style tags, exclude, vocal gender, weirdness, style influence, duration, voice_id? | 2 versions × {wav, sections[]} | ACE-Step text→music; lyrics via LLM when mode=prompt |
| `cover` | source audio, optional new lyrics, style text, voice_id?, strength | 2 versions | ACE-Step audio+text→music |
| `separate` | source audio | vocals, bvocals?, drums, bass, guitar, piano/synth, other | Demucs htdemucs_6s (6 stems) — label mapping to Suno's 8 is approximate |
| `audio2instrument` | mic/upload clip, instrument, style text | 1–2 versions | `cover` with high strength on a hummed clip |
| `sectionize` | audio (+lyrics) | [{label, start, end}] | v0: LLM over lyrics + fixed-length heuristic; v1: all-in-one / msaf |

## Data model (SQLite)
- `songs(id, title, description, lyrics, style_tags, model, voice_id, parent_id, kind: generate|cover|stem, version_no, duration_s, bpm?, created_at, art_path, audio_path)`
- `voices(id, name, tags, description, art_path, ref_path, consent_at)`
- `stems(id, song_id, label, path)`
- `jobs(id, type, params_json, status, progress, error, result_song_ids, created_at)`
- `projects(id, song_id, state_json)` — Studio timeline state, saved on every change (#092 "Saved")

## Screens → components (frame-grounded)
1. **Shell** — left nav Home / Create / Studio / Library (+ Voices); bottom persistent player (shuffle, prev, play, next, repeat, scrubber, volume, queue) (#017).
2. **Create / Simple** — hero "Describe the song…", dice (random concept from an LLM), Create → 2 versions (#013–#016). (Suno shows 4 because it previews two models; we show 2.)
3. **Create / Advanced** — exactly the #017 + #046 control set: Audio/Voice/Inspo attach row; Song Description; +Lyrics; Instrumental toggle; Suggestions chips; More Options (Lyrics Write|Prompt|Instrumental, Exclude styles, Vocal Gender, Weirdness %, Style Influence %, Duration Auto|Custom); model picker; Create. Right column: Workspace list with filters, thumbnail, title, model chip, like/dislike/share, ⋯ menu (#076 items minus Publish).
4. **Voices** — Create a Voice modal: Record / Upload / Library (#060) → record with waveform (#066) → trim (#068) → details: name, tags, description, art (#071). Consent checkbox replaces #070.
5. **Song page** — art, title, caption, lyrics, Remix, ⋯ → Download MP3 / WAV / Stems / (MIDI, Video: out of scope) (#143–#144).
6. **Song Editor** — section-coloured timeline + lyrics pane + Save as New Song / Get Stems / Edit in Studio (#089).
7. **Studio** — multitrack timeline (wavesurfer.js or custom canvas), S/M per track, Version 1/2 sub-lanes, **Copy to Main Track**, Clip inspector (Tempo/Transpose/Speed/Volume — v0 can stub Tempo/Transpose), Stems drawer (extract, per-stem insert arrow, Insert All, Download), prompt bar (Song|Vocals ▾ · Styles · Lyrics · Replace|Cover ▾), Add Track → No Input/mic record, Export → Full Song | Multitrack (#092, #113, #116, #132–#141).

## Phases
- **Phase 0 — Engine smoke test (do first, ~1 h).** Install ACE-Step 1.5; generate a 60 s song from the "Algorithm Hates Me" prompt (VIDEO-ANALYSIS §2.4); run one cover with a reference clip; run Demucs on the result. Record wall time + peak memory on this Mac (arm64/MPS). If >5 min per song or MPS unsupported, provision a cloud GPU (RTX 3090/4090 class; paper claims <10 s/song on 3090) and point `ENGINE_URL` there. Output: `docs/ENGINE-NOTES.md` with the numbers.
- **Phase 1 — Generate + Library.** Shell, Simple + Advanced create, job queue + SSE progress, song page, player, downloads, LLM lyrics + dice. Done when the narrator's prompt yields two playable WAVs from the UI.
- **Phase 2 — Voice + Cover.** Voices screen, consent, timbre reference stored; Remix → Cover flow; voice chip on create.
- **Phase 3 — Stems + Studio v0.** Demucs integration, stems drawer, multitrack timeline with Version lanes and Copy to Main Track, per-stem Cover, export full/multitrack.
- **Phase 4 — Hum-to-instrument, Song Editor sectionizing, clip Tempo/Transpose.**

## Known risks
- ACE-Step quality < Suno v5.5 (self-reported gap); set expectations.
- ACE-Step on Apple Silicon unverified in the paper — Phase 0 exists for this.
- Demucs gives 4–6 stems, not Suno's 8; "B Vocals / FX / Percussion" won't map cleanly.
- Model weight licenses: confirm ACE-Step 1.5 weights license at install time (paper does not state it); YuE is Apache-2.0 fallback (16 GB VRAM, slow).
