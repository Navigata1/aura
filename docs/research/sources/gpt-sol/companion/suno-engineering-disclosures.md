# Suno engineering disclosures and the next controlled experiments

Research date: **8 October 2026**. Bounded follow-up to the master plan. Evidence includes first-person technical statements, Suno's data disclosure and safety documentation, patent specifications/metadata, and primary singing/multitrack research. No models were installed, audio generated or auditioned, or hardware benchmarked. The experimental designs below are proposals.

**Finding:** public evidence provides more engineering detail than product features alone, but it still does not supply a reproducible v5.5/v6 implementation. The useful next move is to test performance-level singing control, singing-specific alignment, and coordinated part generation. These experiments can expose which portion of the quality gap is actionable without pretending to discover Suno's private recipe.

## 1. What can actually be attributed to Suno

| Primary evidence | Observed disclosure | Version boundary |
|---|---|---|
| **March 14, 2024: recorded CEO interview** | Around 02:41–06:43, Mikey Shulman describes preferring transformers, likelihood over audio/music token sequences, next-token generation, a largely end-to-end approach, and audio tokenization as a major area of proprietary work. Around 10:11 he discusses scaling and producing tokens quickly enough for streaming. | First-person historical technical evidence. It predates v5.5/v6 and cannot establish their architecture, parameter count, tokenizer or objective. He explicitly describes an evolving approach. [Interview/transcript](https://www.latent.space/p/suno). |
| **January 1, 2026: CA AB 2013 disclosure** | Suno reports tens of millions of public audio files with textual metadata; possible user Content/Activity in post-training; associating audio and metadata; organizing, cleaning and filtering; removing structured user identifiers; and synthetic data use. | A direct corporate data/process disclosure, not an independently audited dataset. It predates the March/September releases and gives no per-version corpus manifest, sampling ratios, deduplication recipe or training budget. [Disclosure](https://help.suno.com/en/articles/9709569). |
| **October 1, 2026: Safety Center** | Suno says it checks submitted recordings/lyrics for similarity, uses training strategies named Original Creation, By Design, and attaches C2PA Content Credentials. A displayed example contains a v5.5 system-version field. | Evidence about the broader production system and provenance claims. The example is not our inspection of a downloaded song. No training objective, fingerprinting algorithm or checkpoint design is disclosed. [Safety Center](https://about.suno.com/safety). |
| **Current careers page** | Suno advertises Machine Learning Scientist, ML Data Operations and ML Research product roles. | Useful organizational evidence, not proof of a particular architecture. Linked Ashby descriptions required JavaScript in the research reader; no inaccessible job detail was inferred. [Careers](https://about.suno.com/careers). |

The 2024 interview is particularly useful because it contradicts the easy assumption that Suno must have been built from a hand-written score/phoneme pipeline. A composition-first system remains a reasonable design for **our** controllable studio; the interview does not establish that Suno uses one. Conversely, the historical end-to-end preference cannot prove that current Suno excludes explicit scores, phonemes, duration supervision, flow/diffusion components, or auxiliary models.

The September 9 v6 announcement ties plain-language regional editing, lyric replacement, multiple references and multimodal inputs to v6 product behavior. It does not identify how those operations are implemented. An interface can route a request through transcription, planning, a conditioned renderer and deterministic composition while presenting one action. **That orchestration is an engineering hypothesis, not a Suno disclosure.** [v6 announcement](https://about.suno.com/blog/introducing-v6).

No inspected source provides the exact current layer counts, latent/codebook design, training losses, data splits, preference recipe, quantization, cache strategy, GPU topology, or Custom Model adaptation method. State this as **“not established from inspected public sources,”** rather than claiming nobody could ever find further clues.

## 2. Patent search: reject false attribution

Bounded searches used Suno/Suno Inc/Suno, Inc. plus music generation, audio tokenization, lyrics, patents, and inventor names including Shulman, Camacho, Kucsko and Freyberg, with patent-domain filters. **No relevant Suno-assigned patent or version-linked patent was verified.** This is not an exhaustive patent search, a claim of no pending filings, or a freedom-to-operate opinion. The Google Patents assignee-search interface did not resolve in the reader.

Two deceptively relevant hits illustrate why a keyword match is insufficient:

- **US20260141890A1**, published May 21, 2026, describes AI vocal lyric replacement using a singing model, phonemes/durations and vocal/instrumental components. The displayed inventor is John Chowhan Park and assignee is Individual. It is not verified as Suno work. [Specification and listed metadata](https://patents.google.com/patent/US20260141890A1/en).
- **US20260120836A1** describes synchronized personalized media and names Suno as an example music engine. The displayed inventor is John Devecka; listed assignee is Iconic Inventions LLC. A downstream system mentioning Suno does not disclose Suno's model. [Specification and listed metadata](https://patents.google.com/patent/US20260120836A1/en).

Google cautions that its legal-status and assignee summaries are not legal determinations. Even a genuine Suno patent would describe claimed embodiments; shipment in v5.5/v6 would require separate evidence. Do not promote these records into implementation facts or build around a presumed patent license.

## 3. Experiment A: expressive singing as an editable performance

**Evidence:** OpenVPI's maintained DiffSinger code exposes acoustic synthesis conditioned on phonemes, duration and F0, plus supported speaker/style controls. Its variance models predict duration, pitch and other curves. The code is Apache-2.0; individual voicebanks, vocoders and extractors retain separate terms. This establishes a concrete controllable singing route, not a full-song Suno substitute. [Maintained repository](https://github.com/openvpi/DiffSinger), [input/control documentation](https://github.com/openvpi/DiffSinger/blob/main/docs/BestPractices.md).

**Proposed test:** start with twelve approved phrases covering sustained vowels, fast consonants, melisma, note transitions, vibrato, breath and quiet/loud delivery. Keep one melody/lyric specification and declared candidate budget. Compare native full-song vocal output, an appropriately licensed score-driven singing voice, and an authorized guide performance with a separately selected conversion engine. Preserve dry outputs and any guide take.

Represent a performance as note onsets/durations, syllable-to-note links, language/phonemes, F0 curves, intended breaths and supported expression curves. Test one change at a time: vibrato depth/rate, portamento, consonant timing, breathiness and intensity. Preserve the difference between a written note and a continuous sung pitch trajectory.

Metrics should include note-center error in cents, gross octave errors, onset offsets, voiced/unvoiced decisions, phoneme intelligibility and listener judgments of phrasing/identity. Compare F0 against an approved expressive target; scoring every intentional bend as an error would reward robotic singing. Listen to dry vocals and the same backing mix. Successful timbre conversion with lost consonants or flattened vibrato fails the experiment.

**Specific caveat:** DiffSinger documents coupling among energy, breathiness and voicing, and warns about unnatural tension/loudness combinations on some datasets. An interface should expose supported controls and useful combinations, not pretend every curve is independent. [Variance-control cautions](https://github.com/openvpi/DiffSinger/blob/main/docs/BestPractices.md).

**Decision gate:** expand to cross-range/style/language identity only when the twelve-phrase pilot improves controllability without lowering accepted vocal quality. If guide performance wins, integrate that practical path before commissioning a new voice model. StyleSinger's reference-style research is a further lead, with checkpoint/license availability requiring its own review. [StyleSinger paper](https://arxiv.org/abs/2312.10741).

## 4. Experiment B: lyric correctness, alignment and one-line repair

**Evidence:** SOFA is a singing-oriented forced aligner with dictionary/G2P inputs, confidence output, TextGrid export and boundary evaluation. The repository is MIT, but downloaded alignment checkpoints/language assets need their own record. Its claimed superiority over speech aligners is a hypothesis for our repertoire. [SOFA](https://github.com/qiuqiao/SOFA), [MFA documentation](https://montreal-forced-aligner.readthedocs.io/en/latest/).

**Proposed test:** manually label a small held-out set of approved dry singing in the intended languages. Compare a speech-alignment baseline, singing-specific alignment and human annotations. Include long vowels, repeated words, melisma, pickup consonants, names and non-English passages. Track word/phoneme boundaries, low-confidence regions and correction minutes per finished minute; report boundary error at 10/20/50ms and intelligibility independently.

Do not force incorrect generated lyrics to align to the requested transcript and then treat the result as correctness. First establish what was actually sung through independent ASR plus human review; then align the approved observed transcript. A recognizer can hallucinate a requested word, so keep audio evidence and uncertain spans.

Add a syllable/note map. DiffSinger's data guide explicitly explains that vowels commonly align to note beginnings while leading consonants may precede them; it also calls for manual treatment of polysyllabic word divisions and refined MIDI labels. A word-level karaoke timestamp is insufficient for realistic consonant placement. [Singing-data alignment guide](https://github.com/openvpi/MakeDiffSinger/blob/main/variance-temp-solution/README.md).

For local repair, compare matched syllable-count replacements, altered syllable counts, a sustained vowel across the boundary, and a phrase beginning before the downbeat. Fix duration constraints and context before rendering. Preserve accompaniment when feasible; declare the vocal mask and crossfade/tail region. Evaluate pronunciation, melody/rhythm continuity and identity plus same-rate/dtype dry PCM preservation outside the composited mask. A whole-song rerender is a different operation.

**Decision gate:** implement the align-and-review tool before promising phoneme-accurate generation. Only train an alignment/duration objective if annotation effort, supported backend and held-out error justify it. Weak labels produced by a separator or ASR must not silently become ground truth.

## 5. Experiment C: coordinated multitrack generation

**Evidence:** ACE's supported base model supplies context-conditioned `lego` generation, extraction and completion. This allows an early track-context experiment. [ACE inference contract](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md).

**Further primary research:** SyncTrack uses shared cross-track modules and instrument-specific modules, and proposes within-track stability and cross-track synchronization metrics. Its study uses bass/drums/guitar/piano, 16kHz, 10.24-second Slakh clips. That result cannot establish long-form sung-song quality. The authors' repository contains implementation/metric code; a clear code/weight license and release completeness were not established in this bounded pass. Treat it as architecture/metric evidence until reconciled. [Paper and setting](https://arxiv.org/html/2603.01101v1), [official repository](https://github.com/YangLabHKUST/SyncTrack).

**Proposed test:** create twelve owned eight-bar arrangements with fixed tempo maps, meter, harmony, melody and section markers. Compare three conditions: independently prompted parts; sequential ACE base `lego` using accumulated musical context; and a shared-score arrangement rendered through licensed instruments plus the controlled singer. Hold overall candidate budget and selection process fixed.

Measure downbeat/onset consistency, harmonic agreement, phrase/section boundaries, isolated timbre/artifacts and mixed musical preference. Include intentionally syncopated and rubato examples. Perfectly coincident detected beats are not always the musical target; beat-tracker failures on sustained instruments must be identified. Avoid inferring exact rhythmic synchronization merely from identical BPM fields.

Add a change test: lock drums/bass and alter only guitar harmony; then lock accompaniment and replace one vocal line. Track preserved assets, whether harmony remains compatible, and how edit scope expands. Export all tracks at a common zero/rate/frame count without losing reverb tails.

If sequential conditioning wins, ship it as an assisted arrangement workflow. A later joint model can train on aligned stems with track masks, shared time/score conditioning and explicit arrangement roles. Split training/evaluation by composition/session rather than adjacent clips. Do not use separator-produced pseudo-stems as clean targets without auditing bleed and identity contamination. Shared-codec reconstruction must be tested on each isolated instrument as well as on the sum.

## 6. What to add to the master plan

Add a **PerformanceSpec** beneath SongSpec: pronunciation dictionary revision; syllable/phoneme/note mapping; rests, breaths and slurs; continuous F0 and supported expression curves; singer identity/reference provenance; and confidence plus human corrections. Each engine reports which fields it actually consumes.

Sequence these experiments after engine smoke tests: align/review a small vocal set; run the expressive twelve-phrase comparison; then eight-bar multitrack ablations. Each must yield a fixture manifest, raw outputs, failure labels, declared budget and blind decisions. Long-form performance and broad parity remain subsequent gates. This turns the vague “better vocals and stems” target into three falsifiable engineering programs while preserving room for a human/AI production route to win.
