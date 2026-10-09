# Music generation engines: current evidence and an engineering route

Research date: 8 October 2026. Scope: accessible full-song generators, architecture, release and license custody, hardware, evaluation, and escalation. This is a research module for the master plan, not a listening-test report or a build completion claim. No model was installed, no sample was generated, and no audio was auditioned during this research.

## Decision

Build a model-independent production studio and test several released generators before committing to a training program. ACE-Step is a useful speed/editing foundation, but it is demonstrably not the only route. MiniMax Music 3 is now a released CUDA quality challenger; YuE2 is a particularly relevant composition-first challenger for personal use or after company licensing; HeartMuLa supplies another architecture and a permissive base-weight lane. A claim that this system already matches Suno, or that a fixed “80% gap” has been measured, would be unsupported.

The September releases substantially change the options that older videos and advice describe. Treat “Suno 6.5” as the user's aspirational product quality target. The official Suno blog verifies v5.5 on 26 March 2026 and v6 on 9 September 2026; this research did not find an official v6.5 release. Define the target through audible and operational acceptance criteria rather than through an assumed future version number. [Suno blog](https://suno.com/blog)

## Current shortlist

All figures below are upstream-reported. Memory requirements depend on duration, batch size, precision, attention kernels, decoder, and loading strategy. Public code is not proof that every checkpoint, dataset, third-party component, and output has the same license.

