# A generative edit is a proposal until accepted, leaves audio outside its mask byte-identical, and undo never regenerates

Status: accepted (2026-10-09). From D-17. Scope: v1-studio (TB9, phase P5).

Suno users report edits that destroy songs. Fable observed that most Suno edits are a scoped cover; GPT defined a
testable "local edit". ACE repaint can scope a section, but the explicit chunk mask exists only on main (#1292).

**Decision.**

- An **edit operation** (`edit-operation/1`) holds a mask, crossfades, locked context, its candidates and the accepted
  one. It is a proposal until Jon accepts a candidate through an audition. The result is a new keeper revision.
- **Preservation check**: AURA composites each candidate (the original outside the mask and crossfades, the engine's
  output inside), and the composite's PCM outside the mask and crossfades is byte-identical, in a declared rate,
  channel and sample-type domain. The engine's raw deviation outside the mask is recorded separately as chunk-mask
  evidence against a rule committed in advance. Samples are compared, not WAV headers. Native-rate provenance is kept.
- **Undo** restores the prior artifact by hash. It never regenerates.
- A whole-song re-render is **never labelled a local edit**.
- Section, line and word edits use ACE repaint with main's chunk mask. Extending uses repaint at the start or end.
- Approved lyrics, ASR transcript and alignment are separate assets, and ASR never overwrites approved lyrics.

**Why.** It makes "local edit" a check that can fail, which is how AURA avoids destroying keepers. The rules come from
GPT's edit contract (MG-E06), Fable's scoped-cover insight and repaint's verified behaviour (C4).

## Consequences

Edit results are candidates like any other and go through the same audition. A planted one-sample change outside the
mask must fail the gate (P5-2).

**Reverse if:** nothing foreseen reverses this.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C4; §5 (GPT 4, Fable 2); §6 D-17.
[feature-inventory.md](../research/feature-inventory.md) B7, D2–D5, D8. [architecture.md](../spec/architecture.md) §5
(`edit-operation/1`), §11 (TB9, P5-2, P5-3).
