# Independent video-analysis appendix — 8 October 2026


# Video evidence method — 8 October 2026

The seven user-supplied URLs were retrieved without substitution. An eighth, Simon Crowe's tutorial, was separately added as a supplemental source after the parent identified it from the attached original-Claude screenshot. Source videos remain in `/tmp/music-gen-video-analysis-20261008`; no source videos were copied into the workspace.

Metadata was inspected before download. The installed video-analysis skill and its extraction script were read before use. Every extraction used the skill's `grab.sh URL COUNT OUT 0` with fixed-cadence sampling and no deduplication. Counts: 300, 350, 250, 350, 250, 300, 400 for the seven URLs, then 250 for the supplemental tutorial. Source media was limited to 480p. Each video's `grab.log` records the exact extraction command and result; `metadata-access.log` records metadata access. All downloads and frame extractions succeeded.

The skill script's `--sub-langs en` missed four initial English caption tracks and the supplemental tutorial track. It suppresses subtitle stderr and therefore did not establish why those attempts missed captions. Retrying against saved metadata with `--sub-langs en-orig,en-GB` recovered the relevant tracks; the songwriter's creator-provided en-GB track was retrieved with `--write-subs --sub-langs en-GB`. Each retry's exact command and stdout/stderr is preserved in `caption-retry.log`. Do not describe these initial misses as unavailable captions or a YouTube bot block.

There are **2,450 extracted frames**, **288 overview thumbnails inspected**, and **44 listed frames separately inspected at full resolution**, with overlap: **307 distinct sampled frames were visually inspected**. All eight transcripts were read. Contact sheets preserve all extracted frames for further inspection, but the remaining extracted frames were not individually inspected. This was neither a continuous full-video watch nor a controlled auditory evaluation. No local model was run and no paid API was called. A music playback demonstration confirms that a presenter plays an output; it does not establish measured quality or equivalence.

Frame labels report nominal timestamps using `(frame_number - 1) / fps`, where fps is the extraction script's rounded cadence. Labels are approximate within a cadence interval. Transcript timestamps come from retrieved captions and can contain recognition errors. Original SRT files are retained; `transcript.timestamped.txt` removes repeated rolling-caption text, and `transcript.30s.txt` groups that text for reading. Neither is an authoritative transcription.

Each folder contains minimal metadata, captions, timecoded reading text, complete contact sheets, an overview, copied key frames, and an analysis. `inspection-manifest.json` and the per-video metadata list exactly which thumbnails/full-resolution frames were inspected. Promotional assertions, visible interface behavior, engineering inference, current primary-source correction, and untested audio quality are distinguished in the analyses.

No video reveals Suno's proprietary weights, training corpus, model size, architecture, or inference implementation. An attractive UI and a successful edited demonstration cannot establish that an open local generator matches Suno. The attached Claude 20/80 estimate remains an unmeasured heuristic, not a benchmark result.


# Cross-video engineering synthesis

## What changes the plan

The required seven-video corpus plus the supplemental original tutorial supplies workflow requirements, several useful failure reports, and contradictory claims. It does not demonstrate local Suno parity. All eight captions were recovered and read; 2,450 fixed-cadence frames were extracted. Exactly 307 distinct sampled frames were inspected, including 44 separate full-resolution views and 288 overview thumbnails with overlap. The detailed inspection manifest prevents extracted frames from being mistaken for frames individually watched.

