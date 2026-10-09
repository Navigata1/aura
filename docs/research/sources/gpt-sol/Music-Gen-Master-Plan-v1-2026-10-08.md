# Build the music system that can keep improving

Music Gen · Independent research and engineering master plan · October 8, 2026

**Verdict: build a studio around interchangeable music engines, with a fast local editing lane, a separate quality-generation lane, and an independently evaluated voice service. Existing releases make that a credible starting point. Broad Suno parity remains a research objective that must be demonstrated through listening and control tests.**

Your ambition is reasonable as a direction. We can reproduce many of the workflows, own the project files and controls, and improve the sound through model selection, focused adaptation, better production tools, and a feedback loop. We cannot infer a proprietary model’s complete architecture from its interface, or make a reliable promise that a wrapper and mastering chain will equal its generation quality. The useful question is which capabilities we can match now, which require experiments, and which require a larger data and model program.

This document is a build specification for review by you, Claude and Kimi. It is accompanied by separate generation, voice/studio, and timecoded video research. **No model was installed or benchmarked in this run.** The verified application baseline is an initially empty Music Gen workspace. The local host is an Apple M5 Pro with 48 GiB unified memory; Linux/Windows GPU specifications and compute budget are still unknown. All numerical acceptance thresholds and effort estimates below are proposed planning choices, unless explicitly identified as source facts or measurements.

## 1. Reset the benchmark before choosing the engine

