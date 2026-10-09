# Two candidates per request; hard constraints badge them; automatic scorers are diagnostics only

Status: accepted (2026-10-09). From D-05. No owner decision changes it.

Suno's documented contract is two songs per generation. YuE2's own tables refute the claim that best-of-n closes a
third to a half of the gap to Suno: going from 2 to 8 candidates moved expert preference against six proprietary
systems from 48.0% to 48.4%, and against v6 it fell from 40.0% to 36.1% (VENDOR). The good automatic scorers are mostly
non-commercial, cannot hear above 8–12 kHz, and HeartMuLa's DPO on SongEval and AudioBox shows reward hacking.

**Decision.**

- **Two candidates per request** by default.
- **Hard constraints first**, on every candidate:
  - it decodes, is not silent, and fits its duration tolerance;
  - it has no clipping or true-peak overs;
  - its lyric phoneme error rate is measured on the vocal from the lane's internal separator, with Whisper or
    Qwen3-ASR and a G2P whose license must be verified first; a G2P that pulls in GPL espeak-ng runs only behind a
    process boundary;
  - when seeded, its melody adherence is measured: vocal, then SwiftF0 with a pYIN cross-check, then DTW, giving
    median cents error, octave-error rate, onset F1 and contour correlation. Adherence is validated on NeutralVoice
    ground truth before it is shown on real candidates.
- **A failing candidate is never hidden.** It carries a badge. In an LLC project with no eligible separator,
  adherence reads "unmeasured".
- **A larger n** is an explicit, priced choice with its budget logged (v1-studio). It is promoted only if AURA's own
  blind auditions show a gain.
- **Diagnostic scores** (audiobox-aesthetics, CC-BY-4.0; LAION-CLAP, CC0) are shown and never used to select.
- **No non-commercial scorer selects anything.** SongEval, MuQ and MuQ-MuLan, CMI-RM and TuneJury may run as
  diagnostics in individual and research projects (O-06), behind the process boundary and never selecting, ranking or
  filtering; SongBench stays research-only (academic terms). Their register rows say so.
- A "neither" verdict re-rolls with new seeds and counts toward keeper cost (ADR-0023).

**Why.** Best-of-n was refuted on human listening (C13). The scorers have license and bandwidth limits (C14). Jon's
blind audition is the only acceptance gate (ADR-0010).

## Consequences

The candidate count is part of the SongSpec and of the keeper-cost record. A badge never leaks route or profile in a
blind audition: before the reveal only "unplayable" shows.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Hard constraints are computed before the audition and shown after the reveal; only 'unplayable' shows before it. Their thresholds live in gate records committed before any real evidence. This ADR originally restricted non-commercial scorers to the research lane, narrower than O-06; the review restored O-06.

**Reverse if:** blind auditions on Jon's own briefs show best-of-n with permissively licensed scorers beating best-of-2
at equal listening time.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A13; §2 C11, C13, C14; §4.5; §4.9; §6 D-05.
[evidence-register.json](../research/evidence-register.json) V-qe-1, V-qe-3, X-09, X-14.
[feature-inventory.md](../research/feature-inventory.md) A7, C1, C2, C6, C8, C9.
[architecture.md](../spec/architecture.md) §4.7, §4.9.