| Video | What survives scrutiny | What does not follow | Proposed action |
|---|---|---|---|
| GZtLsvklYBI | VoiceStudio and ACE project identities; visible license cautions; presenter acknowledges inferior ACE demo | Free/local equivalent to Suno or ElevenLabs; local benchmark from a Cloud-selected demo | Evaluate individual model/runtime/license combinations |
| _lHvWn2SNC4 | Current v6 product workflow: multiple references, temporal sampling, multimodal brief, precise edits, diversity and compute modes | Discovery of Suno's hidden architecture; measured preservation, fidelity, or reliability | Turn each visible promise into a backend contract and test |
| CZazcFtS4Co | Human-directed production, provenance and creator concerns | Current policy truth, detector accuracy, watermark mechanism, quantified adoption | Verify policies separately; retain human edit/performance lineage |
| BKDrtzJktO0 | Character/set/audio role binding; draft/finish budget; per-singer stems for lip-sync | Open/local video equivalent; a clean stem proves native multitrack generation | Add an export bridge and explicit reference buses |
| x8EOgO7UQ54 | Duration packages, mood/use-case catalogs and client-service requirements | Verified revenue; stock-platform permission; one human layer grants blanket copyright | Remove contradicted marketplace path; build provenance-rich delivery |
| DrRRvM4oc4w | Lyrics/style separation, persona persistence, loop/sound generation, alternate audition, lyric alignment | Deterministic bracket tags or universal 0–100 control semantics | Capability-aware UI, alignment editor, nondestructive take history |
| MJ4d0-Wi1z8 | Human MIDI/guide-vocal roundtrip, exact lyrics, keeper selection; explicit v5.5 melody regression report | A finished song, a live-guitar seed, or measured improvement on one selected output | Use musician fixtures and retain failures/candidate cost |
| MI6vwl_ZHN8, supplemental | Singing-voice verification, section-preserving Editor→Studio path, instrument replacement, take lanes, recording and EQ | Claude's 20/80 ratio or current August-price/version claims | Preserve project graph across tools; test origin alignment and consent |

## Requirements the screenshots can hide

1. **Every reference needs a role.** Preserve source ID/hash, crop, start/end, instrument or voice target, strength, and permission. The v6 demo's first/second/third-song instructions and the video demo's audio-only MP4 are role-binding examples. Do not let an index change silently target the wrong source. Evidence: _lHvWn2SNC4 02:10–03:26, frame 71; BKDrtzJktO0 frame 161 and 13:30–15:34.
2. **A section map must survive tool boundaries.** Source tutorial 11:30–12:15 routes through Editor specifically to retain sections in Studio. Use one versioned project graph with sections, lyrics, beats, clips, tracks and references, rather than independent tools that discard each other's context.
3. **A generative edit is a proposal until committed.** Both older tutorials show two alternates and a deliberate insertion/copy action. Keep source and candidates separate; undo must restore the true previous artifact, not trigger regeneration. Evidence: DrRRvM4oc4w frame 206; MI6vwl_ZHN8 frame 212.
4. **Identity has separate singing and narration tests.** Suno singing voice verification is visible in supplemental frames 117/118; VoiceStudio narration features are described in the roundup. A single clone UI cannot establish range, language, emotional direction, or longform consistency.
5. **Prompt parsing should expose conflicts.** The songwriter's nominal instrumental gains unwanted vocals because the style text still mentions them (13:00–13:32). Resolve instrumental flags, lyric mode, voice references and vocal tags transparently. A lyric's words must not become hidden style instructions or vice versa.
6. **Correct the words before re-performing them.** The songwriter's 28:00–29:08 workflow fixes recognized lyrics before a new cover. Keep approved lyric text, source transcript and alignment distinct; an ASR guess must not silently replace the author's text. Evidence: frames 286, 292, 297.
7. **Preserve melody and harmony as evaluated constraints.** A newer model can sound better while following the tune worse. The v5.5 regression report at 30:00–30:35 makes cross-version control tests necessary. Actual MIDI/chord/hum fixtures are stronger than free-text adjectives alone.
8. **Separate original isolation from clean reconstruction.** A dropdown listing 12 instruments does not prove 12 independent native tracks. Lead/background separation for lip-sync reveals leakage sensitivity. Test source fidelity separately from clean re-performance quality. Evidence: BK frames 330/340; supplemental frame 186. Root's separate current Suno stem-source research must resolve product specifics.
9. **Replacement requires a reconstruction rule.** Adding a new isolated synth or drum on top of the original stereo mix doubles the original part unless it is removed, suppressed or replaced in a reconstructed mix. The tutorial's muted source/alternate lane screenshots expose the need for explicit mixer routing and residual policy. Evidence: supplemental frames 192, 212, 220.
10. **Diversity differs from adherence.** v6 Variety and My Taste are separate controls from Weirdness, Style Influence and Max Mode. Record the creative intent and actual engine-specific parameters; do not invent a universal slider mapping. Evidence: _lHvWn2SNC4 frame 246 and 11:36–12:07.
11. **Compute quality is a budgeted mode.** The vendor says Max Mode uses more compute to reduce drift; it does not disclose the mechanism. A local implementation could test planning, longer context, multi-candidate selection or a better checkpoint, but these are alternative hypotheses. Record elapsed time and accepted results, not a claimed equivalence. Evidence: _lHvWn2SNC4 15:21–16:00.
12. **Best-of-many demos conceal economics.** The songwriter normally needs four or five tries; the ACE roundup shows repeated short results. Save rejected candidates and selection reason; report total latency/cost per keeper and successes per declared attempt budget. Evidence: MJ4d0-Wi1z8 33:00–33:30; GZ frame 155.
13. **Music-video output requires performer-specific buses.** Chosen lead vocal drives lip-sync, while the audience hears the full mix. Exporting an MP4 guide is a format workaround, not the native musical artifact. Keep time origin, duration, frame rate and vocal reference separate from final mix. Evidence: BKDrtzJktO0 21:30–23:00.
14. **Waveform UI must correspond to sound.** Named sections, crossfades, tempo, EQ, loops and stem controls need actual DSP, alignment, persistence and nonblocking playback. A colored timeline reproduces the screen, not the audio engine. Evidence: Dr frames 197/223; supplemental frame 234.
15. **Policy and price claims need independent sources.** VoiceStudio's year/month discrepancy was caught visually and resolved by current vendor terms; the monetization video's Pond5/AudioJungle advice is contradicted by current policies. Keep dated evidence and refresh volatile facts; do not use popular tutorials as release-clearance records.