Suno released v5.5 on March 26, 2026, with Voices, Custom Models and My Taste. Its current documented generation is **v6**, released September 9, with core, wild and mini variants. The help page documents eight-minute generation. We did not locate an official v6.5 release; “Suno 6.5” is your forward-looking product ambition. These are documented offerings, not our independent measurements of quality. [v5.5 announcement](https://suno.com/blog/v5-5), [v6 documentation](https://help.suno.com/en/articles/13924801).

The v6 announcement describes local section and lyric edits, multi-source mashups, isolate-and-sample workflows, and multimodal inputs. Those are important targets for experiments; an announcement does not prove sample-level preservation or reliability. [v6 announcement](https://suno.com/blog/introducing-v6).

Studio 2.0 also raises the interface baseline: MIDI recording/editing, MIDI-conditioned generation, automation, effects, and chat-directed production are part of the current product. Suno acquired WavTool and its browser DAW team in 2025. A creation form is modest engineering; a reliable multitrack workstation is substantial engineering. [Studio 2.0](https://suno.com/blog/studio-2), [WavTool acquisition](https://suno.com/blog/suno-acquires-wavtool).

Claude’s attached response calls the UI the easy 20% and generation the hard 80%. That is a useful warning about where model capability matters, but it is not a measurement. The attached small contact sheets show creation forms, a recorder, colored tracks, and editing surfaces. They do not establish audio quality, latency, separation fidelity, or the complete internal system. The screenshot’s claim of transcript plus 150 frames was not accepted as our own review evidence; we retrieved new video evidence.

### Define the ambition as a capability vector

| Dimension | What the listener or creator actually experiences | Measurement we need |
|---|---|---|
| Composition | Memorable melody, harmonic movement, repeatable chorus, purposeful ending | Blind full-song evaluation and annotated section map |
| Vocals | Intelligible words, expressive performance, stable identity and pitch | Human lyric audit, pitch/identity diagnostics, listening |
| Fidelity | Clear transients, natural timbre, stereo depth, no metallic/watery collapse | Level-matched comparisons, codec round trips, artifact annotation |
| Control | Tempo/key/structure/reference constraints actually followed | Declared constraint tests, not slider availability |
| Editing | One section or word changes while the kept material survives | Outside-mask PCM comparison and boundary listening |
| Isolation | Useful individual parts and accurate timing | Ground-truth stem tests or explicitly generative reconstruction tests |
| Speed | Ideas audition quickly; expensive rendering has predictable queues | Cold/warm latency, real-time factor, accepted-result cost |
| Studio | Projects survive restart, undo works, exports line up in a DAW | Cross-platform round trips and real hardware playback |

We should aim first for **excellent results in your chosen uses**: original songs, worship/acoustic arrangements, cinematic underscores, and approved narration. Broad coverage of every genre and language is a separate scale goal. You should choose the first use cases when we start; this plan does not assume that a single worship niche defines the entire product.

## 2. What the seven videos can establish

All seven supplied URLs were retrieved, alongside the original Simon Crowe tutorial identified from your screenshot. Across these eight sources, all retrieved transcripts were read; 2,450 frames were extracted; 288 overview thumbnails and 44 full-resolution images were inspected, representing **307 distinct sampled frames** after overlap. This was a transcript-and-sampled-frame analysis, not a continuous watch or independent auditory scoring. The appendix and inspection manifest preserve the exact coverage and approximate frame timestamps.

Read the video appendix as a feature-discovery map: observed screens → candidate controls → required backend contracts → experiments. The strongest ideas are only promoted into a shipping scope after testing the underlying model operation. Audio in a tutorial is also affected by upload compression, voiceover, mastering, and selection. We have not completed a controlled listening comparison of these engines.

| Source and timecoded evidence | What matters for our system | What the evidence does not prove |
|---|---|---|
| [Replacement-tools video](https://www.youtube.com/watch?v=GZtLsvklYBI&t=133s), 02:13–02:25; 16:30–18:51 | VoiceStudio is the voice opportunity. The narrator acknowledges the default model's noncommercial terms, and later describes ACE output/control as short of Suno in his experience. The visible ACE screen uses a selected cloud backend. | Its displayed 14-second results are not a local full-song performance benchmark. A monthly-price narration conflicts with the yearly slide; [current VoiceStudio Pro pricing](https://voicestudio.sh/pro) is $99/year, checked October 8. |
| [Official v6 introduction](https://www.youtube.com/watch?v=_lHvWn2SNC4&t=130s), 02:10–03:26; 09:45–11:08; 15:21–16:00 | Different references supply vocal, drum, atmosphere and energy roles. Requested edits preserve verses or replace words. Extra-compute mode is described as reducing longer-song drift. | Vendor demonstrations do not establish exact preservation, an internal architecture or an independent quality score. |
| [User-reaction discussion](https://www.youtube.com/watch?v=CZazcFtS4Co), 00:00–00:30; 21:48–22:05 | Download/access concerns expose the value of durable local files, transparent provenance and ownership of sessions. | Inspected frames are talking-head commentary. They do not verify a download policy or platform watermark requirement; check the actual current terms. |
| [Music-video workflow](https://www.youtube.com/watch?v=BKDrtzJktO0&t=1290s), 15:00–15:34; 21:30–23:00 | Use cheap draft renders, exact shot durations and stable character references. Route only the intended singer's isolated vocal into lip-sync, then restore the full mix. | A credit-bearing hosted video demo is not a free local pipeline. Its twelve-part split screen does not prove native multitrack generation. |
| [Monetization tutorial](https://www.youtube.com/watch?v=x8EOgO7UQ54&t=188s), 03:08–03:21; 07:43–07:49 | Distribution eligibility must be checked at the destination. Export provenance and human contributions should be retained. | Its Pond5/AudioJungle acceptance claims fail current primary-policy checks. Adding one human element does not automatically make the entire generated work copyrightable. |
| [Deliberate-control tutorial](https://www.youtube.com/watch?v=DrRRvM4oc4w&t=578s), 09:38–11:35; 12:40–13:55 | Lyric alignment, alternate replacements, audition before insert, undo, fades and reusable references are more consequential than a long list of sliders. | Bracketed lyric tags and 0–100 controls are soft directions unless a backend supports an explicit musical constraint. |
| [Working songwriter](https://www.youtube.com/watch?v=MJ4d0-Wi1z8&t=300s), 05:00–07:00; 25:30–33:30 | Preserve a human-authored chord/melody seed, correct lyric transcription, generate arrangements, compare several takes, and return the keeper to Logic. He reports melody-following regression in v5.5 and four or five attempts for a keeper. | The seed is a MIDI-programmed Kontakt guitar, not a documented live guitar recording. The chosen result is explicitly a demo, not a finished song or guaranteed first-take success. |

The original [Simon Crowe tutorial](https://www.youtube.com/watch?v=MI6vwl_ZHN8&t=690s) adds an important project-transfer detail: entering Studio through the editor preserves section markers in the demonstrated workflow (11:30–12:15). It also shows versions and instrument parts. We should preserve annotations and alternate takes in every project transfer, rather than reduce a rich session to one WAV file.

The monetization correction is grounded in [Pond5's contributor FAQ](https://contributor.pond5.com/faq/) and [Envato's author policy](https://help.author.envato.com/hc/en-us/articles/13313674070681-AI-generated-content-policy-for-Market-and-Elements), which prohibit the relevant AI-generated uploads as primary sale content. The [U.S. Copyright Office report](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf) evaluates human authorship case by case. These are destination-specific findings; this research does not conclude that every AI-assisted song is prohibited everywhere.

### Strengths to preserve from the references

Keep the rapid prompt-to-audition loop, human melody and lyric ownership, reusable identity references, alternate takes before commitment, nondestructive edits, and a direct DAW handoff. Preserve the emotional clarity of a polished studio, with real waveforms and audible examples. The challenge is to connect each attractive affordance to a tested musical operation.

### A later music-video extension

Treat video as a separate producer over the music project's accepted assets. A shot manifest should store start/duration, performer identity, visual references, lead-vocal guide, lyric/phoneme timing, camera instructions and generation budget. Keep the guide bus separate from the final playback bus: backing singers and ad-libs should not accidentally drive the lead character's mouth. Verify exact audio/video offsets, frame-rate conversion and shot continuity before a final render. The black-background MP4 workaround in the demonstration can become a deliberate guide-export operation. This is a valuable export/integration lane after reliable stems and alignment; it does not require us to train a video foundation model in the first music build.

## 3. The models: give each engine a job

ACE is useful, and it is not the only route. The current landscape includes genuinely different architectures and legal/runtime constraints. The detailed model register records exact source links, release status, weight licenses and unresolved access. The following is a shortlist for a benchmark, not an asserted quality ranking.

| Engine or family | Proposed role | Evidence and limitation | Decision |
|---|---|---|---|
| ACE-Step 1.5 / XL | Fast local drafts; reference/cover/repaint and layer experiments | Current official repo documents 4B XL and cross-platform backends; functionality varies by checkpoint. Its comparative quality and timing claims were not locally tested. [Official repo](https://github.com/ACE-Step/ACE-Step-1.5) | Initial control engine |
| MiniMax Music 3 | Independent full-song quality challenger | Downloadable model; hierarchical global/local language modeling with flow-based waveform synthesis. Official card requires CUDA and nonstreaming generation; low-memory offload paths are documented. Community license conditions apply. [Model card](https://huggingface.co/MiniMaxAI/MiniMax-Music3) | Initial CUDA challenger |
| HeartMuLa released 3B | Second open full-song/lyric-conditioned candidate | Evaluate released weights, codec, language coverage and actual consumer memory needs; do not count announced unreleased models. [Official repo](https://github.com/HeartMuLa/heartlib) | Next challenger |
| YuE / YuE2 | Original YuE as a reference; YuE2 for explicit musical planning research | YuE2’s study includes v6 and v6-wild. Its expert listeners preferred Suno v6 overall over YuE2’s best-of-eight result, despite strong automatic scores. Company commercial use of weights requires separate licensing. [Official repo](https://github.com/multimodal-art-projection/YuE), [YuE2 paper](https://arxiv.org/abs/2609.33757) | Research lane; reconcile intended-use rights |
| Stable Audio 3 medium | Instrumental textures, beds, samples and inpainting | A specialist for instrumental/audio tasks; intelligible singing is not the intended capability. Community/gated model conditions and dependencies matter. [Model card](https://huggingface.co/stabilityai/stable-audio-3-medium) | Specialist candidate |
| DiffRhythm 2 | Alternative architectural baseline | Released block-flow direction; measure exact lyrics, endings and identity. v1.2 and v2 have different editing/extension capability. [v2 repo](https://github.com/ASLP-lab/DiffRhythm2) | Secondary comparison |
| SongGeneration / LeVo | Potential quality comparison when original assets are reconciled | Canonical repo/model access was unresolved; accessible v2-large has unknown license. The original demo is historical evidence, not current weight clearance. [Original demo](https://levo-demo.github.io/), [canonical repo](https://github.com/tencent-ailab/SongGeneration) | Conditional, not foundational |
| MuLaCover | Reference-conditioned cover/reinterpretation research | The new official release has noncommercial weight/output conditions despite permissive source code. It does not promise the original waveform remains intact. [Official repo](https://github.com/HeartMuLa/MuLaCover) | Separate experiment |
| Shao, formerly Khala | Acoustic-token and reconstruction research | Public repo/weight route exists with noncommercial conditions; upstream warns that changing the pinned NVIDIA runtime can severely degrade output. [Official repo](https://github.com/Shao-Music-AI/Shao) | Released research candidate, not first production engine |
| StepAudio 3 Music | Architecture intelligence and optional hosted trial | Recent report and provider-backed demo exist; downloadable music weights were not verified in this sweep. [Technical report](https://arxiv.org/abs/2609.16034) | Hosted/paper lane, not an assumed local checkpoint |

Start with **two engines**: ACE for speed/control and MiniMax as the provisional independent quality challenger on suitable NVIDIA hardware. The pair is a hypothesis, not a tested optimum. Choose the second installed model after hardware and intended use are known; personal-use YuE2 can replace MiniMax if its rights, control and pilot results suit the job. Add HeartMuLa after the first comparison is reproducible. If hardware, release terms or performance disqualify a candidate, the adapter boundary lets us replace it. Engine routing begins with explicit user choice; automatic selection comes only after our benchmark supplies evidence.

Within ACE, pin separate task profiles: turbo/XL for drafts or fidelity, and the supported base checkpoint for `extract`, `lego` and `complete`. A generation-capable XL checkpoint does not automatically perform every editing task. Keep CFG and other controls faithful to the chosen variant. [Inference contract](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md).

There is no universal settings translation. A diffusion guidance value, sampling temperature, and reference strength are different mechanisms. A studio can expose a common creative intent while keeping the engine-specific controls available and recording the transformation. An unsupported operation must be unavailable or identified as an approximate workflow.

### Decision matrix against your goals

| Strategy | Sound ceiling | Independence | Editing control | Cost and maintenance | Verdict |
|---|---|---|---|---|---|
| One ACE wrapper | Tied to ACE’s current model and codec | Local, but one engine | Good documented starting operations | Lowest initial integration burden | Good prototype; incomplete long-term strategy |
| Interchangeable local/remote engines | Choose and improve task-specific quality | Own files, prompts, adapters and evaluation | Can compose deterministic editing with supported generation | More runner and capability work | **Recommended foundation** |
| Commercial service only | Can access a strong provider where sanctioned access exists | Provider dependent | Limited to provider’s exposed operations | Recurring charges, terms and availability | Optional benchmark/fallback |
| New broad foundation model from scratch | Potentially high, with substantial uncertainty | Highest model ownership | Can design conditioning and native stems | Data, ML team, compute and long iteration program | Earn through measured milestones |
| Human production plus AI | High fidelity for chosen songs | Own performances and sessions | Exact notes, stems and articulation | Human time and recording skill | Valuable integrated route |

## 4. What we can learn about Suno’s engineering

**Known from inspected primary sources:** Suno operates proprietary music models, personalization, reference workflows, a DAW foundation, and a newer generative stem process. Its public Bark repo explicitly distinguishes Bark from its music models. Bark is an older generative audio transformer and is not Suno’s current song engine. [Bark](https://github.com/suno-ai/bark).

There is historical technical disclosure beyond the product pages. In a March 2024 recorded interview, CEO Mikey Shulman described transformer-based next-token music/audio generation, audio tokenization as important proprietary work, and throughput fast enough for streaming. That is firsthand evidence of an earlier engineering direction; it does not identify the current v5.5/v6 recipe. Suno's January 2026 data disclosure reports tens of millions of audio files with textual metadata, cleaning/association, synthetic data and possible user content/activity in post-training. It is a corporate disclosure, not a per-version dataset or an independent training-rights audit. [Recorded interview](https://www.latent.space/p/suno), [Suno data disclosure](https://help.suno.com/en/articles/9709569).

The bounded patent search did not verify a relevant Suno-assigned or version-linked patent. Two plausible-looking hits belonged to other assignees; one merely mentioned Suno as a downstream engine. The engineering appendix preserves those rejected leads, the historical disclosure boundaries, and singing/multitrack research that can inform our experiments.

**Not established by the inspected public sources:** the exact v5.5/v6 parameter count, training objective mix, tokenizer, dataset composition per version, stem architecture, serving topology, and whether Custom Models are implemented with LoRA, embeddings, full tuning or another method. We should not convert a plausible implementation into a statement of fact. A feature demo cannot reveal those details; a patent describes claimed mechanisms without establishing their use in a particular released version.

**Useful inference from open research:** high-quality music systems benefit from a representation of musical structure, a way to encode acoustic detail, strong conditioning/alignment, and a high-quality decoder. These can be hierarchical autoregressive models, latent diffusion/flow models, or hybrids. The engineering proposal below combines those lessons without claiming to reconstruct Suno’s hidden architecture.

### The generation stack we should understand and instrument

1. **Brief and composition plan.** Keep original lyrics, section tags, desired duration, references, instruments, voice identity and arrangement evolution in a structured SongSpec. A language model can suggest improvements, but changes to approved wording remain visible and reversible.
2. **Musical representation.** Where an engine supports it, preserve chord progressions, melody, beat grid, score and section timing as explicit objects. Otherwise mark them as requested constraints with measured adherence, not guaranteed controls.
3. **Acoustic generation.** Generate tokens or continuous latents conditioned on text/audio/score. Track actual model version, context limit, duration limit, precision, steps, seed and reference hash.
4. **Waveform reconstruction.** The codec/vocoder supplies much of the timbre and transient ceiling. A higher-rate file container cannot restore information the generator did not produce. Descript’s DAC provides a concrete open codec family and training/reconstruction tooling, but exchanging a codec under an existing model generally requires adaptation or retraining. [DAC](https://github.com/descriptinc/descript-audio-codec).
5. **Audition and selective repair.** Compare several candidates within a declared budget. Diagnose the failed verse or consonant rather than regenerate a good whole song. Keep the original and all accepted edits.
6. **Production render.** Make gain, EQ, de-essing, dynamics, spatial processing and limiting inspectable. Preserve a dry export. Loudness and true peak use standard measurements; the artistic target depends on the destination. [ITU-R BS.1770-5](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/).

### Closing the sound gap is a sequence of hypotheses

First test whether better prompt structure and engine choice improve the failures. Then test reference conditioning, selection and local repair. Next test approved-domain adapters and the decoder’s reconstruction ceiling. Only then escalate to a new representation or broad model training. Each step needs an ablation: same briefs, same candidate budget, with and without the change.

LoRA can teach a released model a specific vocal/style domain where supported. It does not guarantee improved general musical knowledge, a new codec bandwidth, exact long-form structure or better coverage of unfamiliar languages. “Fine-tune on a handful of songs” describes a personalization experiment, not a shortcut to another company’s entire model.

## 5. Isolation is two different products

The most consequential discovery in this sweep is Suno’s June 2026 description of **regenerated stems**: it says it generates the requested instrument anew to match the source. That explains a plausible route to clean parts beyond ordinary extraction. It also means a clean result and a faithful result are separate requirements. Suno does not publish the full implementation in that post. [Stem update](https://suno.com/blog/stem-separation-updates).

| Operation | What it promises | Useful tools and research | What the gate measures |
|---|---|---|---|
| Separate original | Estimate sources from the existing waveform | Demucs baseline; modern band/roformer or SCNet candidates with exact weight licenses | Bleed, artifacts, mixture residual, timing and ground-truth source metrics |
| Re-perform instrument | Create a new clean performance conditioned on the original | Conditional generation, transcription+render, cover/layer operations | Notes, articulation, rhythm, identity and musical match; residual alone is inappropriate |
| Compose native tracks | Generate coordinated parts from one shared musical plan | Score-conditioned render or trained joint multitrack generator | Harmonic/rhythmic coherence and each part’s isolated quality |

A separated stem is not automatically a clean original recording. A regenerated stem is not the original performance. The project model must record the distinction, and the UI should make the operation understandable: “Isolate original,” “Re-perform this part,” or “Create a new part.”

### Practical implementation path

Start with vocals/accompaniment and a small supported instrument taxonomy. Run a quality preset through a modern separator and retain a residual track so the mix can be inspected. Listen to isolated stems **and** recombined output. Never extrapolate a four-stem model into arbitrary cello-versus-violin isolation because a dropdown can list those names.

For clean controllable instruments, transcribe a well-isolated part, allow note correction, and render it through a quality instrument. Spotify’s Basic Pitch supports polyphonic transcription and pitch bends, but its own documentation says it works best on one instrument at a time. It is a useful starting tool, not a universal mixed-song-to-perfect-MIDI solution. [Basic Pitch](https://github.com/spotify/basic-pitch/blob/main/README.md?plain=1).

Replacement also needs a mix rule. Layering a new guitar onto the original stereo song leaves the old guitar playing underneath. To replace it, reconstruct the mix from retained sources plus the accepted new part, or use a specifically evaluated suppression/residual operation. Keep bleed and subtraction artifacts audible during review; do not hide this distinction behind a “Replace” button.

The next experiment is a reference-conditioned re-performance adapter: source stem + surrounding mix context + tempo/score + instrument label → new dry part. Evaluate whether the model preserves melody, note onset, groove and phrasing. A transient or sustained note crossing the edit boundary needs context, crossfading and explicit tail handling. This is an ML experiment, not merely an API endpoint.

Native multitrack generation is a longer-term opportunity. Shared beat/score/latent conditioning must coordinate instruments; independently generated “same BPM” tracks may disagree on key, phrasing and section transitions. High-quality human-recorded or virtual-instrument parts can also be combined with AI. That hybrid route gives useful ownership and editability before a native joint generator exists.

## 6. Voices: separate singing from narration

Singing identity, speech cloning, expressive narration and long-form consistency are distinct tasks. A TTS engine can read lyrics, but that does not make it a convincing singer with melody and phrasing. Conversely, an expressive song model may not be suitable for exact educational narration.

Suno Voices uses a recording plus a verification phrase and keeps the resulting Voice private. That is a useful product reference for an identity/authorization registry, not evidence of how the underlying conditioning vector or model is trained. [Voices](https://suno.com/products/voices).

For singing, test three paths separately: native reference/identity conditioning; an approved singer adapter; and conversion of an existing performance to an authorized timbre. Conversion needs melody, consonants, breath, vibrato and timing audits; it can introduce new artifacts and must retain the original take. Do not claim voice identity works equally across octaves, styles and languages because one chorus sounds recognizable.

There is also a valuable explicit score-to-singing lane: note pitches/durations + phonemes + lyric alignment + expressive curves → vocal performance. OpenVPI DiffSinger offers this kind of control; RVC is a separate performance-to-timbre conversion route. Their code licenses do not license arbitrary singer banks. Together with MIDI instruments, this gives us a controllable production route that complements full-song sampling. [DiffSinger](https://github.com/openvpi/DiffSinger), [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI).

### The pinned Sabbath Echo voice opportunity

The first supplied video identifies **debpalash/VoiceStudio**. Current source describes an Electron desktop application with local engines and optional remote workers. Its application license and the rights of bundled models are separate. The default OmniVoice weights are noncommercial, and the app’s own notices do not grant blanket commercial clearance. An evaluation fork is useful; using that default stack for a production narration service requires resolving the underlying terms. [VoiceStudio](https://github.com/debpalash/VoiceStudio), [license notice](https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md), [OmniVoice](https://huggingface.co/k2-fsa/OmniVoice).

For an initial production-oriented comparison, inspect Qwen3-TTS, Chatterbox Turbo, CosyVoice3 and Kokoro. The research appendix distinguishes cloning/design features, model sizes and exact licenses. F5-TTS and Fish Speech illustrate why a permissive code repository can still have restricted official weights. Keep a model registry that carries those facts with every engine.

Proposed voice-service contract: approved text + language + versioned voice + pronunciation dictionary + prosody plan → chunked dry audio, word timings, render manifest and QA result. Use semantic chunk boundaries, persistent voice configuration and resumable rendering. Keep breathing/pauses natural, check missing/repeated words, and require human approval for important names and passages. Only apply an SSML instruction if the backend supports its intended meaning; otherwise explain the approximation in the adapter.

Your **$25,000 ElevenLabs cost is a user-reported historical amount**, not an inspected invoice or a current avoided-cost quote. The business case should compare cost per approved finished hour, including inference, retries, editorial review, setup and operations. Past spend is sunk cost. A local engine can reduce future marginal spend while moving labor and maintenance onto us. We need a sample-based cost and quality pilot before projecting annual savings.

Prior Sabbath Echo records distinguish licensed Scripture audio/Bible Brain from EGW/ElevenLabs narration, and forbid synthesized Scripture within that project. We have not re-audited the current repository or contract in this run. Preserve those source lanes provisionally and recheck the governing files before integration. This master plan does not change Sabbath Echo’s content policy.

The future fork card is concrete: source `debpalash/VoiceStudio`; intended owner `Navigata1`; suggested name `voice-studio-lab` (proposed, not created); pin a release/commit; retain notices; audit dependencies/model licenses; compare Qwen3-TTS and Chatterbox/CosyVoice on approved narration; add a thin Sabbath Echo adapter; keep the upstream UI fork distinct from an independently owned service. No fork or integration was performed in this research phase.

## 7. The studio architecture

This section is a proposed implementation. The durable value is the project format, deterministic editing, model interchangeability and evaluation record. A beautiful UI should make these capabilities clear and pleasant to use.

### Layers and boundaries

| Layer | Initial implementation | Durable contract |
|---|---|---|
| Creator experience | React/TypeScript web UI, keyboard-accessible creation and timeline | SongSpec, visible capability support, project revision |
| Audio transport | Web Audio graph/AudioWorklet for bounded preview; separate offline render | Sample-frame clock, synchronized tracks, automation events |
| Local control service | FastAPI, SQLite metadata, content-addressed audio files | Jobs, artifacts, edits, model registry, manifest export |
| Engine workers | Separate pinned Python environments per incompatible model; Linux CUDA workers as needed | Capability discovery, generate, cancel, health, measured resource use |
| Analysis workers | Beat/key, transcription, waveform peaks, loudness, separator | Algorithm/version, confidence, editable annotations |
| Voice service | Separate runner and registry | Narration jobs and authorized identity references |
| Optional desktop/native host | Evaluate after browser/audio proof; native audio/plugin bridge where justified | Device access, signed packages, project compatibility |
| Evaluation system | Fixture library, private blind audition, metrics CSV/JSON | Reproducible comparisons, cost, failures and preference evidence |

The browser audio graph is a viable starting point; the Web Audio specification provides an audio routing graph and real-time/offline facilities. It does not guarantee low total microphone latency, universal device behavior, or arbitrary native plugin hosting. The current 1.1 document is a working draft; test features on actual browsers before depending on them. [Web Audio](https://www.w3.org/TR/webaudio/).

Use the Mac as an initial studio/control workstation and compatible local inference target. Let an NVIDIA Linux or Windows machine provide CUDA services when suitable. A browser on one machine can control a worker on another; owning three operating systems does not require every model to support every accelerator. Shared formats are more valuable than duplicated runners. MPS/MLX support, CUDA kernel dependencies and quantization quality are measured engine-by-engine.

MiniMax’s generic Hugging Face “Use this model” helper contains an image-generation-style snippet and mentions MPS, while its actual model instructions explicitly require CUDA. Follow the substantive model card and pinned implementation. A generated helper is not a compatibility test.

### Core project objects

**SongSpec** stores original and effective prompt; original and approved lyrics; ordered sections; target BPM/key/time signature; requested instrument/voice traits; references with source permissions and hashes; duration; variant budget; and selected engine. Each field also needs `requested`, `supported`, and `observed` where the distinction matters.

**PerformanceSpec** adds pronunciation dictionary revision; syllable/phoneme-to-note mapping; rests, breaths and slurs; continuous pitch and supported expression curves; singer/reference provenance; and confidence with human corrections. An engine declares which fields it consumes. A word timestamp alone cannot describe a vowel spanning several notes or a consonant entering before the beat. Singing-specific alignment and score-driven synthesis offer concrete tools to test this contract. [SOFA](https://github.com/qiuqiao/SOFA), [DiffSinger controls](https://github.com/openvpi/DiffSinger/blob/main/docs/BestPractices.md).

**Artifact** stores immutable audio bytes; SHA-256; original/native sample rate, channels and format; actual duration; model/weight/codec revisions; exact configuration; seed; machine/backend; wall time; parent artifacts; and origin (`generated_mix`, `separated_source`, `regenerated_part`, `human_recording`, `rendered_midi`). Converted/exported files point back to their native source.

**Project** stores tempo map, meter, tracks, clips, automation, markers, lyrics/timing annotations, plugin/render settings and revision history. Clip positions are integer sample frames in a declared project rate; musical positions also reference a tempo-map version. There is one transport clock. Stem exports start at the same zero and contain trailing silence/tails as required.

**EditOperation** stores affected tracks, a mask/time range, instruction, locked context, generation variant IDs, crossfade/tail policy and accepted result. Undo changes references, never overwrites originals. A dry local edit can guarantee exact outside-mask samples by compositing the kept PCM; a later mix/master render may deliberately change the whole signal and must be a separate operation.

**EngineCapability** stores supported tasks, durations, native rate, languages, backend/hardware requirements, reference options, identity controls, precision modes, license records and tested status. Published claims and local test results are distinct fields.

### Job and network behavior

Persist `queued → preparing → loading → generating → analyzing → ready`, plus failed/cancelled states. Report actual steps when available, not invented percentages. Write output to a temporary artifact and commit it atomically after validation; interrupted jobs can be retried without losing finished takes. Cold loads, download/setup, inference and postprocessing have separate timing.

Single-user storage begins local. A remote worker must authenticate, restrict origins, enforce job/resource limits, and receive only the referenced assets. Give the UI a project API, never a general shell. Uploaded media is decoded in a constrained worker; prompt text and generated plugin code never become executable merely because they came from an assistant. If we later add chat-authored effects, restrict them to a reviewed graph or sandboxed DSP interface with CPU/memory limits and a bypass path.

### The studio feature order

Creation/library/audition first. Then aligned multitrack playback, gain/pan/mute/solo, selection, split/trim/fades and export. Next add tempo-map/warp controls, automation, MIDI import/export and piano roll. Effects follow an offline/real-time equivalence test. Recording and native plugins follow actual device and latency proof. Chat is a command interface over these tested operations, with an inspectable diff and undo.

A fixed BPM field cannot represent expressive timing. Transcription confidence must be editable. Time stretching must preserve or deliberately alter pitch and be evaluated on vocals and transients. A MIDI file carries notes, not the original timbre, effects, articulation or mix. Export manifests should retain those relationships.

Design the UI around listening: large audition area, quick A/B and level matching, take history, a legible arrangement, real progress, and clear partial capability. Use restrained track colors, visible waveform/section context, keyboard navigation and accessible controls. A single creation path can reveal advanced controls progressively. The prettiness should support decisions and editing.

## 8. Evaluation: establish a truthful quality ladder

Our current baseline is **unmeasured** for every model. Do not assign a percentage of Suno quality. Build one benchmark that allows the best candidate to win and allows our preferred architecture to lose.

### Benchmark protocol

Create 48 fixed briefs as an initial design: eight categories with six briefs each. Cover sparse acoustic/worship, dense pop, rhythm-heavy music, cinematic/orchestral, instrumental beds, authorized voice/reference control, local repairs and difficult edge cases. Include slow/fast material, sparse/dense mixes, different meters where supported, and languages you actually intend to ship. Keep a separate narration suite. This is a proposal; the evaluation set does not yet exist.

Use original/approved lyrics and licensed reference recordings. Include songs long enough to expose drifting verses and final-chorus identity. Evaluate both a single candidate and equal-budget selected candidates, for example four takes per brief per engine. Keep every failure, total wall time, and the selection rule. A best-of-eight paper result against an older model cannot be compared directly to a single fresh take from v6.

Run separate comparison tracks for equal candidate count and equal compute/cost; four samples from two engines are not automatically equal GPU seconds or equal spend. Compare common supported tasks together. Unsupported local edits belong in the capability report, not in a fabricated audio score; approximate whole-song regeneration is a different operation. Keep native-rate listening and conversion settings consistent, record any loudness adjustment, and show both raw single-take reliability and selected-result quality.

Prepare private, anonymous, level-matched comparisons without heavy mastering. Randomize left/right presentation and review full songs plus marked problem intervals. Separate composition, sonic artifacts, lyrics, identity, instruction adherence and overall preference. Include your own judgment and independent musicians/listeners. Report uncertainty clustered by brief; many votes on a few songs are not many independent songs. A pilot can choose direction without proving universal superiority.

Use signal metrics as diagnostics: true peak/clipping, stereo/mono compatibility, duration, tempo/key adherence, onsets, intelligibility, edit-mask preservation and separation quality. FAD/CLAP can support evaluation with fixed references/settings; they are not a replacement for music listening. Research shows FAD is sensitive to sample size, embeddings and reference sets. [FAD evaluation study](https://arxiv.org/abs/2311.01616).

### Baseline → target gates

| Dimension | Measured baseline in this run | Proposed first acceptance gate | Later gate |
|---|---|---|---|
| Model integration | No local engine installed | Two pinned adapters complete 12 smoke briefs; failures retained | Full 48-brief fair-budget comparison |
| Quality | No independent listening results | Owner and external listeners accept the selected use-case pilot | Pre-registered noninferiority test against current reference; margin chosen before listening |
| Lyrics | No lyric accuracy measured | No missing/repeated lines in human-approved pilot tracks | Per-language word/phoneme error audit with human correction of ASR |
| Identity | No local identity tests | Same approved identity across ten varied excerpts passes blind owner review | Cross-style/octave/language challenge set |
| Local editing | No editor exists | Kept dry PCM outside explicit edit/crossfade masks is byte-identical | Good repair boundaries and musical transitions on unseen examples |
| Stem export | No project export exists | All stems share project rate, zero start and frame count; imported DAW session stays aligned | Independent instrument quality and recombination audit |
| Timing/control | No BPM/key adherence measured | Record actual compliance on every pilot; reject unsupported guarantees | Define tolerance per task and use case before scaling |
| Preview | No audio transport exists | Eight tracks play for 30 minutes on each target platform without observed underruns | Sixteen-track/effects stress test and device matrix |
| Responsiveness | No UI exists | Proposed UI interaction p95 below 100 ms during background generation | Real microphone/controller round-trip tests with measured latency |
| Recovery | No persistence exists | Forced restart preserves accepted takes and project state | Interrupted render/cancel/upgrade tests across three OSes |
| Economics | No render cost measured | Record cost per approved result including retries and review | Owner-set monthly envelope and sustainable accepted-hour cost |
| Narration | Historical $25k is user-reported | Fixed approved-text pilot compares local engines with current reference | Finished-hour cost/quality audit and project-policy integration |

“Byte-identical” compares retained samples with immutable pre-edit **working PCM at the same sample rate, channel layout and dtype**, outside the edit/crossfade mask. Compare canonical sample ranges, not WAV headers. Native-source conversion, resampling and mastering are separate recorded operations. Do not apply this gate to generative covers, re-performances, time stretching or a new full mix render. Separate preservation from creative transformation.

## 9. Compute and economics: buy evidence first

The 48 GiB Mac is a strong development/control machine, but unified memory is not equivalent to 48 GB of NVIDIA VRAM. Backend availability, bandwidth and kernels matter. ACE documents Apple backends; MiniMax currently documents CUDA. Other engines vary. Actual inference, stability and thermals remain unmeasured here.

Before choosing hardware, record each machine’s CPU, RAM, GPU, VRAM, driver, storage and network. Start with existing equipment and a short reproducibility trial. If a suitable CUDA machine is absent, benchmark on a bounded rental or an authorized provider before buying a GPU. We have not ordered hardware or rented compute.

Memory planning must include weights, activations, context/cache, decoder, reference audio, batch and headroom. Minimum advertised offload memory is a fit claim, not an interactive-performance promise. Quantization, offload and smaller checkpoints each need an audible/latency tradeoff test. Keep one heavy model resident at a time initially; serialize scarce-GPU jobs and prioritize short audition requests.

Use these formulas in the run log:

- Inference cost = GPU hourly rate × billable GPU hours, plus storage/egress and any API charge.
- Cost per accepted song = total cost of all attempts, repairs and production / accepted songs.
- Cost per approved narration hour = compute + recurring tools + editorial labor + operations, divided by approved finished hours.
- Real-time factor = inference wall seconds / generated audio seconds; log cold and warm separately.
- Local marginal cost includes measured electricity and review time; ownership cost also includes hardware and maintenance.

No current rental price or savings forecast is assumed. Choose an experiment ceiling before paid runs. For illustration only, a rate of $1/GPU-hour, 60 seconds per candidate and four candidates gives $0.0667 inference per brief; a 25% accepted-brief rate makes that $0.2667 per accepted brief before everything else. These are hypothetical inputs, not measured speed, a provider quote, or a forecast.

Also measure storage. At 48,000 frames/second × two channels × four bytes/sample × 240 seconds, a four-minute stereo float file is 92,160,000 bytes (~87.9 MiB). Twelve such stems are ~1.03 GiB before alternates. Four full versions approach ~4.12 GiB. Keep lossless working files, derived lightweight previews, bounded caches and manifest-based exports.

## 10. Training and data: how we earn the remaining capability

The long-term program needs a rights-aware, musically annotated corpus and increasingly controlled model experiments. Public accessibility is not a training permission. Source code licenses, weight licenses, codec/tokenizer terms, voice permissions and recording/output terms are separate entries. This is essential engineering input for deciding what we can actually use.

### An escalation ladder

**A. Integration and inference quality.** Fix settings, prompting, references, selection and repair. Establish a baseline and ablations. Shipping a better workflow around an existing model is useful even if the raw model’s average fidelity is unchanged.

**B. Domain and identity adapters.** Use approved recordings, multiple performances and deliberate holdouts. Annotate voice/instrument/style without conflating them. Train only the parts supported by the chosen release; compare to prompt/reference-only baselines. Measure memorization, generalization and identity consistency, including styles absent from training.

**C. Decoder/reconstruction research.** Compare source → encode → decode on held-out recordings before generation. If that round trip destroys cymbals, breaths, consonants or stereo imaging, better text conditioning cannot fix the ceiling alone. Test reconstruction losses and perceptual listening across domains. Avoid assuming a new codec is compatible with existing learned tokens.

**D. Controlled generation research.** Add explicit score/beat/section, aligned lyrics and masks where architecture permits. Use licensed mixtures/stems and synthetic renders with documented instrument-library training rights. Couple native parts to a shared plan. Evaluate hard cases such as changing one word, a choir entering halfway through a chorus, and replacing guitar while preserving a human vocal.

**E. Broader foundation training.** Proceed only if the narrower steps expose a material ceiling, assets/rights are secured, and an ML program is funded. This means dataset curation, distributed training, codec/model research, large holdouts, preference evaluation and iteration—not one overnight fine-tune. No responsible compute estimate can be derived without the chosen architecture, sequence length, corpus size and training recipe.

The corpus manifest needs recording/performer permission, allowed uses, expiration/revocation handling, source hash, lyrics and alignment provenance, tempo/meter/key confidence, language, stems when available, recording quality and train/validation/test allocation. Split by performer, work and recording family; overlapping song edits must not leak across splits. Keep licensed human material central and track synthetic provenance to prevent self-generated feedback from masquerading as independent quality evidence.

Three small research programs make the next escalation concrete: twelve approved singing phrases comparing native generation, score-driven singing and an authorized guide/conversion route; singing-specific versus speech alignment with manual boundary labels; and twelve owned eight-bar arrangements comparing independent parts, sequential context-conditioned ACE parts and shared-score instrument/singer rendering. All are proposed, with assets not yet created. Test intentional bends, melisma, consonant pickup, harmony, groove and edit locks; robotic pitch or coincident beat detections are not sufficient musical success. The engineering appendix defines these ablations. The companion machine-readable register contains **16 proposed experiments**, no results, and explicitly records that the 48 music briefs remain uninstantiated.

A preference loop can collect accept/reject decisions and reasons. Use it first to route/select candidates and improve prompts. Training against a learned preference score comes later, with holdout listeners and artifact checks. Optimizing an automatic score can reward the metric instead of the musical result.

## 11. The phased build

Effort below is a planning range for an experienced small team with agent assistance, suitable hardware and available assets. It is not a commitment or measured forecast. Phases may overlap after their contracts stabilize; ML experiments can take longer than UI implementation.

| Phase | Scope | Proposed effort | Exit evidence |
|---|---|---|---|
| 0 — Reproducibility and benchmark | Machine inventory, release/license pins, brief suite, reference files, minimal two-engine runners | 1–2 weeks | Commands, manifests, failures, first blind pilot and cost log |
| 1 — Creator foundation | SongSpec, library, take audition, queued jobs, cancellation, persistent files, local/remote worker selection | 2–4 weeks | Complete create→audition→save→restart→export flow on target OSes |
| 2 — Useful studio | Aligned multitrack timeline, deterministic edits, fades, mixer, undo, tempo map and stem export | 3–6 weeks | DAW round trip, persistence/recovery and real playback evidence |
| 3 — Sound and identity experiments | Fair-budget quality sweep, reference controls, voice consistency, selected local repairs and domain adapter trials | 4–8 weeks of experiments | Ablations improve held-out use cases; rejected approaches documented |
| 4 — Separation and re-performance | Strong separator, editable transcription, renderer integration, conditioned re-performance experiment | 4–8 weeks, research-dependent | Two distinct operations with source/transform provenance and listening results |
| 5 — Production and distribution | MIDI/automation/effects, actual recording devices, packaging/signing, security, backup and updates | 4–8 weeks | Three-platform acceptance; observed reliability, recovery and cost gates |
| 6 — Frontier program | Native multitrack/score control, codec or model training where earned | Separate funded ML program | Pre-registered measurable quality/control improvement against current references |

The full ranges are not simply added as a guaranteed delivery date. A useful creation application can arrive before sophisticated editing. A broad model-quality breakthrough cannot be promised on the same schedule as a timeline implementation.

The required skills span music production/listening, ML and model integration, audio/DSP, data and evaluation, and application engineering. One person can own several early roles; agents can accelerate code and research. Training a new frontier model still needs accountable dataset work, experiment design, compute operations and musical judgment. Keep a named owner for each acceptance gate so coding progress cannot silently substitute for listening or performance evidence.

### First two weeks: concrete task board

| ID | Priority | Deliverable | Dependency | Done when |
|---|---|---|---|---|
| M0-01 | P0 | Machine and use-case inventory | Owner specs/preferences | Actual hardware and first target genres/languages recorded |
| M0-02 | P0 | Pinned release and license register | Research review | Every selected component has revision, hash and intended-use disposition |
| M0-03 | P0 | 48-brief fixture set plus 12-brief smoke subset | Approved lyrics/references | Files and expected constraints are fixed before generation |
| M0-04 | P0 | ACE adapter | M0-01/02 | Native output + complete manifest on smoke subset |
| M0-05 | P0 | MiniMax adapter or documented substitute | CUDA hardware and terms | Same contract, complete smoke results; no false MPS assumption |
| M0-06 | P0 | Blind pilot and failure taxonomy | M0-03/04/05 | Fair-budget results, retained failures, cost and listener notes |
| M1-01 | P1 | Project/artifact/engine/job schemas | M0 findings | Validate real manifests and reject unsupported operations |
| M1-02 | P1 | Creator UX prototype from real audio | M0 outputs | Real audition, honest job states, accessible controls |
| V0-01 | P1, separate | VoiceStudio evaluation fork review card | Pinned upstream and terms | Concrete fork plan and intended backend; remains pinned until build authorization |
| V0-02 | P1, separate | Approved narration comparison | Source/voice permission and project contract | Local vs reference quality and accepted-hour cost recorded |

## 12. Opportunities the demos can obscure

**Control can be the advantage before average model quality is the advantage.** A song you can finish, revise and take into a DAW may be more valuable than a slightly better uneditable mix. Keep human performance, MIDI and generated parts first-class.

**A generation model is only one research axis.** Better reconstruction, alignment, selection, local repair and joint musical planning can produce different improvements. Benchmark them independently so a limiter’s louder result does not get credit as a better composer.

**The best hardware is a system.** Your Mac can offer a responsive studio while another machine renders a CUDA-only engine. The common project/job contracts make that possible without separate products.

**The voice opportunity can pay back sooner than a new music model.** Exact approved narration, consistent voices, resumable chapters and transparent finished-hour cost are smaller and more directly testable targets. Keep that project independent enough to serve Sabbath Echo and other authorized work without coupling release cycles.

**Personal taste is a data product.** A local preference memory can store genres, accepted takes and explicit reasons before any model tuning. Make preference changes editable and retain diversity; do not turn one accepted song into an irreversible style assumption.

**Preservation is a product promise.** Original dry audio, permissions, edits and manifests can give users confidence that their best material survives. It also makes failures and model upgrades diagnosable.

**Current tools move rapidly.** This sweep found new releases, restricted weights behind permissive code, primary assets with access failures and conflicting runtime instructions. Pin the initial stack, then admit updates through regression tests. “Latest” is not a reproducible engine.

## 13. Confirmed, refuted and unverified

| Proposition | Disposition | Consequence |
|---|---|---|
| ACE is the only viable route | Refuted by primary releases for independent full-song families | Use an adapter architecture and fair benchmark |
| Suno 5.5 is the current baseline | Superseded by official v6 documentation and supplied launch video | Test against a dated current reference |
| Suno regenerated stems are the same task as ordinary extraction | Refuted by Suno’s own June post; independently checked | Build and label separation/re-performance separately |
| Open application source grants commercial rights to all its models | Refuted by VoiceStudio and its default weight terms | Maintain component-level release/rights registry |
| Any 48 kHz/32-bit export implies that native generation fidelity | Unsupported; container and native-generation properties differ | Retain original rate and audit codec/output quality |
| A wrapper plus LoRA can guarantee broad Suno parity | Unverified, no controlled benchmark | Use staged ablations and no percentage completion claim |
| VoiceStudio replaces the full $25k production cost | Unverified, no billing/workload/quality pilot | Compare future cost per approved finished hour |
| Exact current Suno architecture is known | Unverified in inspected sources | Study open mechanisms without presenting speculation as discovery |
| This workspace contains a production music app | Refuted by initial filesystem inventory | Start at reproducibility and contracts |

## 14. Review contract for Claude and Kimi

Use the companion review packet. Ask reviewers to add evidence and challenge the shortlist, architecture, evaluation and cost assumptions. The most valuable contribution is a reproducer or primary source that changes a decision. Keep additions separate and reconcile them; do not silently replace this evidence baseline with another confident narrative.

Require four buckets: confirmed additions; corrections/refutations; hypotheses and experiments; unresolved questions. Each recommendation needs source/revision, licensing disposition, hardware assumptions, proposed test and effect on phase order. A screenshot or creator’s selected demo can inspire a test; it cannot close one.

We return to build after that reconciliation with a chosen first-use-case set and actual machine inventory. The first implementation should prove two engines and one honest project contract. Every later feature should earn its place through sound, control and reliability evidence.

## 15. Evidence and limits

Research date: October 8, 2026, America/Chicago. Evidence classes: current official product pages; official repositories/model cards/licenses and papers; fresh video metadata/captions/sampled frames; 11 retained user attachments; local host/filesystem checks; historical Sabbath Echo memory used only as context.

Not performed: local model inference, controlled listening tests, model training, primary-source invoice review, three-platform device QA, implementation, public release, repository fork or Sabbath Echo integration. Model output fidelity, local throughput and claimed parity remain unverified. Document QA checks readability, offline behavior and navigation; it does not validate these future product gates.

This v1 is a new independent plan. It does not overwrite Claude’s original answer or Kimi’s work. The companion appendices preserve the source depth and video-specific findings needed to revise it.
