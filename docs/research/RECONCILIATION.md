# AURA research reconciliation: the verified evidence base

Status: synthesized reference, 2026-10-09, **revised the same day** after a critic pass and eight gap-research questions (see the Revision log at the end). It is the input to `/to-spec`, the ADRs in `docs/adr/` and the ticket DAG.
It is not a spec. The decisions in §6 are **proposals** until each is accepted as an ADR.

## Inputs

| Source | Files (this repo) | SHA-256 (prefix) |
|---|---|---|
| **GPT** (GPT-6.1 SOL): master plan plus its voice/video/experiments corpus | `sources/gpt-sol/Music-Gen-Master-Plan-v1-2026-10-08.md`. The companion corpus is now archived in `sources/gpt-sol/companion/`: `voice-studio-research.md` (`af79b0e0`), `video-analysis.md` (`1a90eb46`), `proposed-experiments.md` / `.json` (`0d342c36` / `80edee6a`), `FRAMING.md` (`8ddc23c4`), `generation-research.md` (`4cfd3451`), `suno-engineering-disclosures.md` (`37af2ba2`), `master-review-input.md` (`a4b2f792`) and the three independent reviews. The claims cited as **GSV-01…69** are archived verbatim, with their evidence pointers, in `sources/workflow-2026-10-09/extract-gpt-sol-voice-video.json` (`4a911ef6`). "GSV §n" means `voice-studio-research.md` §n; "MG-Enn" means `proposed-experiments.md`. GSV points are GPT's assertions: auditable now, but **UNVERIFIED** unless a verification row says otherwise. | `9152ea58` |
| **Kimi** (Kimi K3 swarm): "AURA plan of attack v1" | `sources/kimi-k3/AURA-plan-of-attack-v1.html`, `.extracted.txt` | `a7d31dc8`, `2c80c007` |
| **Fable** (Claude Fable 5.1): Suno teardown, spec, handoff | `sources/claude-fable/HANDOFF.md`, `SPEC.md`, `VIDEO-ANALYSIS.md`. Fable's suno-personal `CLAUDE.md` conventions are research input, not binding. | `be87e287`, `0bbb32d1`, `44ac814c` |
| **Verification pass** | Done 2026-10-09: 54 targeted questions in 8 clusters, each checked by a verifier against primary sources. An independent skeptic re-checked 23 of them (ace-1, 2, 3, 4, 6, 8; cost-1, 4; eng-1, 2, 3, 4; qe-1, 2, 3; sep-1, 2, 7; suno-1, 2, 5; voice-1, 2). Where the two disagreed (cost-1, eng-1, eng-3, sep-7), this document uses the skeptic's verdict as the **final verdict**. Every register claim now carries `verification_question`, `verifier_verdict`, `skeptic_checked` and `skeptic_verdict`. Raw outputs: `sources/workflow-2026-10-09/verify-primary.json` (`a4db572c`) and `verify-skeptic.json` (`cf0ba8fa`). Machine-readable register: [`evidence-register.json`](evidence-register.json). | n/a |
| **Gap research** (revision) | 8 questions raised by the critic (GAP-01…08), each checked by one verifier against primary sources, with **no skeptic pass**. Raw output: `sources/workflow-2026-10-09/verify-gap.json` (`5346a7ae`); register claims V-gap-1…8. The critic's own findings: `critic.json` (`964433fd`). | n/a |
| **Local measurement** | `df`, `sw_vers`, `sysctl`, `system_profiler`, run on this Mac on 2026-10-09; `df -h /System/Volumes/Data` repeated at 15:27Z for the revision | n/a |

## Labels

The labels follow JOVRA's research convention, extended for verification.

- **Verdicts.** **CONFIRMED** means a primary source says so. **CORRECTED** means a source's claim was partly wrong and the corrected value is given. **CONTESTED** means primary sources disagree, so the point is not fact. **REFUTED** means primary evidence contradicts the claim. **UNVERIFIABLE** means no primary source could be reached. **UNVERIFIED** means a source asserted it and this pass did not check it.
- **Kinds of number.** **VENDOR** is a figure from the maker, not measured by us. That includes a model's own authors scoring it on a benchmark they built or ran (YuE2 on WildSongBench). **COMMUNITY** comes from a third-party user or port. **COMPETITOR-RUN** is a benchmark run by the authors of a rival model. **MEASURED-LOCAL** was measured on this Mac today. **OWNER-REPORTED** came from Jon. **INFERRED** is our own arithmetic or reasoning.

**Nothing has been installed, generated or listened to.** Every quality, speed and memory figure below is VENDOR, COMMUNITY or COMPETITOR-RUN unless it is marked MEASURED-LOCAL. **Every quality figure that supports the chosen engine pair was produced by an interested party**: ACE's own self-scored reward models, and WildSongBench plus the expert-preference study, both run by the YuE2 authors. This document cites no independent human evaluation of ACE-Step 1.5 or YuE2.

---

## 0. Verdict

**No open-weights engine has been shown to match Suno v6, and the owner's "Suno 6.5" does not exist.** Suno's blog (to 2026-10-05) and release notes (to 2026-10-08) contain no v6.5, so v6 is the reference.

The strongest human evidence against parity comes from YuE2's own expert study, which is **VENDOR-run** (the YuE2 authors built and ran it). Listeners preferred Suno v6 over YuE2 best-of-8 by **59.3% to 31.6%**, while YuE2 best-of-8 and Suno v5 were level (40.4% vs 39.9%) ([arXiv 2609.33757v1 §4.1](https://arxiv.org/html/2609.33757v1)). AURA should therefore be a **multi-engine studio built on a capability registry, honest provenance and a blind listening harness**, not a wrapper around one model.

The proposed first pair **depends on who operates the work (Q3) and on the CUDA hardware (Q1)**:

- **ACE-Step 1.5 on the Mac, every lane.** MIT throughout, with native MLX upstream. It is fast, and it scores below Suno v5: [WildSongBench](https://huggingface.co/datasets/m-a-p/WildSongBench) SongBench Avg 6.01 vs 6.87, COMPETITOR-RUN by the YuE2 authors.
- **Individual lane: YuE2-3B on a CUDA worker.** It has the highest published open scores (WSB 6.73, VENDOR/self-run). Its **native, documented score input** (a caller-supplied two-voice ABC; GAP-02) fits Jon's hum-to-song goal, though it is conditioning, not exact rendering: 84% exact pitch on edited scores (VENDOR), Chinese and English only, about 6 minutes maximum. Its weights are CC BY-NC 4.0 with an *individual*-creator permission that does not cover LLC-directed work ([MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE); GAP-05).
- **LLC lane (which presumably includes Sabbath Echo): HeartMuLa 3B or MiniMax Music 3**, chosen by smoke test. HeartMuLa is the only non-ACE open vocal song model found with permissive (Apache-2.0) weights. MiniMax carries Community License obligations, is CUDA-only (its README says two GPUs; a single-GPU diffusers path contests that), and closed its hosted API to new users on 2026-08-20 ([MiniMax API ref](https://platform.minimax.io/docs/api-reference/music-generation)). **Neither offers a verified melody-score input**, so in the LLC lane only ACE cover can try to keep a hummed tune.

Four things block building today:

1. **The Mac's internal disk.** Free space read **2.0–5.5 GiB across the day** (4.5 GiB at 15:27Z; MEASURED-LOCAL), never the 8.5 GiB reported. It fluctuates rather than falls steadily.
2. **The Linux and Windows GPUs are unknown.** Neither machine is on the tailnet. YuE2 does not run on native Windows without patches; WSL2 is the practical route there (GAP-03).
3. **No verified path keeps a hummed melody through to a sung song.** A competitor's test found ACE cover keeps song identity poorly, and YuE2's score route is only self-reported.
4. **No hum transcriber is both license-clean and benchmarked on humming** (GAP-01). Basic Pitch is the only clean candidate with any humming figure (onset+pitch F1 0.27–0.43, COMMUNITY), so the human correction step carries the melody.

**Without a CUDA worker, every sung song would be ACE-only**, which breaks the owner's "not ACE-only" requirement. Metal ports of YuE2 and HeartMuLa exist but none has parity evidence (GAP-04). That outcome needs Jon's sign-off (Q14). It is not a routine fallback.

The first build is therefore:

1. Disk and hardware inventory.
2. A local hum benchmark that picks the transcriber and F0 tracker.
3. A 12-brief smoke benchmark that includes hum and MIDI fixtures.
4. The melody-seed flow, with **two candidates per request and blind A/B as the acceptance gate**.

Automatic scorers are diagnostics, and most of the good ones are noncommercial.

---

## 1. What all three sources agree on, with verification status

| # | Agreement | Sources | Status after verification |
|---|---|---|---|
| A1 | ACE-Step 1.5 belongs in the first build as the fast, controllable lane. It is below Suno v5. | GPT, Kimi, Fable | **CONFIRMED.** The paper's alignment numbers are self-scored ([2602.00744v3 Table 1](https://arxiv.org/html/2602.00744v3)). WildSongBench, run by the YuE2 authors, gives 6.0118 vs Suno v5 6.8721 (COMPETITOR-RUN, automatic). ACE's README places it "between Suno v4.5 and v5" (VENDOR, no published numbers). |
| A2 | Do not promise Suno-level quality from ACE. | all | **CONFIRMED** (same evidence). |
| A3 | A second, slower lane for quality sits beside ACE. Which engine fills it was disputed. | all | Agreed. The engine is resolved as a proposal in **D-02**. |
| A4 | The YuE family needs a 24 GB-class NVIDIA GPU. | GPT, Kimi (Fable said 16 GB) | **OPEN for YuE2.** 24 GB (plus 24 GB host RAM, Linux, BF16) is the vendor's *recommendation* ([generation.md](https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md)), not a measured floor. The vendor's own NVML peaks are 11.18 GiB typical and 14.08 GiB at maximum context ([HF card](https://huggingface.co/m-a-p/YuE2-3B); VENDOR). On a 16 GB card the pipeline caps PyTorch at about 14 GiB, so maximum context is borderline; `--budget`, fp8 and `--offload-ar` are built-in levers, and GGUF ports report 7.8–12.5 GiB (COMMUNITY). **Whether a 16 GB card qualifies is decided by a smoke run on that card** (GAP-03). Speed is **CORRECTED**: about 71 s per 3.6-min song on an RTX 4090 (VENDOR). Fable's "16 GB, ~5 min" has no primary source; it is not confirmed either. |
| A5 | Engines sit behind an abstraction. The Mac is the studio and control station, and CUDA engines run on a box or rental. | all | Agreed. See **D-01** and **D-03**. |
| A6 | 48 GiB of unified memory is not 48 GB of NVIDIA VRAM. | all | **CONFIRMED.** The Metal API reports `recommendedMaxWorkingSetSize` = 37.44 GiB on this M5 Pro (MEASURED-LOCAL by a verifier). |
| A7 | Stack shape: browser UI on localhost, FastAPI, SQLite metadata, audio on local disk, Python workers, SSE progress. | GPT, Kimi, Fable | Agreed. See **D-12**. |
| A8 | Each engine runs in its own pinned environment. | GPT, Kimi | **CONFIRMED necessary.** Torch pins conflict: ACE pins 2.7.1/2.10.0, YuE2 2.10.0, HeartMuLa <2.11, SGLang-Omni 2.13.0, and Shao uses NGC's 2.7.0a0 (see cost-4). |
| A9 | Open separators give fewer and different stems than Suno, with Demucs as the baseline and RoFormer as the upgrade. | all | **CONFIRMED with corrections.** See conflict row C23. Revision (GAP-06): Demucs's pretrained weights are research/personal-only per its author, so Demucs is a baseline for the individual and research lanes only. |
| A10 | Replacing a stem means a new lane plus "Copy to Main Track", which rebuilds the mix. Never layer over a mix that still contains the old part. | GPT, Fable, GSV | A design rule. Adopted in **D-06**. |
| A11 | Basic Pitch transcribes polyphonic audio to MIDI with pitch bends and works best on one instrument. | GPT, Kimi | **CONFIRMED.** Apache-2.0. The README says it "works best on one instrument at a time", and its training data includes iKala singing ([repo](https://github.com/spotify/basic-pitch)). Revision (GAP-01): 0.4.0 will not install on macOS arm64 under Python 3.12 ([#203](https://github.com/spotify/basic-pitch/issues/203)), and its only humming figure is onset+pitch F1 0.27–0.43 with offsets ignored ([arXiv 2410.05455](https://arxiv.org/abs/2410.05455), COMMUNITY). |
| A12 | A hum, voice memo or recorded-track seed is the feature closest to Jon's starting point, and **no source designed the full path**. | all | **CONFIRMED gap.** Addressed in **D-04**. |
| A13 | Generate several candidates and A/B them before committing one. | all | **CONFIRMED** as Suno's model: "Each time you generate, you make two songs" ([v6 FAQ](https://help.suno.com/en/articles/13924481)). |
| A14 | Section labels must survive tool boundaries. | all | Agreed. See **D-09** (one project graph). |
| A15 | Suno v6 shipped on 2026-09-09. | GPT, Kimi | **CONFIRMED** ([blog](https://suno.com/blog/introducing-v6)). Its variants are v6, v6-wild and v6-mini. "Core" is not an official name. |
| A16 | v5.5 (March 2026) added personalization: Voices, Custom Models, My Taste. | GPT, Kimi | **CONFIRMED** ([blog 2026-03-26](https://suno.com/blog/v5-5)). The mechanism is undisclosed. |
| A17 | Voice creation needs consent. | all | **CONFIRMED.** Suno's flow is detailed in C25. |
| A18 | Suno bought WavTool's browser DAW in 2025. | GPT, Kimi | **CONFIRMED**: 2025-06-30 ([blog](https://suno.com/blog/suno-acquires-wavtool)). |
| A19 | Suno pricing is Free, $10 Pro and $30 Premier, with download caps of 20 and 60 a month from 2026-09-03. | Kimi, Fable | **CONFIRMED** for monthly billing. Annual billing works out to $8/$24 a month. The $2.99 per extra download is **UNVERIFIABLE** ([pricing](https://suno.com/pricing)). |
| A20 | Simple mode returned 4 results (2× v4.5 + 2× v5.5). | Kimi, Fable | Tutorial-only and pre-v6. **Superseded**: v6 documents 2 songs per generation, and earlier models are retired. |
| A21 | Do not build on unofficial "Suno API" endpoints. | GPT, Kimi, Fable | Agreed. Reinforced by Suno's ToS (see **D-21**). |
| A22 | MiniMax Music 3 is under a custom Community License, not MIT. | GPT, Kimi | **CONFIRMED** ([LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE)). |
| A23 | HeartMuLa 3B and DiffRhythm 2 are Apache-2.0. | GPT, Kimi | **CONFIRMED with caveats.** At inference DiffRhythm 2 loads MuQ-MuLan-large, which is CC BY-NC. |
| A24 | Open Stable Audio 3 is instrumental-only and trained on licensed data. | GPT, Kimi | **CONFIRMED.** The prompting guide says "our models don't output intelligible vocals" ([guide](https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md)). |
| A25 | The SongGeneration / LeVo 2 license is unresolved. | GPT, Kimi | **Worse than unresolved.** The canonical sources are withdrawn (C20). |
| A26 | Exclude MusicGen (CC-BY-NC weights). | Kimi, Fable | **CONFIRMED** ([HF card](https://huggingface.co/facebook/musicgen-melody)). |
| A27 | Track licenses per component. A permissive code license does not clear weights. | GPT, Kimi | **CONFIRMED.** Dozens of cases in §4. |
| A28 | No foundation training from scratch. Escalate to training only when cheaper levers are measured and insufficient. | GPT, Kimi | Agreed. Cost figures are corrected in C45. |
| A29 | Local-first ownership: no credits, no caps, durable files, no accounts. | Kimi, Fable, GPT | Agreed. |
| A30 | RVC code is MIT, but that does not license singer models. | GPT, GSV, Kimi | **CONFIRMED.** The pretrained-weights license is itself contested (C24). |
| A31 | No source ran anything. | all | **CONFIRMED.** That remains true after this pass. |
| A32 | Personalization comes after selection and evaluation. | GPT, Kimi | Agreed. See **D-20**. |

---

## 2. Conflicts and how verification resolved them

Abbreviations: "n/s" means the source said nothing on the point. Each "verified answer" is the final verdict.

| # | Question | GPT | Kimi | Fable | Verified answer | Primary source |
|---|---|---|---|---|---|---|
| C1 | License of each ACE-Step 1.5 component | Repo and XL-SFT card MIT; other checkpoints unchecked | MIT, code and model | Weights unconfirmed | **CONFIRMED MIT, ungated** for every 1.5 DiT (2B and XL), LM, VAE, captioner and transcriber. The LMs are Qwen3 fine-tunes, and the bundled Qwen3-Embedding-0.6B is Apache-2.0, so keep the Apache notices when redistributing. ACE-Step-DAW is **AGPL-3.0**, and the CNY LoRA is OpenRAIL-M. | [LICENSE](https://github.com/ace-step/ACE-Step-1.5/blob/main/LICENSE), [HF API](https://huggingface.co/api/models?author=ACE-Step&full=true), [ACE-Step-DAW](https://github.com/ace-step/ACE-Step-DAW) |
| C2 | ACE VRAM and disk | XL ≥20 GB without offload, 12 GB with INT8+offload | <4 GB; XL 12–20 GB | <4 GB | **CORRECTED.** "<4 GB" only applies to CUDA Tier 1: 2B DiT alone, no LM, INT8 plus full offload. XL tiers are ≥12 (marginal), ≥16 (offload), ≥20 (none) and ≥24 GB (with the 4B LM). On **MPS, INT8 and offload are disabled**. Downloads: the main bundle is 10.09 GB, each native XL checkpoint 19.95 GB stored F32 (the card's "bf16 ~18.8 GB" label is wrong), and diffusers XL bf16 about 11.1–11.5 GB. | [GPU_COMPATIBILITY.md](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/GPU_COMPATIBILITY.md), [gpu_config.py](https://github.com/ace-step/ACE-Step-1.5/blob/main/acestep/gpu_config.py), [HF tree](https://huggingface.co/api/models/ACE-Step/acestep-v15-xl-sft/tree/main) |
| C3 | ACE on Apple Silicon | Upstream documents MLX/MPS | "clockworksquirrel" fork at ~25 s/song (and, elsewhere, "official MLX") | Unverified; Phase 0 decides | **CORRECTED.** Upstream has native MLX for the DiT, VAE and LM, plus MPS, with macOS launch scripts. The fork is optional, and its 25 s is for a **30-second clip** on an M3 Pro (fork-claimed). Upstream publishes no Mac timings. On an M5 Max, XL-SFT/base output was garbled because DCW is on by default. The CLI/API fix landed **after v0.1.8** (#1282, 2026-08-28). | [INSTALL.md](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INSTALL.md), [#1259](https://github.com/ace-step/ACE-Step-1.5/issues/1259), [#1282](https://github.com/ace-step/ACE-Step-1.5/pull/1282), [fork](https://github.com/clockworksquirrel/ace-step-apple-silicon) |
| C4 | ACE tasks per checkpoint | lego/extract/complete are base-only; turbo CFG forced to 1 | cover, repaint, extract and timbre-clone; turbo 8-step, SFT 50-step | One engine covers every primitive | **CORRECTED (GPT right).** base and xl-base do every task. SFT and turbo (incl. XL) do only text2music, cover (+cover-nofsq) and repaint. On turbo, `guidance_scale` is auto-corrected to 1.0, but `shift` is not auto-set (use 3.0). "Complete" means *add accompaniment*. Time extension is done with repaint. `reference_audio` sets a global timbre/style, and the maintainer says **no direct voice cloning** (#776). | [INFERENCE.md](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/INFERENCE.md), [#776](https://github.com/ace-step/ACE-Step-1.5/issues/776) |
| C5 | ACE quality band | Unmeasured; assign no bands | v4.5–v5 band; WildSongBench 6.01 vs 6.87 | "Good, not v5.5" | **CONFIRMED.** Style/lyric alignment of 39.1/26.3 vs Suno v5's 46.8/34.2 uses ACE's proprietary reward models. WildSongBench SongBench Avg is 6.0118 vs 6.8721 (COMPETITOR-RUN, automatic). | [paper](https://arxiv.org/html/2602.00744v3), [WSB results](https://huggingface.co/datasets/m-a-p/WildSongBench/blob/main/benchmark/results.md) |
| C6 | ACE training data | ~20M pairs; licensed/PD/synthetic per the authors | 6M stem-separated tracks | n/s | **Both figures are in the paper.** A 27M-sample corpus; ~20M pretraining pairs; the omni-task phase adds 6M stem-separated tracks; 2M SFT. The "licensed / royalty-free / synthetic MIDI" claim appears **only on the HF cards**, not in the paper. It is VENDOR. | [paper §2/§4](https://arxiv.org/html/2602.00744v3), [HF card](https://huggingface.co/ACE-Step/Ace-Step1.5) |
| C7 | ACE LoRA cost | n/s | 8 songs in ~1 h on a 3090 / 12 GB | n/s | **CONTESTED.** The README says 12 GB on a 3090. The LoRA tutorial says 16 GB minimum, ~17 GB typical, and that LoKr cuts about 1 h to ~5 min. A 2026-09-22 report of all-NaN gradients on M5 Max MPS is unresolved. | [README](https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md), [LoRA tutorial](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/LoRA_Training_Tutorial.md), [#619](https://github.com/ace-step/ACE-Step-1.5/issues/619) |
| C8 | Hum to song via ACE cover | No hum path | Basic Pitch → MIDI → sampler, or MusicGen-melody (which Kimi also excludes) | Cover at high strength on the hum | **CONTESTED.** The vendor docs say cover keeps "note direction and pitch". The maintainer says it "does not preserve the exact melody note-for-note" (#972). In the YuE2 authors' SHS100K test, ACE XL-SFT cover at strength 0.8 scored **Hit@1 2.4%** and SongEcho 48.4% (both COMPETITOR-RUN), against 71.3% for YuE2 with a score (VENDOR, self-reported). It has not been tested on hums, and one user reports failure on a hum (#1100). | [Tutorial.md](https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md), [#972](https://github.com/ace-step/ACE-Step-1.5/issues/972), [YuE2 Table 5](https://arxiv.org/html/2609.33757v1) |
| C9 | YuE / YuE2 license | Code Apache; weights CC BY-NC + individual permission; LLC separate | Apache-2.0 | YuE 7B Apache | **CORRECTED.** GPT is right for YuE2 and Fable is right for YuE1. YuE2-3B/Vae weights are CC BY-NC 4.0 plus a **GitHub-only** "Individual creator permission" (2026-09-16), which excludes "commercial use of the model weights by companies". The HF LICENSE copies are plain NC. YuE1 weights are Apache-2.0. SheetSage2 and MERT2 are plain NC. Revision (GAP-05): the permission covers outputs Jon generates "in an individual capacity", including licensing them to clients; LLC-directed generation is not covered; the single-member-LLC case is unanswered; the README and MODEL_LICENSE name different licensing contacts. | [MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE), [HF LICENSE](https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE), [YuE-v1](https://github.com/multimodal-art-projection/YuE/tree/YuE-v1) |
| C10 | YuE hardware and speed | Linux, Py 3.12, BF16 24 GB, one request at a time | YuE 24–80 GB, 15 min (H800) / 36 min (4090); YuE2 24 GB+, 15–36 min | YuE 7B 16 GB, ~5 min | **CORRECTED.** YuE2 takes ~71 s per 3.6-min song on an RTX 4090 at 11.18 GiB peak, 14.08 at maximum context (VENDOR). Officially it *recommends* Linux, 24 GB and 24 GB host RAM; whether 16 GB qualifies is **open** (A4). The 15/36-min figures are YuE1 extrapolations. Fable's figure matches no source. On Mac it is unofficial, with open bugs: silent BF16 corruption on MPS (#176, fixed only in torch ≥2.13, which main does not pin) and Metal memory runaway (#187). Native Windows needs patches; WSL2 works with raised memory (GAP-03). | [YuE2 card](https://huggingface.co/m-a-p/YuE2-3B), [YuE-v1 README](https://github.com/multimodal-art-projection/YuE/tree/YuE-v1), [#176](https://github.com/multimodal-art-projection/YuE/issues/176), [#187](https://github.com/multimodal-art-projection/YuE/issues/187) |
| C11 | YuE2 vs Suno | Experts preferred v6 59.3% vs 31.6% | Best-of-8 6.96 beats v5's 6.87 | n/s | **CORRECTED; both partly right.** Both measurements are **VENDOR (self-run)** for YuE2: the YuE2 authors built WildSongBench and ran the expert study. On automatic SongBench: YuE2 Bo8 6.9632 > v5 6.8721 > v6 6.5562. Expert preference: v6 beats YuE2 Bo8 59.3% vs 31.6%; v5 vs YuE2 Bo8 is a tie at 40.4% vs 39.9%; YuE2 beats v4.5 57.3% vs 30.5%. The paper treats expert listening as its primary evidence. The Bo8 candidates were selected with SongBench Musicality → Q3O → PER; SongBench is academic-only and Q3O needs an 80 GB GPU, so AURA cannot reproduce the 6.96 under D-05. | [arXiv 2609.33757v1](https://arxiv.org/html/2609.33757v1), [benchmarks.md](https://github.com/multimodal-art-projection/YuE/blob/main/docs/benchmarks.md) |
| C12 | YuE2 training data | ~346k h | "Primarily CC0 + synthetic"; YuE scale 650k h | n/s | **CONFIRMED both.** About 346,000 h, "primarily on CC0 music and synthetic data" licensed from Tokenwave.AI. The 650k h of in-the-wild internet music is **YuE1**. | [YuE2 App. C](https://arxiv.org/html/2609.33757v1), [YuE1](https://arxiv.org/abs/2503.08638) |
| C13 | How much best-of-n helps | Separate equal-candidate and equal-compute tracks; keep rejects | Closes ⅓–½ of the gap; Suno hides 2–4 survivors | Always 2 | **REFUTED (⅓–½).** Going from 2 to 8 candidates moved average expert preference against six proprietary systems from 48.0% to 48.4%, and against v6 it *fell* from 40.0% to 36.1%. SongBench rose 6.73 → 6.96. Suno documents 2 songs per generation. Hidden internal ranking is **UNVERIFIABLE**. | [YuE2 Tables 21–22](https://arxiv.org/pdf/2609.33757v1), [Suno v6 FAQ](https://help.suno.com/en/articles/13924481) |
| C14 | Scorers for reranking and reward | SongEval license conflict; FAD/CLAP are diagnostics; SongPrep academic | audiobox-aesthetics + SongEval + MuLan-CLAP + lyric-WER, also as DPO reward | n/s | **CORRECTED.** Shippable: audiobox-aesthetics (CC-BY-4.0), LAION-CLAP (CC0, Apache ports), Whisper (MIT), Qwen3-ASR (Apache). **Noncommercial:** SongEval checkpoint (CC-BY-NC-SA per the maintainer, [#8](https://github.com/ASLP-lab/SongEval/issues/8)), MuQ/MuQ-MuLan (CC-BY-NC), SongBench (academic-only). audiobox scores at 16 kHz and MuQ at 24 kHz, so none of them sees content above 8–12 kHz. HeartMuLa trained DPO on SongEval/AudioBox and then topped SongEval while ranking last on prompt control, which is reward-hacking evidence. | [audiobox](https://github.com/facebookresearch/audiobox-aesthetics), [MuQ](https://github.com/tencent-ailab/MuQ), [CLAP](https://github.com/LAION-AI/CLAP), [SongBench](https://github.com/Tencent/SongBench) |
| C15 | Initial engine set | ACE + MiniMax (YuE2 as substitute); install one challenger at a time | ACE turbo/SFT + YuE2 batch | ACE only, YuE 7B fallback | **Proposal in D-02, now lane-conditional**: ACE on the Mac in every lane; YuE2 on CUDA for the individual lane; HeartMuLa or MiniMax (by smoke) for the LLC lane. The deciding facts: MiniMax's hosted API is closed to new users and it is CUDA-only; HeartMuLa is the only non-ACE vocal model with permissive weights; on WSB, MiniMax 6.28 and HeartMuLa 6.25 are COMPETITOR-RUN by YuE2's authors, while YuE2's own 6.73 is VENDOR (self-run). | [MiniMax API](https://platform.minimax.io/docs/api-reference/music-generation), [WSB results](https://huggingface.co/datasets/m-a-p/WildSongBench/blob/main/benchmark/results.md) |
| C16 | MiniMax license and hardware | Community License; CUDA; 57.4 GB; the HF MPS helper is no evidence | "API / weights", $20M cap | n/s | **CORRECTED.** The license is confirmed, including AUP #11, which requires a **"machine-generated" disclosure** on public content. Repo is 57.35 GB, of which the diffusers subset is ~28.5 GB. Single GPU at ~23 GB bf16 (8 GB with group offload) through **diffusers ≥0.40.0**; the PR-commit pin is obsolete. The README says "two CUDA GPUs" for SGLang-Omni, which is **CONTESTED**. No official Mac path. Native rate is 32 kHz, but the diffusers docs say the vocoder is 44.1 kHz (**CONTESTED**). | [HF card + LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-Music3), [GitHub](https://github.com/MiniMax-AI/MiniMax-Music3), [diffusers v0.40.0](https://github.com/huggingface/diffusers/releases/tag/v0.40.0) |
| C17 | HeartMuLa | 3B released; 7B unreleased; MuLaCover NC | ~8 GB; "proven" reference webapp | n/s | **CONFIRMED (GPT).** HF returns 401 for 7B. There is no official 8 GB figure. RTF ≈ 1.0 (VENDOR); the FAQ suggests splitting across 2 GPUs or `--lazy_load`. HeartMuLa-Studio is **community-made with no LICENSE file**. | [heartlib](https://github.com/HeartMuLa/heartlib), [HeartMuLa-Studio](https://github.com/fspecii/HeartMuLa-Studio) |
| C18 | Stable Audio | SA3 Small CPU 120 s; Medium CUDA 380 s; gated license | ~8 GB, fast on Mac, "open weights" | "Stable Audio Open" rejected for its 47 s cap | **CONFIRMED (GPT), plus:** Medium runs **officially through MLX**: 380 s of audio in 47.8 s at 5.05 GB on an M4 Pro 48 GB (VENDOR). The license is the Stability Community License plus Gemma terms (gated). SAO 1.0's 47 s cap is correct, but SA3 supersedes it. No "Stable Audio Open 2.0" exists. | [stable-audio-3](https://github.com/Stability-AI/stable-audio-3), [MLX README](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/mlx/README.md) |
| C19 | DiffRhythm 2 | Extension and instrumental still TODO | 8 GB+, good for instrumentals | n/s | **CONFIRMED (GPT).** Instrumental is still unchecked in the TODO list. The 8 GB figure is from v1. It needs MuQ-MuLan (CC BY-NC). The repo has been dormant since 2025-11-09, and there is no MPS path. | [DiffRhythm2](https://github.com/ASLP-lab/DiffRhythm2) |
| C20 | LeVo 2 access | GitHub 404, HF 401 | GitHub-vs-HF license conflict; verify | n/s | **UNVERIFIABLE; canonical sources withdrawn.** The GitHub repo is gone, HF returns 401, and the Space redirects to SongPrep. The lglg666 mirror says "unknown", and mirror license text says research/education only. | [GitHub](https://github.com/tencent-ailab/SongGeneration), [lglg666](https://huggingface.co/lglg666/SongGeneration-v2-large) |
| C21 | Kimi's audit of Fable | n/s | Fable hallucinated "Melodyssey" and "Stable Audio Open 2.0" | n/a | **Not supported by the archived Fable files.** A grep of `sources/claude-fable/*` finds neither name (MEASURED-LOCAL). No "Melodyssey" model exists on HF or arXiv. Fable's "Stable Audio Open, 47 s cap" matches SAO 1.0. Kimi may have audited a different Fable artifact. | local grep; [Stability SAO](https://stability.ai/news-updates/introducing-stable-audio-open) |
| C22 | How Suno makes stems | Regenerated, not extracted | 8 stems; phantom reverb; ~2% replacement success | Demucs-style separation, 8 stems | **CORRECTED (GPT right).** "Suno listens to it and regenerates each stem from scratch." Auto Split gives up to **12** stems. Advanced Split offers ~100 instruments and is Premier-only. "8" was the count detected on one demo song. The phantom reverb and ~2% claims have **no source**. | [Suno blog 2026-06-11](https://suno.com/blog/stem-separation-updates), [release note](https://about.suno.com/release-notes/advanced-stems) |
| C23 | Which separator | Demucs as a pinned baseline (archived); RoFormer checkpoint rights | htdemucs_6s/ft give a "clean 6-way"; demucs-mlx 73× | htdemucs_6s including "bvocals?" | **CORRECTED.** Demucs is **maintained** at adefossez/demucs v4.1.0 (2026-07-11), with safetensors on HF. Revision (GAP-06): its author has stated three times that the pretrained weights are for research or personal use only ([#327](https://github.com/facebookresearch/demucs/issues/327), [#384](https://github.com/facebookresearch/demucs/issues/384), [#508](https://github.com/facebookresearch/demucs/issues/508)), and removed `license: mit` from the HF cards on 2026-08-31. htdemucs and htdemucs_ft give **4** stems. 6s adds guitar and piano but has **no backing vocals**, and piano is weak. The best open 6-stem model (BS-RoFormer SW) has an **unknown license**, and its guitar 9.01 / piano 7.80 SDR is a near tie with Logic Pro 11.2's Stem Splitter. demucs-mlx now claims 114× warm on a 40-core M4 Max (VENDOR). | [adefossez/demucs](https://github.com/adefossez/demucs), [demucs-mlx](https://github.com/ssmall256/demucs-mlx), [MVSep guitar](https://mvsep.com/quality_checker/leaderboard/guitar/), [SW mirror](https://huggingface.co/FractalSurfer/BS-RoFormer-SW-6stem) |
| C24 | Voice and cover stack | Native identity vs adapter vs conversion tested separately; DiffSinger | Seed-VC (GPL) / RVC v2 (MIT, trains in 5–15 min); efegen/rvc-pipeline | ACE timbre cloning | **CORRECTED.** Seed-VC is **archived**, GPL-3.0 for code *and* weights. efegen/rvc-pipeline **does not exist** (404). RVC wants 10–50 min of *data* and has no official training-time figure; release 2.3.260718 **dropped macOS** (the Applio fork has MPS). The HF license text for RVC's base and rmvpe weights adds "本软件仅供研究使用" (research use only), so it is **CONTESTED**. ACE does not do direct voice cloning. | [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI), [lj1995 LICENSE](https://huggingface.co/lj1995/VoiceConversionWebUI), [Applio](https://github.com/IAHispano/Applio), [seed-vc](https://github.com/Plachtaa/seed-vc) |
| C25 | Voice consent gate | Registry with verification phrase | pyannote speaker verification | Checkbox + `consent_at` | **CORRECTED.** Suno's flow: record a sung sample (help article: 15 s–4 min, best 2 min; product page: ≥10 s, so Suno contradicts itself), speak a displayed random phrase, have it **compared to the singing for same speaker**, then tick a rights checkbox; 18+ only. An embedding model can do the speaker match. Checking the phrase needs ASR. A checkbox alone is weaker than Suno's gate. | [Suno help 11362369](https://help.suno.com/en/articles/11362369), [WeSpeaker](https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM) |
| C26 | Sections and lyric alignment | SOFA after ASR + human review; SongPrep academic | all-in-one + WhisperX at ±50 ms | LLM heuristic, then all-in-one/msaf | **CORRECTED.** WhisperX ±50 ms on singing has no source: the paper evaluates speech only with a 200 ms collar. Its fr/de/es/it aligners are CC BY-NC, and it runs CPU-only on Mac. all-in-one is MIT, stale (2023), with no MPS. msaf outputs cluster IDs, not verse/chorus. SOFA's only English checkpoint is community-made. | [WhisperX](https://github.com/m-bain/whisperX), [paper](https://arxiv.org/html/2303.00747), [all-in-one](https://github.com/mir-aidj/all-in-one), [SOFA](https://github.com/qiuqiao/SOFA) |
| C27 | Mastering chain | Measure with BS.1770-5; keep a dry export; upsampling changes the container | Matchering + pyloudnorm to −14 LUFS / −1 dBTP + Apollo/AudioSR (MIT) | None | **CORRECTED.** Matchering is GPL-3.0 and matches a reference track. pyloudnorm implements **BS.1770-4**, not -5; whether the two revisions give identical integrated loudness for stereo programme is **UNVERIFIED** (X-47). pyloudnorm has **no true-peak meter**. Apollo is **CC BY-SA 4.0** and is a 44.1 kHz MP3-restoration model, not a 48 kHz upsampler. AudioSR is generative and synthesizes the top octave. | [matchering](https://github.com/sergree/matchering), [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm), [Apollo](https://github.com/JusperLee/Apollo), [BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en) |
| C28 | Is v6 better than v5? | YuE2 study implies v6 > v5 | v6 "muffled", below v5 on WSB, Arena #1 at 1142 | n/s | **CONTESTED.** On automatic WSB, v6 (6.56) < v5.5 (6.72) < v5 (6.87). Experts indirectly prefer v6 (no direct head-to-head). On the Artificial Analysis Vocal v1.1 board, v6 is #1 at 1142 ±15 (recruited panel; MiniMax Music 3.0 anchored at 1000). The backlash is anecdotal. The "v5 1293 Elo" figure appears in no primary source. | [AA vocals](https://artificialanalysis.ai/music/leaderboard/vocals), [YuE2 paper](https://arxiv.org/html/2609.33757v1) |
| C29 | The quality target | Acceptance criteria; no percentages; no v6.5 | "v5 parity on your genres" | Do not promise v5.5 | **No v6.5 exists.** Treat v6 as the operational reference (**D-10**). | [Suno blog](https://suno.com/blog), [release notes](https://suno.com/release-notes) |
| C30 | Which feature baseline defines parity | v6 + Studio 2.0 | Pre-v6 tutorial | Pre-v6 tutorial (v4.5/v5.5, Studio 1.2) | **v6 + Studio 2.0 is current.** All pre-v6 models are retired. Studio 1.2 dates from 2026-02-06. | [What's new in v6](https://help.suno.com/en/articles/13924801), [Studio 2.0](https://suno.com/blog/studio-2) |
| C31 | v6 training data | "Partner-developed", flagged by GPT as unsourced | Licensed WMG/BMG/Believe catalogs | n/s | **CORRECTED.** "Partner-developed" *is* Suno's own wording ("developed with our industry partners"). The CPO told Axios v6 used licensed Warner music plus user data, with BMG and Believe catalogs being added after launch. UMG and Sony sued again on 2026-09-18 (1:26-cv-14275), alleging taint (an allegation). | [Suno blog](https://suno.com/blog/introducing-v6), [complaint](https://www.musicbusinessworldwide.com/files/2026/09/26-cv-14275-Dkt.-1-Complaint.pdf) |
| C32 | Suno architecture and data | 2024 interview; v5.5/v6 recipe not established | Speculative 4-stage pipeline, called "verified" elsewhere; breach figures | n/s | **CONFIRMED (GPT).** The interview describes end-to-end next-token prediction over audio tokens. The 4-stage claim is **unsupported**. The 404 Media breach figures (2,013,545 clips / 113,879 h YouTube Music, and more) are confirmed *as reported* (paywalled, leaked material). | [Latent Space](https://www.latent.space/p/suno), [404 Media](https://www.404media.co/hack-reveals-suno-ai-music-generator-scraped-youtube-deezer-and-genius/), [AB 2013](https://help.suno.com/en/articles/9709569) |
| C33 | Suno personalization mechanism | Undisclosed | Per-user LoRA from ≥6 tracks; "RLHF-as-product" | n/s | **CORRECTED.** As few as 6 songs, up to 3 models, now tuning v6. The mechanism is undisclosed, so "LoRA" is speculation. | [Custom Models help](https://help.suno.com/en/articles/11362497), [pricing](https://suno.com/pricing) |
| C34 | Legal and market claims | Pond5/Envato bans; USCO Part 2 | RIAA suit; Warner settlement + Songkick; GEMA; Jamendo €17.8M; Udio downloads off; $5.4B; ARR | n/s | **CONFIRMED**, except: Suno's **ARR is undisclosed** (UNVERIFIABLE); €17.8M is Jamendo's *claimed* damages; the GEMA judgment (LG München I, 42 O 763/25, 2026-07-31) is **not final**. Valuation is $5.4B post-money (Series D, 2026-06-03). | [WMG](https://www.wmg.com/news/warner-music-group-and-suno-forge-groundbreaking-partnership), [GEMA/LG München](https://www.justiz.bayern.de/gerichte-und-behoerden/landgericht/muenchen-1/presse/2026/16.php), [Udio](https://www.udio.com/blog/a-new-era), [Series D](https://suno.com/blog/series-d-announcement), [Pond5](https://www.pond5.com/help/en/articles/10086182-does-pond5-allow-ai-generated-content-for-licensing), [Envato](https://help.author.envato.com/hc/en-us/articles/13313674070681-AI-generated-content-policy-for-Market-and-Elements) |
| C35 | Rights lane | Record the operator entity (individual vs LLC) | "Low risk for personal use" | n/s | **GPT confirmed.** YuE2 excludes companies. MiniMax places obligations on commercial products. SA3 is free under US$1M revenue (registration required). Suno's ToS forbids using its Output to "power, enable or train" other AI or to compete. | [MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE), [stability.ai/license](https://stability.ai/license), [Suno terms](https://suno.com/terms-september-2026) |
| C36 | Data for adapters and DPO | Owning a WAV is not training permission | CC0/CC-BY via MTG-Jamendo CC cores and FMA | n/s | **CORRECTED.** MTG-Jamendo is ~70% NC, ~34% ND, with **0 CC0** tracks, and Jamendo added a non-commercial-research-only notice on 2025-07-02. FMA is "meant for research purposes". | [mtg-jamendo](https://github.com/MTG/mtg-jamendo-dataset), [FMA](https://github.com/mdeff/fma) |
| C37 | Hosted music APIs | Mureka 9.5, SA3 Large, StepAudio Space | ElevenLabs is "the only real music API"; Mureka $10 unlimited + MIDI | Suno has no public API | **CORRECTED.** Several APIs are live: Mureka (model pinnable to `mureka-9.5`; stems with MIDI; region edit), Gemini Lyria 3.5 ($0.08/song), Stability SA3, and paid ElevenLabs Music. Mureka's MIDI/WAV export is Premier-only, not $10 unlimited. MiniMax's API is closed to new users. | [Mureka API](https://platform.mureka.ai/docs/api/operations/post-v1-song-generate.html), [Lyria](https://ai.google.dev/gemini-api/docs/music-generation), [ElevenLabs Music](https://elevenlabs.io/docs/overview/capabilities/music) |
| C38 | Frontend stack | React/TS, Web Audio/AudioWorklet | React + wavesurfer-multitrack | Next.js 15 + Tailwind + shadcn | **Proposal in D-12/D-13.** The fact that settles it: wavesurfer-multitrack is **dormant** (npm 0.4.12, 2024-07), pinned to wavesurfer ^7, imports a file removed in v8, and syncs tracks with a **0.3 s tolerance**. | [wavesurfer-multitrack](https://github.com/katspaugh/wavesurfer-multitrack), [wavesurfer 8.0.0](https://github.com/katspaugh/wavesurfer.js/releases/tag/8.0.0) |
| C39 | DAW / audio engine | Two clocks; measure latency; effects after an equivalence test | "The UI is the easy 20%" | wavesurfer or custom canvas | **CORRECTED toward GPT.** Measured browser round-trip latency on a MacBook Pro 2021: Chrome 52.33 ms, Safari 100.02 ms, Firefox 38.89 ms (WAC 2025, peer-reviewed). WebKit ignores `latencyHint` and has no `setSinkId`. Chromium's macOS default output buffer is 256 frames. Web Audio 1.1 is a Working Draft (2026-09-22). All of these figures come from **one 2021 MacBook Pro**; Windows and Linux Chrome are unmeasured (X-49). | [WAC 2025 data](https://doi.org/10.5281/zenodo.17642262), [WebKit source](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/Modules/webaudio/AudioContext.cpp), [Web Audio](https://www.w3.org/TR/webaudio/) |
| C40 | Desktop shell | Evaluate after the browser proof | Tauri 2 (42 MB vs Electron 168 MB) | n/s | **CORRECTED.** 42/168 MB are **RAM** figures from a blog, not bundle sizes. A minimal Tauri app can be under 600 KB, while Electron's arm64 runtime zip is 124 MB. On macOS, Tauri uses WKWebView, which has the audio gaps above. Tauri v3 alpha adds a CEF (Chromium) runtime. | [Tauri webviews](https://v2.tauri.app/reference/webview-versions/), [Electron 44.7.0](https://github.com/electron/electron/releases/tag/v44.7.0), [Tauri releases](https://github.com/tauri-apps/tauri/releases) |
| C41 | Job queue | Honest states, atomic commits, one heavy model resident | asyncio.Queue + SSE | SQLite-polled table | A design choice: **D-12** uses a durable SQLite table with honest states and SSE. asyncio.Queue alone does not survive a restart (INFERRED). | n/a |
| C42 | What gates UI work | MG-E01: two adapters pass 12 briefs before any studio UI | Phase 0 in days 1–3 | ~1 h smoke test; scaffolding may run in parallel | **Proposal in D-04/D-10.** Disk and inventory come before any smoke test, because nothing installs today (MEASURED-LOCAL). | local `df` |
| C43 | Evaluation protocol | 48 briefs / 12 smoke (the generation module says 40×4 seeds and "three engines") | LUFS-matched A/B vs Suno; exit at ≥70% win rate vs stock ACE | One prompt | **Proposal in D-10** (48/12; two engines). | n/a |
| C44 | Inference cost | Hypothetical $1/h | $1.10/h; $0.01–0.03 per song; <$15/mo for 500 songs | n/s | **CORRECTED.** RunPod serverless 4090 PRO at **$1.10/h** is confirmed. Per candidate, INFERRED: ACE ~$0.002–0.003 (VENDOR "under 10 s on an RTX 3090"), YuE2 ~$0.009–0.022 (VENDOR 71 s per 3.6-min song on a 4090). **MiniMax ~$0.03–0.13 is COMMUNITY-derived and on mismatched hardware**: an audio.cpp GGUF benchmark gives RTF 0.74 (Q4/Q8) to 1.39 (BF16) on an **RTX 5090** for a **30-s clip**, extrapolated to a 3.5-min song and priced at RunPod serverless 5090 ($1.58/h) and Vast 5090 rates. That is a quantized community port, not the official pipeline (which the README says needs two GPUs), on a different card from the 4090 tier used for the others. Treat it as order-of-magnitude only. "<$15/mo" holds only for ACE-class bursts. YuE2 best-of-8 at 500 songs is about $36–87/mo. | [RunPod](https://www.runpod.io/pricing), [Vast](https://vast.ai/pricing), [Modal](https://modal.com/pricing) |
| C45 | Training cost | Foundation training needs a decision packet | ACE-scale 46K A100-h ($55–76K); YuE $200–300K+, 512 GPUs | n/s | **CORRECTED.** 46K A100-h is **ACE v1** (31.7K DiT + 14.4K VAE). v1.5 compute is not stated, and the dollar figures are derived. YuE1 trained on 512 H800s and YuE2 on 64; neither states a cost. | [ACE v1](https://arxiv.org/html/2506.00045), [YuE1](https://arxiv.org/html/2503.08638), [YuE2](https://arxiv.org/abs/2609.33757) |
| C46 | CUDA stack | Per-engine pinned envs | cu126 vs cu128, sm_120, flash-attn | n/s | **CORRECTED.** cu128 wheels **ended at torch 2.11** (cu129 at 2.13). Torch 2.14.1 ships cu126 (no Blackwell), cu130 and cu132. FA2 prebuilt wheels are Linux-only, torch ≤2.9. Shao is pinned to NGC 25.02. Drivers: CUDA 12.8 needs ≥570, CUDA 13.x needs R580+. | [PyTorch RELEASE.md](https://github.com/pytorch/pytorch/blob/main/RELEASE.md), [flash-attn](https://github.com/Dao-AILab/flash-attention/releases/tag/v2.8.3.post1) |
| C47 | Owner hardware and disk | M5 Pro 48 GiB verified; disk not addressed | M3 Pro 36 GB assumed | "macOS arm64" only | **MEASURED-LOCAL.** Mac17,8, Apple M5 Pro (18 CPU, 20 GPU cores), 48 GiB, **macOS 26.6.2 (25G83)**. Internal free space read 5.5, 4.0 and **2.0 GiB** during the pass and **4.5 GiB** at 15:27Z: it fluctuates between about 2 and 5.5 GiB. External `/Volumes/Backup Plus` (exFAT, USB 5 Gb/s, "BUP Slim", probably HDD) has **1.2 TiB free**. No Linux or Windows machine is reachable. | local |
| C48 | Narration lane priority | Narration pilot is the fastest defensible route; separate service | n/s | n/s | **Proposal in D-08.** | n/a |
| C49 | UX direction | Listening-first, capability-aware | Mirror Suno's frames | Mirror Suno's look and exact control names | **Proposal in D-12.** Do not imitate Suno's branding or look. Use plain, standard names where they help. | n/a |
| C50 | Watermark vs provenance | C2PA-style export manifest | No watermark | n/s | **Proposal in D-09.** Use an export manifest with an AI-disclosure field (required for MiniMax output by AUP #11) and no forced watermark. Chatterbox embeds a Perth watermark in every output. | [MiniMax LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-Music3/blob/main/LICENSE), [Chatterbox](https://github.com/resemble-ai/chatterbox) |
| C51 | Suno audio upload limit | 30 min (v6 demo) | n/s | 8 min (Free) | **CONFIRMED both.** 8 min on Free, 30 min on Pro and Premier. | [pricing](https://suno.com/pricing) |
| C52 | Studio version and tier | Studio 2.0 shipped 2026-08-13 | n/s | Premier-only; tutorial shows Studio 1.2 | **CONFIRMED.** Studio 2.0 is Premier-only, with 32-bit/48 kHz stem export and MIDI clips usable as prompts. | [Studio 2.0](https://suno.com/blog/studio-2) |
| C53 | GPT's internal inconsistencies | 48 vs 40 briefs; 8 vs 16 tracks for the audio gate | n/a | n/a | **Resolved in D-10 and D-13.** | n/a |
| C54 | The Sabbath Echo Scripture rule | "Never TTS Scripture"; Bible Brain (from memory) | n/s | n/s | **UNVERIFIABLE as a current rule.** The `sbe_app` ADR (2025-12-17) routes "ElevenLabs for EGW, AudioVerse for Bible". That is a design decision, not a stated prohibition, and it names AudioVerse, not Bible Brain. | `Navigata1/sbe_app` `docs/architecture-decisions.md` (private) |
| C55 | Current ElevenLabs baseline | v3/v4 do not support SSML breaks; credits vary by model | n/s | n/s | **CONFIRMED.** Breaks up to 3 s, not supported on v3/v4. List prices per 1K chars: v3 / Multilingual v2 / v4 $0.08; Flash / Turbo / v4 Turbo $0.04 (v4 promo pricing until Oct 12). The ~$25k spend stays **OWNER-REPORTED**. | [best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices), [API pricing](https://elevenlabs.io/pricing/api) |

### 2.1 Gap research (revision, 2026-10-09)

The critic found eight questions the first pass had not asked. Each was checked by one verifier against primary sources, with no skeptic pass. Full findings: `sources/workflow-2026-10-09/verify-gap.json`; register claims V-gap-1…8.

| # | Question | Verdict | Finding | What it changes |
|---|---|---|---|---|
| GAP-01 | Is there a license-clean, Mac-ready hum transcriber and F0 tracker with a humming benchmark? | **CORRECTED** | No transcriber meets all three conditions. Basic Pitch (Apache-2.0) is the only clean one with a humming number: onset+pitch F1 0.434 octave-invariant / 0.268 octave-aware, offsets ignored, on relabelled HumTrans ([arXiv 2410.05455](https://arxiv.org/abs/2410.05455), course project, COMMUNITY). It will not install under Python 3.12 on macOS ([#203](https://github.com/spotify/basic-pitch/issues/203)). SOME and GAME weights are CC BY-NC-SA; ROSVOT's are unlicensed and trained on NC data. For F0: **SwiftF0** (MIT code, MIT-labelled ONNX trained on a CC BY-NC-SA dataset, Python 3.8–3.14) and **librosa pYIN** (ISC, no weights). Vocadito pitch F1: RMVPE 0.862, SwiftF0 0.847, pYIN 0.653 (benchmark run by SwiftF0's author, so VENDOR for SwiftF0). | D-04 steps 2 and 6; new §4.9 rows; a hum-benchmark ticket. |
| GAP-02 | Can YuE2 take Jon's own ABC plus lyrics? | **CONFIRMED** | Yes: `abc=` with `cot='full'` or `'melody'`; SheetSage2 and MERT2 are not loaded. Strict two-voice dialect, one integer tempo, full bars only, no tuplets ([PR #185](https://github.com/multimodal-art-projection/YuE/pull/185) open) or pickups. Lyrics bind only by section tags and order. Edit adherence 84.17% exact pitch on edited model scores (VENDOR); none for hand-written ABC. ~6 min maximum. Chinese and English only ([generation.md](https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md), [abc-editing.md](https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/abc-editing.md)). | D-04 R1; the converter row in §4.9; Q6 (lyric language). |
| GAP-03 | YuE2's real hardware floor; Windows? | **CORRECTED** | 24 GB is a recommendation; peaks 11.2/14.1 GiB (VENDOR). 16 GB is plausible but unvalidated on PyTorch. Native Windows is broken on main with official wheels ([PR #166](https://github.com/multimodal-art-projection/YuE/pull/166) open; [#209](https://github.com/multimodal-art-projection/YuE/issues/209)). WSL2 with the Windows NVIDIA driver works if `.wslconfig` memory is ≥24 GB (default 50% of RAM). Drivers ≥570.26 (Linux) / ≥570.65 (Windows) for cu128; R580+ for cu130. | A4 opened; D-03, D-16, Q1. |
| GAP-04 | Can a non-ACE vocal engine run on the M5 Pro? | **CORRECTED** (medium confidence) | Ports exist, none verified: YuE2 via [audio.cpp](https://github.com/0xShug0/audio.cpp) (Apache-2.0) or [yue2.cpp](https://github.com/ServeurpersoCom/yue2.cpp) (MIT), GGUF Q8 ~4–10 GB, ABC path implemented, parity tests on CUDA/CPU only; HeartMuLa via audio.cpp; MiniMax via MLX (23.34 GiB peak for 10 s; full songs unmeasured; ~13.2 GiB weights the disk cannot hold). Official YuE2 MPS stays blocked by #176 and #187. | D-02 reverse-if (c), D-03, Q14. |
| GAP-05 | What exactly does YuE2's individual-creator permission allow? | **CONFIRMED** | Individuals may sell or license outputs, including to clients; "commercial use of the model weights by companies" is excluded; "individual capacity" is undefined; single-member LLC unanswered; no revocability language; HF LICENSE files are plain NC; issue [#219](https://github.com/multimodal-art-projection/YuE/issues/219) (a sole trader asking for terms) is unanswered. Not legal advice. | D-02, D-08, D-11, Q3. |
| GAP-06 | Which engines output native stems? Does Demucs's MIT cover its weights? | **CORRECTED** | Only YuE1 writes native vocal and instrumental tracks. YuE2 and MiniMax output one mix. ACE base `lego` appears to return the new part alone (medium confidence; [#1286](https://github.com/ace-step/ACE-Step-1.5/issues/1286)). Demucs weights are research/personal-only per the author. | D-06, D-11 blocker list, YuE1 → watch. |
| GAP-07 | May Jon import his own Suno output into AURA? | **CONFIRMED** (medium confidence) | Under the [2026-09-03 ToS](https://suno.com/terms-september-2026): DSP mix/master/format conversion is allowed ("incidental", undefined); ML separation is grey; generative edits, voice conversion, or using Suno audio to **develop or test AURA** is the highest risk ("power, enable" plus the "compete with Suno" covenant); release of a DSP-finished permitted download is allowed. Pro/Premier assignment survives cancellation. Not legal advice. | New feature row A12; D-10, D-11 rule 7, D-21, Q7. |
| GAP-08 | Independent narration quality evidence? May ElevenLabs renders seed another engine? | **CONFIRMED** | No independent long-form comparison exists; both arenas are short-form English. Long-form paper [arXiv 2609.16989](https://arxiv.org/abs/2609.16989) shows Qwen3-TTS and VoxCPM2 degrading past ~1,500 words. ElevenLabs' [Prohibited Use Policy](https://elevenlabs.io/use-policy) §9(j)(k)(l) bars Output as ML input, dataset, or for competing models. Eleven v4 / v4 Turbo now top the AA TTS board. | D-08, Q9. |

---

## 3. Corrections to each source

Each source got important things right. Each also made errors, and the errors shared one pattern: a figure was attached to the wrong model or version.

The gap research (§2.1) found four things **no source** flagged: Demucs's checkpoints are research/personal-only per its author; YuE2 does not run on native Windows without patches; no hum transcriber is both license-clean and benchmarked on humming; and ElevenLabs forbids using its renders as a cloning reference or training data. GPT's own framing recorded Linux, Windows and macOS support as an owner requirement (`companion/FRAMING.md`; MG-E14–E16), but none of the three plans turned it into a decision. D-24 now does.

### GPT-6.1 SOL (core plan + voice/video corpus)

**Got right, confirmed.** This was the most reliable source on licenses and contracts:
- Suno stems are regenerated, which gives three stem operations.
- ACE's task matrix: lego/extract/complete are base-only, and turbo CFG is forced to 1.
- ACE XL VRAM tiers.
- YuE2: weights are NC plus an individual permission that excludes companies, and listeners preferred v6 59.3% vs 31.6%.
- MiniMax: license terms, CUDA requirement, 57.4 GB, and that the MPS helper proves nothing.
- HeartMuLa 7B is unreleased, and MuLaCover's outputs are NC.
- DiffRhythm 2's instrumental mode is still TODO.
- LeVo is unreachable.
- SongEval's license conflicts and SongPrep is academic-only.
- RoFormer checkpoint rights.
- The TTS license traps: F5, OmniVoice, Fish, VibeVoice.
- VoiceStudio costs $99/year, not per month.
- Pond5/Envato bans.
- Web Audio's draft status and latency caveats.
- JUCE, CPAL and Rubber Band license types.
- Mastering can't recover detail, and upsampling changes the container, not the information.
- Edits should be byte-identical outside the mask.
- Upload limit is 30 min. Studio 2.0's contents.

**Corrected:**
- **Demucs is not just a frozen baseline.** The author's fork released v4.1.0 on 2026-07-11 ([adefossez/demucs](https://github.com/adefossez/demucs)).
- **MiniMax as the "provisional quality challenger" is weaker than presented.** Its hosted API closed to new users on 2026-08-20. It needs CUDA and ~28.5–57 GB. It scores 6.28 vs YuE2's 6.73 on WSB (COMPETITOR-RUN). The diffusers PR pin is obsolete (≥0.40.0).
- "Partner-developed" was flagged as unsourced, but it is **Suno's own wording**.
- "Core" is not an official v6 variant name.
- JUCE is now **v9** with a $20k free Starter tier ([JUCE 9 licence](https://juce.com/legal/juce-9-licence/)).
- The Mac's disk was never addressed.
- There was no hum-to-song path, though GPT's SongSpec/PerformanceSpec gives the right place to put one.
- Internal inconsistencies: 48 vs 40 briefs, two vs three engines, and 8 vs 16 tracks for the audio gate.
- "Every model's quality baseline is unmeasured" is still true locally, but WildSongBench now gives COMPETITOR-RUN automatic numbers for ACE, MiniMax, HeartMuLa, LeVo and DiffRhythm 2.
- The phase estimates assume a team, not a single owner.

### Kimi K3 swarm

**Got right, confirmed:**
- ACE is MIT for code *and* models, and Kimi was correct to flag Fable's gap there.
- ACE turbo is 8-step and SFT 50-step.
- ACE's headline numbers are self-scored. WSB has ACE at 6.01 vs Suno v5 at 6.87.
- YuE2 best-of-8 scores 6.96 vs v5's 6.87 on SongBench (true on the automatic metric).
- Suno v6 is #1 at 1142 on the Arena (Artificial Analysis Vocal v1.1).
- v6 is below v5 on WSB (automatic).
- WavTool was acquired in June 2025.
- The 404 Media breach figures, as reported.
- The Warner settlement plus Songkick, the GEMA ruling, Udio's download shutdown, and Suno's $5.4B valuation.
- RunPod serverless 4090 costs $1.10/h.
- CUDA-stack fragility is the top infrastructure risk.
- Avoid gcui-art/suno-api and MusicGen.
- Verify LeVo's license (the reality is worse: it was withdrawn).
- Seed-VC is GPL.
- HeartMuLa Studio exists, though it is community-made and unlicensed.
- Two valuable ideas: a staged ladder for closing the gap, and keeping Suno's consent gate.

**Corrected or refuted:**
- **YuE2 is not Apache-2.0.** Its weights are CC BY-NC 4.0.
- **The "15–36 min" YuE2 time is a YuE1 figure.** The vendor gives about 71 s per 3.6-min song on a 4090.
- **"Best-of-n closes ⅓–½ of the gap" is refuted** (C13). "Suno hides 2–4 survivors" is unverifiable.
- The clockworksquirrel "25 s/song" is per 30-s clip, and the fork is unnecessary because upstream has native MLX.
- "<4 GB VRAM" applies only to a narrow CUDA tier.
- htdemucs_ft gives 4 stems, not 6. "Clean 6-way" overstates it: guitar is ~9 dB and piano ~7.8 dB SDR, and the best checkpoint has an unknown license.
- demucs-mlx's "73×" is a stale README figure. It now claims 114× on an M4 Max (VENDOR).
- Suno offers up to 12 stems, not 8. The phantom-reverb and "~2%" claims have no source.
- WhisperX ±50 ms on singing has no source.
- Seed-VC's 300 ms is algorithm delay only (~400 ms total, measured on a speech model).
- **efegen/rvc-pipeline does not exist.**
- RVC's "5–15 min" is a data duration, not training time.
- MusicGen-melody is both proposed and excluded.
- DiffRhythm 2's 8 GB and instrumental role are v1 figures, and instrumental mode is a TODO.
- Stable Audio 3 is gated under a community license, not simply "open weights".
- Tauri's 42 vs 168 MB are RAM figures.
- Apollo and AudioSR are not both MIT: Apollo is CC BY-SA.
- pyloudnorm cannot measure dBTP.
- "Every model including Suno is the same 4-stage pipeline" is unsupported.
- The per-user LoRA mechanism is undisclosed.
- v6 was not trained on all three catalogs at launch.
- The 1293 Elo figure for v5 was not found in any primary source.
- **MTG-Jamendo and FMA are not a CC0/CC-BY source** (C36).
- Mureka's MIDI export is Premier-only.
- ElevenLabs is not the only music API.
- The 46K A100-hour figure is ACE v1.
- The "Fable hallucinated" audit is not supported by the archived Fable files.
- Kimi assumed an M3 Pro 36 GB Mac and made no disk analysis.
- The plan is ACE-centric, contrary to the owner's instruction.
- It has no narration lane.

### Claude Fable 5.1

**Got right, confirmed:**
- The frame-level Suno UI inventory. It was later superseded by v6, but the command surface (#088 Edit menu, the Song Editor, Studio clip settings, the stems panel, the hum-to-instrument flow, export options) is real and is the most complete list any source gave.
- **Two versions per generation**, which matches the v6 FAQ.
- Cover and regenerate are separate contracts, and per-stem replacement means a new lane plus Copy to Main Track.
- htdemucs_6s gives 6 stems, and the labels won't match Suno's.
- Studio is Premier-only.
- "Don't promise v5.5." The ACE weights license really was unstated in the paper; it is now confirmed MIT.
- SAO 1.0 has a 47 s cap. YuE1 7B is Apache. MusicGen is NC.
- A single engine URL, a SQLite job table, the `parent_id` / `kind` / `version_no` lineage, gating on `consent_at`, never committing audio or weights, and treating every claim as context to verify.

**Corrected:**
- **"ACE alone claims every primitive"**: stems, lego and complete need base or xl-base (another 4.79 or 19.95 GB), and the timbre reference is global, not a voice clone.
- **"Cover at high strength on the hum" is an unvalidated hypothesis**, and third-party evidence leans against it (C8).
- "YuE 7B, 16 GB, ~5 min" has no primary source.
- htdemucs_6s has no backing-vocals stem.
- "<4 GB VRAM" is a narrow tier.
- MPS is in fact supported upstream.
- A consent checkbox alone is weaker than Suno's gate.
- The corpus is pre-v6: Studio 1.2 and v4.5/v5.5 pickers.
- The primitives table has no extend, repaint, DSP or mastering primitive.
- It claims to be "fully specified" while leaving Sounds, Hooks, Labs, Inspo and Personas unspecified.
- It has no narration lane, no license analysis beyond ACE, and no evaluation protocol.
- It recorded no hardware specifics.

---

## 4. Component register

**Verdicts.** **adopt-v1** means it is in the first build; it still has to pass its smoke test. A verdict can carry a **condition** (an owner answer or a lane) that must hold before it applies. **evaluate** means it competes in a benchmark before adoption. **watch** means not now, revisit if named conditions change. **research-only** is for personal experiments with no shipping path. **reference-only** is a benchmark, comparator or UX reference that is never integrated. **reject** means do not use.

"Mac" means Apple Silicon. "Disk" is download size in decimal GB unless marked GiB. Memory figures are VENDOR unless labelled otherwise.

### 4.1 Song engines

| Component | Role | Code license | Weights license | Output terms | Mac | CUDA / other | VRAM / disk | Verdict | Primary source |
|---|---|---|---|---|---|---|---|---|---|
| **ACE-Step 1.5 2B** (turbo, sft, base, turbo-shift variants) | Fast draft and render lane. base handles extract, lego and complete. | MIT | MIT, ungated | The cards say commercial use is allowed. The training-data claim appears on the cards only (VENDOR). | **Official** native MLX (DiT, VAE, LM) plus MPS. INT8, offload and compile are disabled on MPS. | CUDA, ROCm, XPU, CPU. Windows uses torch 2.7.1+cu128. | 2B DiT 4.7 GB bf16 resident. Main bundle 10.09 GB; each extra 2B variant +4.79 GB; turbo-only selective download ~6.34 GB. | **adopt-v1** | [repo](https://github.com/ace-step/ACE-Step-1.5), [HF](https://huggingface.co/ACE-Step/Ace-Step1.5) |
| **ACE-Step 1.5 XL** (base, sft, turbo; 4B; ~4.99B params) | Higher-quality render profile | MIT | MIT | Same as 2B | MLX supported since v0.1.6. **XL-SFT/base garble fixed only on main** (pin ≥ `ca1e85fe9` or set `dcw_enabled=False, shift=1.0`). | ≥12 / 16 / 20 / 24 GB tiers | ~9 GB bf16 resident. **19.95 GB F32 download each.** Diffusers bf16 ~11.1–11.5 GB. | **adopt-v1** (after Mac smoke) | [#1259](https://github.com/ace-step/ACE-Step-1.5/issues/1259), [XL-SFT](https://huggingface.co/ACE-Step/acestep-v15-xl-sft) |
| ACE LM planners 0.6B / 1.7B / 4B | Lyric/structure planning for text2music, lego, complete | MIT. Qwen3 fine-tunes, so Apache-2.0 notices apply. | MIT | n/a | `mlx` backend | `vllm` / `pt` | 1.2 / 3.4 / 8.0 GB resident; 1.37 / 3.76 / 8.43 GB disk | **adopt-v1** (1.7B default) | [README](https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md) |
| acestep.cpp + Serveurperso GGUF | Small-footprint Mac runtime | MIT (community, hosted in the ace-step org) | MIT tag (community quantization) | As ACE | Metal | CUDA, Vulkan, CPU | XL-SFT Q8 5.31 GB, Q4_K_M 2.99 GB; turbo Q8 2.55 GB. The sibling `ace-step/acestep.vst3` (MIT, updated 2026-10-05) also runs on Metal and supports `lego` (GAP-06). | **evaluate** (quantization quality unmeasured) | [GGUF](https://huggingface.co/Serveurperso/ACE-Step-1.5-GGUF), [acestep.vst3](https://github.com/ace-step/acestep.vst3) |
| ACE-Step-DAW | Not used | **AGPL-3.0** | n/a | n/a | n/a | n/a | n/a | **reject** (do not vendor) | [repo](https://github.com/ace-step/ACE-Step-DAW) |
| **YuE2-3B + YuE2-Vae** | Quality lane and **score/melody-conditioned** lane. Native user-ABC input (`abc=`, `cot='full'`/`'melody'`): strict two-voice dialect, no tuplets or pickups, lyrics bound by section tags only, ~6 min, **zh/en only** (GAP-02) | Apache-2.0 | **CC BY-NC 4.0** plus the individual-creator permission (2026-09-16, GitHub only); ungated | Individuals may monetize outputs, including licensing to clients. **LLC-directed generation needs a commercial license** (GAP-05). | Unofficial. MPS blocked by #176 (fix needs torch ≥2.13; pin PR #190 unmerged) and #187. Community Metal routes: `yue2.cpp` and audio.cpp (below), no parity data. | Officially Linux, BF16 NVIDIA (Ampere+ in practice), 24 GB *recommended*, 24 GB host RAM, torch 2.10.0 (cu128: driver ≥570.26 Linux / ≥570.65 Windows). **Native Windows broken on main; use WSL2** with `.wslconfig` memory ≥24 GB (GAP-03). | 11.18 GiB peak, 14.08 max (VENDOR); **16 GB cards OPEN** (A4); 7.30 + 0.53 GB | **adopt-v1, conditional** on Q1 (a worker or rental passes smoke) and Q3 (individual operator). Never LLC work. | [card](https://huggingface.co/m-a-p/YuE2-3B), [MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE), [generation.md](https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md) |
| SheetSage2 (+ MERT2) | Audio → melody ABC transcription | Apache (YuE repo) | **CC BY-NC 4.0**, no creator permission. The HF LICENSE file is mislabeled. | NC | CUDA/CPU code paths | CUDA | 0.23 GB | **research-only** (the shippable transcriber is chosen by the hum benchmark; YuE2's user-ABC path does not load SheetSage2) | [SheetSage2](https://huggingface.co/m-a-p/SheetSage2) |
| YuE1 7B (s1-7B, s2-1B) | LLC-lane last resort. The **only engine with native vocal and instrumental tracks** (`vtrack` / `itrack`; GAP-06) | Apache | Apache | Trained on 650K h of in-the-wild internet music (provenance risk) | n/a | 24 GB for ≤2 sessions; 80 GB for full songs | 12.45 + 3.93 GB | **watch** (was reject): only if HeartMuLa and MiniMax both fail the LLC smoke. SongBench 4.92 vs YuE2 6.73 (both VENDOR, YuE2 paper) | [YuE-v1](https://github.com/multimodal-art-projection/YuE/tree/YuE-v1), [infer.py](https://github.com/multimodal-art-projection/YuE/blob/YuE-v1/inference/infer.py) |
| **MiniMax Music 3** | Challenger an LLC can license | Community License (covers the inference code; the GitHub repo has no LICENSE file) | Community License: show "MiniMax-Music3" in commercial UIs; written authorization above US$20M yearly revenue (with affiliates); third-party services must keep safeguards; 19-item AUP | User is responsible. **AUP #11 requires "machine-generated" disclosure** when published publicly. | None official. Community MLX ports: 13.2 GiB 8-bit weights, 23.34 GiB peak for a **10-s** clip on an M3 Max; full songs unmeasured; the Mac's disk cannot hold them today (GAP-04). | diffusers ≥0.40.0: single GPU ~23 GB bf16, 22 GB with auto offload, 8 GB with group offload. SGLang-Omni: CUDA 13, torch 2.13, "two GPUs" per README (**CONTESTED** against the single-GPU path). | **57.35 GB** full repo; **~28.5 GB** diffusers subset | **evaluate** as an **LLC-lane challenger** beside HeartMuLa (D-02) | [card + LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-Music3), [GitHub](https://github.com/MiniMax-AI/MiniMax-Music3) |
| MiniMax hosted music API | n/a | n/a | n/a | n/a | n/a | **Closed to new users since 2026-08-20**; free tiers discontinued | n/a | **reject** (unavailable) | [API ref](https://platform.minimax.io/docs/api-reference/music-generation) |
| **HeartMuLa-oss-3B** (happy-new-year) + HeartCodec | **LLC-lane challenger**: the only non-ACE open vocal song model found with permissive weights (GAP-04) | Apache-2.0 | Apache-2.0 (since 2026-01-20), ungated | None stated | No official MPS. audio.cpp's heartmula family on Metal (unmeasured); `heartlib-mlx` has no LICENSE file (**CONTESTED**). | CUDA; split across 2 GPUs or `--lazy_load`; RTF ≈ 1.0 (VENDOR) | LM 15.75 GB + codec ~6.6 GB (fp32). WSB 6.25 (COMPETITOR-RUN) | **evaluate** (LLC lane, ahead of MiniMax on license; was "after the first comparison reproduces") | [heartlib](https://github.com/HeartMuLa/heartlib), [HF](https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year) |
| audio.cpp v0.9.1 | Candidate cross-machine runtime: one ggml engine (CUDA, Vulkan, HIP, Metal) running YuE2 (with ABC), HeartMuLa, MiniMax, SheetSage2, MuScriptor and ACE-Step | Apache-2.0 | Per model loaded | Per model | Metal backend "intended for portability and testing"; **no Metal parity data** | CUDA, Vulkan, HIP | YuE2 7.8–12.5 GiB Q4–BF16 on an RTX 5090 (COMMUNITY); Q8 GGUFs ~4.3 GB | **evaluate** (a Metal route counts only after a parity check plus the smoke gate) | [audio.cpp](https://github.com/0xShug0/audio.cpp) |
| yue2.cpp + YuE2 GGUFs | Dedicated YuE2 runtime with ABC, continuation, LoRA stacking, WebUI | MIT | GGUFs CC BY-NC 4.0; **whether the creator permission carries over to converted weights is not stated** | As YuE2, if the permission carries over | README: Metal auto-enabled; parity tests green on CUDA and CPU only | CPU, CUDA, Vulkan | Q8 3.81 GB; 5.8 GB for a 65-s song (COMMUNITY) | **evaluate** (research lane until the permission question is answered) | [yue2.cpp](https://github.com/ServeurpersoCom/yue2.cpp), [GGUF](https://huggingface.co/Serveurperso/YuE2-GGUF) |
| MiniMax MLX ports (vanch007; appautomaton) | Possible Mac route for MiniMax | Community License; MIT (pre-alpha) | Community License (pass-through) | AUP #11 | MLX; see the MiniMax row | n/a | 13.2 GiB 8-bit; 26.56 GiB dense | **watch** (disk-blocked; long-form unmeasured) | [vanch007](https://github.com/vanch007/mlx-minimax-music3), [appautomaton](https://github.com/appautomaton/mlx-minimax-music3) |
| HeartCodec-oss-encoder | Codec round-trip ceiling study | Apache | Apache | n/a | Unknown | CUDA | n/a | **research-only** (codec study) | [HF](https://huggingface.co/HeartMuLa/HeartCodec-oss-encoder) |
| HeartMuLa 7B | n/a | n/a | **Unreleased** (HF 401) | n/a | n/a | n/a | n/a | **reject** (not available) | [heartlib README](https://github.com/HeartMuLa/heartlib) |
| MuLaCover | Melody/MIDI-conditioned cover | Apache | CC BY-NC 4.0 per its card. heartlib's README says all related weights are Apache, which **CONTESTS** this. | **Outputs NC** without written permission | n/a | Tested on B300 | 8.76 GB | **research-only** | [MODEL_LICENSE](https://github.com/HeartMuLa/MuLaCover/blob/main/MODEL_LICENSE) |
| **Stable Audio 3 Medium** (1.4B) | Instrumental beds, loops, intros on the Mac | MIT | Stability Community License plus Gemma terms. HF main repo is gated ("auto"); the `-optimized` repo is ungated. | User owns outputs. Free under US$1M revenue; commercial use requires registration; "Powered by Stability AI" when distributing; **outputs may not train other foundation models**. | **Official MLX**: 380 s of audio in 47.78 s at 5.05 GB on an M4 Pro 48 GB (VENDOR). LoRA training in MLX. | CUDA + FlashAttention 2 | MLX bundle ~8.4 GB | **evaluate** (v1-studio instrumental lane) | [repo](https://github.com/Stability-AI/stable-audio-3), [MLX](https://github.com/Stability-AI/stable-audio-3/blob/main/optimized/mlx/README.md), [license](https://stability.ai/license) |
| Stable Audio 3 Small (433M) | Fast sketches and SFX | MIT | Same as Medium | Same as Medium | CPU, TFLite, CoreML | CPU | 120 s maximum | **evaluate** | [repo](https://github.com/Stability-AI/stable-audio-3) |
| Stable Audio Open 1.0 | n/a | n/a | n/a | n/a | n/a | n/a | 47 s maximum | **reject** (superseded by SA3) | [Stability](https://stability.ai/news-updates/introducing-stable-audio-open) |
| DiffRhythm 2 | n/a | Apache | Apache, but **requires MuQ-MuLan-large (CC BY-NC)** at inference | Pipeline is not commercially clean | No MPS (CUDA or CPU only) | CUDA | No official v2 VRAM figure | **reject** (instrumental mode TODO; dormant since 2025-11-09) | [DiffRhythm2](https://github.com/ASLP-lab/DiffRhythm2) |
| LeVo 2 / SongGeneration v2 | n/a | Withdrawn | "unknown" (lglg666); mirror text says research/education only | Unverifiable | Community MLX | Mirror: 22/28 GB | 25.8 GB | **reject** | [lglg666](https://huggingface.co/lglg666/SongGeneration-v2-large) |
| Shao (ex-Khala) | n/a | **No LICENSE file** | CC BY-NC 4.0 ("intended") | NC | n/a | NGC 25.02 Docker; verified only on H800 and RTX 4090; warns of noise-like output on other stacks | 52.21 GB | **research-only** | [repo](https://github.com/Shao-Music-AI/Shao) |
| StepAudio 3 Music | n/a | n/a | No downloadable weights verified | n/a | n/a | Provider-backed Space only | n/a | **reject** | [Space](https://huggingface.co/spaces/stepfun-ai/StepAudio-3-Music) |
| MusicGen-melody; JASCO | Melody/chord conditioning, instrumental only | MIT | **CC-BY-NC 4.0** (JASCO gated) | NC | n/a | n/a | n/a | **reject** | [musicgen-melody](https://huggingface.co/facebook/musicgen-melody), [JASCO](https://huggingface.co/facebook/jasco-chords-drums-melody-1B) |
| SongEcho | Melody-conditioned cover (48.4% Hit@1, COMPETITOR-RUN) | Unverified | Unverified | n/a | n/a | n/a | n/a | **research-only** (check its license first) | [arXiv 2602.19976](https://arxiv.org/abs/2602.19976) |
| MuSeC | Semantic/acoustic codec research | n/a | No weights | n/a | n/a | n/a | n/a | **research-only** | [arXiv 2609.21240](https://arxiv.org/html/2609.21240v1) |

### 4.2 Hosted services (benchmark or reference; never in the core path)

| Service | Role | Terms that matter | Verdict | Primary source |
|---|---|---|---|---|
| **Suno v6 / v6-wild / v6-mini** | Owner's paid first attempt, and the quality reference | 2 songs per generation for 10 credits; up to 8 min. Commercial use needs Pro or Premier **and a permitted download** (Pro 20/mo, Premier 60/mo; Studio exports uncapped). **ToS: Output may not be used "to power, enable or train other artificial intelligence and machine learning models", or to compete with Suno.** Suno takes a "royalty-free, perpetual, irrevocable" license to uploaded Content, which would include Jon's melody. Studio 2.0 is Premier-only. Advanced Split is Premier-only. **Importing Jon's own downloads** (GAP-07): DSP finishing is allowed ("incidental"); ML separation is grey (prefer Suno's own stems); generative edits, voice conversion, or using the audio to develop or test AURA carry the highest risk. | **reference-only** (listening benchmark, subject to Q7); DSP-finishing import allowed | [terms](https://suno.com/terms-september-2026), [pricing](https://suno.com/pricing), [v6 FAQ](https://help.suno.com/en/articles/13924481) |
| Suno Speech (beta, 2026-10-01) | Possible Sabbath Echo comparator | "Generates voice and music together as one cohesive track". Plan, commercial and language terms are not stated. | **reference-only** | [blog](https://suno.com/blog/introducing-speech-beta) |
| Mureka API (`mureka-9.5`) | Hosted benchmark: stems with MIDI, region edit | The model can be pinned (avoid `auto`). Extend works only on 7.6/8. Pro carries commercial rights; MIDI/WAV export is Premier. | **reference-only** (optional v2) | [changelog](https://platform.mureka.ai/docs/en/changelog.html), [song/generate](https://platform.mureka.ai/docs/api/operations/post-v1-song-generate.html) |
| Gemini API Lyria 3.5 | Cheapest hosted reference | $0.08 per song, 44.1 kHz stereo, single-turn, **SynthID-watermarked** | **reference-only** | [docs](https://ai.google.dev/gemini-api/docs/music-generation) |
| Stability SA3 Large API | Hosted instrumental reference | 8 credits (~$0.08) per the pricing page; GPT's secondary figure was 26 credits (**CONTESTED**) | **reference-only** | [pricing](https://platform.stability.ai/pricing) |
| ElevenLabs Music v2.5 | Reference | Paid API. Free plan requires attribution and allows no streaming. Film, TV, radio and studio games need Enterprise Music. | **reference-only** | [terms](https://elevenlabs.io/eleven-music-model-specific-terms) |
| Artificial Analysis music boards (v1.1) | External context | Recruited panel; Bradley-Terry; MiniMax Music 3.0 anchored at 1000; outputs normalised to −16 LUFS / −1 dBTP and 320 kbps MP3. Suno v5 is not on v1.1, so Elo cannot be compared across versions. | **reference-only** | [vocals](https://artificialanalysis.ai/music/leaderboard/vocals) |

### 4.3 Separation, transcription, alignment, structure

| Component | Role | Code | Weights | Mac | CUDA / other | Notes | Verdict | Source |
|---|---|---|---|---|---|---|---|---|
| **Demucs 4.1.0** (adefossez): htdemucs, htdemucs_ft, htdemucs_6s | "Isolate original" baseline; internal vocal separation for the filters in the **individual** lane | MIT | **Research/personal use only per the author** ([#327](https://github.com/facebookresearch/demucs/issues/327), [#384](https://github.com/facebookresearch/demucs/issues/384), [#508](https://github.com/facebookresearch/demucs/issues/508)); `license: mit` removed from the HF cards on 2026-08-31. Trained on MUSDB18-HQ (academic-only) plus 800 internal Meta songs. | MPS auto (complex STFT falls back to CPU) | CUDA, ~7 GB default (3 GB with `--segment 8`) | 4 / 4 / 6 stems. 6s adds guitar and piano (piano is weak). **No backing vocals.** Weights 160 / 641 / 105 MB. | **adopt-v1, individual and research lanes only** (pinned, downloaded at runtime). Not for LLC work. | [adefossez/demucs](https://github.com/adefossez/demucs), [PyPI 4.1.0](https://pypi.org/project/demucs/4.1.0/) |
| facebookresearch/demucs | n/a | MIT | n/a | n/a | n/a | Archived 2025-01-01 | **reject** as a source (use adefossez) | [repo](https://github.com/facebookresearch/demucs) |
| **demucs-mlx 1.6.1** | Mac-native separation | MIT | MIT tag on the conversion, but these are converted Meta checkpoints, so the **author's research/personal restriction applies** | MLX only. 114× warm on a 40-core M4 Max (VENDOR). Caches 16–31 GB, so set `mx.set_cache_limit`. | n/a | htdemucs 160 MB. A Swift package also exists. | **evaluate** (Mac default for the individual lane if M5 Pro smoke passes) | [repo](https://github.com/ssmall256/demucs-mlx) |
| Kim Mel-Band-RoFormer vocals | Better vocal isolation; **candidate LLC-lane separator** for the internal PER and adherence filters | MIT (via ZFTurbo MSST) | MIT. Training data not stated (**UNVERIFIED**). | MPS via python-audio-separator; MLX ports exist | CUDA | 1 stem | **evaluate** (allow-list candidate; check training data before LLC use) | [HF](https://huggingface.co/KimberleyJSN/melbandroformer) |
| BS-RoFormer SW (6-stem) | Best open 6-stem: bass, drums, other, vocals, guitar, piano | n/a | **Unknown**; original uploader deleted; mirrors grant no rights | GGUF Metal via BSRoformer.cpp (COMMUNITY) | CUDA | Guitar 9.01 / piano 7.80 SDR, a tie with Logic Pro 11.2 | **research-only** (never bundle) | [mirror](https://huggingface.co/FractalSurfer/BS-RoFormer-SW-6stem), [MVSep piano](https://mvsep.com/quality_checker/leaderboard/piano/) |
| Other community RoFormer checkpoints (anvuew, Sucial, HiDolen V2, viperx/TRvlvr, becruily karaoke) | Dereverb, karaoke, lead/backing vocals | n/a | GPL-3.0 / CC-BY-NC-SA / CC-BY-NC / **none** / none | n/a | n/a | Best back-vocal SDR ~7.1 dB | **research-only**; ship only from a verified allow-list | [ZFTurbo list](https://github.com/ZFTurbo/Music-Source-Separation-Training/blob/main/docs/pretrained_models.md) |
| lucidrains/BS-RoFormer, ZFTurbo MSST | Architecture and training/inference framework | MIT | Per checkpoint | n/a | n/a | Code only | **evaluate** | [BS-RoFormer](https://github.com/lucidrains/BS-RoFormer), [MSST](https://github.com/ZFTurbo/Music-Source-Separation-Training) |
| python-audio-separator | Separation orchestration | MIT | Per model | MPS (needs PyTorch 2.13+, macOS 14+) | CUDA, ONNX | n/a | **evaluate** | [repo](https://github.com/nomadkaraoke/python-audio-separator) |
| mlx-audio-separator | MLX Roformer, MDXC, Demucs | MIT | Per model | MLX | n/a | No PyTorch at inference | **evaluate** | [repo](https://github.com/ssmall256/mlx-audio-separator) |
| SCNet | Alternative separator | MIT | Google Drive download, no license, trained on MUSDB | n/a | CUDA | 4 stems | **research-only** | [repo](https://github.com/starrytong/SCNet) |
| SAM Audio | Prompt-selected target and residual | SAM License (custom; commercial allowed; **Meta can modify it unilaterally**) | Same; gated with manual approval | MPS with community patches; community MLX port | CUDA recommended; 12–38 GB (COMMUNITY) | Text, visual and time-span prompts | **research-only** | [repo](https://github.com/facebookresearch/sam-audio), [LICENSE](https://github.com/facebookresearch/sam-audio/blob/main/LICENSE) |
| Logic Pro 11.2 Stem Splitter | Comparator | Apple commercial | n/a | macOS | n/a | Ties BS-RoFormer SW on guitar and piano | **reference-only** (if owned) | [MVSep guitar](https://mvsep.com/quality_checker/leaderboard/guitar/) |
| **Basic Pitch** | Hum/stem → MIDI with pitch bends | Apache-2.0 | Apache (bundled TF, CoreML, TFLite, ONNX) | CoreML default. **Only Python 3.10 is supported on Apple Silicon**; 0.4.0 fails to install under 3.12 ([#203](https://github.com/spotify/basic-pitch/issues/203)), so use a py3.10 env or a `--no-deps` CoreML/ONNX install. Last release 0.4.0 (2024-08). | TF, ONNX | Trained partly on singing (iKala). Humming: onset+pitch F1 0.27–0.43, no offsets (COMMUNITY, GAP-01). | **adopt-v1, provisional**: the local hum benchmark (§4.9) decides between it, SwiftF0 `segment_notes` and pYIN+HMM | [repo](https://github.com/spotify/basic-pitch) |
| Whisper large-v3 / -turbo | Lyric ASR | MIT | Apache-2.0 / MIT | Community MLX | CUDA | n/a | **adopt-v1** (lyric check) | [repo](https://github.com/openai/whisper) |
| Qwen3-ASR 0.6B / 1.7B | Lyric phoneme error rate, as in the WSB protocol (4 passes) | Apache | Apache | Community MLX | CUDA | n/a | **evaluate** against Whisper | [HF](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) |
| HeartTranscriptor-oss | Whisper fine-tuned for sung lyrics | Apache | Apache | n/a | n/a | n/a | **evaluate** | [HF](https://huggingface.co/HeartMuLa/HeartTranscriptor-oss) |
| WhisperX | Word timing | BSD-2 | English aligner MIT; **fr/de/es/it aligners CC BY-NC**; most others Apache | **CPU-only** on Mac (int8) | CUDA | Evaluated on speech only, with a 200 ms collar | **evaluate** (English only) | [repo](https://github.com/m-bain/whisperX) |
| SOFA (+ community `tgm_en_v100`) | Singing forced aligner | MIT | Official checkpoints are unlicensed (trained partly on NC data). The English checkpoint carries the author's statement "Commercial Use: Approved" but no license file. | ONNX | n/a | Needs phoneme lyrics | **evaluate** (v2) | [SOFA](https://github.com/qiuqiao/SOFA), [discussion 31](https://github.com/qiuqiao/SOFA/discussions/31) |
| Montreal Forced Aligner | Speech aligner baseline | MIT | CC BY 4.0 (speech models) | conda | n/a | Singing is out of its domain | **evaluate** (baseline) | [repo](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) |
| SongPrep | n/a | **Academic-only** | Academic-only | n/a | n/a | n/a | **reject** | [LICENSE](https://github.com/tencent-ailab/SongPrep/blob/main/LICENSE) |
| all-in-one (`allin1`) | Beats, downbeats, functional sections (10 labels) | MIT | MIT tag (Harmonix) | **No MPS**; NATTEN breaks; PR #39 unmerged | CUDA, CPU | Stale (1.1.0, 2023) | **evaluate** (vendor or fork; run on CUDA) | [repo](https://github.com/mir-aidj/all-in-one) |
| msaf | Unsupervised segmentation | MIT | None needed | CPU | n/a | Labels are cluster IDs, not verse/chorus names | **evaluate** (fallback) | [repo](https://github.com/urinieto/msaf) |

### 4.4 Voice: singing conversion, consent, narration/TTS

| Component | Role | Code | Weights | Output / other terms | Mac | CUDA | Verdict | Source |
|---|---|---|---|---|---|---|---|---|
| RVC WebUI 2.3.260718 | Singing voice conversion | MIT | HF `lj1995` is tagged MIT, but its LICENSE text adds "research use only" (**CONTESTED**). rmvpe.pt has no license, and its training data includes M4Singer (CC BY-NC-SA). | User is responsible for converted voices. **Whether a released song with converted vocals is permissible is CONTESTED** (research-use rider; unlicensed rmvpe). | **Dropped** (CUDA → DirectML → CPU) | CUDA 11.8 / 12.8 | **evaluate** (CUDA worker, v2) | [repo](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI), [HF](https://huggingface.co/lj1995/VoiceConversionWebUI) |
| Applio 3.6.5 | RVC on the Mac | MIT + Terms of Use | Inherits the lj1995 weights question | ToU: commercial use only with rights to the audio. Release of converted vocals is **CONTESTED** as for RVC. | **MPS** (macOS installer) | Yes | **evaluate** (v2 singing conversion) | [repo](https://github.com/IAHispano/Applio) |
| Seed-VC | n/a | **GPL-3.0** | **GPL-3.0** | n/a | MPS on unpinned nightly torch | Yes | **reject** (archived 2025-11-21) | [repo](https://github.com/Plachtaa/seed-vc) |
| efegen/rvc-pipeline | n/a | n/a | n/a | n/a | n/a | n/a | **reject** (does not exist, 404) | [API 404](https://api.github.com/repos/efegen/rvc-pipeline) |
| so-vits-svc | n/a | AGPL, archived | n/a | n/a | n/a | n/a | **reject** | n/a |
| OpenVPI DiffSinger 2.5.1 | Score-to-singing (note-level control) | Apache-2.0 | Voicebanks carry each creator's terms. The community NSF-HiFiGAN and PC-NSF vocoders are **CC BY-NC-SA 4.0**. | Disclaimer forbids voices used without consent | Python inference is CUDA/CPU only; deploy as ONNX through OpenUtau (osx-arm64, CoreML) | Yes | **research-only** (v2; train your own vocoder for commercial use) | [DiffSinger](https://github.com/openvpi/DiffSinger), [vocoders](https://openvpi.github.io/vocoders/) |
| SingingVocoders | Train your own vocoder | MIT | Self-trained | n/a | n/a | Yes | **research-only** | [repo](https://github.com/openvpi/SingingVocoders) |
| OpenUtau | DiffSinger host | MIT | n/a | n/a | osx-arm64 build | n/a | **evaluate** (v2) | [repo](https://github.com/stakira/OpenUtau) |
| pyannote WeSpeaker ResNet34-LM | Speaker match for the consent gate | MIT | **CC-BY-4.0, ungated** (attribution) | n/a | CPU is feasible | Yes | **evaluate** (v2) | [HF](https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM) |
| SpeechBrain ECAPA (voxceleb) | Alternative speaker match | Apache | Apache, ungated | n/a | CPU | Yes | **evaluate** (v2) | [HF](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) |
| **VoxCPM2** (2B, 48 kHz, 30 languages, cloning and voice design) | Narration candidate #1 | Apache | Apache ("free for commercial use") | Degrades badly past ~1,500 words in an independent long-form test ([arXiv 2609.16989](https://arxiv.org/abs/2609.16989)), so chunking plus ASR verify-and-regenerate is required | **Official MPS** (`--device auto`). llama.cpp-omni on Metal at RTF ~1.76 (Q8) on an M4 Pro (VENDOR). | ~8 GB | **evaluate** (narration pilot) | [repo](https://github.com/OpenBMB/VoxCPM), [HF](https://huggingface.co/openbmb/VoxCPM2) |
| Qwen3-TTS (0.6B / 1.7B: Base, VoiceDesign, CustomVoice) | Narration candidate | Apache | Apache, ungated | Same long-form degradation: 0.6B worst-of-10 WER 35.2% past ~1,500 words (arXiv 2609.16989) | Official examples are CUDA only; mlx-audio is community | Yes | **evaluate** | [repo](https://github.com/QwenLM/Qwen3-TTS) |
| Chatterbox (original, Turbo, Nano, Multilingual V3) | Narration candidate | MIT | MIT, ungated | **Every output carries a Resemble Perth watermark** | The Mac example covers only the original model; Turbo/Nano code accepts `mps` | Yes | **evaluate** | [repo](https://github.com/resemble-ai/chatterbox) |
| Fun-CosyVoice3-0.5B-2512 | Narration candidate; pronunciation inpainting | Apache | Apache | n/a | No official Mac support | Yes | **evaluate** | [HF](https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512) |
| Kokoro-82M | Low-resource baseline; no cloning | Apache | Apache | `misaki[en]` pulls in **espeak-ng (GPL-3.0)** | mlx-audio | CPU | **evaluate** (baseline) | [HF](https://huggingface.co/hexgrad/Kokoro-82M) |
| OmniVoice | n/a | Apache | **CC-BY-NC** (Emilia data) | NC | Yes | Yes | **reject** (commercial narration) | [HF](https://huggingface.co/k2-fsa/OmniVoice) |
| F5-TTS | n/a | MIT | **cc-by-nc-4.0** | NC | n/a | n/a | **reject** | [HF](https://huggingface.co/SWivid/F5-TTS) |
| Fish Speech S2-Pro | n/a | **Fish Audio Research License** | Same | Commercial use requires a separate license; outputs may not train foundation models | n/a | H200 published | **reject** | [LICENSE](https://github.com/fishaudio/fish-speech/blob/main/LICENSE) |
| VibeVoice | n/a | MIT | MIT tags, but "research and development purposes only"; TTS code removed 2025-09-05 | n/a | n/a | n/a | **reject** | [repo](https://github.com/microsoft/VibeVoice) |
| mlx-audio | Community MLX runtime for TTS and SAM Audio | MIT | Per model | MLX | n/a | n/a | **evaluate** | [repo](https://github.com/Blaizzy/mlx-audio) |
| VoiceStudio (debpalash) | UX reference for narration | **AGPL-3.0-only** + commercial license | Default OmniVoice is NC; tokenizer under Higgs Audio 2 / Llama terms | Pro $99/user/year or Lifetime $299; neither includes closed-source distribution or private hosting | MPS; macOS 13.3+; **~10 GB disk** | Yes | **reference-only** | [LICENSE-NOTICE](https://github.com/debpalash/VoiceStudio/blob/main/LICENSE-NOTICE.md), [Pro](https://voicestudio.sh/pro) |
| ElevenLabs (v3, v4, Flash, Turbo) | Current narration vendor; cost baseline. **v4 / v4 Turbo now top the AA TTS board** (1326 / 1329 vs v3 1177), so v4 is the bar. | Closed | n/a | Per 1K chars: v3 / v2 / v4 $0.08; Flash / Turbo / v4 Turbo $0.04 (list). No SSML breaks on v3/v4. **Prohibited Use Policy §9(j)(k)(l): Output may not be ML input, a training/testing dataset, or used to build competing models**, so renders cannot seed or train another engine. Clones cannot be exported. Paid-plan output stays commercial after the subscription ends. | n/a | n/a | **reference-only** | [pricing](https://elevenlabs.io/pricing/api), [use policy](https://elevenlabs.io/use-policy), [terms](https://elevenlabs.io/terms-of-use) |
| DeepFilterNet | Speech-only enhancement | MIT / Apache | Same | **Never apply to music** | n/a | n/a | **evaluate** (narration v2) | [repo](https://github.com/Rikorose/DeepFilterNet) |

### 4.5 Scorers and benchmarks

| Component | Role | Code | Weights | Fit | Verdict | Source |
|---|---|---|---|---|---|---|
| audiobox-aesthetics | Aesthetic diagnostic (CE/CU/PC/PQ) | CC-BY-4.0 (+ MIT unilm) | CC-BY-4.0, ungated | Resamples to 16 kHz in 10 s windows. Frontier systems land in a narrow PQ band (7.87–8.40). | **adopt-v1** (diagnostic only) | [repo](https://github.com/facebookresearch/audiobox-aesthetics) |
| LAION-CLAP (music checkpoint) | Text–audio agreement diagnostic | CC0-1.0 | CC0 (lukewys) / Apache (HF ports) | Training data was copyrighted and not released (provenance note) | **adopt-v1** (diagnostic) | [repo](https://github.com/LAION-AI/CLAP), [larger_clap_music](https://huggingface.co/laion/larger_clap_music) |
| SongEval | Musicality scorer | Apache (code) | **CC-BY-NC-SA** checkpoint; loads MuQ (CC-BY-NC) | Within-model pairwise accuracy is close to random (43–55%) | **research-only** (personal) | [repo](https://github.com/ASLP-lab/SongEval), [#8](https://github.com/ASLP-lab/SongEval/issues/8) |
| MuQ / MuQ-MuLan | Music embeddings / alignment | MIT | **CC-BY-NC 4.0** | 24 kHz input | **research-only** | [MuQ](https://github.com/tencent-ailab/MuQ) |
| SongBench (Tencent) | Learned 7-dimension judge (WSB's selector) | **Academic-only** (LICENSE.txt) despite an MIT badge | Uses MuQ (NC). Trained on 12k Suno v4–v5 samples, so biased toward v5. | n/a | **research-only** | [repo](https://github.com/Tencent/SongBench), [paper](https://arxiv.org/html/2604.25937v1) |
| CMI-RM; TuneJury | Pairwise music reward models | Apache / n/a | **CC-BY-NC** (TuneJury's "Apache CLAP-only variant" has **UNVERIFIED** data provenance) | Reports best-of-N gains on its own reward axis only; no human test | **research-only** | [CMI-RM](https://huggingface.co/HaiwenXia/CMI-RM), [TuneJury](https://github.com/yonghyunk1m/TuneJury) |
| WildSongBench | External benchmark context | n/a | Prompts carry no license tag | Evaluator needs Linux, an **80 GB GPU** for Q3O and ~83 GB of weights. Built and run by the YuE2 team, so YuE2's own scores on it are VENDOR (self-run) and other engines' are COMPETITOR-RUN. | **reference-only** | [dataset](https://huggingface.co/datasets/m-a-p/WildSongBench) |

### 4.6 Post-production and DSP

| Component | Role | License | Fit | Verdict | Source |
|---|---|---|---|---|---|
| pyloudnorm | Integrated loudness (BS.1770-4) and LRA | MIT | **No true-peak meter**; `normalize.peak` measures sample peak | **adopt-v1**, plus our own ≥4× oversampled true-peak meter | [repo](https://github.com/csteinmetz1/pyloudnorm) |
| ITU-R BS.1770-5 (11/2023) | The measurement standard | n/a | K-weighting coefficients given at 48 kHz; 400 ms blocks with 75% overlap; −70 LKFS absolute and −10 dB relative gates; true peak by ≥4× oversampling. **pyloudnorm implements -4. Whether -5 changes integrated loudness for stereo programme is UNVERIFIED** (X-47), so results are labelled "BS.1770-4 (pyloudnorm)" until the two revisions are diffed. | **adopt-v1** (spec; diff -4 vs -5 as a ticket) | [ITU](https://www.itu.int/rec/R-REC-BS.1770/en) |
| Matchering 2.0.6 | Reference-matching master | **GPL-3.0** | Last release 2022; needs a reference track | **evaluate** (v2, separate process only) | [repo](https://github.com/sergree/matchering) |
| AudioSR | Generative super-resolution to 48 kHz | MIT code; `audiosr_basic` Apache | Synthesizes the top band. Not trained on MP3-type losses. | **research-only** | [repo](https://github.com/haoheliu/versatile_audio_super_resolution) |
| Apollo | MP3-loss restoration at 44.1 kHz | **CC BY-SA 4.0** (code and weights) | Wrong tool for 48 kHz upsampling | **reject** | [repo](https://github.com/JusperLee/Apollo) |
| Rubber Band 4.0.0 | Time and pitch | **GPL-2.0-or-later** or commercial | App Store distribution needs the commercial license | **reject** (for bundling) | [site](https://breakfastquay.com/rubberband/) |
| SoundTouch 2.4.1 | Time and pitch | LGPL-2.1 or commercial on request | Now on Codeberg | **evaluate** (fallback) | [Codeberg](https://codeberg.org/soundtouch/soundtouch) |
| Signalsmith Stretch 1.4.0 | Time and pitch | **MIT**; WASM/AudioWorklet npm build and a Rust crate | Quality unmeasured | **evaluate** (preferred candidate) | [repo](https://github.com/Signalsmith-Audio/signalsmith-stretch) |

### 4.7 UI and runtime

| Component | Role | License | Fit | Verdict | Source |
|---|---|---|---|---|---|
| Web Audio + AudioWorklet (Chromium) | Preview playback graph | W3C. Web Audio 1.0 is a Recommendation; 1.1 is a Working Draft. | Chromium's macOS output buffer defaults to 256 frames. Chrome 146 adds `playbackStats` (underruns); Chrome 153 adds `renderSizeHint`. | **adopt-v1** (Chromium-based browser required for Studio) | [spec](https://www.w3.org/TR/webaudio/), [Chromium mac](https://github.com/chromium/chromium/blob/main/media/audio/mac/audio_manager_mac.cc) |
| Safari / WKWebView Web Audio | n/a | n/a | **Ignores `latencyHint`**, pins a 128-frame buffer, no `setSinkId`, ~100 ms round trip measured on MBP 2021 | Not supported for Studio | [WebKit](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/Modules/webaudio/AudioContext.cpp) |
| wavesurfer.js 8 (core) | Single-waveform display | BSD-3-Clause | Active (8.0.2, 2026-10-07) | **evaluate** (display only) | [repo](https://github.com/katspaugh/wavesurfer.js) |
| wavesurfer-multitrack | n/a | BSD-3 (support is paid) | Dormant; pinned to ^7 and breaks on v8; one file per track; **0.3 s drift tolerance** | **reject** | [repo](https://github.com/katspaugh/wavesurfer-multitrack) |
| waveform-playlist v16 (+ Tone.js) | Timeline base | MIT | Multiple clips per track, sample-based positions, per-clip gain and fades, crossfades, AudioWorklet recording, WAV export | **evaluate** (versus our own timeline) | [repo](https://github.com/naomiaro/waveform-playlist) |
| openDAW | Full browser DAW | **AGPL-3.0** | n/a | **reference-only** | [repo](https://github.com/andremichelle/openDAW) |
| JUCE 9 | Native audio framework | **AGPLv3** or JUCE 9 EULA (Starter free ≤$20k; Indie ≤$300k at $40/mo or $800; Pro $175/mo or $3,500); EULA bars copyleft mixing | n/a | **reject** for now | [licence](https://juce.com/legal/juce-9-licence/) |
| CPAL 0.18 | Native audio I/O (Rust) | Apache-2.0. Its `asio` feature brings in Steinberg's ASIO SDK, which has been proprietary or GPLv3 since 2025-10-15. | I/O only; graph, DSP and plugins are left to us | **evaluate** (v2 native engine, if browser gates fail) | [repo](https://github.com/RustAudio/cpal) |
| VST3 SDK | Plugin hosting | **MIT** | n/a | **evaluate** (v2+) | [repo](https://github.com/steinbergmedia/vst3sdk) |
| Electron 44 | Desktop shell | MIT | Chromium 152 audio. Runtime zip 124 MB. Needs macOS 13+. | **evaluate** (v2 shell; preferred) | [release](https://github.com/electron/electron/releases/tag/v44.7.0) |
| Tauri 2.12 | Desktop shell | Apache-2.0 (also commonly MIT) | Uses WKWebView on macOS, with the audio gaps above | **reject** for v1/v2 Studio | [webviews](https://v2.tauri.app/reference/webview-versions/) |
| Tauri v3 (`tauri-runtime-cef`) | Desktop shell with Chromium | Apache | Alpha (CEF 152) | **watch** | [releases](https://github.com/tauri-apps/tauri/releases) |
| HeartMuLa-Studio | Webapp pattern reference (React, FastAPI, SQLModel, SSE) | **No LICENSE file** (only a README badge) | Do not copy code | **reference-only** | [repo](https://github.com/fspecii/HeartMuLa-Studio) |
| Prior-art studios: Ruach Studio, Riff, Remiqora | Review before building. Ruach: score-first ABC/MIDI, stems, LoRA training, DAW export on yue2.cpp (Linux, 24 GB NVIDIA). Riff: Apple Silicon Metal via audio.cpp. Remiqora: YuE2 + MuScriptor + ACE-Step + Demucs. | Ruach **AGPL-3.0**; Riff MIT; Remiqora MIT per the audio.cpp README (**UNVERIFIED**) | Reported by gap research; not separately verified. Never mix Ruach's AGPL code into AURA. | **reference-only** | [Riff](https://github.com/Flip-Engineering/riff), [audio.cpp README](https://github.com/0xShug0/audio.cpp) |
| FastAPI, SQLite, uv, React, Vite | Control service, metadata, envs, UI | Permissive (licenses not re-verified in this pass) | Standard stack | **adopt-v1** (re-check licenses in the D-11 register) | n/a |

### 4.8 Data and compute

| Component | Terms / prices (2026-10-09) | Verdict | Source |
|---|---|---|---|
| MTG-Jamendo | 55,701 tracks: ~70% NC, ~34% ND, **0 CC0**. A 2025-07-02 Jamendo notice limits it to non-commercial research. | **reject** for shareable adapters | [repo](https://github.com/MTG/mtg-jamendo-dataset) |
| FMA | Per-artist licenses; "meant for research purposes"; ~90% NC by duration (secondary tally) | **reject** for shareable adapters | [repo](https://github.com/mdeff/fma) |
| RunPod serverless | 4090 PRO $1.10/h; 24 GB L4/A5000/3090 $0.69; 48 GB A6000 $1.22; 5090 $1.58 (used only for the COMMUNITY-derived MiniMax estimate in C44); per-second billing. **Model load and a 5 s idle are billed.** Scales to zero. Default spend limit $80/h. | **evaluate** (bounded rental) | [pricing](https://www.runpod.io/pricing), [billing](https://docs.runpod.io/serverless/pricing) |
| Vast.ai | Snapshot at 14:04 UTC: 4090 median $0.449/h (n=30); 5090 $0.776; A6000 48 GB $0.40–0.80; per-second billing; bandwidth billed per GB | **evaluate** | [API snapshot](https://console.vast.ai/api/v0/bundles/) |
| Modal | A10 24 GB $1.10/h; L40S 48 GB $1.95/h; A100-80 $2.50/h. These are **preemptible** base rates (non-preemptible ×3, region ×1.15–1.75). 60 s keepalive is billed. $30/mo Starter credit. | **evaluate** | [pricing](https://modal.com/pricing) |
| PyTorch / CUDA | 2.14.1 ships cu126 (no Blackwell), cu130 and cu132. cu128 ended at 2.11. Drivers: CUDA 12.8 needs ≥570, CUDA 13 needs R580+. | Rule in D-16 | [RELEASE.md](https://github.com/pytorch/pytorch/blob/main/RELEASE.md) |

### 4.9 v1-core plumbing: pitch, transcription, conversion, decoding (added in revision)

The v1-core flow (D-04, D-05) depends on these components. The first pass had no rows for them, so the ticket DAG had no nodes. Rows marked **UNVERIFIED** were not checked against a primary source; their licenses must be verified before adoption.

| Component | Role in v1-core | Code | Weights / data | Mac | Notes | Verdict | Source |
|---|---|---|---|---|---|---|---|
| **SwiftF0 0.3.0** | F0 tracker for melody adherence (D-04 step 6); `segment_notes()` is a transcriber candidate | MIT | MIT-labelled bundled ONNX (14k params), trained on the author's CC BY-NC-SA dataset (provenance caveat) | ONNX Runtime, CPU; Python 3.8–3.14 | Vocadito pitch F1 0.847 vs RMVPE 0.862 in a benchmark run by SwiftF0's author (VENDOR) | **adopt-v1** (individual lane; LLC after a provenance review) | [swift-f0](https://github.com/lars76/swift-f0), [pitch-benchmark](https://github.com/lars76/pitch-benchmark) |
| **librosa 1.0.0** pYIN (+ `sequence.dtw`) | Weights-free F0 cross-check; HMM note segmentation; DTW alignment for the adherence metric | ISC | None | CPU; **requires Python ≥3.12**, so it cannot share Basic Pitch's 3.10 env | Vocadito F1 0.653. Whether librosa's DTW suits the adherence metric is **UNVERIFIED**. | **adopt-v1** | [librosa 1.0.0](https://github.com/librosa/librosa/releases/tag/1.0.0) |
| torchcrepe 0.0.24 / CREPE | Secondary F0 tracker | MIT | MIT-labelled; trained partly on MedleyDB (non-commercial) | PyTorch; MPS undocumented | Vocadito F1 0.789 / 0.781 | **evaluate** (individual/research lanes) | [torchcrepe](https://github.com/maxrmorrison/torchcrepe) |
| PESTO 2.0.1 | Secondary F0 tracker | **LGPL-3.0** | LGPL-3.0 (self-supervised on MIR-1K) | ONNX / TorchScript | Vocadito F1 0.759 | **evaluate** (separate process) | [pesto](https://github.com/SonyCSLParis/pesto) |
| FCPE; RMVPE | n/a | MIT; Apache (Dream-High) | FCPE v001 data unstated, DDSP-200K CC BY-NC-SA; RMVPE has **no official weights**; yxlllc weights unlicensed | PyTorch | RMVPE tops the Vocadito board but has no clean weights | **research-only** | [FCPE](https://github.com/CNChTu/FCPE), [RMVPE](https://github.com/Dream-High/RMVPE) |
| SOME, GAME 1.0.3, ROSVOT | Singing note transcription | MIT | SOME/GAME **CC BY-NC-SA 4.0**; ROSVOT unlicensed, trained on NC M4Singer | GAME ONNX; ROSVOT CUDA 11.8 | No humming data for any of them | **research-only** | [GAME](https://github.com/openvpi/GAME/releases/tag/v1.0.0), [ROSVOT](https://github.com/RickyL-2000/ROSVOT) |
| HumTrans | Humming fixtures for the local benchmark | Eval repo unlicensed | **CC BY-NC 4.0** | n/a | Its own baselines score F1 3.0–5.8 with offsets ignored; labels reported misaligned | **research-only** (personal evaluation) | [paper](https://arxiv.org/abs/2309.09623), [dataset](https://huggingface.co/datasets/dadinghh2/HumTrans) |
| mir_eval | COn / COnP / COnPOff scoring | **UNVERIFIED** | n/a | CPU | Named by GAP-01; license not checked | **evaluate** | n/a |
| VocalParse | Lead for the A4 transcriber (Qwen3-ASR-based singing transcription) | Apache-2.0 per gap research (**UNVERIFIED**) | Same | unknown | Not benchmarked on humming | **watch** | [arXiv 2605.04613](https://arxiv.org/abs/2605.04613) |
| MuScriptor | Multi-instrument audio → MIDI (stems to MIDI, E4) | MIT | **CC BY-NC 4.0**, auto-gated | Official MPS | Reported by gap research; not separately verified | **research-only** | [audio.cpp README](https://github.com/0xShug0/audio.cpp) |
| **MelodySpec → ABC converter** (AURA code) | R1: emit YuE2's native two-voice ABC; store the lyric syllable plan as a sidecar | AURA's license | n/a | Pure Python | Dialect **CONFIRMED** (GAP-02); pad pickups with rests, re-quantize tuplets, single integer tempo; validate with the YuE skill's `abc_tools.py` (Apache-2.0). Converter unbuilt. | **adopt-v1** | [abc-editing.md](https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/abc-editing.md) |
| Internal vocal separator (for the filters) | Separated vocal for lyric PER and melody adherence (D-05); not the user-facing stems feature | see §4.3 | Demucs: individual lane only. Kim Mel-Band-RoFormer: LLC-lane candidate (training data **UNVERIFIED**). | MPS / MLX | Internal analysis only; never exported as a stem | **adopt-v1** (lane-aware) | §4.3 |
| G2P / phonemizer (to choose) | Phonemes for lyric PER (D-05, C2) | **UNVERIFIED** | **UNVERIFIED** | unknown | Any espeak-ng-backed G2P inherits **GPL-3.0** (the Kokoro trap). Which G2P the WSB PER protocol uses is unchecked. | **evaluate** | [misaki pyproject](https://github.com/hexgrad/misaki/blob/main/pyproject.toml) |
| MIDI / General MIDI synth + soundfont (to choose) | R2(ii) "neutral synth render" of the MelodySpec; F6 instrument render; MIDI preview | **UNVERIFIED** | Soundfont terms **UNVERIFIED** (some restrict rendered audio) | unknown | No candidate checked | **evaluate** | n/a |
| Audio decoder (ffmpeg / PyAV / `afconvert`; to choose) | Decode phone voice memos (m4a/AAC, A2) and imported songs (A12) to working PCM | **UNVERIFIED**: ffmpeg is LGPL or GPL depending on build flags | n/a | `afconvert` ships with macOS only | `afconvert` cannot serve the Windows/Linux control service (D-24). Record the ffmpeg build used. | **evaluate** | n/a |

**Hum benchmark ticket (from GAP-01).** Score Basic Pitch, `SwiftF0.segment_notes` and pYIN with HMM note segmentation on Jon's own hums plus HumTrans (personal evaluation only), using mir_eval COn / COnP / COnPOff. The winner becomes the A4 transcriber. Whatever wins, the human correction step (D-04 step 3) stays mandatory.

---

## 5. Unique contributions the build must keep

### From GPT

1. **Three stem operations with separate contracts**: Isolate original, Re-perform this part, Create a new part. This follows from Suno's own "regenerated" disclosure. **D-06**
2. **Engine ≠ profile.** A capability registry keeps published claims and locally measured results in separate fields and records license and use mode. **D-01**
3. **A component-level rights registry with the operator entity** (individual vs LLC). **D-11**
4. **The edit-preservation gate**: working PCM is byte-identical outside the mask, in a declared rate/channels/dtype domain, and native-rate provenance is kept. **D-17**
5. **A codec round-trip ceiling study** before any training. Upsampling changes the container, not the information. **D-19 / D-20**
6. **SongSpec and PerformanceSpec.** Artifact provenance with an origin enum. Honest job states. One heavy model resident at a time. Remote workers expose a project API, never a shell. **D-09 / D-12**
7. **The benchmark design**: 48 briefs with a 12-brief smoke set, equal-candidate and equal-compute tracks, uncertainty clustered by brief, a gate the preferred pair is allowed to lose, and a named owner for each gate. **D-10**
8. **Align only after ASR plus human review.** Do not let a forced aligner "confirm" the requested words.
9. **The DiffSinger warning that energy, breathiness and voicing are coupled**, so they must not be shown as independent sliders.
10. **The narration/TTS survey with its license traps**, the voice_id bundle (the clean recording is the source of truth), the ElevenLabs SSML facts, and cost per *approved* hour. **D-08**
11. **The real-time architecture: two clocks.** No blocking work in the audio callback. Integer sample positions plus ticks plus a versioned tempo map. **D-13**
12. **Practitioner failure modes turned into fixtures**: melody adherence regressing across versions, instrumental flags conflicting with style text, ASR overwriting the author's lyrics, section maps lost between tools.
13. **Storage arithmetic**: a 4-min stereo float32 file at 48 kHz is 92,160,000 bytes (≈ 87.9 MiB). **D-15**

### From Kimi

1. **A cost-bounded ladder for closing the gap**, stopping when the harness says the gap is closed: post-chain → selection → adapters → preference tuning → continued SFT, with scratch training rejected. The ladder is kept. Several rungs are re-costed and re-labelled in **D-05 / D-20**.
2. **Using a third-party benchmark rather than self-scores** for ACE (WSB 6.01 vs 6.87).
3. **The complaint corpus as an attack surface**: export hostage-taking, lyric adherence, edits that destroy songs, dirty stems, no MIDI. AURA's wedge is ownership and export, and that holds even if quality never reaches parity.
4. **Keeping Suno's consent gate** in a personal tool, and automating it. **D-07**
5. **Concrete component leads**, all now checked: demucs-mlx, all-in-one, WhisperX, Matchering, pyloudnorm, Seed-VC, the HeartMuLa webapp pattern.
6. **CUDA fragility named concretely**, with pinned envs and CI. **D-16**
7. **Cloud economics**: serverless scale-to-zero, and rent before buy. **D-03 / D-23**
8. **The cross-audit habit**: one model's research must be checked against another's. This pass is that habit applied to every source, Kimi included.

### From Fable

1. **The fullest Suno command surface**: the #088 Edit menu (Extend, Crop, Remove Section, Reverse, Adjust Speed, Fade, Replace Section, Remaster), Song Editor "Replace Lyrics" and "My Edits", Studio clip settings, the stems panel, the hum-to-instrument flow, and export options. **feature-inventory.md**
2. **Most edits are a scoped Cover.** A lyric fix is a cover of one section's vocals. A per-stem replace is a new lane plus Copy to Main Track. **D-06 / D-17**
3. **Two versions per generation** as the base contract. **D-05**
4. **Primitive contracts with I/O signatures**, a schema with lineage (`parent_id`, `kind`, `version_no`), an autosaved project state, and a single engine-URL switch. **D-09 / D-01**
5. **Repo hygiene**: `data/` gitignored, never commit audio or weights, keys in `.env.local`. Already in this repo's `.gitignore`.
6. **Facts for the owner's paid attempt**: Studio is Premier-only. Voice capture works best at about 2 minutes in a quiet room. **Open question Q7**
7. **Hints from the images**: auto titles and expanded style captions suggest a hidden LLM layer, and lyric-fragment clip labels suggest aligned segments.
8. **Media-capture traps**: YouTube 429 errors from cloud containers, `ffmpeg -fps_mode vfr`, and `-frame_pts` returning frame indices.

---

## 6. Proposed decisions for ADRs

Each entry gives the options considered, the choice, why, and the evidence that would reverse it. All are **proposed**. Accepting one means writing `docs/adr/NNNN-*.md`; the suggested numbering is at the end of this section.

### D-01 Engine adapters and a capability registry
- **Options.** (a) One engine wired in (Fable, effectively). (b) One engine URL or abstraction (Fable, Kimi). (c) Engine = provider boundary and profile = checkpoint + task + backend, with a capability registry (GPT).
- **Choice: (c).** Each worker serves one or more **profiles**. Examples: `ace-2b-turbo` (draft), `ace-2b-sft`, `ace-xl-sft` (render), `ace-2b-base` and `ace-xl-base` (extract, lego, complete), `yue2-3b` (score/text), `sa3-medium-mlx` (instrumental). A profile declares:
  - tasks: `text_to_song`, `instrumental`, `cover`, `repaint`, `extend`, `extract`, `lego`, `complete`, `reference_timbre`, `score_input`
  - limits: max duration, sample rate, channels, **input languages** (YuE2: zh/en only)
  - backend and **host OS** (D-24)
  - **published claims and local test results as separate fields**
  - status: `published`, `smoke-passed`, `benchmarked`, `disabled` (JOVRA ADR-0004 pattern)
  - license record and allowed operator lanes
  
  Workers **reject unsupported jobs before loading**.
- **Why.** Task support really does differ per checkpoint (C4). Turbo silently ignores CFG. Mac behaviour differs per checkpoint (#1259). Licenses differ per component (§4).
- **Reverse if.** A single profile passes every task gate at accepted quality. Nothing does today.

### D-02 First engines and install order
- **Options.** ACE-only (Fable). ACE + YuE2 as a batch path (Kimi). ACE + MiniMax with YuE2 as substitute (GPT). Install everything at once.
- **Choice (revised: now conditional on the operator lane, Q3).** Install in this order, one challenger at a time:
  1. **ACE-Step 1.5 on the Mac, every lane**: 2B turbo draft, then 2B SFT and XL-SFT render profiles. Base checkpoints only when stems or lego are needed.
  2. **The second engine depends on the lane:**
     - **Individual lane: YuE2-3B on a CUDA worker** as the quality and score-conditioned challenger. Every YuE2 artifact is tagged `operator_lane=individual`. Its `adopt-v1` verdict is **conditional on Q1** (a worker or rental passes smoke) **and Q3** (Jon operates the work personally).
     - **LLC lane** (which presumably includes Sabbath Echo; X-50): **HeartMuLa 3B** (Apache-2.0) and **MiniMax Music 3** (Community License) compete in smoke for the second slot. HeartMuLa leads on license; MiniMax carries UI-naming, revenue-threshold and disclosure obligations, and its README asks for two GPUs (CONTESTED against the single-GPU diffusers path). YuE1 (Apache, native stems, much weaker) is a last resort.
  3. **Stable Audio 3 Medium (MLX)** as an optional instrumental lane on the Mac. It needs a gated download and Community License registration.
  4. The other lane's engine, only once its lane has real work.
  
  **Reject**: LeVo 2, DiffRhythm 2, MusicGen/JASCO, StepAudio, HeartMuLa 7B. **Watch**: YuE1. **Research-only**: Shao, MuLaCover, SongEcho.
- **What changed and why.** The first draft put HeartMuLa last and treated MiniMax as the LLC fallback. The gap research found that HeartMuLa is the only non-ACE open vocal model with permissive weights, that MiniMax is CUDA-only (its README asks for two GPUs) and its API is closed, and that YuE2's permission does not cover LLC-directed work (GAP-04, GAP-05, GAP-06). So the second slot is chosen per lane.
- **Why YuE2 for the individual lane.** It has the **only primary-documented melody-score path** (C8, GAP-02) and runs about 71 s per song on a 4090 (VENDOR). Its published quality lead is **VENDOR (self-run)**: WSB 6.73 and the expert study are the YuE2 authors' own. The 6.96 best-of-8 was selected with SongBench (academic-only) and Q3O, which D-05 forbids, so **AURA cannot reproduce it**. Like every quality figure behind this pair, these numbers come from an interested party; no independent human evaluation of ACE or YuE2 is cited. Jon's blind A/B is the only evidence that will count.
- **Selection gate.** Each lane's pair is provisional. The 12-brief smoke set, hum fixtures included, may demote YuE2 in favour of HeartMuLa or MiniMax.
- **Reverse if.** (a) Q3 says the work is the LLC's: YuE2 is out unless its licensors (m-a-p) grant a commercial license in writing. (b) YuE2 fails smoke on the worker. (c) **No CUDA worker or rental is approved.** Then every sung song is ACE-only, because Stable Audio 3 produces no intelligible vocals. That **violates the owner's "not ACE-only" requirement**, so it is a constraint violation that needs Jon's sign-off (Q14), not a routine fallback. The only mitigation is a Metal port of a non-ACE engine (YuE2 via audio.cpp or yue2.cpp in the individual lane; HeartMuLa via audio.cpp in any lane), and it counts only after a Metal-vs-reference parity check and the same smoke gate (GAP-04).

### D-03 Topology: Mac studio plus CUDA worker
- **Options.** Mac-only. CUDA-only. A split.
- **Choice: split.**
  - **Mac**: UI, control service, project store, and a Mac worker (ACE via MLX/MPS, SA3 MLX, Demucs MPS / demucs-mlx, Basic Pitch, TTS candidates).
  - **CUDA worker**: **Linux preferred**, because YuE2 and Shao are Linux-only and ACE is the only engine with official Windows support. **On the Windows box, run CUDA engines under WSL2** with the Windows NVIDIA driver only and `.wslconfig` memory raised to ≥24 GB (WSL2 defaults to half the RAM); native Windows YuE2 needs unmerged patches (GAP-03). Pinned per-engine environments. Containers for SGLang-Omni and Shao.
  - **Job protocol**: workers authenticate, accept only referenced assets, expose a project API and never a shell, enforce VRAM and queue limits, and keep one heavy model resident per GPU.
  - **Until inventory exists**: a **bounded rental** with a spend cap. Vast 4090 median $0.449/h snapshot. RunPod serverless 4090 PRO $1.10/h, which bills model load. Modal A10 24 GB $1.10/h (preemptible).
  - **If no worker is approved**, the topology collapses to the Mac and every sung song is ACE-only. That needs Jon's sign-off (Q14; D-02 reverse-if (c)).
  - **Which host runs the studio** is set by D-24.
- **Why.** Agreement A5/A6. YuE2 has open Mac bugs (#176, #187). MiniMax is CUDA-only. Only two macOS nodes are on the tailnet (C47).
- **Reverse if.** A community Mac port (yue2.cpp or audio.cpp for YuE2 or HeartMuLa; MiniMax MLX once disk allows) passes a Metal-vs-reference parity check and the same smoke gate as the CUDA profile.

### D-04 North-star first flow: melody seed to song
- **Options.**
  - (a) ACE cover at high strength on the raw hum (Fable).
  - (b) Hum → MIDI → sampler (Kimi). This gives an instrument part, not a song.
  - (c) Score-first: transcribe, have a human correct the result into a MelodySpec, render through several measured routes (GPT/GSV direction plus the YuE2 discovery).
  - (d) Suno Studio 2.0's "MIDI clips as a prompt" (hosted).
- **Choice: (c)**, as the first end-to-end flow:
  1. **Capture**: record a hum or sung line in the browser, import a phone voice memo (m4a/AAC, decoded by the §4.9 decoder, license **UNVERIFIED**), or import MIDI.
  2. **Transcribe** with the winner of the local hum benchmark (§4.9): Basic Pitch (Apache-2.0, provisional), `SwiftF0.segment_notes`, or pYIN with HMM segmentation. Each note carries a confidence. **No transcriber is both license-clean and benchmarked on humming** (GAP-01), so step 3 carries the melody.
  3. **Correct** in a piano roll: notes, onsets, tempo map, key. The result is the **MelodySpec**: ticks plus a versioned tempo map, and the source audio hash.
  4. **SongSpec**: lyrics (approved text kept separate from any ASR transcript) **and their language**, sections, style, references with permissions, duration, candidate budget.
  5. **Render routes.** Phase 0 runs **three** of them side by side (R1, R2-raw, R2-synth); R3 is research.
     - **R1, YuE2 score route** (CUDA, **individual lane only**): MelodySpec → the §4.9 converter → YuE2's native two-voice ABC (fixed header, one integer tempo, full bars only, no tuplets or pickups) → `abc=` with `cot='melody'` (chord symbols stripped) or `cot='full'`. Lyrics bind only by section tags and order; the syllable plan is a sidecar. It is **conditioning, not exact rendering**: 84% exact pitch on edited scores (VENDOR, GAP-02). About 6 minutes maximum; **Chinese and English lyrics only**.
     - **R2, ACE cover route** (Mac, every lane): cover or `cover-nofsq` on **(i) R2-raw**, the raw hum, and **(ii) R2-synth**, a neutral render of the MelodySpec through the §4.9 MIDI synth (license **UNVERIFIED**), sweeping `audio_cover_strength` from 0.8 to 1.0 and `cover_noise_strength`.
     - **R3, guide-vocal route** (research): DiffSinger/OpenUtau score-to-singing, then ACE `complete` (base) for accompaniment.
  6. **Measure** every candidate's melody adherence against the MelodySpec. Separate the vocal with the lane's **internal separator** (Demucs in the individual lane; an LLC-clean separator such as Kim Mel-Band-RoFormer otherwise), track F0 with SwiftF0 (pYIN as the cross-check), DTW-align, then compute median cents error, octave-error rate, onset F1 and contour correlation.
  7. **Candidate fan-out.**
     - **Phase 0 (benchmark)**: each enabled route produces **2 candidates per hum fixture**, so routes are compared at equal candidate count.
     - **Product (v1-core)**: each request shows **2 candidates**. By default they come from the **two best routes that passed the Phase-0 adherence gate in the request's lane**, one each, so an individual-lane pair is normally mixed-engine (R1 + R2). If only one route passed, both candidates come from it with different seeds. In the LLC lane only R2 exists today, so both candidates are ACE. Every candidate records its route, engine profile and seed, which stay hidden during blind A/B. **Jon's ear decides.**
- **Why.** The owner's starting point is a melody in his head (A12). ACE cover poorly preserves cover identity (Hit@1 2.4% at strength 0.8, COMPETITOR-RUN), and the maintainer says it is not note-for-note (C8). YuE2 with a transcribed score reached 71.3% Hit@1 (VENDOR, self-reported). A human-corrected symbolic stage makes the tune explicit, editable and testable. Suno itself moved toward MIDI-as-prompt (C52).
- **Reverse if.** Phase-0 hum fixtures show R2 passing the adherence gate. The simpler Mac-only path then becomes the default and R1 drops to optional.
- **Note.** SheetSage2 (YuE2's own transcriber) is NC, and YuE2's user-ABC path does not load it. Basic Pitch needs Python 3.10 on Apple Silicon, while librosa 1.0 needs ≥3.12, so they run in separate environments.

### D-05 Candidate count, best-of-n and scoring
- **Options.** Always 2 (Fable). Best-of-8–16 with automatic scorers (Kimi). Equal-candidate and equal-compute tracks with priced tiers (GPT).
- **Choice.**
  - **Default 2 candidates per request.** This matches Suno's documented contract and WSB's protocol.
  - Apply **hard-constraint filters first**: decodes, non-silent, duration within tolerance, no clipping or true-peak overs, lyric phoneme error rate on the vocal separated by the lane's internal separator (Qwen3-ASR or Whisper, with phonemes from the §4.9 G2P, whose license is **UNVERIFIED** and must not pull in GPL espeak-ng unless run as a separate process), and melody adherence when seeded. These filters use the internal separator; they do not depend on the user-facing stems feature (E1). **Never hide a candidate.** Show its failure badges instead.
  - Larger n is an **explicit, priced tier** with its budget logged. It is promoted only if AURA's blind A/B shows a gain.
  - Aesthetic scores (audiobox-aesthetics, LAION-CLAP) are **diagnostics** and never select by default.
  - **No NC scorer in shipped code.** SongEval, MuQ, SongBench, CMI-RM and TuneJury may run only in personal research jobs flagged NC.
- **Why.** C13 (refuted). C14 (licenses, plus scorers that can't see above 8–12 kHz). HeartMuLa's reward-hacking evidence.
- **Reverse if.** Blind A/B on Jon's own briefs shows best-of-n with permissive scorers beating best-of-2 at equal listening time.

### D-06 Stems: three operations
- **Choice.** Three operations with separate contracts:
  - **Isolate original**: a separator stores mixture, stems **and residual**. Gates: bleed, sum-to-mixture residual, and listening to stem, residual and rebuilt mix.
  - **Re-perform this part**: generative. ACE `extract`, repaint or cover on a stem, and later other engines. Always labelled a *new performance*. Gates are on notes, onsets and timbre identity, not residual.
  - **Create a new part**: ACE `lego` / `complete` on base / xl-base.
  
  **ACE's `extract` is generative, so it falls under Re-perform even though it is named "extract".**
  
  Separators: Demucs 4.1.0 htdemucs as the baseline, plus demucs-mlx on the Mac, **in the individual and research lanes only**, because the author says the weights are research/personal-only (GAP-06). The LLC lane needs a separator with verified weights; Kim Mel-Band-RoFormer (vocals) is the first candidate, and ACE `extract` is generative, so it belongs to Re-perform. RoFormer checkpoints only from an allow-list keyed on verified license. Logic Pro 11.2 as a comparator if Jon owns it. **Replace = rebuild the mix from retained sources**, never layer.
  
  **Native generation stems** (GAP-06): only YuE1 writes separate vocal and instrumental tracks. YuE2 and MiniMax output one mix. ACE base `lego` appears to return the generated part on its own (medium confidence), which fits "Create a new part".
- **Why.** C22 (Suno regenerates). C23 (open separators reach guitar 9 / piano 7.8 dB at best, 6s has no backing vocals, the best checkpoint has an unknown license). GAP-06 (Demucs weights).
- **Reverse if.** None for the contract. The separator choice is revisited by benchmark.

### D-07 Singing voice lane
- **Choice.**
  - **v1 has no voice cloning.** ACE `reference_audio` is offered and labelled as a "global timbre/style reference" only.
  - **v2 adds a private voice registry with a consent gate modelled on Suno's.** The owner (or an authorized singer) records a sung sample, then speaks a displayed random phrase. Two checks: a speaker-embedding match between phrase and singing (WeSpeaker, CC-BY-4.0, or ECAPA, Apache), and an ASR check of the phrase. Then a rights checkbox, `consent_at`, and permitted uses. The clean recording is the source of truth, and embeddings are cache.
  - Conversion uses **Applio/RVC as an optional, auditioned operation in a separate process**. The contested weights license is recorded on every artifact.
  - **Seed-VC is rejected** (archived, GPL).
  - DiffSinger stays research. Commercial use would need a self-trained vocoder.
- **Why.** C4 (no ACE voice cloning), C24, C25.
- **Reverse if.** Jon wants his own voice on this first song. Conversion then moves into v1 for the **individual lane only**, and it **stays CONTESTED**: the lj1995 base weights that Applio and RVC use carry a "research use only" rider, and rmvpe.pt is unlicensed and trained partly on CC BY-NC-SA data. **Whether a released song with converted vocals is permissible is unresolved**, so converted-vocal songs are flagged in the export manifest and Jon decides per release (Q6). Not legal advice.

### D-08 Narration lane (Sabbath Echo), pinned separately
- **Choice.** A **detachable narration service with its own spec and tickets**. It shares only the artifact, provenance, job and storage contracts with music.
  - **Operator lane: LLC (presumed).** Per the owner's domain registry, Sabbath Echo is an Island Development Crew venture, so its narration and any music beds are presumably LLC work (X-50; Jon confirms in Q3). In that lane **YuE2 and every NC component are excluded**: no YuE2 beds, no Demucs, no NC scorers. Every candidate below has permissive weights.
  - **Pilot** on approved, permitted text and consented voices: VoxCPM2 (Apache, official MPS), Qwen3-TTS (Apache), the Chatterbox family (MIT, watermarked), CosyVoice3 (Apache), and Kokoro as a baseline. Ranked by cost per **approved finished hour** against current ElevenLabs list prices (C55), with **Eleven v4** as the quality bar, since v4 and v4 Turbo now top the AA TTS board (GAP-08).
  - **Long-form is a core requirement, not an add-on.** No independent long-form evaluation of these engines exists, and an independent paper shows Qwen3-TTS and VoxCPM2 degrading badly past ~1,500 words ([arXiv 2609.16989](https://arxiv.org/abs/2609.16989)). The service chunks at semantic boundaries and runs **ASR verify-and-regenerate** per chunk, and quality is measured in-house: long-form WER drift plus blind listening.
  - **Voice continuity is seeded only from original human recordings** (Jon's or a consenting narrator's). ElevenLabs' Prohibited Use Policy §9(j)(k)(l) bars using its renders as ML input or training data, so existing renders can be neither a cloning reference nor a dataset. If the current voice is an ElevenLabs Voice Library or Voice Design voice, it cannot be carried over (Q9).
  - **Excluded**: OmniVoice, F5-TTS, Fish S2-Pro, VibeVoice.
  - VoiceStudio is a UX reference, not an embedding (AGPL; NC default weights; ~10 GB).
  - The Scripture boundary waits for the **owner's confirmation** (C54).
- **ElevenLabs baseline (INFERRED).** At ~150 words per minute a finished hour is ~9,000 words, or ~50–58k characters. At the $0.08 per 1K list price (v3, Multilingual v2, v4), that is **about $4.0–4.6 per finished hour**, half that at the $0.04 Flash/Turbo price. The OWNER-REPORTED ~$25k would therefore buy roughly **5,400–6,300 finished hours** at list API price with no regeneration. If the real output is far smaller, the difference is regeneration, subscription overhead or voice multipliers. The business case depends on which, so Q9 asks for the plan and usage split (X-48).
- **Why.** The owner pinned this separately. GPT judges narration the faster payback (GSV §3; `companion/voice-studio-research.md`). Narration targets are smaller and directly testable.
- **Reverse if.** Jon makes narration the priority. It then becomes the first spec, with music second.

### D-09 Project and artifact provenance format
- **Choice.**
  - **Storage**: SQLite (WAL) for metadata and **content-addressed immutable audio** (SHA-256). Native-rate originals are always kept, and conversions point to their source.
  - **Entities**:
    - `Project`, `SongSpec`, `MelodySpec` (`PerformanceSpec` later)
    - `Reference`: hash, role, crop, strength, permission
    - `Job`, `Candidate`
    - `Artifact`, with origin enum `generated_mix | separated_source | regenerated_part | new_part | human_recording | rendered_midi | tts_render | conversion | imported_mix` (`imported_mix` carries its source service and terms, e.g. a Suno download; A12), plus: engine profile, weights revision and hash, code commit, params as *intent + actual*, seed, machine/backend, cold/warm wall time, parents, `operator_lane`, license chain
    - `EditOperation`: mask, crossfade, locked context, variants, accepted
    - `TakeLane`
    - `ExportManifest`: human contributions, model/license chain, AI-disclosure flag (required when any MiniMax output is included), converted-vocal flag (D-07), imported-source terms (A12), loudness report with the standard revision used
  - One versioned project graph holds sections, lyrics, beats, clips, tracks and references. C2PA-style credentials are optional and later.
- **Why.** All sources agree on SQLite. GPT's provenance model. MiniMax AUP #11. JOVRA ADR-0004.
- **Reverse if.** Multi-user sharing becomes a goal, which would need a server store.

### D-10 Evaluation harness and quality target
- **Choice.**
  - **Target**: "Suno v6-class", defined operationally because no v6.5 exists. It is a **blind, loudness-matched, randomized A/B** of AURA keepers against Suno v6 outputs on the same briefs. Loudness is BS.1770-4 integrated loudness from pyloudnorm with our own true-peak meter; whether BS.1770-5 gives the same result for stereo is **UNVERIFIED** (X-47). The v6 outputs come from Jon's own paid Suno generations, used for **listening only**: the harness applies only DSP loudness matching to them, never separation, ASR or any model scoring.
  - **Revised (GAP-07): the Suno arm needs Jon's explicit acceptance of a ToS risk (Q7).** Suno's 2026-09-03 ToS bars using Output to "create, develop or improve any competing products" and to "compete with Suno", and using Suno audio to test AURA is the highest-risk reading. If Jon declines, the target arm uses human-made reference recordings he owns or has licensed, with WSB and AA numbers as external context only. Not legal advice.
  - It also includes **operational gates**: melody adherence, lyric PER, edit preservation, export alignment, playback stability.
  - **Fixtures**: a **12-brief smoke set**:
    1. Hummed melody
    2. MIDI chord seed
    3. Guide vocal with corrected lyrics
    4. Explicit no-vocal instrumental
    5. Three-reference role task
    6. One-word replace
    7. Chorus-only replace with protected verses
    8. Long (>4 min) piece
    9. Sparse acoustic worship
    10. Dense pop
    11. Rhythm-heavy
    12. Cinematic instrumental bed
    
    Then the **48-brief set** (8 categories × 6). This resolves GPT's inconsistency: 48/12 and two engines, not 40×4 and three engines.
  - **Protocol**: equal-candidate and equal-compute tracks; uncertainty clustered by brief; everything preregistered (asset hashes, operator, pins, budgets, paid-run ceiling); rejects retained; **Jon is the named gate owner and listener**. Each brief is run in the lane it belongs to, so LLC-lane briefs never use YuE2.
  - Automatic metrics are diagnostics. WSB and AA numbers are external context only.
- **Why.** C11, C13, C28, C29, C43.
- **Reverse if.** None for the process. Thresholds are set at preregistration.

### D-11 Licensing doctrine: personal now, ready to open-source later
- **Choice.**
  1. Keep a component register (this document, §4, plus the JSON) recording code, weights and output terms, gating, redistribution status and allowed operator lanes.
  2. AURA's own code uses a permissive license; Jon chooses MIT or Apache-2.0.
  3. **Never vendor or redistribute weights.** Download at runtime and record the license acceptance.
  4. **Copyleft and NC tools run only as optional separate processes behind the job protocol.** GPL: Matchering, Seed-VC. AGPL: ACE-Step-DAW, openDAW, VoiceStudio, JUCE-AGPL. NC: weights.
  5. **Every artifact records `operator_lane`** (individual / LLC). YuE2, SheetSage2, MuQ-family, SongEval and **Demucs** outputs are tagged individual or research only. LLC work includes Sabbath Echo and every other Island Development Crew venture (presumed; Q3).
  6. Maintain a **release-blocker list**:
     - NC weights: YuE2 (and its GGUF conversions), SheetSage2/MERT2, MuQ/MuQ-MuLan, SongEval, MuLaCover, OmniVoice, F5-TTS, the DiffSinger vocoders, Shao, MusicGen/JASCO, SOME/GAME, MuScriptor, the HumTrans dataset
     - Non-commercial by author statement: **Demucs weights** (and demucs-mlx conversions), moved here from "unknown" (GAP-06)
     - Research-only or academic: SongBench, SongPrep, Fish, VibeVoice
     - Unknown license: BS-RoFormer SW, LeVo, SCNet weights, ROSVOT weights, RMVPE community weights
     - Permissive label over NC training data (provenance review before LLC use): SwiftF0, CREPE/torchcrepe
     - Contested: RVC/rmvpe weights, heartlib-mlx (no LICENSE file), whether YuE2's creator permission covers converted GGUF weights
     - Copyleft: Rubber Band, espeak-ng (via Kokoro or any espeak-backed G2P), PESTO (LGPL-3.0), ffmpeg if a GPL build is bundled
     - Unverified (must be checked before adoption): mir_eval, the G2P, the MIDI synth and soundfont, the audio decoder
     - Obligations: MiniMax (UI naming, revenue threshold, AUP), Stability (<$1M, registration, attribution, no training on outputs)
  7. **Suno outputs are a listening reference, and Jon's own downloads may be imported for DSP finishing** (mix, master, format; GAP-07). ML separation of Suno audio is grey, so prefer Suno's own stems. Suno audio is never training data, and never conditioning or generative-edit input, unless Jon accepts the ToS risk explicitly (C35, Q7).
- **Reverse if.** Jon decides AURA stays private permanently. Rules 3–4 then relax to record-keeping only.

### D-12 Application stack and UX direction
- **Choice.**
  - **Browser on localhost first.** React + TypeScript (Vite build, no SSR needed for a local single-user tool), talking to a **FastAPI** control service.
  - **SQLite**, with a **durable `jobs` table**. States: `queued`, `preparing`, `loading`, `generating`, `analyzing`, `ready`, `failed`, `cancelled`. Progress reports real steps, never invented percentages. Outputs commit atomically.
  - **SSE** for progress.
  - Python workers in **per-engine `uv` environments**.
  - The control service and UI stay **portable across macOS, Windows and Linux** (D-24).
  - A **Chromium-based browser is required for Studio** (C39).
  - **UX**: listening-first. A large audition area, level-matched A/B, and progressive disclosure. Controls appear only where a backend implements them. **No imitation of Suno's branding or look**, per the owner's design rules. Standard names (Cover, Extend, Replace) where they help muscle memory.
- **Why.** A7, C38, C41, C49. Fable's Next.js is workable but adds SSR and routing complexity this single-user tool doesn't need.
- **Reverse if.** An installable app is needed earlier, in which case add the D-14 shell.

### D-13 Studio audio engine and timeline
- **Choice.**
  - **Two clocks.** An AudioWorklet playback graph for bounded preview. A separate offline render for export. No inference, disk or network work in the audio path.
  - **Timeline**: integer sample positions, musical ticks, and a versioned tempo map. Quantization is reversible.
  - **Base**: evaluate **waveform-playlist v16 (MIT)** against a timeline of our own. **Do not use wavesurfer-multitrack.**
  - **Time and pitch**: Signalsmith Stretch (MIT) first, SoundTouch as fallback.
  - **Recording**: deferred until measured. When it ships, it is latency-compensated recording, not live monitoring (browser round trip is ~52 ms in Chrome).
  - **Gates**: 8 tracks for 30 minutes with no underruns, measured with Chrome `playbackStats`, and UI p95 under 100 ms while a generation runs, **on each OS that will host the Studio** (MG-E14; D-24). 16 tracks is a stretch gate. This resolves GPT's 8-vs-16 inconsistency. The ~52 ms Chrome round trip is from a 2021 MacBook Pro; Windows and Linux are unmeasured (X-49).
- **Reverse if.** The gates fail in Chromium. Then build a native engine on CPAL (Apache), with VST3 (MIT) for plugins later. JUCE only under its EULA.

### D-14 Desktop shell
- **Choice.** **Defer.** When a shell is needed, prefer **Electron** (Chromium audio, MIT). Re-evaluate Tauri v3's CEF runtime when it leaves alpha. Tauri 2 on macOS (WKWebView) is not suitable for Studio.
- **Why.** C40.
- **Reverse if.** Tauri CEF ships stable, or WebKit gains `latencyHint` and `setSinkId`.

### D-15 Storage
- **Facts.**
  - Internal free space read 5.5, 4.0, 2.0 and 4.5 GiB on 2026-10-09 (MEASURED-LOCAL). It fluctuates, probably with purgeable space, and never approached the reported 8.5 GiB.
  - External `/Volumes/Backup Plus` is exFAT with 1.2 TiB free, writable, on USB 5 Gb/s. It is probably an HDD, and its throughput has not been measured.
  - exFAT has no symlinks, so the Hugging Face cache runs in its **degraded no-symlink mode**.
  - About 58 GB may be reclaimable internally (`~/.ollama` 21 GB, simulators and runtimes, caches). The figures differ between verifiers, and **the owner decides**.
- **Choice.**
  1. **Nothing installs until Jon picks a model-store volume.** The model store root is configurable. The proposed default is `/Volumes/Backup Plus/aura/models`, with `HF_HOME` and the xet cache set there before any download, accepting slower loads. An APFS SSD is recommended.
  2. **The project store is content-addressed and configurable**, on internal SSD if Jon frees space, otherwise on the external volume.
  3. **A disk preflight refuses any job or download** that would leave less than a configured margin free on any volume (proposed 10 GiB).
  4. **Downloads are selective** (`allow_patterns`):
     - ACE turbo + encoder + VAE: ~6.34 GB
     - XL: prefer diffusers bf16 (~11 GB) over F32 (~20 GB) once loader support is verified
     - MiniMax: diffusers subset (~28.5 GB)
  5. Caches are bounded (MLX cache limit for demucs-mlx). Working files are float32 and budgeted at ~87.9 MiB per 4-minute stereo stem. Previews are lightweight.
- **Reverse if.** Jon frees about 60 GB or more internally. Then the Mac-local profiles (ACE, SA3, Demucs, TTS) move to internal SSD.

### D-16 Environment pinning
- **Choice.** One `uv` environment, or container, per engine profile, with its pins recorded in the registry:
  - **ACE**: main ≥ `ca1e85fe9430179831e6bc6be790c332190a3866`, or v0.1.8 (`dce62140…`) with `dcw_enabled=False, shift=1.0` for non-turbo models.
  - **YuE2**: torch 2.10.0 on Linux or WSL2 (cu128 wheel: driver ≥570.26 on Linux, ≥570.65 on Windows). Raising torch to ≥2.13 to get the MPS fix (#176, PR #190) would push Blackwell cards onto cu130 and R580+ drivers.
  - **MiniMax**: diffusers ≥0.40.0 (not the PR commit).
  - **Shao**: the NGC 25.02 container only.
  - **CUDA wheel by GPU generation**: Blackwell needs cu128 (torch ≤2.11) or cu130+ with driver R580+. Turing–Ada can use any. Pascal is limited to cu126.
  
  **"Latest" is never a version.** Upgrades are admitted only after the smoke set passes.
- **Why.** C46, A8.
- **Reverse if.** None.

### D-17 Edit semantics
- **Choice.**
  - A generative edit is a **proposal until committed**. Undo restores the prior artifact; it never regenerates.
  - **Preservation gate**: working PCM is byte-identical outside the edit and crossfade mask, in a declared rate/channels/dtype domain. Compare samples, not WAV headers.
  - A whole-song rerender is **never labelled a local edit**.
  - Section and word edits use ACE repaint, which needs main's explicit chunk mask (#1292).
  - Approved lyrics, ASR transcript and alignment are separate assets.
- **Why.** GPT/GSV contract, Fable's scoped cover, verified repaint behaviour.
- **Reverse if.** None.

### D-18 Generation controls
- **Choice.** Controls are capability-aware. Record the creative **intent** and the **actual** engine parameters. There is no universal slider mapping: turbo hides CFG, and Weirdness or Style Influence appear only where a profile maps them. Conflicts are resolved before submission, e.g. an instrumental flag alongside vocal tags.
- **Why.** C4; GSV-14 (an "instrumental" generation picked up vocals because the style text still named them: `companion/video-analysis.md`, MJ4d0-Wi1z8 13:00–13:32); GSV-06 (v6 exposes Variety, Weirdness, Style Influence and Max Mode as separate controls, so record intent and actual parameters).
- **Reverse if.** None.

### D-19 Post-production
- **Choice.** Measure first.
  - **v1**: BS.1770-4 integrated loudness with pyloudnorm, **plus our own ≥4× oversampled true-peak meter**. A ticket diffs BS.1770-4 against -5 for stereo programme; until then reports name the revision actually used (X-47). Always keep a dry export. Loudness targets depend on the destination.
  - **v2**: optional mastering through Matchering (GPL), as a separate process.
  - **No generative super-resolution by default.** DeepFilterNet runs on speech only.
  - A codec round-trip ceiling study (ACE VAE, HeartCodec, SA3 SAME) runs before any enhancement or training claim.
- **Why.** C27, qe-5.
- **Reverse if.** A blind A/B shows a mastering stage improves keepers without hiding defects.

### D-20 Training and personalization
- **Choice.**
  - **No scratch training.** The non-ML taste memory comes first: preferences, accepted takes, reasons.
  - Adapters (ACE LoRA/LoKr; plan for 16–20 GB per the tutorial; Mac MPS is unproven) come only after the harness exists, and only on data Jon owns or has consent for, with a per-track license record.
  - **MTG-Jamendo and FMA are excluded for anything shareable. Suno outputs are never used.**
  - Preference tuning (DPO) runs only with held-out human preference and an evaluator distinct from the reward. Tango2 is text-to-audio with NC-SA weights. DiffRhythm+ evaluated on its own reward scorers.
- **Why.** C7, C36, C45, qe-6.
- **Reverse if.** None for the doctrine. The adapter timing moves with the harness.

### D-21 The Suno boundary
- **Choice.**
  - Jon uses Suno for his first attempt at this song, through the official app only.
  - AURA treats Suno outputs as a **listening reference** (the A/B arm itself needs Jon's acceptance of the ToS risk; D-10, Q7).
  - **AURA may import Jon's own permitted Suno download and finish it with DSP** (mix, master, format), and the result may be released (GAP-07; feature A12). Suno grants that edit/process right "to the extent such use is incidental", which it does not define. Suno's provenance marks must not be removed or altered.
  - **Separating Suno audio with an ML model is grey**: use Suno's own stems (Pro "Auto" / "Split from mix"; Premier adds "Advanced split").
  - **Generative edits** (cover, repaint, extend), **voice conversion**, and **any use of Suno audio to develop or test AURA** stay out unless Jon accepts the ToS risk explicitly. Re-performing from Jon's own melody and lyrics, which are his Submissions, is unaffected.
  - Jon should know that uploading the melody grants Suno a perpetual license to it.
  - No third-party "Suno API".
  - Plan choice: Premier ($30/mo, or $24/mo billed yearly) gets Studio 2.0, 32-bit/48 kHz stems and Advanced Split. Pro ($10/mo) has no Studio and a cap of 20 downloads a month (Q7). On Pro/Premier, Suno assigns its rights in the output to Jon, and the assignment and download rights survive cancellation.
- **Why.** C35, C51, C52, GAP-07. Not legal advice.
- **Reverse if.** Suno changes its ToS.

### D-22 Hosted provider lane
- **Choice.** Optional, explicit, pinned, and **not in v1-core**: Mureka `mureka-9.5`, Gemini Lyria 3.5, Stability SA3 Large. Each records billing and terms. MiniMax's API is unavailable.
- **Why.** C37.
- **Reverse if.** Jon wants a premium hosted fallback for the LLC lane.

### D-23 Cost accounting
- **Choice.** Every job logs compute cost, cold and warm wall time, candidates per keeper and review time. The reporting denominators are **accepted song** and **approved narration hour**. Rent before buying. Rental figures are snapshots.
- **Why.** C44; GSV-50 (GPT's cost model, `compute_hours = A·r·m`, with accepted hours as the denominator: `companion/voice-studio-research.md` §8).
- **Reverse if.** None.

### D-24 Cross-platform scope (added in revision)
- **Context.** Jon requires Linux, Windows and macOS support (X-46; recorded in GPT's `companion/FRAMING.md` and operationalized as MG-E14–E16). No source and no earlier decision addressed it. D-03 implicitly made the Mac the only studio host and the other machines workers.
- **Options.** (a) Mac-only studio; Linux and Windows are workers forever. (b) The control service and localhost UI must run on all three OSes, with the Studio's real-time playback gated per OS. (c) Full three-OS parity in v1.
- **Choice: (b).**
  - **The control service and localhost UI run on macOS, Windows and Linux.** They are written portably: Python/FastAPI, SQLite, `uv`, React served to a Chromium browser. No macOS-only dependency in the control service (for example `afconvert` for decoding, §4.9). MLX and Metal code live only inside Mac worker environments. CI runs the control service's tests on all three OSes from the first tickets.
  - **Workers are per OS by capability**: the Mac for MLX profiles; Linux, or WSL2 on the Windows box, for CUDA engines (D-03).
  - **Studio playback is gated per OS**: 8 tracks for 30 minutes with no underruns and UI p95 under 100 ms (MG-E14). Never call the Studio three-platform ready from one OS. All browser latency evidence (C39) comes from a 2021 MacBook Pro, and **Windows and Linux Chrome are unmeasured** (X-49).
  - **v1 delivery order**: the Mac first, because it is the only reachable machine. Windows and Linux hosting is verified as soon as either machine is reachable, and the MG-E15 DAW round trip and MG-E16 recovery tests follow on each OS.
- **Why.** Owner requirement (X-46). The stack in D-12 is already portable, so (b) costs little now and avoids a later rewrite. (c) cannot be tested while neither machine is reachable.
- **Reverse if.** Jon says the studio host is always the Mac (Q13). Then this relaxes to (a) and CI on Windows and Linux covers only the workers.

### Suggested ADR files

| Decision | Proposed file |
|---|---|
| D-01 | `0001-engine-profiles-and-capability-registry.md` |
| D-02 | `0002-first-engines-ace-mac-yue2-cuda.md` |
| D-03 | `0003-mac-studio-and-cuda-worker-topology.md` |
| D-04 | `0004-melody-seed-score-first-flow.md` |
| D-05 | `0005-two-candidates-hard-constraints-scorers-as-diagnostics.md` |
| D-06 | `0006-three-stem-operations.md` |
| D-07 / D-08 | `0007-singing-voice-lane-and-consent.md`, `0008-narration-is-a-separate-service.md` |
| D-09 | `0009-content-addressed-artifacts-and-provenance.md` |
| D-10 | `0010-blind-listening-harness-and-v6-target.md` |
| D-11 | `0011-licensing-doctrine-and-operator-lanes.md` |
| D-12 – D-14 | `0012-localhost-react-fastapi-sqlite.md`, `0013-two-clock-audio-engine.md`, `0014-desktop-shell-deferred.md` |
| D-15 – D-23 | One ADR each, or fold D-16 – D-23 into the spec's "rules" section |
| D-24 | `0024-cross-platform-control-service-and-per-os-studio-gates.md` |

---

## 7. Open questions only the owner can answer

1. **CUDA hardware.** For the Linux and Windows machines, please run `nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv`, `nvidia-smi`, `lscpu` / `free -h` / `df -h` on Linux, and `dxdiag` or `systeminfo` on Windows. Include **total system RAM** (YuE2 recommends 24 GB of host RAM) and, on Windows, whether WSL2 is installed. Can either machine join the tailnet? A 16 GB card is worth a YuE2 smoke run (A4 is open); otherwise, is a bounded rental acceptable, and what is the monthly ceiling?
2. **Disk.** Internal free space read between 2.0 and 5.5 GiB today. Do you know what is filling it? Which of these should go: `~/.ollama` (21 GB), Xcode simulators and runtimes, caches? Or should models live on "Backup Plus"? That drive is exFAT and probably an HDD, so loads will be slow. Reformatting a partition to APFS would erase it. A new SSD is the other option.
3. **Operator.** Will this song, and AURA output generally, be released by **you personally** or by **Island Development Crew LLC**? And is **Sabbath Echo** work (narration and any music beds), like other IDC ventures, LLC work? The answer decides which second engine each lane gets (D-02) and whether YuE2, Demucs or any NC component may touch the work. Two sub-questions the YuE2 licensors have not answered publicly: does a single-member LLC count as a "company", and does the individual permission cover converted (GGUF) weights? If you want YuE2 for any LLC work, write to the licensing contacts named in the YuE README and MODEL_LICENSE (they differ) before relying on it.
4. **Release plans.** Will the first song be streamed or sold? MiniMax output requires an AI disclosure. Pond5 and Envato ban AI uploads. Copyright requires human authorship.
5. **Open-source intent and license.** Should AURA's own code be MIT or Apache-2.0, and roughly when might it be public?
6. **The melody itself.** Is it recorded anywhere yet (voice memo, MIDI, notation)? Do you play an instrument? Are there lyrics, and in what language? **YuE2 accepts only Chinese and English lyrics.** Do you want to **sing it yourself**? If so, own-voice conversion moves into v1 for the individual lane, but releasing a song with converted vocals is **CONTESTED** under the RVC base-weights rider, so you would decide per release.
7. **Suno plan for your paid attempt.** Premier ($30/mo; Studio 2.0, 32-bit/48k stems, Advanced Split) or Pro ($10/mo)? Do you accept that uploading the melody gives Suno a perpetual license to it, and that Suno outputs may not be used to train or "power" AURA? Two further choices: (a) do you want AURA to **finish your Suno version with DSP** (allowed), and (b) do you accept the ToS risk of using your Suno outputs as the **blind A/B reference** when evaluating AURA? If not, the target arm uses human-made reference tracks you own (D-10).
8. **Listening.** Are you the gate owner and blind-A/B listener? How many listening minutes per week? Is anyone else allowed to vote?
9. **Sabbath Echo.** Is "never TTS Scripture" still the rule? Is it AudioVerse or Bible Brain? Can you share ElevenLabs invoices or a usage export, split by **plan, model and characters billed**? At list API price, $25k would buy roughly 5,400–6,300 finished hours (INFERRED, D-08), so the split shows whether the spend was output, regeneration or plan overhead. Which narration languages? Is the current voice a **clone of a human recording you hold**, or an ElevenLabs Voice Library / Voice Design voice? Only the first can be carried to a local engine, because ElevenLabs bars its renders as cloning references. Which voices are consented? Is narration higher priority than music?
10. **Browser.** Is requiring Chrome or another Chromium browser for the Studio acceptable?
11. **Logic Pro.** Do you own it? Its Stem Splitter is a strong free comparator for you.
12. **Name.** Keep "AURA" for now?
13. **Cross-platform.** Must the studio itself (control service, UI, playback) run on Windows and Linux, or is the Mac always the studio host with the other machines as workers? D-24 proposes portable code with per-OS playback gates.
14. **No-CUDA outcome.** If no CUDA worker or rental is approved, every sung song would be ACE-only, which breaks your "not ACE-only" requirement. Do you accept that, or should a non-ACE Metal port (YuE2 or HeartMuLa) be attempted first, knowing none has parity evidence yet?

---

## 8. What remains unverified

Nothing was installed or generated, and nobody listened. Specifically:

- **Quality**: how any engine performs on Jon's genres and briefs; whether any route keeps a **hummed** melody; whether ACE `cover-nofsq` or strength 1.0 does better than 0.8; YuE2's score route on a hum (its 71.3% Hit@1 is self-reported on SHS100K, not hums) and on **hand-written** ABC (its 84% pitch figure is for edited model scores). **No independent human evaluation of ACE-Step 1.5 or YuE2 is cited**; every quality figure behind the chosen pair comes from an interested party. Whether the AA board or the CMU Music Arena lists either engine was not checked.
- **Mac performance**: ACE turbo, SFT and XL timings on the M5 Pro (no official figures exist); SA3 Medium MLX on an M5 Pro (the vendor figure is an M4 Pro); demucs-mlx speed on a 20-core GPU; any transcriber's accuracy on **Jon's** hums (the only public humming figure is COMMUNITY); WhisperX accuracy on singing; Mac LoRA (a NaN report is open); **Metal parity** of YuE2 or HeartMuLa through audio.cpp or yue2.cpp, and MiniMax through MLX at full length.
- **Hardware**: the Linux and Windows GPUs (**UNVERIFIABLE** from here); whether a 16 GB card runs YuE2 at maximum context (A4); YuE2 under WSL2 on the Windows box; the external drive's type and throughput; why internal free space fluctuates; whether the ACE app loads diffusers-format XL weights.
- **Contested points (not fact)**: ACE LoRA VRAM (12 vs 16–20 GB); whether ACE cover keeps melody; whether v6 beats v5; the RVC/rmvpe weights license; MiniMax one vs two GPUs and 32 vs 44.1 kHz; MuLaCover's weights license; heartlib-mlx's license (no LICENSE file); whether YuE2's creator permission covers converted GGUF weights; the SA3 Large API price (8 vs 26 credits); Suno's minimum voice-sample length (10 s vs 15 s).
- **Unverifiable**: the LeVo 2 license; whether Suno ranks hidden candidates; Suno's $2.99 extra download; v5's 44.1 kHz; Suno codenames (chirp-crow/fenix); Suno ARR; the "1293 Elo" for v5; the current Sabbath Echo Scripture rule; the ~$25k ElevenLabs spend; Max Mode's credit cost.
- **Never checked**: Kimi's ~150-source claims beyond those above; GPT's companion corpus beyond the points cited here (now archived, still UNVERIFIED); SongEcho's license; the training-data provenance of TuneJury's "Apache CLAP-only" variant and of Kim Mel-Band-RoFormer; Signalsmith Stretch quality; the fit of waveform-playlist; browser round-trip latency on an **M5 Pro** with an audio interface, and on **Windows and Linux** Chrome at all (X-49); HeartMuLa and DiffRhythm 2 VRAM on consumer cards; licenses of FastAPI, SQLite, React, Vite and uv (assumed permissive), and of **mir_eval, the G2P, the MIDI synth and soundfont, and the audio decoder** (§4.9); whether BS.1770-5 changes stereo integrated loudness relative to -4 (X-47); VoxCPM2 and Qwen3-TTS quality on Sabbath Echo text; SAM Audio memory on 48 GB unified memory; the prior-art studios (Ruach, Riff, Remiqora), VocalParse and MuScriptor, which the gap research reported but did not verify separately.
- **Legal readings are interpretations, not legal advice**: whether listening comparisons against Suno outputs breach the ToS's "power, enable" item or its "develop or improve any competing products" and "compete with Suno" covenants; whether ML separation of a Suno download is "incidental" processing; whether a single-member LLC is a "company" under YuE2's permission, and whether Jon can license an individually made YuE2 song to his LLC; whether a released song with RVC/Applio-converted vocals is permissible; whether GPL tools behind a process boundary keep AURA's license clean.

---

## Sources

Primary URLs are inline. The per-claim source lists, verdicts, asserting sources and the verifier and skeptic verdicts are in [`evidence-register.json`](evidence-register.json), and every observed or proposed feature is in [`feature-inventory.md`](feature-inventory.md). The archived source corpora, the GPT companion files, and the raw extraction, verification, gap and critic outputs are in `sources/`, with SHA-256 sums in `sources/SHA256SUMS`. The checks marked MEASURED-LOCAL were made on this Mac on 2026-10-09 with `df -h`, `sw_vers`, `sysctl`, `system_profiler` and `grep` over `sources/claude-fable/`.

---

## Revision log

**2026-10-09, second pass** (critic review plus gap research GAP-01…08). Decisions are still proposals.

- **Decisions changed.** D-02 is now lane-conditional: YuE2 for the individual lane; HeartMuLa or MiniMax by smoke for the LLC lane, with HeartMuLa promoted from last. YuE2's `adopt-v1` is conditional on Q1 and Q3. D-02/D-03's no-CUDA fallback is reframed as an owner sign-off (Q14), not a routine fallback. D-04 gains a transcriber benchmark, the YuE2 ABC contract, lane-aware internal separation and a defined candidate fan-out. D-06 restricts Demucs to the individual and research lanes. D-10's Suno A/B arm now needs Jon's acceptance of a ToS risk. D-11 rule 7 and D-21 allow DSP finishing of Jon's Suno downloads. **D-24 (cross-platform) is new.**
- **Labels corrected.** YuE2's WildSongBench scores and expert study are VENDOR (self-run), not unlabelled; the 6.96 best-of-8 cannot be reproduced under D-05. MiniMax's cost estimate is COMMUNITY-derived on a 5090 for a 30-s clip. A4 is OPEN, not confirmed. pyloudnorm is BS.1770-4. Dates are ISO 8601.
- **Register.** X-06 restated as "Suno v6.5 exists" (refuted); X-02 is `corrected`. Every claim carries `verification_question`, `verifier_verdict`, `skeptic_checked` and `skeptic_verdict`, recovered from the workflow journal. New claims V-gap-1…8 and X-46…50; 19 new component rows, including the §4.9 plumbing nodes (several UNVERIFIED).
- **Archived.** GPT's companion corpus (`sources/gpt-sol/companion/`), the GSV-01…69 extraction and the raw verification, gap and critic outputs (`sources/workflow-2026-10-09/`), all hashed in `sources/SHA256SUMS`. GSV citations now resolve to files and sections.
- **New measurement.** Internal free space 4.5 GiB at 15:27Z, so the volume fluctuates rather than falls steadily.
- **Feature inventory.** New rows A11 (internal analysis separation, v1-core), A12 (import a finished song), H8 (voice continuity from human recordings), J19 and J20 (cross-platform). A6 and C7 were reconciled with D-04's routes, and the coverage check now lists `separate` and the §4.9 plumbing.