## Experiments suggested directly by the corpus

The first evaluation should contain a human MIDI chord seed, a hummed melody, a guide vocal with corrected lyrics, an explicit no-vocal instrumental prompt, a three-reference role-binding task, one-word replacement, chorus-only replacement with protected verses, a long voice-conditioned piece, a per-singer isolation/lip-sync guide, an alternate take commit/undo cycle, and an Editor→Studio→DAW roundtrip. Use original or approved assets. Fix the candidate budget before comparing engines, retain failures and intermediate versions, and assess full-song coherence as well as short segments. None of these experiments has been run in this research phase.

The immediate product opportunity is finishing and revising human-directed work with dependable files, identity permissions, clips, alignment and exports. The longer-term generation opportunity requires an independent benchmark and model/data program. These are complementary engineering programs; neither the tutorials nor Claude's ratio assigns a defensible percentage of completion.


# GZtLsvklYBI — open-source replacement roundup

[Source](https://www.youtube.com/watch?v=GZtLsvklYBI), The Next New Thing, published 6 October 2026, runtime 32:30. Retrieved 300 frames and English auto-captions. Inspected `overview.jpg` (36 thumbnails) and `key-frames/f_0023.jpg`, `f_0155.jpg`, `f_0172.jpg` at full resolution.

The useful thesis is ownership and customization through independently replaceable components. The ten named projects are VoiceStudio, Odysseus, FreeLLMAPI, Vane, InvokeAI, ACE-Step 1.5, OpenShorts, Dyad, OpenManus, and Upscayl. Their claimed prices, adoption counts, speed, and replacement quality are presenter assertions; metadata descriptions and slides identify projects, not production qualification.

**Voice evidence.** At 01:41–02:13 the presenter describes short-clip cloning, voice design, dubbing, and audiobooks. At 02:13–02:25 he explicitly identifies the default OmniVoice model as noncommercial and says paid work needs another model. Frame 23, nominal 02:23, visibly identifies VoxCPM2/CosyVoice 3, AGPL-3.0 app licensing, and model-specific restrictions. It also lists recent Macs or NVIDIA 6 GB and 10 GB disk as requirements. These are the video's stated requirements, not measured hardware results.

**A discrepancy the transcript alone misses.** Narration/captions around 02:26 say $99 per month; frame 23 says $99 per year. Current vendor [Pro terms](https://voicestudio.sh/pro) resolve this as $99/user/year or $299 Lifetime. Private hosting and closed-source distribution are excluded from those tiers. The commercial app license does not rewrite individual model licenses.

**Music evidence.** At 13:57–19:30 ACE-Step is presented as self-hostable. Frame 155, nominal 16:41, visibly has **Cloud selected**, the model label **ACE-Step V1.5 XL Turbo**, and several 14-second results. It is not a demonstrated local full-song benchmark. At 16:30–17:16 and 18:30–18:51 the presenter himself finds its quality below Suno; at 17:49–18:06 he says its editing is less extensive. Frame 172, nominal 18:31, shows the comparison to Suno 4.5/5 as a maker claim while acknowledging Suno 6 is current. It displays MIT code/model licensing, but that statement still needs repository/model-card checking for the chosen revision.

**Engineering implication, inferred.** Keep frontend, job orchestration, music generation, speech, separation, editing, and video generation behind independently versioned interfaces. A free shell can still incur hardware, model, service, storage, and support costs. Evaluate local full-song output on the actual worker, and evaluate voice engines separately on longform pronunciation, speaker continuity, and chunk boundaries. No replacement-quality conclusion follows from this roundup.


# _lHvWn2SNC4 — Suno v6 introduction

[Source](https://www.youtube.com/watch?v=_lHvWn2SNC4), Suno Music, published 9 September 2026, runtime 16:58. Retrieved 350 frames and English auto-captions. Inspected `overview.jpg` and full-resolution frames 71, 96, 111, 150, 174, 204, 220, 222, 246 under `key-frames/`.

This is the most relevant product target in the submitted set: the announced generation is v6, v6-wild, and v6-mini. It supersedes the attached v5.5 tutorial as a current visible feature baseline. The vendor describes quality improvements at 00:06–00:16 and 16:02–16:08; these are vendor claims and selected demonstrations, not independent auditory scoring.

**Observed controls and demonstrated requests.** At 02:10–03:26 references assign vocals, drums, rhythm, atmosphere, and vocal energy to different inputs. Frame 71, nominal 03:24, visibly contains three separately named song attachments and role-specific instructions. At 04:33–04:48 the presenter requests a guitar riff at a timestamp, isolation, and a new beat around it; frame 96, nominal 04:36, shows the 0:45 instruction. Image input and iterative restyling appear at 05:08–06:18, with frame 111 showing an image attachment. Video-energy direction is described at 06:56–07:59; frame 150 shows a video-associated song page. A phone memo is captured at 08:15–08:43; frame 174 shows recording UI. Melody preservation is requested at 08:44–08:58.

**Specificity is part of the target.** At 09:45–10:03 the vendor asks to change chorus energy while retaining verses. At 10:33–11:08 it describes word replacement with song structure preserved. The inspected frames around that second demonstration do not establish waveform-level preservation: frame 220 shows an attachment and a suggested style prompt, while frame 222 is the presenter. Keep the exact preservation claim attributed to the vendor. Frame 246, nominal 11:53, visibly separates Max Mode, Weirdness, Style Influence, Variety, and My Taste. At 11:36–12:07 Variety is explained as between-output diversity, with optional personal taste; at 15:21–16:00 Max Mode is described as extra compute reducing long-song/voice/cover drift, particularly after two minutes. No backend mechanism is disclosed.

**Engineering implication, inferred.** Build role-bound multi-reference assets, time-indexed source selection, protected edit regions, a lyric/word alignment layer, melody-preservation tests, distinct diversity/adherence controls, and quality/compute budgets. Image/video understanding can produce a structured musical brief without proving that the core generator is natively multimodal. Test protected audio outside edit masks bytewise or with explicitly bounded DSP exceptions. Test model upgrades against vocal identity, harmony, melody, and longform drift. Slider names are not proof of particular sampling, guidance, or transformer mechanisms.


# CZazcFtS4Co — policy and authenticity commentary

[Source](https://www.youtube.com/watch?v=CZazcFtS4Co), Bolo's Hot Takes, published 18 August 2026, runtime 23:22. Retrieved 250 frames and English auto-captions. Inspected `overview.jpg` and `key-frames/f_0001.jpg`. The 36 overview samples show a presenter speaking in a studio; no policy document, technical diagram, separation demonstration, or Suno settings is visible in those inspected samples.

The presenter argues for human-directed music and against mass automated uploads. Download limits and watermarking are alleged at 00:00–00:30 and 21:48–22:05. Explanations involving lawsuits, future detection, streaming economics, and who uses AI professionally remain commentary unless separately verified. The video does not specify a watermark implementation or prove detection reliability.

At 08:30–09:58 and 11:30–12:00 he describes a constructive alternative: write material, obtain a generated backing/demo, separate it, add or replay instruments, and have an actual artist sing the final result. This is workflow opinion and anecdote, not a controlled engineering demonstration. At 17:00–18:35 he argues that technical perfection does not automatically create emotional resonance. That is useful product direction but cannot be turned into a numerical quality target.

**Engineering implication, inferred.** Preserve human contributions and edit lineage; make reference ownership and commercial-use restrictions legible per asset; enable controlled DAW handoff. Evaluate the product by usable keepers and musical control, not bulk generation counts. Store the source of policy claims and refresh current terms before distribution. Do not design around unverified assumptions that watermark removal, unlimited publishing, or claimed automatic detection solves provenance. This source contributes creator expectations, not proof of Suno's internal engineering.


# BKDrtzJktO0 — music-video production workflow

[Source](https://www.youtube.com/watch?v=BKDrtzJktO0), Dan Kieft, published 5 October 2026, runtime 23:36. Retrieved 350 frames and English auto-captions. Inspected `overview.jpg` and full-resolution key frames 161, 210, 230, 330, 340.

The seven-step workflow combines Suno music, Higgsfield video/image generation, and an LLM for structured prompts. From 02:30–04:50 the presenter starts with an instrumental, reuploads it as an audio reference, adds lyrics, and changes style. From 05:00–09:30 he builds face, clothing, and character sheets with different references; 10:00–12:30 adds sets. These demonstrations support a modular production workflow, not evidence that a local music generator or video engine matches the paid systems.

**What frames add.** Frame 161, nominal 10:47, explicitly binds the video reference's audio while excluding its visual content, then specifies initial scene, stage timing, lip-sync, camera, and foreground/background action. Frame 210, nominal 14:06, shows a Markdown prompt-builder file plus reference files in an LLM. Frame 230, nominal 15:26, shows a hosted video-generation interface with 10 seconds, 16:9, 1080p, high bitrate, and a credit-bearing generate button. Prompt structures are source material, not instructions to this project. At 15:00–15:34 the narrator recommends cheap draft generations before higher-quality render and checks duration matching; 16:00–17:30 demonstrates multi-angle references; 18:00–18:30 stresses a consistent visual anchor.

**The consequential overlooked requirement.** At 21:30–23:00 the presenter identifies lip-sync responding to unwanted ad-libs/backing vocals. The workaround is to select the intended vocal stem, export that alone as audio in a black-background MP4, drive the chosen performer from it, and restore the full mix later. Frames 330 and 340, nominal 22:11 and 22:51, visibly show Lead Vocal and Background Vocals separated alongside drums, bass, percussion, synth, and other. The extraction dialog has Auto split, Split from mix, and Advanced split, plus a list-of-12-instruments description. This does not prove the original generator emits native stems.

**Engineering implication, inferred.** Require per-performer reference routing, separate guide and playback buses, synchronized stem origins, word/phoneme alignment, exact shot-duration contracts, draft/finish budgets, and asset identity continuity. A local music studio can export these references without building an entire video foundation model. Separation should be assessed for vocal leakage and transient damage before it drives lip-sync. Camera/character taste and final editing remain human decisions.


# x8EOgO7UQ54 — monetization advice, with necessary corrections

[Source](https://www.youtube.com/watch?v=x8EOgO7UQ54), Mr. Money, published 5 September 2026, runtime 9:18. Retrieved 250 frames and English auto-captions. Inspected `overview.jpg` and `key-frames/f_0093.jpg`, nominal 03:26, which shows an AudioJungle landing page. A landing page is not evidence of contributor eligibility, actual sales, or policy acceptance.

The video proposes niche music channels (01:07–02:49), stock/sync licensing (02:51–04:42), and client commissions (04:43–06:30). Claimed revenues at 01:49–02:06, 03:31–03:44, and 05:38–05:52 are unsourced examples, not verified earning forecasts. More useful product requirements are mood/use-case cataloging at 04:12–04:39 and deliberate service packages at 05:17–05:28. No paid outcome, client delivery, rights audit, or stem quality test is shown in the inspected samples.

**A material error.** At 03:08–03:21 and 07:43–07:49 it says Pond5 and AudioJungle accept AI-generated music if disclosed. Current primary policies contradict that advice: [Pond5's AI policy](https://www.pond5.com/help/en/articles/10086182-does-pond5-allow-ai-generated-content-for-licensing) and [contributor FAQ](https://contributor.pond5.com/faq/) do not allow AI-generated submissions; [Envato's Market/Elements policy](https://help.author.envato.com/hc/en-us/articles/13313674070681-AI-generated-content-policy-for-Market-and-Elements) does not allow AI-generated content as a primary sale item. AudioJungle belongs to Envato Market. Treat the video's proposed upload path as contradicted by checked current policies, not as a business plan.

At 03:48–04:12 and 06:32–07:28 it suggests adding a human element improves legal defensibility. Do not infer that a single played note, sung line, or percussion layer grants copyright over an entire otherwise generated composition. Commercial permission, copyrightability, model licensing, reference rights, and platform eligibility are separate questions.

**Engineering implication, inferred.** Offer cue sheets, duration-constrained versions, loop-safe edits, instrumental/voice variants, metadata, consent/provenance records, and client-ready aligned stems. Keep monetization outside model-quality claims. For this user's internal personal studio, usable music and freedom to iterate can be valuable before any public marketplace business exists.


# DrRRvM4oc4w — deliberate control and iteration

[Source](https://www.youtube.com/watch?v=DrRRvM4oc4w), Isa does AI, published 17 March 2026, runtime 15:23. Retrieved 300 frames and English auto-captions. Inspected `overview.jpg` and full-resolution key frames 95, 155, 197, 206, 223. This tutorial uses a v5-era interface; its title's 99% comparison is not a measured benchmark.

The coherent workflow is project organization (00:44–01:35), separate lyrics/style controls (02:00–03:40), structural/performance tags (04:00–05:12), a hummed reference with cover and influence control (05:30–07:06), reusable persona (07:30–08:30), short sounds/loops (08:30–09:30), section replacement/rearrangement (09:38–11:35), stems/MIDI handoff (11:38–12:35), and lyric pacing (12:40–13:55). These are practical creator affordances; claims that settings or tags always yield precise behavior are unverified.

**What frames add.** Frame 95, nominal 04:49, visibly separates the lyric-tag editor from the style editor. Frame 155, nominal 07:54, shows persona creation based on a selected existing song and a Public control, exposing a persistence/privacy requirement. Frame 197, nominal 10:03, shows named waveform sections, reset/undo, Save as New Song, Get Stems, Edit in Studio, and a replace range. Frame 206, nominal 10:31, shows source/new lyrics, Fix Alignment, two alternate replacement candidates, and an Insert action. Frame 223, nominal 11:23, shows a final fade handle and tempo control. These are real visible UI states, not evidence of sample-exact audio invariance.

At 14:00–14:55 the narrator gives broad slider interpretations for Weirdness and Style Influence. A 0–100 UI does not reveal numerical sampling parameters; specific hard endpoints should be verified against current product behavior. Bracketed tags and punctuation are soft generative directions, not an executable music score.

**Engineering implication, inferred.** The studio needs section/lyric alignment, candidate audition before commitment, nondestructive history, reproducible generation parameters, reusable identity references, loop/sound presets, and cross-project asset governance. Separate generation controls by backend capability. Use rhythm/melody/word timing evidence to test actual adherence; do not make every backend show sliders it cannot meaningfully implement.


# MJ4d0-Wi1z8 — songwriter-led DAW roundtrip

[Source](https://www.youtube.com/watch?v=MJ4d0-Wi1z8), Hit Songwriter Meets AI, published 15 April 2026, runtime 39:51. Retrieved 400 frames and creator-provided English en-GB captions. Inspected `overview.jpg` and full-resolution key frames 58, 104, 108, 286, 292, 297, 343. The captions still contain mistakes; creator-provided does not mean perfectly transcribed.

The defining workflow keeps human melody, chords, lyrics, and keeper decisions central. A title/chord seed becomes a generated arrangement; a DAW captures humming and later a guide vocal; Suno covers that with explicit lyrics and constrained variation; selected output goes back to Logic. Sections: seed 05:00–07:00, cover/arrangement 07:30–15:15, humming 16:00–19:30, lyric/guide-vocal preparation 25:30–29:30, selection 30:00–33:30, final demo 33:34–38:50.

**The description alone is misleading.** It describes an acoustic-guitar start, but at 05:00–05:30 the presenter explains that this is a keyboard-programmed Kontakt guitar instrument. Frame 58, nominal 05:41, shows green MIDI regions and a piano roll in Logic. This is human-authored musical input, not proof of a live acoustic-guitar recording. Frame 108, nominal 10:39, shows a concrete final setting in that step: Weirdness 15%, Style Influence 90%, Audio Influence 90%. Frame 104 earlier shows different values, so freeze the parameters of the actual submitted job rather than copying any passing screenshot.

**Failure evidence matters.** At 13:00–13:32 an unintended vocal layer appears because the style prompt included vocals. At 28:00–29:08 he corrects automatic lyric transcription before covering; frames 286/292/297 show that edit progression. At 30:00–30:35 he explicitly says the new v5.5 follows melody less accurately than earlier versions. At 33:00–33:30 he says he normally needs four or five generations before a keeper. At 36:00–36:30 he calls the result a demo, not a completed full song. A selected successful output hides rejected generations and revisions.

**Engineering implication, inferred.** Preserve original human MIDI/audio, instrument and sample licenses, original lyric text, take lineage, selected alternatives, and model revision. Build chord/melody-preservation regression sets, explicit vocal/no-vocal constraints, exact lyric correction, WAV handoff, and keeper-cost reporting. Measure a model by reliable success across attempts rather than its best clip. His satisfaction is creator testimony; no independent sonic-equivalence test was performed here.


# MI6vwl_ZHN8 — supplemental v5.5 beginner/studio baseline

[Source](https://www.youtube.com/watch?v=MI6vwl_ZHN8), Simon Crowe, published 25 August 2026, runtime 20:19. This is the supplemental eighth source, independently identified by the parent from the attached Claude-response screenshot, not substituted for a user-supplied URL. Retrieved 250 frames and English auto-captions. Inspected `overview.jpg` and full-resolution frames 99, 115, 116, 117, 118, 158, 186, 192, 212, 220, 221, 224, 234.

The tutorial confirms the attached baseline's broad feature inventory: simple/advanced creation, two candidates, user singing voice, editor sections, Studio multitrack edits, separation, mic recording, covers, and WAV export. It contains no measured 20%/80% engineering split and cannot substantiate Claude's ratio. Its free-plan/price/version statements at 02:26–04:05 describe August conditions and need current primary verification.

**Voice setup has a consent-related workflow.** At 07:45–09:45 the presenter records a singing sample, trims it, reads a challenge phrase, and saves a named voice. Frame 115, nominal 09:15, shows a 32-second trim; frame 117, nominal 09:25, visibly shows a read-aloud verification phrase and waveform; frame 118, nominal 09:30, displays an own-voice confirmation. His suggested sample durations are advice, not an evaluated optimum. Singing identity and narration quality still require separate testing.

**What the studio frames add.** At 11:30–12:15 the presenter deliberately routes Editor → Studio to retain automatically named sections; direct Studio entry reportedly lacks that segmentation. Frame 158, nominal 12:45, shows clip-local lyrics. At 14:45–17:15 he isolates synth/drums, covers each, auditions candidates, then commits the selected replacement. Frame 186, nominal 15:01, shows a wider detected stem list including lead/background vocals, drums, bass, guitar, keyboard, percussion, strings, synth, FX, brass, and woodwinds. Frame 192 shows an inserted synth layer. Frame 212, nominal 17:08, shows alternate take lanes, Copy to Main Track, and tempo/transpose/speed controls. At 17:30–18:35 mic input is converted into an electric-guitar part; frames 221/224 show input selection and recording. Frame 234, nominal 18:55, shows EQ and Follow Track Tempo. Export is described at 18:55–19:40.

**Engineering implication, inferred.** Build an explicit project graph that preserves segmentation across tools, track-local variants, a safe commit action, recording-device/error handling, consent records, origin-aligned stems, tempo maps, DSP preview, and consistent exports. Isolating then replacing a stem requires subtraction or reconstruction of the old part to avoid doubled instruments. A stem extraction interface does not establish the generator's internal multitrack architecture. These screenshots support product requirements; audio invariance, identity quality, and clean isolation remain unmeasured.

