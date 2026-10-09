# HANDOFF: suno-personal — teardown complete, zero code written
Generated: 2026-10-08T12:40:00Z · Focus: personal single-user Suno clone; research phase done, build not started

## 1. Goal
Build a self-hosted, single-user Suno-style app for Jony's own use: prompt→song, own-voice cover, stems + per-stem regeneration, a Studio timeline, export. UI parity with Suno's late-2026 interface; engine is open-weights.

## 2. Background
- Suno's models are proprietary; there is no public Suno API. The engine must be an open model.
- Owner's machine: macOS arm64 ("mac-lan"), Homebrew, yt-dlp/ffmpeg/python3/node/deno installed. GPU is Apple Silicon — ACE-Step on MPS is unverified.
- Research source is one 20-min tutorial (Simon Crowe, Aug 2026). It shows Suno v4.5 and v5.5, Studio, voice cloning Beta, stems, hum-to-instrument. Fully cited in docs/VIDEO-ANALYSIS.md.

## 3. Current State
- DONE: video pulled (transcript + 150 deduped frames), frame-cited teardown (docs/VIDEO-ANALYSIS.md), build spec with primitives/data model/screens/phases (docs/SPEC.md), CLAUDE.md, reference frames copied into docs/reference/, git repo initialised with one commit.
- NOT STARTED: Phase 0 engine smoke test; any code in apps/; docs/ENGINE-NOTES.md.
- NOT VERIFIED: ACE-Step 1.5 install, MPS support, weights license, actual quality on the owner's prompt.

## 4. Key Decisions
- **Engine candidate = ACE-Step 1.5** because it alone claims all three primitives the UI needs (text→song, cover/audio-conditioned regen, stems + timbre cloning) and claims <4 GB VRAM / <10 s per song on a 3090. Fallback: YuE 7B (Apache-2.0, 16 GB, ~5 min/track). Rejected: MusicGen (no vocals, CC-BY-NC), Stable Audio Open (47 s cap, textural).
- **Everything reduces to 3 primitives** (`generate`, `cover`, `separate`); hum-to-instrument is `cover` at high strength; Song Editor sections are a `sectionize` helper. Spec is organised around this so features don't multiply the engine surface.
- **Two versions per generation, always** — matches Suno's A/B + "Copy to Main Track" ergonomics (#102–#103) and is the cheapest quality lever.
- **Demucs for stems, not the model's own stem head** — mature, local, deterministic; label mismatch with Suno's 8 stems accepted.
- **Drop credits/plans/Explore/publishing/liveness gate**; keep a consent flag on voices.
- **Phase 0 gates UI** — the one unknown that can sink the project is whether the engine runs acceptably on the Mac; decide Mac vs cloud GPU before building anything that depends on latency.
- **Stack**: Next.js + Tailwind + shadcn / FastAPI + SQLite / Python worker, SQLite-polled queue. Chosen for solo-dev velocity; Redis/Postgres explicitly deferred.

## 5. Traps & Dead Ends
- YouTube blocks the cloud container (429 / "sign in to confirm you're not a bot"); media had to be pulled on the Mac. Don't retry from a container.
- yt-dlp subtitle fetch 429'd twice; `en-orig` with `--sleep-subtitles 5` after a 20 s wait succeeded. Video stream itself was never blocked.
- Modern ffmpeg rejects `-vsync`; use `-fps_mode vfr`. `-frame_pts` numbers are frame indices, not seconds — the sheet timestamps read 00:00 for that reason; frame numbers (#NNN) are the stable reference, not times.
- Auto-captions mangle names ("Sunno", "electroop"). UI labels in the docs come from frames; don't "correct" them from the transcript.
- ACE-Step's quality numbers are self-reported (style/lyric 39.1/26.3 vs Suno v5 46.8/34.2). Don't promise Suno v5.5 quality.
- Per-stem "Cover" in Suno is implemented as a new lane + Copy to Main Track, not in-place regeneration (#117–#122). Modelling it as in-place will fight the UI.
- The tutorial's Suno pricing has "starting 9/3/26" caveats (#028) — Suno was mid-policy-change; don't treat the matrix as stable.

## 6. Files & Pointers
- `CLAUDE.md` — project conventions; read first.
- `docs/SPEC.md` — architecture, primitives table, SQLite schema, screen→component map, phases 0–4, risks.
- `docs/VIDEO-ANALYSIS.md` — flagship teardown; §2.4 has the full "Algorithm Hates Me" prompt (use it as the Phase 0 test prompt), §2.10 lists frame-only findings, §3 lists claims to verify.
- `docs/reference/transcript.txt` — timestamped captions (474 lines).
- `docs/reference/sheet_1..6.jpg` — all 150 frames, numbered; `create-panel-and-more-options.jpg` (#017/#046), `pricing-and-studio.jpg` (#028/#092), `stems-panel.jpg` (#113/#116), `create-voice-and-song-editor.jpg` (#060/#089) at full 960 px.
- Scratch (not in repo, may be gone): `/tmp/va-suno/` on the Mac — video.mp4, frames/, VTT.
- External: ACE-Step 1.5 paper https://arxiv.org/html/2602.00744v1 ; v1 paper https://arxiv.org/html/2506.00045v1 ; survey https://www.spheron.network/blog/deploy-open-source-ai-music-generation-gpu-cloud-2026/ ; Mac notes https://lilting.ch/en/articles/ace-step-music-generation-mac ; source video https://youtu.be/MI6vwl_ZHN8

## 7. Open Work
- Phase 0 is the only unblocked item and blocks everything else: engine installed? runs on MPS? wall time per 60 s song? cover works with a reference clip? Demucs runs? → `docs/ENGINE-NOTES.md`. Outcome decides `ENGINE_URL` = local vs cloud GPU.
- Phase 1 (shell, create, library, player) depends on Phase 0 only for latency expectations; scaffolding could start in parallel if the owner accepts the risk.
- ACE-Step weights license unconfirmed; YuE fallback untested.
- LLM provider for lyrics/dice not chosen (any chat model works; needs an API key in `.env.local`, never committed).
- No secrets exist yet in this project.

## 8. Fleet State
None — no lanes claimed, no finding register, no review verdicts. Single commit `e8feab8` on `main` (docs only).

## 9. Suggested Skills
- `frontend-design` before building the shell (the Suno look is dark, dense, pink-orange gradient CTAs — see #017/#046).
- `engineering:system-design` if the SQLite-polled queue needs revisiting after Phase 0 numbers.
- `anthropic-skills:video-analysis` if a second tutorial (e.g. Suno's music-video flow teased at [19:46]) needs tearing down.
- `anthropic-skills:handoff` on the way out of every session.

---
## Prompt for the Fresh Agent
You are picking up `~/Projects/suno-personal`. The research phase is complete: a frame-cited teardown of Suno's 2026 UI (docs/VIDEO-ANALYSIS.md) and a build spec (docs/SPEC.md) exist and are committed. No application code exists. ACE-Step 1.5 is the chosen engine candidate but has not been installed or tested on this Mac; Phase 0 (engine smoke test) is the gate for all UI work. Apple Silicon support is unverified. Voice cloning is owner-only with a consent flag.
Before responding, run the wake protocol: read every file under "Files & Pointers",
re-read any verdicts and finding-register entries named under "Fleet State" from the
tree, and treat every claim in this handoff as context to verify — not fact to trust.
Then wait for instructions.