| Engine | Release custody and hardware | Code / weights / data distinction | Useful role and limit |
|---|---|---|---|
| **ACE-Step 1.5, especially XL** | Official repo and weights available. XL 4B DiT variants released 2 April 2026. Upstream recommends at least 20GB VRAM without offload; 12GB with INT8 and CPU offload. Mac MLX/MPS, NVIDIA CUDA, AMD ROCm, Intel XPU and CPU paths are documented. | Repo MIT; XL SFT model card MIT. Authors describe licensed, public-domain/royalty-free and synthetic training sources; that statement is not an independently audited dataset release. | Fast drafts, full-song generation, covers/repaint, and base-model extraction/layering/completion. Different checkpoints expose different tasks; XL SFT/turbo do not automatically inherit every base task. Source: [repo](https://github.com/ace-step/ACE-Step-1.5), [XL SFT card](https://huggingface.co/ACE-Step/acestep-v15-xl-sft). |
| **MiniMax Music 3** | Official HF weight tree available, 57.4GB repository. Current model card documents CUDA, five-minute songs, non-streaming generation; current Diffusers instructions say 24GB+ with offload pathways below that. Original official GitHub recipe uses two CUDA GPUs. | Custom Community License covers software and weights, permits commercial use subject to UI attribution, safeguards, AUP and a revenue authorization threshold. No released training dataset was verified. | Quality challenger for complete lyric-conditioned songs. Hierarchical global/local LMs plus flow synthesis. Integration maturity must be tested: HF currently instructs installing a pinned Diffusers PR commit. Sources: [model card](https://huggingface.co/MiniMaxAI/MiniMax-Music3), [files](https://huggingface.co/MiniMaxAI/MiniMax-Music3/tree/main), [official repo](https://github.com/MiniMax-AI/MiniMax-Music3). |
| **YuE2, replacing YuE1 as current candidate** | September 2026 released inference package and YuE2-3B/VAE weights. Official supported starting point: Linux, Python 3.12, BF16 NVIDIA GPU, 24GB VRAM, one request at a time; 48kHz stereo. | Code/docs/skill Apache-2.0. Weights CC BY-NC 4.0 plus individual creator permission. Individual musicians can monetize outputs; commercial company use of weights needs separate licensing. | Editable melody/chord plans, full-song rendering, score edits and zero-shot covers. Score edits regenerate a full recording and do not preserve the unedited original waveform. Sources: [repo](https://github.com/multimodal-art-projection/YuE), [generation guide](https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md), [weight terms](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE). |
| **HeartMuLa released 3B family** | Released 3B “happy-new-year” checkpoint, HeartCodec and HeartTranscriptor. Repo defaults to 240-second generation. CUDA example supports model/codec split across GPUs or lazy loading. Approximately real-time inference is described as current; acceleration remains a TODO. | Repo and related base weights were updated to Apache-2.0 on 20 January 2026. Training-data release/provenance was not independently verified. | Diverse full-song generation, another useful singing/lyrics comparison, and Apache-licensed lyrics-transcription candidate. The headline parity claim refers to an **internal 7B model**; its public release remains a TODO. Sources: [repo](https://github.com/HeartMuLa/heartlib), [released 3B card](https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year). |
| **MuLaCover** | Public code and weights released 16 September 2026; Linux/NVIDIA. Tested configuration in repo is Ubuntu 24.04, PyTorch 2.10/CUDA 13 and B300. Lazy loading exists; consumer-card memory/latency was not verified. | Source Apache-2.0, but official weights **and generated outputs** are noncommercial under separate terms without written authorization. The base HeartMuLa Apache license does not carry across. | Research into MIDI/reference-song reinterpretation and composition-conditioned cover generation. Keep outside a commercial production dependency until rights are obtained. Sources: [repo](https://github.com/HeartMuLa/MuLaCover), [weight card](https://huggingface.co/HeartMuLa/MuLaCover). |
| **Stable Audio 3** | Released Small-Music/SFX 433M models: CPU, up to 120s. Released Medium 1.4B: CUDA, up to 380s. Large API-only. Optimized official routes include cross-platform CPU and Apple MLX. | Weight Community License and Gemma component terms; downloads gated. Code, weights, optimizations and training-source terms need separate records. Model card describes licensed AudioSparx plus filtered CC Freesound data. | Strong instrumental, individual-instrument, SFX, inpainting, continuation and LoRA specialist. Official guide explicitly says it is not intended for intelligible vocals. Sources: [repo](https://github.com/Stability-AI/stable-audio-3), [medium card](https://huggingface.co/stabilityai/stable-audio-3-medium), [prompt guide](https://kb.stability.ai/knowledge-base/stable-audio-3-prompt-guide). |
| **DiffRhythm 2** | Public code/weights released 30 October 2025. Semi-autoregressive block flow-matching route. Inference uses reference audio and lyrics; first-run weight downloads documented. | Official repo says code and weights Apache-2.0. Released training/encoder completeness should be checked per asset; do not assume the v1 minimum memory figure applies to v2. | Diversity/research challenger. Extension and instrumental features are listed TODOs. v1.2 remains a separate available editing/continuation model, but should not be confused with v2 capability. Sources: [v2 repo](https://github.com/ASLP-lab/DiffRhythm2), [v1 repo](https://github.com/ASLP-lab/DiffRhythm). |
| **Shao, formerly Khala** | Public repo/weight link; full pipeline recommends NVIDIA 24GB+ and the pinned NGC container. Authors explicitly warn alternative GPU/runtime stacks can produce severely degraded, noise-like output. | Repo describes weights as intended CC BY-NC 4.0. No independently verified commercial license. | Separate acoustic-token architecture research lane, not first production dependency. 64-layer RVQ, coarse generation followed by acoustic super-resolution. Source: [official repo](https://github.com/Shao-Music-AI/Shao). |
| **SongGeneration / LeVo 2** | Historical official card/search evidence describes v2-large. During this research official GitHub/API/raw README returned 404; Tencent HF returned 401. Public linked v2-large repository exists but its card contains only `license: unknown`. | Current license/release chain unresolved. Cached readme, forks and benchmark use are insufficient to clear production or redistribution rights. | Serious historical quality comparator and research architecture, but do not make it a production foundation until maintainers/current authoritative release reconcile access and terms. Sources: [official GitHub target](https://github.com/tencent-ailab/SongGeneration), [Tencent card target](https://huggingface.co/tencent/SongGeneration), [linked v2-large](https://huggingface.co/lglg666/SongGeneration-v2-large). |

### Three observations that change the build decision

1. **Sufficiently good released alternatives are broader than ACE.** YuE2's authors compare released weights with Suno v5/v6, MiniMax Music 3, HeartMuLa, LeVo and other public models. This makes a multi-engine trial justified. It does not make the authors' best-of-eight leaderboard equivalent to a single take in the user's genres. [YuE2 benchmark protocol](https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md)
2. **Licensing is an architectural input.** Personal experiments, an IDC-hosted product, a library embedded in Navigata1 and a monetized song are different acts. The studio should preserve asset/license provenance with each take, and the engine registry should expose permitted use modes instead of treating every public download as a commercial dependency. This is a proposed implementation response to the verified license distinctions above.
3. **One UI can span all three operating systems without every model doing so.** Use cross-platform browser/desktop clients; let Linux/CUDA workers host models with narrower support. ACE and Stable Audio offer plausible Mac/local options. MiniMax's autogenerated HF helper contains an irrelevant image example and a generic MPS comment; the actual model limitations say CUDA. It is not Mac compatibility evidence. [MiniMax actual model instructions](https://huggingface.co/MiniMaxAI/MiniMax-Music3)

MiniMax's controlling license requires prominent model naming in commercial product/service UI, prior written authorization above $20 million in aggregate annual revenue from covered products/services across the licensee and affiliates, and maintained safeguards for third-party generation services. This is materially different from a simple MIT weight grant. Its broad AUP and downstream obligations must be preserved in the engine manifest. [MiniMax weight license](https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE)

## What public research says about the hard engineering

This section describes known published systems, not Suno's undisclosed internals. Recreating a UI, copying exposed feature names or observing an output cannot identify a proprietary checkpoint, dataset, optimizer schedule, safety service or inference stack.

### 1. A song needs an explicit long-range representation

YuE2 uses an autoregressive/non-autoregressive Mixture-of-Transformers: text and lyrics produce an ABC melody/chord plan, semantic tokens, then flow-matched acoustic latents and stereo VAE decoding. Its main model has approximately 3.58B parameters and was trained on approximately 346,000 hours of music. The same checkpoint can render its own plan, a transcribed source composition or an edited plan. Authors report a matched comparison favoring planning over no planning, but published evidence is still upstream research. [YuE2 report](https://arxiv.org/html/2609.33757v1)

Engineering inference: give the user's project an inspectable composition object before the expensive render. It should carry form, bars, meter, tempo map, key/chord map, melody, syllable alignment, section arrangement, energy trajectory and voice role. Preserve it even when a provider cannot consume every field. This creates reproducible experiments and future editing leverage. Do not market a free-text BPM request as sample-accurate tempo control.

### 2. Acoustic rendering and structural planning are different bottlenecks

MiniMax Music 3 separates an 8B global LM from a 0.6B local LM. The global model predicts the first music codebook for long-range structure; the local model predicts the remaining codebooks. Fused continuous hidden states feed flow matching and a music-adapted Flow-VAE instead of relying only on hard discrete token decoding. Its reported native output is 32kHz, 16-bit stereo. [MiniMax architecture](https://github.com/MiniMax-AI/MiniMax-Music3)

Engineering inference: retain model-native audio for evaluation. Upsampling 32kHz to 48kHz changes the container, not the information captured. A clean 32kHz signal can outperform a flawed 48kHz one perceptually; a higher sample rate alone is not a quality ranking. The studio session can resample for mixing while retaining the original file and sample rate in provenance.

### 3. The codec/decoder can constrain every upstream improvement

MuSeC's September 2026 paper studies the tradeoff between high-fidelity reconstruction and token predictability. It proposes separating music semantic and acoustic information within a codec learned from mixed signals. The authors argue reconstruction-only tokens are difficult for LMs, while speech-centered semantic codecs can lose musical information. This is a paper/research lead here; this research did not verify deployable MuSeC weights or a commercial license. [MuSeC report](https://arxiv.org/html/2609.21240v1)

Engineering inference: before training any generator, run a codec reconstruction study on owned/reference-quality audio. Compare original versus encode/decode output for cymbals, transients, bass attacks, vocal sibilance, stereo image, quiet reverb tails and dense ensembles. If a decoder already removes detail, a better prompt or larger song planner cannot restore that exact lost information. Compare the same latent through candidate decoders where technically supported, rather than generating different songs and assigning the difference to the decoder.

### 4. Editing requires task supervision and a preservation contract

ACE's inference guide specifies that `lego`, `extract` and `complete` are base-model tasks. Cover, repaint and extract skip the LM; text generation, lego and completion can use it. Turbo guidance is distilled, so CFG is auto-corrected to 1; parameter widgets should not imply a CFG slider changes a turbo model. Audio output defaults to 48kHz. [ACE inference API](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md)

Engineering inference: an engine adapter must state whether an edit preserves waveform outside its mask, preserves composition statistically, or makes a completely new interpretation. Those are different promises. A proposed “replace one line” command should carry the original take, source interval, lyric phonemes, neighboring context, musical grid and a required preservation rule. Prove it through sample comparisons outside the edit region and seam listening. Never silently turn a local correction into a whole-song rerender.

### 5. Large-scale foundation training and small personalization are different investments

ACE's technical report describes pretraining using about 20 million pairs, a stem-enriched task curriculum and a curated high-quality SFT stage. It reports adversarial VAE training on 120 A100 GPUs, and distilled eight-step rendering. These describe the authors' foundation-development work, not the cost for a downstream LoRA or a measured requirement for this project. [ACE technical report](https://arxiv.org/html/2602.00744v1)

StepAudio 3 Music uses a 50Hz single-codebook semantic tokenizer, an MoE ABC planner, a flow-matching DiT and 48kHz audio. Its report describes more than five million hours and roughly one trillion corpus tokens, followed by expert-preference DPO. Official demonstrations and a provider-backed Space exist; this research did not verify downloadable StepAudio 3 Music weights. It is a hosted/paper architecture lead, not a local checkpoint promise. [StepAudio 3 report](https://arxiv.org/html/2609.16034v1), [official Voice AI Lab](https://audio.stepfun.ai/), [official Space README](https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music/blob/main/README.md?code=true)

Engineering inference: the realistic first advantage is targeted curation, workflow, evaluation and specialization on top of already-trained foundations. A new from-scratch foundation program would need a separate data, compute, scientific-team and financing decision. No credible exact parity budget can be derived from the user's screenshots or these papers.

## Hosted engines worth benchmarking through official interfaces

| Provider route | Verified public capability | Role and unresolved contract |
|---|---|---|
| **Mureka 9.5 API** | Official changelog dates 9.5 to 28 August 2026. Song endpoint supports structured lyrics, prompt, voice/reference controls and up to three outputs. Docs also expose extension, stems, complementary tracks, region edits and remix routes. | Useful hosted quality/feature baseline and optional premium fallback; browser subscription and API billing are separate. Paid API outputs have commercial authorization per FAQ. Record model explicitly rather than `auto`, which can drift. [changelog](https://platform.mureka.ai/docs/en/changelog.html), [song endpoint](https://platform.mureka.ai/docs/api/operations/post-v1-song-generate.html), [FAQ](https://platform.mureka.ai/docs/en/faq.html). |
| **Stable Audio 3 Large API** | Official asynchronous text/audio/inpaint routes, 44.1kHz stereo, duration field up to 380s, 26 credits per successful text generation in current docs. | Instrumental/SFX specialist. Six minutes in marketing is rounded; duration schema is the contract to implement. Dollar cost depends on current credit purchase terms and retries. [API reference](https://platform.stability.ai/docs/api-reference). |
| **StepAudio 3 Music** | Official Space describes create-song, instrumental, vocal arrangement and cover workflows using a backend API key and `step-music` submit/query protocol. | Quality/architecture challenger subject to official endpoint, geography, quota, privacy and current commercial terms verification. A public demo is not an SLA. [official Space](https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music/blob/main/README.md?code=true). |

Do not build the plan around third-party “Suno API” endpoints merely because they use the Suno name. An official model provider or a user-authorized manual import is a stronger custody route than a service that may depend on account automation, undocumented endpoints or short-lived access. This is a project strategy recommendation, not a claim that every third-party vendor is unlawful.

## Proposed multi-engine architecture

This is a design proposal. It has not been implemented in the workspace.

```text
Cross-platform studio client
  └─ project graph: musical intent, source takes, edit history, stems, plans
      └─ generation contract + capability/licensing registry
          ├─ draft worker: ACE turbo / XL turbo
          ├─ fidelity challengers: ACE XL SFT, MiniMax Music 3, HeartMuLa 3B
          ├─ composition lane: YuE2 when permitted
          ├─ instrumental/SFX lane: Stable Audio 3
          └─ optional official hosted provider lane
              └─ immutable native outputs → analysis → comparison → keeper approval
                  └─ stems / edit variants / human performance / mix / export
```

Every generation request should contain a request ID, requested operation, model/version/revision, recipe version, prompt, exact lyrics, reference hashes, seed, duration, engine-specific controls, quality tier, allowed providers and use classification. Every result should retain native audio, effective parameters, seed, timing, truncation flags, environment identity, license manifest and parent-take relationship. “Model changed” must be visible and recorded; a retry should not silently substitute another voice or model.

The registry should separately declare `text_to_song`, `instrumental`, `cover`, `inpaint`, `extend`, `native_stems`, `separate_stems`, `add_instrument`, `vocal_to_bgm`, `reference_voice`, `score_input`, `score_output`, `streaming`, `max_duration` and platform/runtime support. Do not infer `native_stems` from an extract feature. Do not infer a guaranteed voice identity from reference-audio style conditioning.

Use isolated environments or containers per engine; these projects depend on incompatible Python, CUDA, attention, diffusion and serving versions. A worker should be restartable, report readiness, reject unsupported jobs before loading models, enforce queue/VRAM limits, expose cancellation status and write results atomically. Schedule one loaded engine per constrained GPU initially. Keep non-generative project playback and editing responsive while workers compute. Run heavier CUDA workers on Linux and let all OS clients use the same job protocol.

## Making up the quality gap: proposed interventions in order

### First: find out which gap exists

The Fable “20% UI / 80% engine” formulation is a useful warning about difficulty, but there is no measured decomposition. Treat at least eight quality axes separately: composition; long-range arrangement; lyric correctness; singer identity/expressiveness; acoustic fidelity; controllability; edit preservation; latency/reliability. A narrow repertoire may reach a satisfying result much earlier than general parity. A faith-music workflow that needs accurate scriptural words, choir intelligibility and consistent narrators has different failure costs from generic background loops.

Build an owned evaluation set across the user's actual target uses. Suggested starting design: 40 briefs, four controlled seeds per eligible engine, short excerpts plus full-song listening. Cover sparse acoustic songs, dense choral/gospel music, synth-pop, cinematic instrumentals, spoken-word underscoring, difficult proper names, quiet endings, strong dynamic builds, unusual meters and long repeated choruses. These are **proposed test counts**, not an existing benchmark result. Retain all failures, silent outputs, truncations and rejected candidates.

Compare both equal-candidate budgets and equal-cost/time budgets. Log single-take quality, best-of-two quality and a separately priced best-of-eight tier. Normalize loudness for listening without modifying the archived native originals. Blind A/B/X presentation should hide model and order, collect audible reasons, track ties and confidence, and include representative experts and the user. Split prompt/train development cases from a held-out acceptance set.

### Second: improve inference before touching weights

Use each model's supported structured caption conventions; separate lyrics from arrangement instructions. Expand a brief into a validated composition specification, retain the exact expansion, and allow human edits. Sweep a small number of justified parameters against held-out prompts, then freeze recipes. Compare default versus high-quality checkpoints and decoders under controlled conditions. A slow SFT/base lane can serve keepers while a turbo lane supplies explorations.

Candidate reranking can reject hard failures and expose attractive takes, but optimization for one aesthetic scorer can hide lyric mistakes or reward generic polished outputs. Proposed reranking should combine objective hard constraints with diverse candidates and human choice: valid/non-silent audio, duration/truncation, lyric transcription agreement, rough section adherence and clipping checks first; aesthetic signals afterward. The best take should keep its full provenance and candidate budget.

### Third: use reconstruction and editing carefully

Postprocessing should fix a measured defect, not merely add loudness. Preserve the original; use mix-stage EQ, de-essing, dynamics, automation, gain staging and limiting with listening comparisons. Separating an already mixed song introduces its own artifacts; replacing a bad separated source with a performed or separately generated part may be more useful than repeatedly denoising it. Reverb removal, bandwidth extension and spectral repair cannot establish that authentic missing information was recovered.

For local edits, use source-aware models where available. Maintain protected regions and validate unchanged audio outside the edit plus overlap seams. Where a model only supports score-conditioned complete regeneration, label the result a new performance. If no available engine reliably repairs one word while preserving singer and accompaniment, the honest production fallback is human editing/performance, targeted voice synthesis after consent, or a selected alternative take—not a nonfunctional UI button.

### Fourth: specialize using owned data

Begin with adapters/LoRA on one permitted model and a coherent owned style/voice domain. ACE upstream describes small-song LoRA personalization; this is a way to specialize, not evidence that a few songs train a general Suno substitute. Separate singer adaptation, genre/instrument adaptation and decoder/domain adaptation experiments. Preserve train/validation/test splits by composition and performer; audio from the same song should not leak between them.

Create a data ledger for each recording: master and composition rights, performer consent and allowed voice uses, source and checksum, stem provenance, license, duration/sample rate, lyrics/phonemes/timestamps, tempo/meter/key/chords, section annotations, quality flags and exclusions. Owning a WAV file is not automatically permission to train on composition, lyrics or a performer's identity. For adaptations intended for distribution, keep the permission chain reviewable.

Commission clean original multitracks across target styles and languages; capture dry voices plus room/effect variants and paired stems/mixes. Label why takes succeed or fail. Improve language alignment and rare-word pronunciation separately from sonic mastering. If augmenting data synthetically, record the generator and terms; provider output-use permission alone may not permit training a competing model.

### Fifth: decide whether the foundation program is justified

Only after the strongest released/hosted baseline and specialization plateaus should the project consider continued pretraining, new control conditioning, a stem-aware foundation or a new codec. The decision packet should show reproducible shortcomings, why a smaller intervention failed, a rights-cleared dataset inventory, actual tokens/hour from a training pilot, memory/distributed-training measurements, checkpoint recovery, an evaluation holdout and a funded cap.

Use measured compute rather than a universal hardware quote. Proposed planning formulas:

```text
training hours = training tokens / (measured cluster tokens per second × 3600)
training cost = GPU count × paid GPU-hour rate × training hours
                + annotation + storage + preprocessing + failed runs + engineering

accepted-song cost = generation spend / accepted takes
                    + separation/edit/mastering spend + human curation time

serial best-of-k latency ≈ k × per-candidate generation time + judging time
```

Example only: at a measured 10-second render and serial best-of-eight, raw rendering already requires about 80 seconds before judging. That is arithmetic, not a claim that any candidate engine runs at ten seconds on the user's hardware. Parallelism changes latency, memory and cost together. Queue time and model warmup should be measured separately from steady-state generation.

## Proposed acceptance ladder

All workspace quality baselines are presently **unmeasured** in this module. Proposed numeric gates below are project requirements to validate, not achieved model claims; tune them after the first honest comparison.

| Dimension | Initial gate | Why it matters |
|---|---|---|
| Model integration | Each of three primary engines completes fixed smoke briefs; native audio, timing, config and failure flags retained | Demonstrates a real engine rather than a UI mockup |
| Comparative fidelity | Blind paired listener preference with confidence intervals and written artifact categories; report both single-take and selected-take results | No uncontrolled “sounds like Suno” claim |
| Lyrics | Human-verified reference plus transcription/phoneme error measures; no omitted or altered required sacred/proper-name phrase on accepted takes | ASR scores alone can miss consequential wording errors |
| Composition | Requested section order, tempo/meter and melody invariants checked where promised | Distinguishes generative suggestions from exact musical controls |
| Edit preservation | Unedited PCM regions byte-identical when contract promises it; seam audit and held-out edits passed | Prevents destructive whole-song changes |
| Reliable performance | p50/p95 warm/cold job latency, peak memory, queue time, cancellation and recovery recorded per duration/recipe/hardware | Operating systems alone do not specify compute performance |
| Quality economics | Cost per accepted minute and keeper yield compared with alternative models/provider tiers | A free checkpoint can be expensive to curate |
| Licensed use | Exact revision and component/license manifest; no unresolved restricted dependency in the chosen production mode | Makes personal and commercial reuse explicit |

## Adversarial findings for the master report

These findings were checked against direct primary text and, where access failed, direct unauthenticated requests. The parent should independently refute the load-bearing findings before incorporating them as confirmed verdict drivers.

| Finding | Severity | Attempted refutation and current disposition |
|---|---|---|
| “ACE is the only viable route” is false | High decision error | Released MiniMax Music 3 files and YuE2 generation/weight artifacts directly contradict exclusivity. **Confirmed as a release/access finding**, not a quality win in the user's repertoire. |
| “YuE2 is Apache, therefore IDC can ship its model commercially” is false | High | Repo has Apache code, but the actual separate MODEL_LICENSE restricts company commercial weights use and grants creator-specific permission. **Confirmed.** |
| “MuLaCover inherits HeartMuLa's commercial Apache permission” is false | High | Dedicated repo explicitly restricts official weights and generated outputs; weight card marks CC BY-NC. **Confirmed.** |
| “HeartMuLa 7B parity is a downloadable product” is unsupported | High decision error | Repo's strongest parity claim refers to the internal 7B model; TODO and CLI comments say 7B unreleased. **Confirmed release limitation.** |
| “Current MiniMax works on Mac because HF says switch to MPS” is unsupported | High | Autogenerated library helper is an image pipeline; actual card says CUDA and non-streaming. HF and GitHub also differ about GPU count. **Confirmed documentation mismatch; Mac feasibility unverified.** |
| “LeVo is immediately a safe production foundation” is unsupported | High | Canonical repo/API 404 and Tencent card 401; reachable v2-large card has unknown license. **Confirmed access/terms limitation on this date**, not proof of permanent removal or bad faith. |
| “Best-of-eight leaderboard means one generation universally beats Suno” is false | High | Protocol selects using a benchmark component and uses a special benchmark decoder. Other metrics and expert preference vary; study reports Suno v6 more overall preferences than YuE2 best-of-eight. **Confirmed protocol limitation.** |
| “Small LoRA can replace foundation pretraining” is unsupported | High financial/engineering error | ACE/YuE2/StepAudio disclose very different foundation scales. LoRA may solve narrow style adaptation but none of the reviewed sources establishes general parity from a handful of songs. **Confirmed distinction; exact training budget remains unverified.** |

## Evaluation and preprocessing license traps

SongPrep offers full-song structure/lyric transcription with timestamps, but its actual code/weight license permits academic use only and explicitly excludes production and commercial uses. Do not make it the deployed lyric evaluator simply because its Qwen base is Apache. [SongPrep license](https://github.com/tencent-ailab/SongPrep/blob/main/LICENSE)

SongEval provides five song-aesthetic dimensions, but its README says CC BY-NC-SA 4.0 while GitHub's license metadata shows Apache-2.0. Resolve the exact code, model and dataset terms before including it in a commercial scoring service. Use as research evidence with the limitation visible; for early product acceptance, human blind review and permitted transcription/signal-analysis tools can supply an independent path. [SongEval repo](https://github.com/ASLP-lab/SongEval)

The YuE2 study illustrates why evaluator reuse matters: best-of-eight selection includes SongBench Musicality; PER takes the lowest value across four ASR passes. Its benchmark decoder differs from the default listening decoder. Do not report its aggregate as a fresh local reproduction, or hide this selection budget when comparing with a provider's delivered pair. Small differences of reported means do not establish statistical superiority. [protocol](https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md)

## Source register

All URLs were accessed or explicitly attempted on 8 October 2026. Repo/model cards can change after this date. “Verified” here means publication/access/primary text was inspected; it does not mean model behavior, legal sufficiency or sonic quality was independently validated.

| ID | Primary source | Evidence class / scope |
|---|---|---|
| G01 | https://suno.com/blog | Current release dates and official v6 baseline |
| G02 | https://github.com/ace-step/ACE-Step-1.5 | Current model family, platforms, API/feature inventory |
| G03 | https://huggingface.co/ACE-Step/acestep-v15-xl-sft | XL checkpoint MIT metadata, hardware tiers, architecture, author data claims |
| G04 | https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md | Exact task/checkpoint boundaries and parameter behavior |
| G05 | https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/BENCHMARK.md | Wall-time/LM/DiT/VAE profiling method; example tables are illustrative |
| G06 | https://arxiv.org/html/2602.00744v1 | Foundation-scale data/curriculum and codec/distillation research |
| G07 | https://huggingface.co/MiniMaxAI/MiniMax-Music3 | Current supported inference, audio format and GPU instructions |
| G08 | https://huggingface.co/MiniMaxAI/MiniMax-Music3/tree/main | Actual public weight files and repository size |
| G09 | https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE | Actual Community License, commercial credit/revenue threshold/AUP requirements |
| G10 | https://github.com/MiniMax-AI/MiniMax-Music3 | Architecture and older two-GPU serving instructions |
| G11 | https://github.com/multimodal-art-projection/YuE | YuE2 current release replacing original v1 main branch |
| G12 | https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE | Actual weight vs individual/company rights |
| G13 | https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md | Hardware, one-candidate behavior, artifact custody, decoder/revision identity |
| G14 | https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md | 192-prompt scope, selection/decoder/evaluator differences |
| G15 | https://arxiv.org/html/2609.33757v1 | Symbolic architecture, training scale, expert listening counterevidence |
| G16 | https://github.com/HeartMuLa/heartlib | Released 3B vs unreleased internal 7B; codec/transcription and lazy-loading boundaries |
| G17 | https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year | Apache checkpoint metadata; no independent quality validation |
| G18 | https://github.com/HeartMuLa/MuLaCover | Dedicated September cover release, tested runtime, restrictive output terms |
| G19 | https://huggingface.co/HeartMuLa/MuLaCover | Public checkpoint files/checksums, CC BY-NC metadata |
| G20 | https://github.com/Stability-AI/stable-audio-3 | Models, hardware routes, duration, edit/training support |
| G21 | https://huggingface.co/stabilityai/stable-audio-3-medium | Gated Community/Gemma terms and detailed dataset statement |
| G22 | https://kb.stability.ai/knowledge-base/stable-audio-3-prompt-guide | Instrumental/intelligible-vocal boundary, inpaint/timbre transfer behavior |
| G23 | https://platform.stability.ai/docs/api-reference | Current async Stable Audio 3 API schema and per-generation credits |
| G24 | https://github.com/ASLP-lab/DiffRhythm2 | Released block-flow checkpoint/code and TODO limits |
| G25 | https://github.com/ASLP-lab/DiffRhythm | Separate v1.2/release/license and minimum-memory details |
| G26 | https://github.com/Shao-Music-AI/Shao | Rename, acoustic-token route, NGC/runtime quality warning, license intention |
| G27 | https://arxiv.org/abs/2605.01790 | Shao paper identity; originally called Khala |
| G28 | https://arxiv.org/html/2609.16034v1 | StepAudio 3 Music architecture/data/evaluation; does not establish released weights |
| G29 | https://audio.stepfun.ai/ | Official accessible product/demo |
| G30 | https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music/blob/main/README.md?code=true | Provider-backed Space, `step-music` submit/query path |
| G31 | https://arxiv.org/html/2609.21240v1 | MuSeC semantic/acoustic codec research lead; deployable assets not verified |
| G32 | https://platform.mureka.ai/docs/en/changelog.html | API model 9.5 dated 28 August 2026 |
| G33 | https://platform.mureka.ai/docs/api/operations/post-v1-song-generate.html | Song request contract, output count, voice/prompt controls |
| G34 | https://platform.mureka.ai/docs/en/faq.html | Paid API commercial output authorization and separate billing |
| G35 | https://github.com/tencent-ailab/SongGeneration | Direct target unavailable (404); no asserted reason |
| G36 | https://api.github.com/repos/tencent-ailab/SongGeneration | Direct unauthenticated API check returned 404 |
| G37 | https://huggingface.co/tencent/SongGeneration | Direct target unavailable (401); no authentication attempted |
| G38 | https://huggingface.co/lglg666/SongGeneration-v2-large | Accessible linked checkpoint; card says unknown license |
| G39 | https://github.com/tencent-ailab/SongPrep/blob/main/LICENSE | Academic-only, excludes commercial and production |
| G40 | https://github.com/ASLP-lab/SongEval | Useful dimensions and conflicting license presentation |

Preserve: the user's multi-platform flexibility, project ownership, ambitious sonic target, willingness to use multiple engines, and desire to have Claude/Kimi independently critique the plan. The next milestone should be a reproducible listening and editing comparison packet, not a claim of Suno parity based on a beautiful interface.
