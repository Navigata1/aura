# Voice, stems, and studio engineering research

Research date: **2026-10-08 (America/Chicago)**. Prepared as an evidence input for the Music Gen master plan. Research and engineering proposals only: no models downloaded, no app installed, no voice generated, and no repository forked. The linked video identified VoiceStudio; frame/transcript evidence belongs to the companion video analysis. Here, capabilities are verified against maintainers' documentation and model cards, not against a runtime on the user's machines.

## Verdict

The studio and narration opportunities are real. A strong local speech system is more attainable than a frontier full-song foundation model, while a useful music studio can be built around several interchangeable generation, separation, singing, and DSP engines. **Do not treat a polished shell, an open model license, or clean-sounding isolated stems as proof of Suno parity.** The fastest defensible route is a measured narration pilot and a capable audio editor, with full-song quality treated as a separate research program.

The important discovery is that Suno's current stem feature uses **generative reconstruction**, according to Suno itself. That changes the engineering target. A conventional separator extracts an estimate from an existing recording; a generative system can create a cleaner new performance with changed detail. These need different labels and different tests. [Suno's June 11, 2026 explanation](https://suno.com/blog/stem-separation-updates).

The user's reported **$25,000 ElevenLabs cost is a project-specific input, not an independently verified invoice or quote**. A local system may reduce provider spend, but savings cannot be calculated until the corpus, voice rights, actual characters, rejected takes, editorial labor, and required quality are known.

## 1. What VoiceStudio actually offers, and what the video cannot establish

The linked project is [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio). Its current documentation describes cloning, designed voices, timed dubbing, dictation/transcription, audiobook/batch workflows, optional remote workers, and local service integration. It publishes macOS, Windows, and Linux packages. CUDA is the documented acceleration route on NVIDIA Windows/Linux; Apple Silicon uses MPS. Intel Mac supports the UI with a remote backend, rather than a supported local backend. Current main uses Electron; Tauri is retired. These are maintainer claims and documented distribution paths, not results from our own test. [README](https://github.com/debpalash/VoiceStudio), [macOS guide](https://github.com/debpalash/VoiceStudio/blob/main/docs/install/macos.md).

The public GitHub commits API resolved main to `06c6e077f0fc35149efefc3561e9be5ae835d916`, committed **2026-10-07 13:18 UTC**, with merge message `release/0.5.7-final`. An evaluation should pin that revision or a chosen release; a video may show an older shell. [Exact revision](https://github.com/debpalash/VoiceStudio/commit/06c6e077f0fc35149efefc3561e9be5ae835d916).

The app is **AGPL-3.0-only**, with separate commercial licensing for proprietary embedding. Its license notice permits commercial and internal use of the application under AGPL, and explains the source-offer obligation when a modified app is made available over a network. App rights do not settle model rights. In particular, the default **k2-fsa/OmniVoice pretrained weights are CC-BY-NC**, with separate tokenizer terms. The notice says its initial model inventory does not establish commercial clearance. This is a concrete dependency decision, not a reason to abandon personal evaluation. [VoiceStudio license notice](https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md), [OmniVoice model card](https://huggingface.co/k2-fsa/OmniVoice).

VoiceStudio's benchmark page currently contains **no verified result rows**. Its performance guide has useful profiling advice, but a model's published low latency and an app's supported device are not measurements on an M5 Pro. [Benchmark page](https://github.com/debpalash/VoiceStudio/blob/main/docs/benchmarks.md), [performance guide](https://github.com/debpalash/VoiceStudio/blob/main/docs/performance.md).

**Recommendation:** pin VoiceStudio for personal evaluation in the separate narration lane. Keep app/model terms visible in a future fork. Before proprietary embedding choose AGPL compliance, negotiated embedding/hosting terms, or an independently built shell around licensed engines.

The video's narration and visible pricing slide disagree on billing period. Current vendor pricing resolves that to **$99 per user/year**, or **$299 one-time Lifetime**, each advertising three registered devices/concurrent uses. Crucially, the same page says **closed-source distribution and private hosting are not included in Pro/Lifetime**; those need separately negotiated terms. Buying Pro does not clear noncommercial model weights. Several advertised future features are marked upcoming. This is a checked current price, not a purchase or a recommendation to buy. [Vendor Pro page](https://voicestudio.sh/pro).

## 2. Speech models worth a controlled audition

These are speech engines. Their ability to clone a speaking voice does not establish controllable, convincing singing or Suno-style whole-song composition. The table records released capabilities and upstream license metadata; it does not claim that all training rights have been audited or that the output will meet the user's quality target.

| Candidate | Verified release/capability | Code / selected weight terms | Recommended role and unresolved work |
|---|---|---|---|
| **Qwen3-TTS** | Official 12Hz family released Jan 22, 2026; 0.6B and 1.7B Base cloning models, 1.7B VoiceDesign, CustomVoice variants; ten advertised languages. Base uses reference audio plus transcript; a reusable voice prompt is supported. | Repo Apache-2.0; selected 1.7B Base card Apache-2.0. | First audition for reusable narrator identity and designed characters. Verify MPS/MLX integration separately; official examples use CUDA. Do not copy its advertised minimum latency into product promises. [Code](https://github.com/QwenLM/Qwen3-TTS), [Base model](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base). |
| **Chatterbox / Turbo / Nano** | Current repo has original, multilingual, Turbo and Nano examples. Turbo is a 350M English engine with paralinguistic tags; original has expressive controls; multilingual advertises 23+ languages. Original has an official Mac MPS example. | Repo MIT; Turbo card MIT. | English narration and an efficient comparison voice. Test the exact engine on Mac rather than assuming the original's Mac example validates Turbo/Nano. Preserve the intended watermark path. [Repo](https://github.com/resemble-ai/chatterbox), [Turbo card](https://huggingface.co/ResembleAI/chatterbox-turbo), [Mac example](https://github.com/resemble-ai/chatterbox/blob/master/example_for_mac.py). |
| **CosyVoice 3, 0.5B-2512** | Official release, cross-lingual cloning, instruction control and bi-streaming; pronunciation inpainting for English CMU phonemes and Chinese pinyin is particularly relevant. | Repo and selected model card Apache-2.0. | Strong second audition for difficult names and repeatable pronunciation; evaluate local deployment and dependency footprint. [Repo](https://github.com/QwenAudio/CosyVoice), [model card](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512). |
| **Kokoro-82M** | Small released TTS model with supplied voices and a documented pipeline. | Model card Apache-2.0. | Low-resource baseline and ordinary narration; not evidence of arbitrary zero-shot voice cloning. [Model card](https://huggingface.co/hexgrad/Kokoro-82M). |
| **F5-TTS** | Official flow-matching TTS implementation and checkpoints. | Code MIT; official pretrained models CC-BY-NC because of training-data constraints. | Research comparison or properly licensed retraining; do not silently bundle official weights into a commercial service. [Official repo](https://github.com/SWivid/F5-TTS), [paper](https://arxiv.org/abs/2410.06885). |
| **Fish Audio S2-Pro** | Current canonical Fish Speech repo is S2-Pro, a 4B system with fine-grained tags and multi-speaker support; published performance is on an H200. | Current code and weights use Fish Audio Research License; commercial purpose requires a separate written license. | Quality reference and possible licensed worker. Legacy OpenAudio S1 guidance and an Apache-code assumption are stale for current main. Internal organizational operations can fall within its commercial definition. [Canonical repo](https://github.com/fishaudio/fish-speech), [license](https://github.com/fishaudio/fish-speech/blob/main/LICENSE), [technical report](https://arxiv.org/abs/2603.08823). |
| **OmniVoice** | Released ~0.6B model; diffusion-language-model approach; 646-language metadata, cloning, voice design and pronunciation controls. | Code Apache-2.0; pretrained model CC-BY-NC. | Personal/research breadth comparison, not a automatically cleared commercial default. Language count is availability metadata, not uniform quality across 646 languages. [Model card](https://huggingface.co/k2-fsa/OmniVoice). |
| **VibeVoice Realtime 0.5B** | Official Microsoft streaming TTS release advertises around ten-minute single-speaker generation, primarily English. Repo records removal/disablement of the earlier 1.5B TTS path. | Selected card metadata says MIT, while its responsible-use body limits intended use to research and discourages real-world/commercial deployment without development/testing. Resolve that discrepancy before production adoption. | Optional research/latency audition, not a cleared default. Do not plan around the old 90-minute 1.5B demonstration as a currently supported official route. [Official repo](https://github.com/microsoft/VibeVoice), [selected model card](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B). |

### A reusable narrator is a managed asset

Proposed architecture: `voice_id` refers to a versioned bundle of authorized references, transcript, language/accent, style defaults, pronunciation dictionary, consent record and engine-specific embedding/prompt. Keep the clean recording as the source of truth; a serialized embedding alone ties the asset to one encoder/model revision. Record every render's model hash, settings, text revision and reference hash. Permit cached prompts to improve throughput, but invalidate them when the reference or encoder changes.

A designed voice can be sampled and then reused as a stable reference. Qwen documents this workflow. It is useful for original characters, but each audition still needs tests for drift across paragraphs, emotional styles and languages. Speaker similarity metrics can miss perceived age, breath texture, vowels and fatigue. [Qwen workflow](https://github.com/QwenLM/Qwen3-TTS).

### The production text layer is as valuable as the speech model

Build an engine-neutral script format that preserves original text, pronunciation overrides, pauses, emphasis, speaker changes, section IDs and desired timing. Compile it into each engine's supported controls. Do not promise universal SSML: even current ElevenLabs documentation distinguishes models and says newer v3/v4 do not support SSML break tags, while dictionary/IPA behavior differs. [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices), [pronunciation dictionaries](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/pronunciation-dictionaries).

For names, preserve the human-readable text and apply a separate spoken-form alias or phoneme field. Never mutate the displayed canonical corpus merely to make a model pronounce it. A chapter should remain identical to its approved source even when the synthesis input uses an approved phonetic rendering. Render previews for difficult names before a large batch; key cached lines by text plus dictionary version.

## 3. Sabbath Echo opportunity: a separate narration service

Historical memory contains an explicit project boundary: Bible Brain supplied Scripture audio; TTS was limited to authorized EGW narration, with a “never TTS Scripture” rule. That boundary is **memory-derived and not revalidated against the current repository in this task**. Preserve it unless the current owner-governed scope changes. This research does not authorize use of any protected corpus, voice, or translation. The new service can support authorized narration, original reflections, user-written material and other cleared texts without changing Scripture delivery.

Build narration as a detachable service consumed by Sabbath Echo and Music Gen, rather than welding religious content into the music engine. The user wants to pin this opportunity for a later Navigata1 fork; no fork is performed during this research pass.

Proposed pipeline:

1. Ingest an approved source manifest with text version, book/chapter/paragraph ID, rights status and language. Hash the original text and preserve its provenance.
2. Select a consented or originally designed voice profile. Specify what is permitted: narration, singing, languages, public distribution, training and duration. Those permissions can differ.
3. Normalize synthesis text deterministically. Expand dates, abbreviations and references according to an approved reading style; maintain original display text and an auditable mapping.
4. Split at semantic boundaries. Keep enough context for prosody; persist paragraph and line IDs. Avoid cuts inside names, quotations or sentence clauses. Render multiple sentences where quality benefits, then align the output back to the text.
5. Run a bounded candidate policy. Retry only the failed paragraph, not an entire chapter. Store rejected audio for analysis separately from approved distribution assets.
6. Compare ASR against the intended text, flag omitted/repeated words, align timestamps, and listen to named edge cases. ASR is a review aid, not proof that every word was spoken correctly.
7. Assemble with intentional pauses and short edit crossfades, while retaining breaths and sentence endings. Normalize playback loudness after selection. Preserve a high-quality master and derive mobile/offline files separately.
8. Produce a content-addressed audio manifest: chapter checksum, duration, engine/model/voice/dictionary revisions, source hash, word/paragraph timestamps, reviewer status and license/consent snapshot.
9. Publish only reviewed chapters through the existing approved distribution route. Check interrupted playback/resume, continuous chapter transitions, airplane-mode cache, and alignment on physical devices before calling it ready.

Longform output can fail subtly: one omitted negation can change meaning, successive chunks can change character, and a 500ms unintended pause can impair comprehension. Budget editorial listening and text integrity from the start. Cheap retries make local generation economically attractive, but they do not remove review costs.

### Proposed pilot gate, before bulk rendering

The following are **targets, not measured baselines**. Start with 60 approved passages: 20 ordinary narration, 20 difficult names/numbers/quotations, and 20 emotional/long-sentence or mixed-format edge cases. Include short clips and ten-minute assembled sessions. Compare the same texts, consented voice assets, loudness and format across Qwen, Chatterbox, CosyVoice and a Kokoro baseline; if commercial model use is not cleared, use permissible personal evaluation or obtain clearance first.

| Dimension | Proposed acceptance evidence |
|---|---|
| Text integrity | No omitted/repeated meaningful words in human-reviewed accepted outputs; ASR discrepancies reviewed rather than automatically accepted. |
| Pronunciation | A frozen difficult-name list with each name manually approved in context, plus a dictionary regression audition after changes. |
| Identity | Blind listening across paragraph starts/ends and emotionally different passages; no obvious unintended narrator changes. |
| Longform | Ten-minute assembly without clipped syllables, missing endings, audible chunk seams or persistent voice drift. |
| Quality | Loudness-matched blind preferences and defect tags; report per-passage outcomes and confidence rather than one marketing MOS. |
| Throughput | Warm and cold time, RTF, first audible latency where applicable, peak memory, audio seconds per successful job, retries and review minutes. |
| Reliability | Crash/interruption resume, deterministic asset custody, cancellation that does not corrupt accepted work, and rerender of only invalidated paragraphs. |
| Delivery | Per-chapter manifests and timestamps validated on existing player routes; physical/offline evidence remains distinct from local generation. |

## 4. Why clean Suno stems require two engineering lanes

Suno says its current process regenerates each stem from scratch using its latest model. It advertises automatic separation into up to 12 stems, plus selection from nearly 100 instrument types, with some fine-grained cases still improving. That is a vendor account of behavior; it does not reveal the network, training data, exact conditioning signals or quantitative fidelity. [Suno stem update](https://suno.com/blog/stem-separation-updates).

Conventional source separation solves an inverse problem: a mix contains overlapping sources, reverberation and nonlinear processing, and the original multitrack generally cannot be recovered uniquely. A separator can estimate vocals, drums, bass or other parts, but bleed, smeared transients, phase issues and hallucinated harmonics remain possible. A generative reconstruction can reduce those artifacts by synthesizing a plausible replacement; it can also change fingering, timing, timbre and articulation.

Offer explicit operations:

| Operation | Contract | Appropriate tests |
|---|---|---|
| **Extract original part** | Estimate the source performance from the mix; preserve musical detail as far as the model permits. | Reference-stem comparison where licensed multitracks exist, bleed, transient detail, stereo stability, sum-to-mixture residual and blind listening. |
| **Re-perform this part** | Synthesize a cleaner new performance conditioned on the selected instrument and source music. | Melody/onset/harmony fidelity, section timing, character consistency, audible quality, edit usefulness and disclosed difference from the source. |
| **Generate a new part** | Compose new content compatible with the surrounding arrangement. | Beat/key/chord compatibility, user control, independence of existing parts and cross-boundary continuity. |

A stem-native generator is a further possibility: generate coordinated sources as separate tracks before summing. Independent generation per instrument does not automatically coordinate groove, harmony, acoustic space or arrangement. Joint conditioning, a shared structure/beat plan, and synchronized latent timing are necessary research directions. This is a proposed design, not a claim that Suno publicly uses stem-native generation.

### Separation shortlist

| Tool/family | Grounded capability | Engineering disposition |
|---|---|---|
| **Hybrid Transformer Demucs** | Official music separator with published checkpoints. Original Meta repository archived Jan 1, 2025. | Reproducible baseline, not the only route or an actively maintained product commitment. Pin code/checkpoint; evaluate separately on generated mixes. [Repo](https://github.com/facebookresearch/demucs). |
| **BS-RoFormer** | Research uses band splitting and RoPE transformers for music source separation. A well-known independent implementation is MIT licensed, but code terms do not license every third-party checkpoint. | Audition a provenance-verified vocal/instrument checkpoint; do not mix mirror downloads and assume inherited commercial rights. [Paper](https://arxiv.org/abs/2309.02612), [implementation](https://github.com/lucidrains/BS-RoFormer). |
| **SCNet** | Official sparse-compression separator with released MUSDB-trained checkpoint and a large variant; repo MIT. | Candidate for speed/quality balance, with checkpoint and data-use review. Separate architecture availability from permission to ship a specific weight file. [Repo](https://github.com/starrytong/SCNet), [paper](https://arxiv.org/abs/2401.13276). |
| **SAM Audio** | Meta released text/visual/time-span conditioned target-plus-residual separation. CUDA recommended; checkpoints gated; reranking increases memory and latency. Custom SAM License applies. | Valuable prompt-selected instrument/sound lane. Measure faithfulness; it is not proof of 100-instrument Suno parity or exact multitrack recovery. [Repo](https://github.com/facebookresearch/sam-audio), [paper](https://arxiv.org/abs/2512.18099), [license](https://github.com/facebookresearch/sam-audio/blob/main/LICENSE). |

For any chosen separator, record clip length, overlap, normalization, channel handling and resampling. Chunked inference needs overlap-add and tests for seam artifacts. Stereo channels should remain coherently related; independently processing left/right can shift image and phase. Store source, estimated stems and residual, not just polished output.

Do not judge extraction only by how attractive the solo sounds. A clean solo part may omit something important. Listen to the stem, the residual, and the reconstructed mix. Conversely, sum-to-mixture agreement can be artificially enforced while a separator assigns wrong instruments; it is one test, not the complete quality objective.

## 5. Singing consistency: three distinct products

**A stable singer inside a full-song generator** requires singer conditioning, training data that covers singing registers and articulations, long-range identity control and a quality model that catches timbre drift. A speech clone is an input candidate, not sufficient evidence. The user might value a named singer across many songs; that should be an explicit evaluation set covering low/high register, quiet/belted lines, harmonies and long songs.

**Score-to-singing** is a controllable route for original music: note pitches, durations, phonemes, lyric-to-note mapping, phrase boundaries and expressive curves feed a singing synthesizer. OpenVPI's maintained DiffSinger supports 44.1kHz synthesis and variance controls such as pitch, energy and breathiness, with Apache-2.0 code. Voicebanks and recordings have their own permissions. This can give far better note-level control than hoping a full-song prompt chooses the correct melody, while requiring score preparation and a suitable singer bank. [OpenVPI DiffSinger](https://github.com/openvpi/DiffSinger).

**Singing voice conversion** transforms an existing sung performance into an authorized target timbre. RVC is a candidate, with MIT code, retrieval-based conversion and F0 extraction. It does not compose the song or turn ordinary speech into a perfectly performed score. The source singer's timing and expression remain load-bearing; strong source separation, pitch handling and voicebank provenance matter. [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI).

Recommended studio sequence: keep a full-song generation lane for ideation; add editable symbolic notes and a consented score-to-singing lane for predictable melodies; add voice conversion only as an auditioned optional operation. Do not equate these workflows with a universally cloned Suno persona.

## 6. MIDI and temporal alignment

Suno Studio 2.0 publicly supports MIDI import/record/edit, a wavetable synth, MIDI as a generation prompt, audio effects including sidechain compression and convolution reverb, automation, and 32-bit/48kHz exports for Premier. The engineering work includes transport, editing, DSP and asset handling in addition to generation. [Suno Studio 2.0, Aug 13, 2026](https://suno.com/blog/studio-2).

Spotify's Basic Pitch outputs MIDI and pitch bends and works best on one instrument at a time. That suggests a useful separation → transcription → piano-roll correction flow, not a perfect mixed-song score extractor. [Basic Pitch](https://github.com/spotify/basic-pitch).

Proposed timeline representation:

- Use integer sample positions for audio and musical ticks/beat positions for score events. Maintain a versioned tempo/time-signature map to convert between them.
- Store detected beat/downbeat and key/chord candidates with confidence, then allow manual correction; variable-tempo music and weak percussion cannot be assumed to lie on a perfect grid.
- Preserve original performance offset separately from quantized note placement. Quantization should be reversible and local.
- Represent lyric alignment at word and phoneme level when supported, with note spans and melisma explicitly modeled. A syllable stretched over three notes is not three repeated words.
- Let MIDI-conditioned generation advertise a tolerance rather than exact obedience until measured. Test melody preservation, note onset timing, rhythm and lyric alignment separately.
- Maintain edit history: source take, extracted MIDI, corrected MIDI, regenerated audio and selected take remain distinct assets.

## 7. Mix/master quality and cross-platform audio

The user has Linux, Windows and Mac. The local host is reported by the parent research as **M5 Pro with 48GiB unified memory**; Windows/Linux GPU, RAM and audio-interface specifications remain unknown. This is enough to justify a Mac pilot, not a universal render-speed promise. Multiple operating systems help testing and deployment; they do not add together automatically into one GPU.

Proposed architecture has two clocks and two engines. The real-time audio engine owns sample scheduling, monitoring, effects and device I/O. Background workers own generation, transcription, separation, denoising and heavy export. Never execute blocking inference, disk reads, network calls or unbounded allocations in the audio callback. UI updates consume summarized meter/transport data; they do not clock playback.

For a browser studio, use AudioWorklet for custom real-time DSP and the audio clock for scheduling. A Web Audio latency hint is at the browser's discretion; measure actual latency and device behavior. Importing/resampling into a browser can change latency. [W3C Web Audio API](https://www.w3.org/TR/webaudio-1.0/).

For a desktop engine, JUCE offers established device and plugin abstractions but current modules are dual licensed AGPL/commercial. Its APIs expose input/output latency and overruns. CPAL is a lower-level Rust Apache-2.0 option with CoreAudio on macOS, WASAPI/optional ASIO on Windows, and ALSA plus optional PipeWire/JACK/PulseAudio on Linux. A permissive I/O layer still leaves an audio graph, DSP, plugin isolation and DAW semantics to build. [JUCE license](https://github.com/juce-framework/JUCE/blob/master/LICENSE.md), [device API](https://docs.juce.com/master/classjuce_1_1AudioIODevice.html), [CPAL](https://github.com/RustAudio/cpal).

Start with gain/pan, trim/fades, metering, EQ, compressor, limiter, sends/buses, sidechain routing, convolution reverb and automation. Add plugin hosting only after the core graph survives device changes and offline rendering. Treat each plugin process or generated DSP script as potentially faulty: bound resources, retain crash recovery and audition at a safe level. Generated plugin code is a software feature with compilation/runtime/ear-safety requirements, not merely an LLM chat response.

Tempo/pitch adjustment needs quality and license selection. Rubber Band supports independent time and pitch changes but proprietary distribution requires its commercial license under the published GPL/commercial terms. SoundTouch is another audition candidate. Do not choose solely from a toy stretch demo; test drums, sustained strings, vocals, stereo reverbs and extreme ratios. [Rubber Band](https://breakfastquay.com/rubberband/), [SoundTouch](https://www.surina.net/soundtouch/).

Speech cleanup can use a separate enhancement path such as DeepFilterNet, which targets 48kHz speech and has MIT/Apache code. A speech denoiser should not be globally applied to music: it may suppress intended instrumental textures. [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet).

**Engineering inference:** mastering cannot recover missing performance detail or solve lyric errors. EQ/compression, clipping control and careful export can improve a good render, but aggressive limiting or generative enhancement can conceal defects and change material. Quality should be measured before and after every enhancement stage. A 32-bit/48kHz container does not prove 32 bits of source precision or restore a model's discarded bandwidth.

### Proposed audio-engine gates

These numbers are engineering test targets, not measured performance or externally established Suno specifications:

- Begin at 48kHz sessions with 256-frame buffers; one block is `256 / 48000 = 5.33ms`. Input/output hardware buffering, converter delay and effects add to that value.
- Measure round-trip latency with wired loopback separately from generated-audio TTFA. Bluetooth monitoring has a different latency profile and must be reported separately.
- Test 16 audio tracks, routine inserts, automation and scrubbing for 30 minutes without callback overruns on each intended platform/device. Expand load only after the minimum works; state the measured ceiling.
- Test mixed sample-rate imports, device disconnect/reconnect, sleep/wake, missing assets, project reload and a canceled export.
- Compare real-time and offline output where the DSP is deterministic. Account for intended nondeterministic reverb/noise rather than declaring every sample mismatch a failure.
- Export master plus multitracks with correct sample rate, frame count, channel order, metadata and bounded true peak. Retain 32-bit float for intermediate processing and apply appropriate dither only when reducing integer bit depth.

## 8. Cost model: count accepted output, not raw generation

Use `accepted audio hours` as the denominator. Track engine warm/cold times and repeated attempts; a fast model with many defects can be more expensive than a slower model that is accepted on the first pass. Separately report first-audio latency, completed-render latency and batch throughput; these are different product experiences.

Define:

```
A = final accepted audio hours
r = measured real-time factor = compute seconds / generated audio seconds
m = generated audio hours / accepted audio hours, including rejected takes
c = compute price per active hour (or local hardware allocation)
e = measured electrical kW while running; p = price per kWh
h = editorial/review hours; w = review hourly cost
F = acquisition, consent, engineering, hardware and licensing costs allocated to corpus

compute_hours = A * r * m
local_energy_cost = A * r * m * e * p
total_local_cost = F + compute_hours * c + local_energy_cost + h * w + storage/ops
cost_per_accepted_hour = total_local_cost / A
```

For a cloud worker, do not double count energy if it is included in `c`. For local hardware, choose explicitly whether `c` is depreciation, opportunity cost or zero incremental cash; those answer different questions.

**Arithmetic illustration only:** 1,000 final minutes is 16.667 hours. If a future measured RTF were 0.5 and generated/accepted ratio were 1.5, inference would consume 12.5 active compute hours. This is not a benchmark on the user's machines, and it excludes review, model startup, transfers, idle billing and rights costs. It shows why corpus size alone cannot substantiate a $25k saving.

For hosted TTS, compare the actual selected plan/model, billed character or audio units, voice multipliers, rerenders and batch output requirements. ElevenLabs documents model-dependent credit conversion and custom voice multipliers; the user's historical spend cannot be reconstructed from a generic monthly plan. [ElevenLabs credits](https://help.elevenlabs.io/hc/en-us/articles/27562020846481-What-are-credits), [voice multipliers](https://help.elevenlabs.io/hc/en-us/articles/26050485079057-What-are-custom-rates-and-credit-multipliers).

## 9. Prioritized implementation program

| Priority | Deliverable | Why it precedes the next step | Exit evidence |
|---|---|---|---|
| **P0 — asset and evaluation contracts** | Frozen voice/text permissions, model/license manifest, blind test corpus, track provenance labels and per-job metrics schema. | Prevents investing in an unusable default or optimizing an irrelevant benchmark. | Selected artifacts/model revisions identified; test corpus and review rubric executable. |
| **P0 — Mac narration audition** | Qwen3-TTS, Chatterbox, CosyVoice and Kokoro comparison on the existing Mac, using permitted voices/text. | Establishes whether narration is the first realistic high-value win. | Accepted samples, defect register, warm/cold memory/RTF/TTFA, reproducible runtime versions; no parity claimed from docs. |
| **P1 — resumable narration service** | Script compiler, voice profile registry, per-paragraph cache, retries, alignment, manifests and review UI. | Makes bulk audio economical and repeatable instead of manual copy-paste. | Failed paragraph-only regeneration, crash resume and approved ten-minute assembly. |
| **P1 — studio transport and basic mixing** | Non-destructive clips, routing, effects, automation, meters and multitrack export around existing generation workers. | Useful on day one even while generation quality improves. | Platform/device load tests, real/offline export verification and project recovery. |
| **P2 — faithful extraction** | Demucs baseline versus audited BS-RoFormer/SCNet/SAM Audio candidates. | Gives measurable stem utility before proposing generative reconstruction. | Licensed multitrack test set, mixture/residual results, blind solo/remix comparisons. |
| **P2 — controlled singer** | OpenVPI DiffSinger voicebank pilot and optional authorized RVC comparison. | Tests note/lyric/identity control independently of full-song composition. | Pitch/duration fidelity plus listening across registers/styles; clean rights manifest. |
| **P3 — generative re-performance** | Instrument-conditioned reconstructions synchronized to source/score and arrangement. | This is a closer functional analogue to Suno's described clean stems. | Source fidelity and quality tradeoffs reported; operation visibly distinguished from extraction. |
| **P3 — narration integration** | Approved Sabbath Echo route integration and separate future Navigata1 fork decision. | Bulk generation only helps if approved assets work in the real app and honor existing corpus policy. | Owner-governed scope, review manifest, real device/offline route evidence. |

No calendar duration is claimed from documentation. A two-week starting board can reasonably contain the contract/schema, candidate environment setup, a limited audition and a first comparison register; production narration and DAW quality remain gated by observed results.

## 10. Independent refutation register

| Hypothesis to challenge | Refutation attempt / surviving conclusion | Confidence |
|---|---|---|
| VoiceStudio is a free commercial ElevenLabs replacement. | Application and model terms inspected independently; app freedoms do not automatically cover weights. See section 1. | **Confirmed documentation finding**, runtime untested. |
| Fish Speech current main has Apache code and OpenAudio S1 weights. | Canonical current main names S2-Pro and Fish Audio Research License for both code/weights. Legacy guidance cannot drive implementation. | **Confirmed current-source correction**. |
| Demucs can reproduce Suno's clean stems. | Suno says stems are regenerated from scratch. Extraction and re-performance are different tasks. No published evidence that Demucs alone implements that contract. | **Confirmed scope mismatch**, actual comparative quality unmeasured. |
| A local speech clone solves singing personas. | Official speech model capabilities do not establish score/lyric/pitch control or singing identity. DiffSinger and VC provide separate workflows with distinct inputs. | **Unverified parity claim rejected**. |
| 48GiB unified memory guarantees fast frontier audio. | Model fit, operator backend, precision, context length and concurrency affect memory and speed. No VoiceStudio verified benchmark rows; no runtime test performed. | **Unverified speed claim rejected**. |
| 32-bit/48kHz exports establish higher sonic fidelity. | Container precision/sample rate and source information are different quantities. Upsampling and float export cannot recreate information absent from generated audio. | **Engineering distinction**, source comparisons still required. |
| Local models will save precisely $25k. | User's project cost is not independently verified and cost inputs/review burden unknown. A pilot must establish cost per accepted hour. | **Unverified savings claim rejected**. |

## Primary-source register

All web sources below were inspected on **2026-10-08**. Dates in names or statements are publication/release dates; current `main` URLs can change. Capability statements remain claims by their authors unless runtime evidence is explicitly recorded.

| ID | Primary source | Evidence used |
|---|---|---|
| VS-01 | [VoiceStudio README](https://github.com/debpalash/VoiceStudio) | Platform packaging, engine shell, Electron transition. |
| VS-02 | [VoiceStudio license notice](https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md) | AGPL application scope, proprietary licensing, separate model/tokenizer rights. |
| VS-03 | [VoiceStudio benchmark page](https://github.com/debpalash/VoiceStudio/blob/main/docs/benchmarks.md) | No verified rows, measurement schema. |
| VS-04 | [VoiceStudio performance guide](https://github.com/debpalash/VoiceStudio/blob/main/docs/performance.md) | Stage profiling, reference transcript caching advice; not extrapolated to M5. |
| VS-05 | [VoiceStudio macOS guide](https://github.com/debpalash/VoiceStudio/blob/main/docs/install/macos.md) | Current Electron shell, Intel Mac local-backend limitation. |
| VS-06 | [VoiceStudio main API snapshot](https://api.github.com/repos/debpalash/VoiceStudio/commits/main) | SHA and Oct 7, 2026 commit timestamp; use immutable linked commit for future evaluation. |
| VS-07 | [VoiceStudio Pro page](https://voicestudio.sh/pro) | Current per-year/one-time price; standard seats do not include private hosting/proprietary distribution. |
| TT-01 | [Qwen3-TTS repo](https://github.com/QwenLM/Qwen3-TTS) | Released family, reusable prompts, designed-voice reuse. |
| TT-02 | [Qwen selected Base card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) | Selected weight license metadata. |
| TT-03 | [Chatterbox repo](https://github.com/resemble-ai/chatterbox) | Current engine variants, MIT code. |
| TT-04 | [Turbo card](https://huggingface.co/ResembleAI/chatterbox-turbo) | English 350M variant, MIT model metadata. |
| TT-05 | [Chatterbox Mac example](https://github.com/resemble-ai/chatterbox/blob/master/example_for_mac.py) | MPS path for original engine only. |
| TT-06 | [CosyVoice official repo](https://github.com/QwenAudio/CosyVoice) | Cloning/instructions, pronunciation inpainting. |
| TT-07 | [CosyVoice3 selected card](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512) | Apache selected model, release availability. |
| TT-08 | [Kokoro card](https://huggingface.co/hexgrad/Kokoro-82M) | Small supplied-voice baseline, Apache model metadata. |
| TT-09 | [F5-TTS repo](https://github.com/SWivid/F5-TTS) | MIT code versus NC weights. |
| TT-10 | [Fish canonical repo](https://github.com/fishaudio/fish-speech) | Current S2-Pro architecture and release. |
| TT-11 | [Fish license](https://github.com/fishaudio/fish-speech/blob/main/LICENSE) | Separate written license for commercial purpose. |
| TT-12 | [OmniVoice card](https://huggingface.co/k2-fsa/OmniVoice) | 646-language metadata, 0.6B, Apache code/NC weights. |
| TT-13 | [Microsoft VibeVoice](https://github.com/microsoft/VibeVoice) | Current Realtime route; older TTS disabled/removal record. |
| TT-14 | [VibeVoice Realtime selected model card](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B) | MIT metadata versus research-intended-use language; English/single-speaker limitation. |
| SU-01 | [Suno stem update](https://suno.com/blog/stem-separation-updates) | Jun 11, 2026 generative reconstruction account. |
| SU-02 | [Suno Studio 2.0](https://suno.com/blog/studio-2) | Aug 13, 2026 MIDI/effects/automation/export surface. |
| ST-01 | [Demucs repo](https://github.com/facebookresearch/demucs) | Music separation baseline, archival status. |
| ST-02 | [BS-RoFormer paper](https://arxiv.org/abs/2309.02612) | Band-split RoPE research architecture. |
| ST-03 | [Independent BS-RoFormer implementation](https://github.com/lucidrains/BS-RoFormer) | Implementation route distinct from checkpoint rights. |
| ST-04 | [SCNet repo](https://github.com/starrytong/SCNet) | MIT code, checkpoint availability. |
| ST-05 | [SCNet paper](https://arxiv.org/abs/2401.13276) | Sparse compression architecture. |
| ST-06 | [SAM Audio repo](https://github.com/facebookresearch/sam-audio) | Prompted target/residual separation, gating and CUDA recommendation. |
| ST-07 | [SAM Audio paper](https://arxiv.org/abs/2512.18099) | Foundation separation design. |
| ST-08 | [SAM license](https://github.com/facebookresearch/sam-audio/blob/main/LICENSE) | Custom license, not inferred MIT. |
| SV-01 | [OpenVPI DiffSinger](https://github.com/openvpi/DiffSinger) | Controlled singing architecture, Apache code, voice consent requirement. |
| SV-02 | [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) | Voice conversion, source performance dependence. |
| AU-01 | [Basic Pitch](https://github.com/spotify/basic-pitch) | MIDI/pitch bends, one-instrument preference. |
| AU-02 | [W3C Web Audio](https://www.w3.org/TR/webaudio-1.0/) | AudioWorklet/browser clock, latency-hint limitation. |
| AU-03 | [JUCE license](https://github.com/juce-framework/JUCE/blob/master/LICENSE.md) | Current AGPL/commercial choice. |
| AU-04 | [JUCE device API](https://docs.juce.com/master/classjuce_1_1AudioIODevice.html) | Device latency/overrun observability. |
| AU-05 | [CPAL](https://github.com/RustAudio/cpal) | Apache low-level I/O and platform backends. |
| AU-06 | [Rubber Band](https://breakfastquay.com/rubberband/) | Time/pitch processing and GPL/commercial terms. |
| AU-07 | [SoundTouch](https://www.surina.net/soundtouch/) | Alternative time/pitch processor to audition. |
| AU-08 | [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) | 48kHz speech enhancement, code licenses. |
| EL-01 | [ElevenLabs speech best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices) | Model-specific markup support. |
| EL-02 | [Pronunciation dictionaries](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/pronunciation-dictionaries) | Phoneme and alias controls vary by model. |
| EL-03 | [ElevenLabs credits](https://help.elevenlabs.io/hc/en-us/articles/27562020846481-What-are-credits) | Billed units vary by model/product. |
| EL-04 | [Voice multipliers](https://help.elevenlabs.io/hc/en-us/articles/26050485079057-What-are-custom-rates-and-credit-multipliers) | Voice cost cannot be inferred only from text count. |

Memory provenance used only for historical Sabbath Echo scope: `/Users/IDC2.5/.codex/memories/MEMORY.md:1427`, rollout `019fc328-a1e7-7062-8edd-d1665a91a6bd`. No current Sabbath Echo repository or corpus was inspected.
