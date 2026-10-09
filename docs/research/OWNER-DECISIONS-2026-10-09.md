# Owner decisions, 2026-10-09

Jon's answers to the questions raised while fusing the research (RECONCILIATION.md §7). They are binding inputs to the ADRs, spec and tickets. Anything not listed here keeps the proposed default and is marked **owner-pending** wherever it appears.

| # | Topic | Decision | Effect |
|---|---|---|---|
| O-01 | Tracker | Private GitHub repo `Navigata1/aura`, JOVRA-style: one issue per ticket, native blocking edges, one branch/PR per ticket into an integration branch. | `docs/agents/issue-tracker.md` |
| O-02 | Compute | A **compute profile** is chosen at install and at the start of any session, and can be switched at any time. There are four tiers: **1** NVIDIA 24–32 GB (4090/5090 class), **2** NVIDIA 24 GB (3090 class), **3** NVIDIA 12–16 GB with offload or burst, **4** Apple Silicon MLX/MPS plus a rented CUDA burst. AURA detects the hardware and recommends a tier. On the current machine (M5 Pro, 48 GB) the recommendation is tier 4. Jon may select any tier or platform whenever he needs to. | Closes Q1 for the design (actual Linux/Windows GPU specs remain **owner-pending**), Q13 → D-24 option (b), and Q14: a rented burst is approved, so sung songs are not ACE-only. |
| O-03 | Storage | Model weights live on the external **Backup Plus** drive (exFAT, USB, about 1.2 TiB free). The internal disk is nearly full (2–8 GiB free, fluctuating). | AURA's store is an **APFS sparse bundle on Backup Plus**, which restores symlinks and POSIX permissions without reformatting. It holds models, HF/uv/pnpm caches, engine environments, worktrees and, by default, the project store. Disk preflight applies to every volume. |
| O-04 | Melody input | Both: **hum or sing into a mic, and MIDI** (keyboard or file). Either way the melody becomes an editable, owned MelodySpec. | D-04 confirmed as the north-star first flow. |
| O-05 | First feel | All four categories: **worship / acoustic ballad**, **cinematic / orchestral**, **R&B / soul / pop ballad**, and a **broad mix**. Jon supplies one reference "standard" song for each. | Briefs, evaluation and later adapters are anchored to these. The reference standards are listening-only assets with a permission record. |
| O-06 | Operator lane | **Per project, defaulting to individual.** Jon's personal songs are `individual`. Sabbath Echo and every other Island Development Crew venture are `llc`. AURA enforces each lane's component eligibility. | Closes Q3. YuE2, Demucs and NC scorers are allowed only in `individual` (and `research`) projects. |
| O-07 | Own voice | **v2.** v1 uses the engines' vocals, plus ACE reference timbre labelled as a global style reference. The consent-gated voice registry and own-voice conversion come in v2. | Closes Q6 (voice). The RVC/rmvpe contested weights stay out of v1. |
| O-08 | A/B target | Jon's **reference standards**, listening only. Suno outputs are **excluded from the harness**. AURA may import Jon's own Suno download for DSP finishing (mix, master, format). | Closes Q7 (risk declined). D-10's target arm = owned or licensed references. |
| O-09 | Rented GPU | A standing cap of **$25 per month**, and **every paid run still needs Jon's explicit yes**. Every run is logged against the cap before it starts. | The burst runner has a budget guard and an approval gate. |
| O-10 | Name | "AURA" is the working name while the tool is personal. It lives in one constant so a rename is cheap. | |
| O-11 | Cross-platform | Jon wants to select platform and compute whenever necessary. The control service and UI stay portable across macOS, Windows and Linux. Studio playback is gated per OS. | D-24 (b). |

## Still owner-pending (defaults used until answered)

- Linux/Windows GPU, RAM and WSL2 details, and tailnet reachability (Q1). Default: tier 4 on the Mac.
- Release plans for the first song (Q4). Default: personal; every export carries an AI-disclosure-ready manifest.
- AURA code license (Q5). Default: choose MIT or Apache-2.0 before the repo goes public; until then, all rights reserved, but every component must already pass the open-source-readiness register.
- The melody itself, lyric language (Q6). Default: English lyrics. Jon will record his melody as the first hum fixture.
- Listening gate owner (Q8). Default: Jon is the named gate owner and the only voter.
- Sabbath Echo narration details (Q9). The narration lane is **out of scope for the music v1 spec** and gets its own spec later. Only the shared artifact, provenance, job and storage contracts must not preclude it.
- A Chromium browser required for Studio (Q10). Default: yes.
- Logic Pro ownership (Q11). Default: unknown, so it is not a comparator.
