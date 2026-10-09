# AURA feature inventory

Status: synthesized reference, 2026-10-09, revised the same day (see the Revision log in
[`RECONCILIATION.md`](RECONCILIATION.md)). Companion to [`RECONCILIATION.md`](RECONCILIATION.md) and
[`evidence-register.json`](evidence-register.json).

**Citation key for GPT's companion corpus**, now archived in `sources/gpt-sol/companion/` (hashes in `sources/SHA256SUMS`):
"GSV §n" is `voice-studio-research.md` §n; "GSV-nn" is a claim in
`sources/workflow-2026-10-09/extract-gpt-sol-voice-video.json`; "MG-Enn" is an experiment in `proposed-experiments.md`;
video IDs with timestamps are sections of `video-analysis.md`. These are GPT's assertions: they show where a feature was
proposed, not that it works.

This file lists every feature that was **observed** (in Suno or a competitor) or **proposed** by GPT-6.1 SOL, Kimi K3
or Claude Fable 5.1, de-duplicated. Each row gives:

- **Evidence**: where the feature was seen or where it is documented.
- **Proposed by**: G = GPT (core plan + voice/video corpus), K = Kimi, F = Fable. "obs." means only observed in a product, not proposed.
- **Primitive**: the AURA operation the feature needs.
- **Unverified dependency**: the capability it relies on that is not yet verified. "—" means none.
- **Tier**, defined below.

## Tiers

| Tier | Meaning |
|---|---|
| **v1-core** | Needed to take Jon's melody to a finished, exported song, with honest provenance and evaluation. |
| **v1-studio** | Editing and studio work in v1 once the core flow passes its gates. |
| **v2** | Valuable, but waits for a v1 gate, a license decision, or a separate lane. |
| **research** | An experiment with no product promise. |
| **out-of-scope** | Not built. A reason is always given. |

## Primitives

The primitive names used in this file:

- `capture`, `transcribe` (audio to MIDI), `melodyspec`, `songspec`
- `generate` (text to song; profile-specific), `render-from-score`, `cover` (audio-conditioned; ACE cover / cover-nofsq), `repaint` (also used for extend), `lego` / `complete` (ACE base only)
- `separate`, `reperform`, `new-part`
- `align`, `sectionize`, `rerank`
- `dsp` (gain/fade/EQ…), `timeline`, `mix-render`
- `export`, `provenance`, `job`, `eval`
- `voice-convert`, `tts`

---

