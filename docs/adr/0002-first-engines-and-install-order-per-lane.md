# First engines: ACE-Step on the Mac in every lane, YuE2 for the individual lane, HeartMuLa or MiniMax by smoke for the LLC lane

Status: accepted (2026-10-09). Owner decisions O-02 (a rented burst is approved, so sung songs are not ACE-only), O-06
(operator lane per project, default individual) and O-09 (cap and per-run approval). From D-02, which was conditional
on Q1 (CUDA hardware) and Q3 (operator). O-02 and O-06 settle both conditions for the design.

No open-weights engine has been shown to match Suno v6. In the YuE2 authors' own expert study, listeners preferred v6
over YuE2 best-of-8 by 59.3% to 31.6% (VENDOR-run). Every quality figure behind the engines chosen here comes from an
interested party, and only Jon's blind auditions will count (ADR-0010).

**Decision.** Install one challenger at a time, in this order:

1. **ACE-Step 1.5 on the Mac (MLX/MPS), every lane.** 2B turbo (draft) first, then 2B SFT (render), then XL-SFT after
   its own smoke run and the diffusers bf16 loader check. Base checkpoints only when stems, lego or complete are
   needed. Code and weights are MIT.
2. **Individual lane: YuE2-3B on CUDA.** In tier 4 it runs as an approved burst (ADR-0030); in tiers 1–3 it runs on a
   local CUDA host once smoke passes there. It is the only engine with a documented melody-score input (`abc=` with
   `cot='melody'` or `'full'`; GAP-02). Its weights are CC BY-NC 4.0 plus an individual-creator permission that
   excludes "commercial use of the model weights by companies" (GAP-05). So every YuE2 artifact is eligible only for
   the individual and research lanes, and a YuE2 request in an LLC project is refused at submit and again by the
   worker.
3. **LLC lane (Sabbath Echo and every IDC venture): HeartMuLa 3B (Apache-2.0) and MiniMax Music 3 (Community License)
   compete in smoke** for the second slot, in phase P6 or as soon as a CUDA host is reachable. HeartMuLa leads on
   license. MiniMax carries UI-naming, revenue-threshold and AUP #11 disclosure obligations, and its README asks for
   two GPUs (CONTESTED against a single-GPU diffusers path). YuE1 (Apache, native vocal and instrumental tracks, much
   weaker) is a last resort.
4. **Stable Audio 3 Medium (MLX)** as an optional instrumental profile on the Mac (v1-studio), after its gated
   download and Community License registration. It produces no intelligible vocals.

**Rejected:** LeVo 2, DiffRhythm 2, MusicGen/JASCO, StepAudio 3 Music, HeartMuLa 7B (unreleased), Stable Audio Open 1.0,
and the MiniMax hosted API (closed to new users since 2026-08-20). **Watch:** YuE1, the MiniMax MLX ports.
**Research-only:** Shao, MuLaCover, SongEcho.

**Why YuE2 for the individual lane.** A score input fits the hum-to-song goal. ACE cover kept song identity poorly in
a competitor's test (Hit@1 2.4% at strength 0.8, COMPETITOR-RUN), while YuE2 with a score reached 71.3% (VENDOR,
self-reported on SHS100K, not on hums). Its WildSongBench 6.73 is VENDOR (self-run). Its best-of-8 score of 6.96 was
selected with SongBench (academic-only) and Q3O (which needs an 80 GB GPU), both of which ADR-0005 forbids, so AURA
cannot reproduce it.

## Consequences

- In tier 4 every YuE2 candidate is a burst run: quoted, approved by Jon, reserved and logged against the $25 monthly
  cap. If Jon declines a run, that request's plan is labelled "ACE-only: burst declined". Nothing is substituted
  silently.
- In the LLC lane only ACE has a melody route until a challenger passes smoke, so LLC candidate pairs are ACE-only
  for now.
- Each lane's pair is provisional. The smoke set, hum fixtures included, may demote YuE2.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Every profile installs on its own (preflight, license acceptance, verified selective download, conformance, smoke), one at a time. YuE2's license acceptance archives two documents, the Hugging Face LICENSE (CC BY-NC 4.0) and the GitHub MODEL_LICENSE that carries the individual-creator permission; both are hashed again at install and at quote time, and a change voids the acceptance and refuses R1 until Jon accepts again, which is how a narrowing of that permission (this ADR's reverse condition) is detected. YuE2 earns smoke-passed on its burst host class in its own ticket before any product R1 run.

**Reverse if:**

- YuE2 fails smoke on its host class.
- Its licensors narrow the individual permission, or Jon obtains a written commercial license and wants YuE2 for LLC
  work.
- A Metal port (yue2.cpp or audio.cpp for YuE2, audio.cpp for HeartMuLa) passes a Metal-against-reference parity check
  and the same smoke gate. It then becomes another host class, and YuE2 stops needing a burst in tier 4.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §0; §2 C8, C9, C11, C13, C15–C17, GAP-02, GAP-04, GAP-05,
GAP-06; §4.1; §6 D-02. [evidence-register.json](../research/evidence-register.json) V-ace-6, V-ace-8, V-eng-1,
V-eng-3, V-eng-4, V-eng-5, V-gap-2, V-gap-4, V-gap-5, X-13.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-02, O-06, O-09.
[architecture.md](../spec/architecture.md) §4.10, §7.3, TB3, TB7.
