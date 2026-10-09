# Topology follows a compute profile: four tiers, recommended from detected hardware, chosen per session and switchable at any time

Status: accepted (2026-10-09). Owner decisions O-02, O-09 and O-11. From D-03 (Mac studio plus CUDA worker), amended:
the split topology becomes one of four compute tiers, and the no-CUDA sign-off (Q14) is closed because a rented burst is
approved. The Linux and Windows GPU, RAM and WSL2 details are still owner-pending (Q1); until they arrive the default
is tier 4 on the Mac.

Jon's Mac is an M5 Pro with 48 GiB of unified memory, which is not 48 GB of NVIDIA VRAM (Metal
`recommendedMaxWorkingSetSize` 37.44 GiB, MEASURED-LOCAL). YuE2 and MiniMax need CUDA, and YuE2 has open MPS bugs
(#176, #187). The Linux and Windows machines are not reachable today, and Jon wants to choose platform and compute
whenever he needs to.

**Decision.**

- A **compute tier** describes the studio's hardware: **1** NVIDIA 24–32 GB (4090/5090 class), **2** NVIDIA 24 GB
  (3090 class), **3** NVIDIA 12–16 GB with offload or burst, **4** Apple Silicon (MLX/MPS) plus a rented CUDA burst.
- **Recommendation** is a pure, golden-tested function over detected hardware: Apple Silicon gives tier 4; NVIDIA with
  at least 23.5 GiB and compute capability 8.9 or higher gives tier 1; at least 23.5 GiB at 8.0–8.6 gives tier 2;
  11.5–23.5 GiB gives tier 3; every NVIDIA tier needs compute capability 8.0 or higher (BF16), so an older card or a
  host with no accelerator is burst only (tier-4 placements for CUDA profiles; MLX profiles are unavailable off the
  Mac), with a warning. O-02 names tier 3 as 12–16 GB; placing 16–23.5 GiB cards in tier 3 is a deliberate extension,
  with a warning, until Jon confirms it. It warns on host RAM under
  24 GiB for YuE2, drivers below 570.26 (Linux) or 570.65 (Windows) for cu128, a Blackwell card paired with cu126, and
  WSL2 memory under 24 GiB. It never qualifies a tier from hardware it has not probed. **This Mac recommends tier 4.**
- A **compute profile** is the chosen tier preset plus a placement for each engine profile: local, a registered worker
  host, or burst. `studioctl setup` writes the default from the recommendation. Every session start shows the hardware
  snapshot, any change since last time, the recommendation with reasons and per-tier evidence, and all four tiers.
  Jon may pick any tier, host or platform. If the hardware cannot satisfy a tier, its profiles resolve to burst or to
  `Unavailable(reason, remedy)`, and the plan says so before submit.
- **Switching** is allowed at any time and is logged. Jobs not yet dispatched are re-planned. Jobs awaiting approval
  are re-quoted, which invalidates the old approval. Running jobs finish where they are unless Jon cancels them. Every
  job and artifact records its compute profile, placement and host class. Projects never change.
- **Topology.** The **studio host** runs the browser, the control service, the store and the analysis worker: the Mac
  in tier 4, and the Mac or the CUDA host in tiers 1–3. **Worker hosts** run engine workers: Linux preferred, or WSL2
  on the Windows box with `.wslconfig` memory of at least 24 GB, because native Windows YuE2 needs unmerged patches.
  Workers bind loopback or the tailnet, require a token and expose no shell (ADR-0026). One heavy model is resident
  per device.
- **Burst** is the tier-4 home for CUDA-only profiles and an overflow in tiers 1–3, always under the $25 monthly cap
  and with Jon's approval of every run (ADR-0030). A 16 GB card gets YuE2 only after a smoke record on that card,
  because whether 16 GB is enough is still open (A4).

**Why.** O-02 and O-11. A fixed Mac-plus-worker topology cannot follow Jon between machines. Tier presets let the same
projects run on any of them, and the recommendation is honest about what has been measured.

## Consequences

Tiers 1–3 are designed and tested against recorded `nvidia-smi` output, but stay unverified on Jon's hardware until a
host is reachable (P6). A Metal port of YuE2 or HeartMuLa becomes placeable only as another host class, after a parity
check and the smoke gate.

**Reverse if:** a community Metal port passes parity and smoke (YuE2 then leaves burst in tier 4), or Jon's Linux or
Windows hardware arrives with facts that break a threshold (the presets change; the mechanism stays).

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A4–A6; §2 C10, C44, C46, C47, GAP-03, GAP-04; §4.8;
§6 D-03. [evidence-register.json](../research/evidence-register.json) V-cost-1, V-cost-2, V-eng-2, V-gap-3, V-gap-4,
X-04. [OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-02, O-09, O-11.
[architecture.md](../spec/architecture.md) §3, §7.1–§7.4.