## A. Melody seed and capture: the north-star flow (D-04)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| A1 | Record a hum or sung line in the browser as the song's seed | Suno Studio hum-to-instrument (MI6vwl_ZHN8 17:22–18:50, frames #129–139); v6 phone recorder (_lHvWn2SNC4 08:15–08:43) | G, K, F | `capture` | Browser mic capture quality on the Mac (unmeasured) | **v1-core** | This is how Jon starts: a melody in his head. |
| A2 | Import a phone voice memo | v6 demo frame 174, which shows a 30-min upload limit; Suno uploads are 8 min on Free and 30 min on Pro/Premier ([pricing](https://suno.com/pricing)) | G | `capture` | An m4a/AAC decoder (ffmpeg LGPL vs GPL build, or macOS-only `afconvert`); license **UNVERIFIED** (RECONCILIATION §4.9) | **v1-core** | The easiest way to capture an idea already recorded. |
| A3 | Import MIDI as a seed (MIDI clip as prompt) | Suno Studio 2.0: "MIDI clips can also be used as a prompt" ([blog](https://suno.com/blog/studio-2)); songwriter's Kontakt seed (MJ4d0-Wi1z8 05:00–05:41) | G, K | `capture` → `melodyspec` | — | **v1-core** | Lossless melody input with no transcription step. |
| A4 | Transcribe a hum or stem to MIDI with pitch bends | [Basic Pitch](https://github.com/spotify/basic-pitch) (Apache-2.0; best on one instrument); SwiftF0 `segment_notes` (MIT); librosa pYIN + HMM (ISC) | G, K, F | `transcribe` | **No transcriber is both license-clean and benchmarked on humming** (GAP-01). Basic Pitch's only humming figure is onset+pitch F1 0.27–0.43 (COMMUNITY); it fails to install under Python 3.12 on macOS (#203). A local hum benchmark (mir_eval COn/COnP/COnPOff on Jon's hums plus HumTrans, personal evaluation only) picks the winner. | **v1-core** | Turns the tune into something editable and measurable. A5's human correction is what makes it reliable. |
| A5 | Piano-roll correction of the transcribed melody, plus tempo map and key | GPT SongSpec / timeline model; Studio 2.0 MIDI editing | G, K | `melodyspec` | — | **v1-core** | A human-corrected symbolic stage protects the tune from engine drift. |
| A6 | Render a full song that **keeps my melody** | v6 "melody preservation" request (_lHvWn2SNC4 08:44–08:58); YuE2 `cot='melody'` score route ([card](https://huggingface.co/m-a-p/YuE2-3B)) | G, K, F | `render-from-score` (YuE2), `cover` (ACE) | **Unverified on hums.** ACE cover kept song identity poorly in a competitor-run test (Hit@1 2.4%); YuE2 with a score reached 71.3% (VENDOR, self-reported). R1 needs the CUDA worker and the individual lane, and takes Chinese or English lyrics only. R2-synth needs a MIDI synth and soundfont (licenses **UNVERIFIED**). | **v1-core** | This is the feature AURA exists for. **Three routes compete in Phase 0**: R1 (YuE2 score), R2-raw (ACE cover of the hum) and R2-synth (ACE cover of a synth render); R3 is research (D-04). Each request then shows 2 candidates from the two best passing routes in its lane (C7). |
| A7 | Melody-adherence score for every candidate (cents error, onset F1, contour correlation) | GSV-12: practitioner report of melody regression in v5.5 (`video-analysis.md`, MJ4d0-Wi1z8 30:00–30:35) | G | `separate` (internal, A11) → F0 → DTW → `eval` | F0 on separated vocals is unmeasured. Tracker: SwiftF0 (MIT; MIT-labelled model trained on CC BY-NC-SA data) with librosa pYIN (ISC) as cross-check (GAP-01). DTW: librosa (adequacy **UNVERIFIED**). | **v1-core** | A newer engine can sound better and follow the tune worse. |
| A8 | Hum to instrument (render the hum as a chosen instrument) | Suno Studio frames #129–139 | K, F | `transcribe` → instrument render, or `cover` | Instrument render quality; ACE cover on a hum | **v1-studio** | Useful for arranging, but the core flow is the sung song. |
| A9 | Editable ABC melody/chord plan before audio | YuE2 symbolic planning ([arXiv 2609.33757](https://arxiv.org/abs/2609.33757)); native user-ABC input ([generation.md](https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md), GAP-02) | G (SongSpec melody), verifier | `songspec` → `render-from-score` | YuE2 on the CUDA worker; NC weights (individual lane). The editor must stay inside YuE2's dialect: two monophonic voices, one integer tempo, full bars, no tuplets, pickups, repeats or `w:` lines. | **v1-studio** | Lets Jon fix a note or chord without regenerating blind. |
| A10 | Guide-vocal route: score-to-singing of the melody (DiffSinger), then generated accompaniment | GPT twelve-phrase pilot (`companion/suno-engineering-disclosures.md` §3); DiffSinger ([repo](https://github.com/openvpi/DiffSinger)) | G | `render-from-score` + `complete` | DiffSinger English voicebank; the NC vocoder needs replacing for commercial use; ACE `complete` is base-only | **research** | Predictable melody, but heavy setup. |
| A11 | **Internal vocal separation for analysis** (feeds A7 and C2; never exported as a stem) | D-04 step 6; D-05 | verifier, critic | `separate` (internal) | Lane-aware: Demucs in the individual lane only (author: weights research/personal-only, GAP-06); an LLC-clean separator such as Kim Mel-Band-RoFormer (training data **UNVERIFIED**) otherwise | **v1-core** | The adherence and PER filters need a separated vocal before the user-facing stems feature (E1) exists. |
| A12 | **Import an existing finished song** (Jon's paid Suno render, or a bounce from a DAW) for finishing, separation or editing | D-21; [Suno ToS 2026-09-03](https://suno.com/terms-september-2026) (GAP-07) | critic | `capture` → `dsp` / `separate` / `cover` | **Suno-ToS dependency.** For a Suno download: DSP mix, master and format conversion are allowed ("incidental"); ML separation is grey (prefer Suno's own stems); generative edits, voice conversion or using it to develop or test AURA are highest risk and stay off unless Jon accepts the risk (Q7). A DAW bounce of Jon's own material has no such limit. Needs the A2 decoder. | **v1-studio** (DSP finishing); generative edits of Suno audio **out-of-scope** unless Q7 says otherwise | Jon's first version will come from Suno (D-21), and finishing it is a real need. |

## B. Brief, lyrics and structure

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| B1 | Simple prompt ("describe the song") | Suno Simple mode (#013–018) | K, F | `songspec` → `generate` | — | **v1-core** | The minimum entry point. |
| B2 | "Dice" random concept | Suno Simple mode (#013–016) | K, F | LLM | LLM provider choice | **v2** | Nice to have. Jon arrives with a song already. |
| B3 | Advanced form: description, lyrics (write / prompt / instrumental), exclude styles, vocal gender, duration | Suno #017/#046; v6 frame 246 | K, F, G | `songspec` | Each control's mapping per engine profile (D-18) | **v1-core** | Shown only where a profile supports it. |
| B4 | Separate lyrics and style editors; bracket tags are soft directions | DrRRvM4oc4w frame 95 | G | `songspec` | — | **v1-core** | Stops lyric words leaking into style. |
| B5 | Prompt-conflict detection, e.g. an instrumental flag with vocal words in the style | MJ4d0-Wi1z8 13:00–13:32 | G | `songspec` validation | — | **v1-core** | A real failure mode seen in practice. |
| B6 | LLM lyric writing in metatag grammar, with reversible suggestions | Suno Lyrics = Prompt; Kimi Ollama; Fable | G, K, F | LLM → `songspec` | LLM choice: local vs API, plus disk | **v1-core** (optional) | Jon may write his own lyrics. LLM edits stay visible and undoable. |
| B7 | Approved lyrics vs ASR transcript vs alignment kept as separate assets | MJ4d0-Wi1z8 28:00–29:08 | G | `songspec`, `align` | — | **v1-core** | ASR must never overwrite the author's words. |
| B8 | SongSpec record: requested / supported / observed values per field | GPT master plan | G | `songspec` | — | **v1-core** | Honest about what each engine consumed. |
| B9 | PerformanceSpec: syllable/phoneme-to-note mapping, F0 and expression curves | GPT disclosures §6 (`companion/suno-engineering-disclosures.md`) | G | `songspec` | A phoneme aligner on singing (SOFA English checkpoint is community-made) | **v2** | Needed for score-to-singing. Overkill for v1. |
| B10 | Auto title and style-prompt expansion | Fable image insight (#046 cards vs typed prompts) | F (observed) | LLM | — | **v2** | A Suno convenience, not core. |
| B11 | Role-bound multi-reference input (rhythm from A, vocal energy from B) | v6 (_lHvWn2SNC4 02:10–03:26, frame 71); natural language only ([FAQ](https://help.suno.com/en/articles/13924481)) | G | `songspec.references` → engine conditioning | Only ACE `reference_audio` (global timbre) is verified. No engine verified for per-role binding. | **v2** | Must be labelled as an approximation where an engine lacks it. |
| B12 | Time-indexed sampling from a reference ("sample the riff at 0:45") | _lHvWn2SNC4 04:33–04:48 | G | `separate` → conditioning | Stem-conditioned generation | **research** | No verified open path. |
| B13 | Image or video to musical brief | _lHvWn2SNC4 05:08–07:59 | G | multimodal LLM → `songspec` | — | **v2** | Doesn't need a multimodal generator. Low priority. |
| B14 | Persona from an existing song (with a Public toggle) | DrRRvM4oc4w frame 155 | G (obs.) | voice registry | — | **out-of-scope** | Public sharing is out of scope. Private identities are covered by G1. |

## C. Generation, candidates and selection

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| C1 | **Two candidates per request** with A/B | Suno v6 FAQ: "you make two songs" | F, G | `generate` ×2 | — | **v1-core** | Matches the documented contract (D-05). |
| C2 | Hard-constraint filtering and badges: silence, duration, clipping/true-peak, lyric PER, melody adherence | GPT inference-improvement section (`companion/generation-research.md`) | G | `rerank` | ASR accuracy on sung vocals; the internal separator (A11); a G2P/phonemizer for PER, license **UNVERIFIED** (any espeak-ng-backed G2P is GPL-3.0) | **v1-core** | Cheap and objective; permissively licensed once the G2P is chosen. |
| C3 | Draft vs render profiles (ACE turbo 8-step vs SFT/XL 50-step) | Kimi; ACE model zoo ([README](https://github.com/ace-step/ACE-Step-1.5)) | K, G | `generate` (profile) | Mac timings on the M5 Pro | **v1-core** | Fast iteration, then a quality render. |
| C4 | Explicit engine choice per request; no auto-routing until the benchmark says so | GPT | G | `job` | — | **v1-core** | Avoids a hidden router. |
| C5 | Capability-aware controls: Weirdness, Style Influence, Audio Influence, Variety, only where mapped; intent and actual parameters both recorded | Suno controls (frame 246; MJ4d0-Wi1z8 frame 108); ACE turbo forces CFG to 1 | G, K, F | `generate` | Per-profile mappings | **v1-core** | No slider that does nothing (D-18). |
| C6 | Max-Mode-style compute tier (best-of-n or a bigger profile) with its budget logged | v6 Max Mode ([FAQ](https://help.suno.com/en/articles/13924481)); Kimi best-of-8–16 | G, K | `generate` ×n + `rerank` | **Best-of-n gain refuted** on human listening (YuE2 Tables 21–22) | **v1-studio** | Opt-in and priced. Promoted only by A/B. |
| C7 | Mixed-engine candidate sets (one candidate per engine or route) | Suno Simple mode previously returned 2× v4.5 + 2× v5.5 | K, F | `job` fan-out | A CUDA worker for the second engine; in the LLC lane only ACE has a melody route today | **v1-core** for the melody-seed flow (default: one candidate from each of the two best passing routes in the lane, D-04 step 7); **v1-studio** for text-only briefs | The v1-core flow is already mixed-engine, so the fan-out has to be specified there. |
| C8 | Aesthetic diagnostic scores (audiobox-aesthetics, LAION-CLAP) | Kimi scorer stack | K | `eval` | Scorers are blind above 8–12 kHz | **v1-studio** | Shown as diagnostics only. Never used to auto-select. |
| C9 | Keeper-cost reporting: every attempt and reject retained | MJ4d0-Wi1z8 (4–5 tries per keeper) | G | `provenance`, `eval` | — | **v1-core** | The economics stay honest. |
| C10 | Extend or continue a song | Suno Edit menu (#088); ACE repaint at start or end, 3–90 s per pass | F, G | `repaint` | Repaint quality at boundaries | **v1-studio** | Common edit. Covered by ACE on all checkpoints. |
| C11 | Instrumental generation and instrumental beds | Suno; SA3 Medium (no vocals) ([guide](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)) | G, K | `generate` (ACE instrumental / SA3) | SA3 needs a gated download and license registration | **v1-studio** | Intros and beds. SA3 runs on the Mac via MLX (VENDOR timing). |
| C12 | Sounds and loops generation | Suno "Sounds" tab (#017; v6 frames 71/96) | G | `generate` (SA3 Small) | — | **v2** | Unexplained in the sources. Low priority. |
| C13 | Remaster | Suno Edit menu (#088) | F (obs.) | `cover` / `mix-render` | Undefined in Suno | **v2** | The semantics are unclear. |

## D. Editing

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| D1 | Named, colour-coded sections carried across Editor, Studio and DAW | MI6vwl_ZHN8 11:30–12:15; #089 | G, K, F | `sectionize` | all-in-one is stale with no MPS; msaf has no functional labels | **v1-studio** | A prerequisite for section edits. A v0 heuristic plus manual labels is acceptable. |
| D2 | Replace a section (time range), with two alternates and Insert | DrRRvM4oc4w frames 197/206; v6 "edit part of an existing song" | G, K, F | `repaint` | Repaint quality; the chunk-mask fix exists only on main (#1292) | **v1-studio** | Core Suno editing parity. |
| D3 | Replace a word or line, keeping the song intact | v6 FAQ "Change one word or line"; Fable section lyric re-sing (#097–103) | G, F | `repaint` scoped to vocals, or a scoped `cover` | Whether ACE can change one word without audible seams | **v1-studio** | High value. Gated by D5. |
| D4 | A generative edit is a proposal until committed; undo restores the prior artifact | GPT; Suno Reset All and undo (#089) | G, F | `provenance` | — | **v1-studio** | Never destroys a keeper. |
| D5 | Byte-identical preservation outside the edit mask, in a declared PCM domain | GPT edit gate (MG-E06, GSV-59) | G | `eval` | — | **v1-studio** | A testable definition of a "local edit". |
| D6 | DSP edits: crop, remove section, reverse, adjust speed, fade in/out | Suno Edit menu (#088); FADE handle (#223) | F | `dsp` | Time/pitch library quality (Signalsmith unmeasured) | **v1-studio** | Deterministic, with no model needed. |
| D7 | Cover / remix (re-style while keeping the composition) | Suno Remix > Cover (#076–085) | F, K, G | `cover` | Composition retention (C8 evidence is weak) | **v1-studio** | Labelled "new performance". Melody adherence is measured. |
| D8 | Edit history ("My Edits") and Save as New Song | #089 | F (obs.) | `provenance` | — | **v1-studio** | Falls out of lineage. |
| D9 | Lyric alignment with "Fix Alignment" | DrRRvM4oc4w | G, K | `align` | Sung-lyric word timing (WhisperX unproven on singing) | **v1-studio** | Needed for word edits. Human correction is always available. |

## E. Stems (D-06)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| E1 | **Isolate original**: separator with stems **and residual** | Demucs 4.1.0 ([adefossez](https://github.com/adefossez/demucs)); demucs-mlx | G, K, F | `separate` | demucs-mlx speed on the M5 Pro. **Demucs weights are research/personal-only per the author** (GAP-06), so LLC work needs another allow-listed separator. | **v1-studio** | Honest separation. Listen to stem, residual and the rebuilt mix. (The filters' internal separation is A11, v1-core.) |
| E2 | Replace-part reconstruction rule: rebuild the mix, never layer | GPT; Fable new lane + Copy to Main Track | G, F | `mix-render` | — | **v1-studio** | Prevents doubled parts. |
| E3 | Per-stem insert, Insert All, download | Suno stems panel (#113–116) | F, K | `timeline` | — | **v1-studio** | Basic stems UX. |
| E4 | Stem to MIDI transcription | Suno "Extract Stems and MIDI"; Basic Pitch | G, K, F | `separate` → `transcribe` | Accuracy on separated stems that contain bleed. MuScriptor (multi-instrument) has CC BY-NC weights, so it is research only. | **v1-studio** | Kimi's "pro" substitute for more stems. |
| E5 | **Re-perform this part** (regenerated stem, as Suno does) | [Suno blog](https://suno.com/blog/stem-separation-updates): "regenerates each stem from scratch"; ACE `extract`, which is generative | G | `reperform` | ACE extract is base-only; no fidelity metric published | **v2** | Must be labelled a new performance. Needs a note/onset fidelity gate. |
| E6 | **Create a new part** (lego / complete) | ACE base tasks ([INFERENCE.md](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md)) | G | `new-part` | Base checkpoint (another 4.79 / 19.95 GB); lego through the API was noisy on M4 Max (#1255); lego appears to return the part alone (medium confidence) and had an LM-override bug (#1286, interim fix #1287) | **v2** | Arrangement help after v1. |
| E7 | Per-stem prompted regeneration ("more epic") | Suno #117–128 | F, K | `reperform` (cover on a stem) | As E5 | **v2** | Same contract as E5. |
| E8 | Lead vs backing vocal split | Suno 12-stem list (frame 186) | G (obs.) | `separate` (karaoke model) | Karaoke checkpoints are unlicensed or NC; best back-vocal SDR ~7.1 dB | **v2** | Needs an allow-listed checkpoint first. |
| E9 | 12-stem / ~100-instrument taxonomy | Suno Auto Split (up to 12) and Advanced Split (~100) | G (obs.) | `separate` / `reperform` | Open separators give 4–6 stems; the best 6-stem model has an unknown license | **research** | Not reachable with clean open weights. |
| E10 | Prompt-selected instrument separation | SAM Audio ([repo](https://github.com/facebookresearch/sam-audio)) | G | `separate` | Custom, modifiable license; CUDA; 12–38 GB | **research** | |

## F. Studio / DAW (D-13)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| F1 | Multitrack timeline: clips, solo/mute, faders, pan, meters | Suno Studio (#092); Studio 2.0 | G, K, F | `timeline`, `mix-render` | waveform-playlist v16 fitness; 8 tracks × 30 min gate | **v1-studio** | Needed to assemble and fix the song. |
| F2 | Version lanes plus Copy to Main Track | MI6vwl_ZHN8 frame 212 | G, K, F | `timeline`, `provenance` | — | **v1-studio** | Safe commits of alternates. |
| F3 | Clip settings: volume, fades | #092 | F, K | `dsp` | — | **v1-studio** | |
| F4 | Clip transpose, speed ½ / ×2, follow tempo | #092; #136–138 | F, K, G | `dsp` (time/pitch) | Signalsmith Stretch quality | **v2** | Fable allowed stubbing these in v0. |
| F5 | Tempo map, time signature, beat grid; reversible quantize | GSV-47 timeline model (GSV §6) | G | `timeline` | Beat tracker (all-in-one is stale) | **v1-studio** | Integer samples plus ticks. |
| F6 | Piano-roll MIDI editing and instrument rendering | Studio 2.0 | G, K | `timeline`, instrument render | A MIDI/General MIDI synth and soundfont; library and soundfont licenses **UNVERIFIED** (some soundfonts restrict rendered audio). The same synth serves D-04's R2-synth route, so a minimal version is needed in v1-core. | **v1-studio** | Same editor as A5. |
| F7 | Wavetable synth | Studio 2.0 | obs. | instrument render | — | **v2** | Not core to Jon's song. |
| F8 | Automation curves | Studio 2.0 | G | `timeline`, `mix-render` | — | **v2** | After the offline/real-time equivalence test. |
| F9 | Effects: EQ, compressor, limiter, sends, sidechain, convolution reverb | Studio 2.0; GSV core DSP set (GSV §7) | G | `dsp` | Offline vs real-time equivalence | **v2** (EQ and gain in v1-studio) | GPT ordering: effects come after the equivalence test. |
| F10 | Mic recording into tracks (latency-compensated) | MI6vwl_ZHN8 17:30–18:35 | G | `capture`, `timeline` | Browser round trip ~52 ms in Chrome (MBP 2021, [WAC 2025](https://doi.org/10.5281/zenodo.17642262)) | **v2** | Low-latency live monitoring is not viable in the browser. |
| F11 | Native plugin hosting (VST3) | GPT | G | native engine | Native audio engine (CPAL) | **research** | Only after device and latency proof. VST3 SDK is MIT. |
| F12 | Chat-directed production and chat-built plugins | Studio 2.0 chat bar (beta) | G | LLM → operations | Sandboxed DSP | **research** | Must be a command interface over tested operations, with diffs. |
| F13 | Generated DSP / plugin code safety (resource limits, ear safety) | GSV §7; `master-review-input.md` §7 ("Job and network behavior") | G | sandbox | — | **research** | Goes with F12. |
| F14 | Autosave ("Saved") and interruption-safe project state | #092; MG-E16 (recovery gate, three OSes) | F, G | `provenance`, `job` | Recovery on Windows and Linux untested (J19) | **v1-core** | Accepted takes must survive crashes. |

## G. Voice: singing (D-07)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| G1 | Create a private voice with a consent gate: sung sample, spoken random phrase, speaker match, ASR phrase check, rights checkbox, `consent_at` | [Suno help](https://help.suno.com/en/articles/11362369); #060–072 | G, K, F | voice registry | Speaker-match thresholds for speech vs singing | **v2** (moves to v1 if Jon wants his own voice; Q6) | The consent pattern matters even in a personal tool. |
| G2 | Global timbre/style reference | ACE `reference_audio` | F | `generate` | Not identity cloning (maintainer, [#776](https://github.com/ace-step/ACE-Step-1.5/issues/776)) | **v1-studio** | Labelled honestly as a style reference. |
| G3 | Voice conversion of a sung performance to an authorized timbre | RVC / Applio | G, K | `voice-convert` | Weights license contested; **whether a released song with converted vocals is permissible is CONTESTED** (lj1995 research-use rider; unlicensed rmvpe); official RVC has no Mac support (use Applio) | **v2** (v1 individual lane if Jon sings it himself; Q6) | Optional, auditioned operation in a separate process, flagged in the export manifest. |
| G4 | "Cover in my voice" (vocal split → conversion → remix) | Suno Remix > Cover with a voice chip; Kimi pipeline | K, F | `separate` → `voice-convert` → `mix-render` | As G3; the cited efegen pipeline does not exist; on Suno audio this is a generative edit the ToS puts at highest risk (A12) | **v2** | Depends on G1 and G3. |
| G5 | Score-to-singing with a consented voicebank | DiffSinger / OpenUtau | G | `render-from-score` | Voicebank effort; NC vocoder | **research** | See A10. |
| G6 | Live "jam mode" voice conversion at ~300 ms | Kimi (Seed-VC) | K | `voice-convert` | Seed-VC archived and GPL; 300 ms is algorithm delay only, measured on a speech model | **out-of-scope** | Dead dependency. Browser latency is too high. |
| G7 | Same-identity test across 10 excerpts (blind owner review) | MG-E05 (GSV-60) | G | `eval` | — | **v2** | The gate for G1–G4. |

## H. Narration lane: Sabbath Echo (D-08, separate spec)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| H1 | Narration service: approved text → semantic chunks → dry audio, word timings, manifest, QA, with **ASR verify-and-regenerate per chunk** | Master plan §6 ("Voices"); GSV §3; long-form degradation in [arXiv 2609.16989](https://arxiv.org/abs/2609.16989) (GAP-08) | G | `tts`, `align`, `provenance` | TTS quality on Sabbath Echo text; Scripture rule (owner); operator lane presumed LLC (X-50), so no NC components | **v2** (own spec) | Pinned separately by the owner. Qwen3-TTS and VoxCPM2 degrade past ~1,500 words, so chunking and ASR checks are core. |
| H2 | Engine-neutral script and pronunciation layer (spoken-form alias, phonemes) | GSV §2; ElevenLabs v3/v4 lack SSML breaks | G | `tts` | Per-engine support | **v2** | Never mutate the canonical text. |
| H3 | Versioned voice_id bundle (clean reference is the source of truth) | GSV-48 (GSV §2, "A reusable narrator is a managed asset") | G | voice registry | — | **v2** | Embeddings are tied to one encoder revision. |
| H4 | Voice design → reusable reference | Qwen3-TTS VoiceDesign; VoxCPM2 | G | `tts` | — | **v2** | |
| H5 | Narration pilot: 60 passages, 4–5 engines, cost per approved hour | GSV-54 (GSV §3 pilot gate); MG-E12/E13 | G | `eval` | Candidate set (VoxCPM2, Qwen3-TTS, Chatterbox, CosyVoice3, Kokoro). **No independent long-form evaluation exists** (GAP-08), so the pilot measures long-form WER drift and blind preference in-house. The bar is **Eleven v4**, now top of the AA TTS board. | **v2** | The business case against ElevenLabs (INFERRED list-price baseline ~$4.0–4.6 per finished hour, X-48). |
| H6 | Speech-only enhancement (DeepFilterNet) | GSV-43 (GSV §7) | G | `dsp` | — | **v2** | Never applied to music. |
| H7 | Spoken word over music (Suno Speech beta) | [Suno blog](https://suno.com/blog/introducing-speech-beta) | G (obs.) | `tts` + `generate` | Terms not stated | **research** | Comparator only. |
| H8 | **Voice continuity seeded only from original human recordings** | [ElevenLabs Prohibited Use Policy](https://elevenlabs.io/use-policy) §9(j)(k)(l) (GAP-08) | critic | voice registry, `tts` | Whether the current Sabbath Echo voice is a clone of a recording Jon holds, or a Voice Library / Voice Design voice that cannot be carried over (Q9) | **v2** | ElevenLabs renders may be neither a cloning reference nor training data. |

## I. Export and delivery

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| I1 | Full-song WAV and MP3 export, with no caps | Suno downloads (#143–145); Kimi "no caps" | G, K, F | `export` | — | **v1-core** | Ownership is the wedge. |
| I2 | Export manifest: human contributions, model/license chain, operator lane, AI-disclosure flag, converted-vocal flag, imported-source terms, loudness report | GPT; MiniMax AUP #11; Suno C2PA (unverified) | G | `export`, `provenance` | — | **v1-core** | Needed for release and for rights. |
| I3 | Loudness and true-peak measurement and a dry export | GPT; [ITU](https://www.itu.int/rec/R-REC-BS.1770/en) | G, K | `eval`, `export` | Our own true-peak meter (pyloudnorm lacks one). pyloudnorm implements **BS.1770-4**; whether -5 gives the same integrated loudness for stereo is **UNVERIFIED** (X-47), so reports name the revision used. | **v1-core** | Measure first. |
| I4 | Aligned multitrack/stem export (common rate, zero start, frame count) plus DAW round trip | MG-E15 (GSV-62; three-OS round trip); MJ4d0-Wi1z8 Logic round trip | G, K | `export` | Round trip on Windows and Linux DAWs untested (J19) | **v1-studio** | Lets Jon finish in Logic or another DAW. |
| I5 | MIDI and tempo-map export | Suno downloads (MIDI); Kimi | G, K | `export` | — | **v1-studio** | Mureka paywalls this. AURA doesn't. |
| I6 | Automatic mastering (reference-matched) | Kimi Rung 0 (Matchering) | K | `dsp` | Matchering is GPL (separate process); risk of hiding defects | **v2** | Only after A/B shows a benefit. |
| I7 | Super-resolution to 48 kHz (AudioSR / Apollo) | Kimi | K | `dsp` | Generative; Apollo is the wrong tool and CC BY-SA | **research** | Upsampling changes the container, not the information. |
| I8 | Destination eligibility checklist (Pond5/Envato bans, disclosure) | GPT | G | `export` | — | **v2** | Pond5 and Envato ban AI primary uploads. |
| I9 | Music video, and a lead-vocal guide bus for lip-sync | BKDrtzJktO0 21:30–23:00; Suno video download | G, K | `export` (guide bus) | Video generator choice | **research** | After the song exists. |
| I10 | Client delivery packages (cue sheets, cutdowns, loop-safe edits) | x8EOgO7UQ54 | G | `export` | — | **out-of-scope** | Not Jon's goal for this tool. |
| I11 | Share link or self-hosted share server | Suno share; Kimi Phase 4 | K, F | n/a | — | **out-of-scope** | No publishing or social features in the personal build. |

## J. Library, project and operations

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| J1 | Local library: search, filter, newest first, workspaces | Suno #017/#046 | K, F, G | `provenance` | — | **v1-core** | |
| J2 | Song page: art, title, lyrics, versions, Remix | #143–145 | F | UI | — | **v1-core** (no social) | |
| J3 | Persistent player bar | #017 | F | UI | — | **v1-core** | |
| J4 | Content-addressed audio store + SQLite metadata; native-rate originals kept | G, K, F all | G, K, F | `provenance` | Storage volume choice (Q2) | **v1-core** | D-09 / D-15. |
| J5 | Artifact provenance with origin enum, weights hash, params intent + actual, seed, operator lane | GPT | G | `provenance` | — | **v1-core** | |
| J6 | Engine capability and license registry (claims vs local results) | GPT | G | registry | — | **v1-core** | D-01 / D-11. |
| J7 | Durable job queue with honest states, SSE progress, cancel, atomic commit | G, K, F | G, K, F | `job` | — | **v1-core** | D-12. |
| J8 | Cross-machine CUDA worker (authenticated, no shell) | G, K, F | G, K, F | `job` | **Hardware unknown; not on the tailnet.** On the Windows box, YuE2 runs under WSL2 with `.wslconfig` memory ≥24 GB; native Windows needs unmerged patches (GAP-03). Whether a 16 GB card qualifies is open (A4). | **v1-core** | Needed for the second engine. Without it every sung song is ACE-only, which needs Jon's sign-off (Q14). |
| J9 | Disk preflight and storage budget; selective downloads | Verification finding (2.0 GiB free) | verifier | `job`, storage | — | **v1-core** | Nothing installs without it. |
| J10 | Blind, level-matched A/B audition with scoring axes and marked problem intervals | GPT; Kimi LUFS-matched A/B | G, K | `eval`, UI | Using Jon's Suno outputs as the reference arm carries a ToS risk Jon must accept (Q7; GAP-07); otherwise the reference is human-made tracks he owns | **v1-core** | The acceptance gate (D-10). |
| J11 | Evaluation harness: 12-brief smoke → 48 briefs, preregistered, clustered uncertainty | MG-E01/E02 (GSV-56, GSV-57); Kimi eval-first | G, K | `eval` | — | **v1-core** | |
| J12 | Cost and economics log (cost per accepted song, cold/warm RTF) | GPT; GSV-50 (GSV §8 cost model) | G | `provenance` | Measured RTF | **v1-studio** | D-23. |
| J13 | Codec round-trip ceiling study (ACE VAE, HeartCodec, SA3 SAME) | MG-E04 (GSV-58) | G | `eval` | — | **research** | Run before any enhancement or training claim. |
| J14 | Cover art generation and voice avatars | #046, #071–072 | F (obs.) | image gen | — | **out-of-scope** (v1) | Not needed for the song. |
| J15 | Accounts, credits, plans, quests, Explore, comments, publishing | Suno | F (dropped), K | n/a | — | **out-of-scope** | Personal, local, no credits. |
| J16 | Forced watermark (SynthID-style) | Google Lyria | K (anti-feature) | n/a | — | **out-of-scope** | The manifest and disclosure cover provenance. |
| J17 | Desktop installers (shell) | Kimi Phase 4 | K, G | shell | Tauri's WebKit audio gaps; Electron preferred | **v2** | D-14. |
| J18 | Mobile companion | Kimi Stretch | K | n/a | — | **out-of-scope** | |
| J19 | **Control service and localhost UI run on macOS, Windows and Linux**, with CI on all three | Owner requirement recorded in `FRAMING.md` (X-46); MG-E14–E16 | G (framing), critic | `job`, UI, storage | Neither the Linux nor the Windows machine is reachable; no macOS-only dependency may enter the control service (e.g. `afconvert`) | **v1-core** (portable code and CI) | D-24. The owner asked for all three platforms; portable code now avoids a rewrite later. |
| J20 | **Studio playback gate per OS**: 8 tracks × 30 min with no underruns, UI p95 < 100 ms during generation | MG-E14 (GSV-61); [WAC 2025](https://doi.org/10.5281/zenodo.17642262) | G, critic | `timeline`, `eval` | All browser latency evidence is from a 2021 MacBook Pro; **Windows and Linux Chrome are unmeasured** (X-49) | **v1-studio** (Mac first; Windows and Linux when reachable) | D-13 / D-24. Never call it three-platform ready from one OS. |

## K. Personalization and training (D-20)

| # | Feature | Evidence | Proposed by | Primitive | Unverified dependency | Tier | Reason |
|---|---|---|---|---|---|---|---|
| K1 | Personal taste memory (non-ML): genres, accepted takes, reasons | Suno My Taste; GPT | G, K | `provenance` | — | **v2** | Routing and prompt help first. |
| K2 | Style LoRA / LoKr per genre | Suno Custom Models (≥6 songs, mechanism undisclosed); Kimi Rung 2 | K, G | training | **Contested**: 12 vs 16–20 GB; a Mac MPS NaN report; data rights | **research** | Only after the harness exists, and only on owned or consented data. |
| K3 | DPO on preference pairs | Kimi Rung 3 | K | training | Reward hacking (HeartMuLa evidence); NC scorers | **research** | Needs held-out human preference. |
| K4 | Continued SFT on licensed / CC0 audio | Kimi Rung 4 | K | training | MTG-Jamendo / FMA are mostly NC | **research** | Escalation only, with a decision packet. |
| K5 | Foundation training from scratch | Kimi Rung X; GPT escalation E | K, G | training | — | **out-of-scope** | Ruled out by every source. |

## L. Competitor features noted (Kimi landscape) and their mapping

| # | Feature | Evidence | Proposed by | Mapping / tier |
|---|---|---|---|---|
| L1 | Udio inpainting | Kimi Udio card | K | → D2 (**v1-studio**) |
| L2 | Soundraw bar-level structure editor | Kimi | K | → B8 + D1 (**v2**) |
| L3 | ACE Studio note-editable vocals | Kimi | K | → A10 / G5 (**research**) |
| L4 | Mureka MIDI / DAW-session export | [Mureka](https://www.mureka.ai/subscribe) (Premier) | K | → I4, I5 (**v1-studio**) |
| L5 | Moises practice suite, mobile parity | Kimi | K | **out-of-scope** |
| L6 | Kits.AI artist voices and custom voice training | Kimi | K | → G1–G4 (**v2**, own or consented voice only) |
| L7 | LANDR mastering, distribution, plugins | Kimi | K | → I6 (**v2**); distribution is **out-of-scope** |
| L8 | Boomy built-in distribution | Kimi | K | **out-of-scope** |
| L9 | Mubert license-certificate trail | Kimi | K | → I2 export manifest (**v1-core**) |
| L10 | AIVA / BandLab MIDI-first flows | Kimi | K | → A3, A5, I5 |
| L11 | ElevenLabs Music API; Mureka API; Lyria 3.5; SA3 Large | Kimi; GPT | G, K | Hosted reference lane (**v2**, D-22) |

---

## Coverage check

- **Every primitive the v1-core flow needs:** `capture` (+ an m4a/AAC decoder), `transcribe`, `melodyspec`, `songspec`, `generate` (ACE draft/render), `render-from-score` (YuE2 on CUDA, individual lane, via the MelodySpec → ABC converter) or `cover` (ACE; R2-synth needs a MIDI synth), **`separate` (internal, for analysis only: A11)**, `rerank` (hard constraints, including lyric PER through a G2P), `eval` (F0 tracking + DTW for melody adherence, and blind A/B), `export` (+ manifest + loudness), `provenance`, `job`, storage preflight, and the portable control service (J19). Lyric **word alignment** (`align`) is not needed in v1-core: B7 only keeps approved lyrics, transcript and alignment as separate assets, and word timing arrives with D9 in v1-studio.
- **v1-core plumbing with no verified component yet** (ticket nodes; RECONCILIATION §4.9): the audio decoder, the G2P/phonemizer, the MIDI synth and soundfont, mir_eval, and the MelodySpec → ABC converter (dialect confirmed, converter unbuilt). The F0 tracker (SwiftF0, librosa pYIN) and the internal separator (Demucs, individual lane) are verified on license and lane; the LLC-lane separator is not.
- **v1-core rows that rest on unverified capabilities:** A4, A6 and A7 (hum transcription and melody keeping), A11 (separation quality on generated vocals), C3 (Mac timings), J8 (CUDA worker) and J19 (Windows and Linux hosts unreachable). These are the Phase-0 experiments (RECONCILIATION §6, D-04 / D-10 / D-24).
