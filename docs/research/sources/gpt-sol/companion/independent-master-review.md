# Independent challenge review of the Music Gen master plan

Reviewed 8 October 2026. Reviewer: generation-research lane, independently checking the root synthesis against primary engine sources. This is a document/evidence review, not an audio audition, model installation, device benchmark, legal opinion, or production approval.

**Verdict: the central recommendations survive, with the initial model choice remaining provisional.** A replaceable engine boundary, native-audio provenance, separate extraction/re-performance semantics, and measured escalation are supported. No source establishes that the proposed system already reaches Suno v6, an aspirational v6.5, or a measured percentage of that quality. The plan states that limitation clearly.

The root corrected several shortlist facts during this review after receiving the first findings. A frozen review input is saved at [master-review-input.md](</Users/IDC2.5/Music Gen/research/2026-10-08/master-review-input.md>). It contains 341 lines, captured at `2026-10-08T14:17:24.862312+00:00`, SHA-256 `a4b2f7925169817e244967e7d1a5dfd604097e4903ca90cebdd18c87ad6d3c4c`. Unless marked “initial wording,” line references below refer to that snapshot; the live master may subsequently change. No master-plan file was edited by this reviewer.

## 1. Corrections found and reconciled

| Finding | Initial wording and evidence against it | Snapshot disposition |
|---|---|---|
| R1 — YuE2 comparisons include current Suno | Initial master line 51 characterized comparisons as against older Suno versions. The report explicitly includes v6 and v6 Wild in both automatic evaluation and expert listening. Experts favor v6 over YuE2 best-of-eight overall; automatic rankings do not establish broad parity. | **Resolved at line 51.** Current wording includes v6/v6-wild, expert preference and company licensing. [YuE2 report, §4.1 and Appendix D.4](https://arxiv.org/html/2609.33757v1), [benchmark protocol](https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md). |
| R2 — Broken SongGeneration project citation | Initial line 54 linked `songgeneration.github.io`, which returned HTTP 404 on direct inspection. The original reachable LeVo demo is `levo-demo.github.io`, HTTP 200; it still contains an older “code will be released soon” notice. | **Resolved at line 54.** The historical demo is correctly distinguished from current asset clearance. Canonical GitHub API remained 404, Tencent HF 401, and the accessible linked v2-large card contains only `license: unknown`. [Original demo](https://levo-demo.github.io/), [canonical repository](https://github.com/tencent-ailab/SongGeneration), [linked v2-large metadata](https://huggingface.co/lglg666/SongGeneration-v2-large/raw/main/README.md). |
| R3 — Khala/Shao and StepAudio have different release custody | Initial line 56 grouped both as architecture leads requiring release verification. Khala is now Shao; its public repository links downloadable weights. Its weight-card metadata is `cc-by-nc-4.0`; maintainers warn that runtime changes can produce noise-like output. StepAudio 3 Music has a provider-backed demo/API path, but downloadable music weights were not verified. | **Resolved at lines 56–57.** Shao is now a released research candidate; StepAudio remains hosted/paper evidence. [Shao repository](https://github.com/Shao-Music-AI/Shao), [linked weight card](https://huggingface.co/liujiafeng/Shao-MusicGeneration-v1.0/raw/main/README.md), [official StepAudio Space](https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music/blob/main/README.md?code=true). |
| R4 — MuLaCover preservation label | Initial line 55 called it “reference-preserving,” which could imply waveform preservation. It produces composition/reference-conditioned reinterpretation; its official weights and outputs also have noncommercial terms. | **Resolved at line 55.** Current wording states reinterpretation and no original-waveform guarantee. [MuLaCover implementation/licensing map](https://github.com/HeartMuLa/MuLaCover). |
| R5 — Current DiffRhythm generation and editing versions | Initial line 53 named DiffRhythm with a v1 repository link. The current v2 release uses block flow matching. Its extension and instrumental options are TODOs; v1.2 has a separate editing/continuation capability history. | **Resolved at line 53.** Version distinction prevents assigning v1 functions or its memory headline to v2. [DiffRhythm 2](https://github.com/ASLP-lab/DiffRhythm2), [DiffRhythm v1](https://github.com/ASLP-lab/DiffRhythm). |
| R6 — ACE checkpoint-specific control | A family-level speed/control recommendation could be read as one turbo/XL checkpoint supplying every task. Official inference documentation limits `extract`, `lego`, and `complete` to the supported base model; turbo guidance behaves differently. | **Resolved at line 61.** The root added separate task profiles and capability-faithful controls. [ACE inference contract](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md). |

These corrections improve research accuracy without changing the central engineering direction.

One small wording correction remains in snapshot line 51: replace “Company use of weights requires separate licensing” with **“Company commercial use of weights requires separate licensing.”** The license distinguishes commercial company use from otherwise-permitted noncommercial use; merely being a company does not negate the base CC BY-NC grant. This is a precision correction to the upstream summary, not a legal determination about a particular deployment. [Controlling weight terms](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE).

## 2. Attempt to refute the load-bearing recommendations

### A. Two-engine foundation: survives; exact second engine is a hypothesis

**Claim tested:** lines 59–70 recommend ACE plus MiniMax as the initial pair, with a replaceable boundary.

**Strongest challenge:** integration breadth can consume time that should be spent listening and improving one engine. “Two engines” also understates that ACE may require multiple pinned checkpoints and that MiniMax has a large download, CUDA-specific kernels, and currently a pinned Diffusers PR recipe. No local benchmark establishes that MiniMax is the best second engine for this user's musical genres. YuE2 offers released composition-first control and has a useful personal-creator permission; placing it only in a research lane is conservative for a genuinely personal music workflow. [MiniMax model instructions](https://huggingface.co/MiniMaxAI/MiniMax-Music3), [YuE2 individual/company weight terms](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE).

**Disposition:** the adapter strategy survives because the plan explicitly permits replacements and declines to claim a quality ranking. ACE/MiniMax is a sensible initial comparison, not an established optimal pair. Choose the second installed model after hardware inventory, exact use mode, and the first 12 smoke briefs. Personal-use YuE2 can replace MiniMax if it provides more useful musical control or better measured results; a company-hosted deployment requires resolving its separate rights. Do not install all challengers at once.

**Implementation consequence:** an engine is a provider boundary; a profile is a specific checkpoint/task/backend. Benchmark and cache profiles separately. The selection gate must allow the proposed pair to lose.

### B. Codec and fine-tuning limits: survives; avoid an absolute codec ranking

**Claim tested:** lines 88–96 say the representation/decoder affects fidelity and a few-song LoRA does not guarantee broad model parity.

**Strongest challenge:** perceptual quality can improve without a new codec, and a learned decoder can invent plausible detail. Domain-specific fine-tuning could substantially improve the user's chosen style even if it does not reproduce all Suno capabilities. Therefore “the codec determines quality” or “fine-tuning cannot help” would be too strong.

**Disposition:** the actual text uses “much of” and “does not guarantee,” which survives this challenge. Published systems place acoustic detail in different representations; ACE's report describes a large foundational data/task program, while the MuSeC paper studies reconstruction-versus-predictability tradeoffs. A reconstruction study can isolate a bottleneck, but it cannot by itself rank complete song generators. [ACE technical report](https://arxiv.org/html/2602.00744v1), [MuSeC research report](https://arxiv.org/html/2609.21240v1).

**Implementation consequence:** test original versus codec round-trip and generator versus decoder separately where technically possible. Fine-tune a supported adapter for a declared domain, evaluate held-out songs/singers, and retain the right to stop if it does not improve accepted-result cost or quality. Better plausible high-frequency detail is not recovery of the exact lost source waveform.

### C. Export/container fidelity and local preservation: survives with an explicit comparison domain

**Claim tested:** lines 88, 171–175 and 215–216 preserve native artifacts, track conversions, and require kept dry PCM to remain byte-identical outside masks.

**Strongest challenge:** a 32kHz MiniMax output placed in a 48kHz studio must be resampled, so the resulting PCM cannot be byte-identical to the native source. Converting 16-bit PCM to float also changes byte representation. A 48kHz/32-bit export may be a good processing/interchange format even when it does not improve the generated information. File-container bytes may differ despite identical decoded samples.

**Disposition:** the plan correctly separates native artifacts and transformed exports. Its preservation gate is achievable for copied PCM, provided “kept dry PCM” means the same declared working rate, channel layout and numerical representation. Exactness cannot be attributed to the generative model itself. MiniMax's documented native rate is 32kHz stereo; the studio's project rate is an implementation choice. [MiniMax architecture/native output](https://github.com/MiniMax-AI/MiniMax-Music3).

**Suggested precision:** add to the eventual test contract: “compare retained samples against the immutable pre-edit working PCM at the same sample rate, channel layout and dtype; resampling/mastering are separate operations.” Compare decoded samples or canonical PCM ranges, not complete WAV headers. Keep source hashes and conversion settings. This is a test-spec clarification, not a blocker to the master plan.

### D. Separation and re-performance lanes: survives; regenerated fidelity is unmeasured

**Claim tested:** lines 100–118 distinguish extracting estimates of existing sources from generating clean new performances, plus a later coordinated-native-track route.

**Strongest challenge:** source separation can use generative priors, and a source-conditioned generative model might behave as an excellent separator. Algorithm families overlap; a clean output does not reveal which architecture produced it. Regenerated stems can change notes, timbre, microtiming, stereo space, or expression and may not recombine into the original mix.

**Disposition:** the distinction remains valid as a promise to the user, independently of internal algorithm labels. Suno's June 11 post specifically describes generating stems anew to match the song. It does not disclose training loss, component network, precise source fidelity, or whether every split mode shares one implementation. [Suno's stem update](https://suno.com/blog/stem-separation-updates).

**Implementation consequence:** extraction is evaluated against ground-truth sources where available, alongside bleed and mixture residual. Re-performance is evaluated for musical matching, identity and isolated quality; perfect mixture recombination is not its presumed contract. Store operation type, original asset, accepted replacement and confidence. Do not say Suno's clean-stem claims have been independently verified by this research.

### E. Knowledge of Suno architecture: survives as an inspected-source boundary

**Claim tested:** lines 77–81 distinguish confirmed product behavior, undisclosed internals, and inference from open research.

**Strongest challenge:** public patents, papers, talks, hiring descriptions and reverse engineering can sometimes reveal additional details. Lack of a disclosure in this sweep is not proof that no public detail exists anywhere. Bark is informative historical audio work but cannot identify the current music architecture.

**Disposition:** no inspected primary source in this review establishes the full v5.5/v6 architecture, parameters, tokenizer, objective mixture, serving stack or personalization algorithm. The plan appropriately avoids turning a feature into a LoRA claim. [Bark's own music-model distinction](https://github.com/suno-ai/bark), [Suno's product stem disclosure](https://suno.com/blog/stem-separation-updates).

**Suggested precision:** interpret “Unknown” as “not established from inspected public sources.” Further patent/talk research may add qualified clues, but should not be reported as exact-version source code or a verified recipe.

## 3. Full shortlist link/access/license/hardware reconciliation

All observations are upstream-documentation facts or direct HTTP access results. “Pass” means the snapshot's bounded statement matches that evidence, not that a runtime or rights audit is complete.

| Snapshot line | Reconciliation | Result |
|---|---|---|
| 48 / ACE | Official repo link is valid; 4B XL and multiple backends are documented. XL recommends 20GB without offload or 12GB with offload/INT8; these are configuration-dependent upstream figures, not local measurements. MIT repo/selected XL-card terms differ from unexamined data provenance. Task caveat at 61 is essential. [Repo](https://github.com/ace-step/ACE-Step-1.5), [selected XL card](https://huggingface.co/ACE-Step/acestep-v15-xl-sft). | Pass |
| 49 / MiniMax | Official released weights/card; CUDA and nonstreaming confirmed. Current card's 24GB+ recipe and lower-memory offload coexist with an older two-GPU repo recipe. Its custom Community License requires commercial UI attribution and other conditions; it is not MIT. Generic HF MPS/image helper is unusable compatibility evidence. [Card](https://huggingface.co/MiniMaxAI/MiniMax-Music3), [license](https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE). | Pass; runtime maturity gate retained |
| 50 / HeartMuLa | Released 3B checkpoint exists and related base code/weights are Apache-2.0; current headline comparison references an internal 7B, which must not be counted as downloadable. CUDA split/lazy-loading guidance does not prove a consumer VRAM target. [Repo](https://github.com/HeartMuLa/heartlib), [released card](https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year). | Pass |
| 51 / YuE2 | Current repo now hosts YuE2, with old YuE preserved separately. Released weights, Linux/Python 3.12/BF16 NVIDIA 24GB starting point, 48kHz stereo. Apache code is distinct from CC BY-NC weights plus individual-creator exception. Company rights require separate licensing. [Repo](https://github.com/multimodal-art-projection/YuE), [weight license](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE). | Pass after correction |
| 52 / Stable Audio 3 | Medium weight card and official repo exist; gated Community/Gemma component terms. Medium CUDA and Small CPU/MLX routes must not be conflated. Official guide says intelligible vocals are not the intended task. No exact revenue threshold was verified in this sweep. [Repo](https://github.com/Stability-AI/stable-audio-3), [card](https://huggingface.co/stabilityai/stable-audio-3-medium), [prompt guide](https://kb.stability.ai/knowledge-base/stable-audio-3-prompt-guide). | Pass |
| 53 / DiffRhythm 2 | Released code and weights since October 30, 2025; Apache-2.0 statement. Block-flow route. README lists extension/instrumental TODOs; Mac/Windows espeak setup instructions alone do not validate full inference support. [Repo](https://github.com/ASLP-lab/DiffRhythm2). | Pass after version correction |
| 54 / LeVo | Historical demo reachable; canonical release and license chain unresolved. Direct 404/401 results do not establish permanent disappearance, but justify conditional custody. Public v2-large metadata says unknown license. | Pass after citation correction |
| 55 / MuLaCover | Official released code/weights; Apache source, separately restricted noncommercial weights and outputs. Tested Ubuntu 24.04/PyTorch 2.10/CUDA 13/B300 is not proof of 24GB consumer performance. [Repo](https://github.com/HeartMuLa/MuLaCover). | Pass after label correction |
| 56 / Shao | Renamed public repo and linked public weight card. Weight metadata CC BY-NC 4.0; runtime warning and 24GB+ recommendation are explicit. Do not promise reproducibility across arbitrary CUDA stacks. [Repo](https://github.com/Shao-Music-AI/Shao), [weight metadata](https://huggingface.co/liujiafeng/Shao-MusicGeneration-v1.0/raw/main/README.md). | Pass after release correction |
| 57 / StepAudio 3 Music | Recent paper plus official provider-backed Space. The Space requires a backend key; that route does not establish downloadable music weights or self-hostable rights. [Official Space](https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music/blob/main/README.md?code=true). | Pass after separation from Shao |

## 4. VoiceStudio first-video sanity check

The saved transcript states “$99 a month” around 02:26. The independently opened official Pro page on October 8 instead lists **$99 per user/year**, and **$299 per user one-time Lifetime**, with three registered devices/concurrent uses per seat. It also says closed-source distribution and private hosting are excluded from those plans and speech-model licenses remain separate. These checked current prices resolve the narration/visible-slide conflict; they should still carry the access date. [Current vendor page](https://voicestudio.sh/pro).

The application's AGPL-3.0-only notice permits commercial/internal use of the application itself under its conditions, but explicitly does not clear downloaded model assets. Default OmniVoice weight restrictions and tokenizer terms remain relevant. The master correctly proposes evaluation rather than declaring production clearance or guaranteed replacement savings. [Current app notice](https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md), [OmniVoice card](https://huggingface.co/k2-fsa/OmniVoice).

The research appendix already records this corrected pricing and the distinction between application and model rights. No price correction is needed in the current master because it does not quote the video's disputed price.

## 5. Remaining gates

1. Inventory the Linux/Windows NVIDIA hardware before choosing local CUDA profiles or buying/renting compute.
2. Resolve intended personal versus company-hosted use for each selected weight license.
3. Run the proposed smoke/integration suite, then the fair-budget listening protocol. Author leaderboard scores remain external evidence, not this project's results.
4. Declare the working-PCM preservation domain in implementation tests; retain native artifacts and separately rendered exports.
5. Evaluate separation and generated replacement stems independently, including boundary listening and musical matching.

No load-bearing recommendation needs to be removed. The first pair of models is conditional; the scientific conclusion remains that actual quality, cost and hardware suitability are **unmeasured** until the benchmark is run.
