# The Suno boundary: Jon's own Suno downloads may be imported for listening and DSP finishing, and never used to build, test or train AURA

Status: accepted (2026-10-09). Owner decision O-08 (Suno outputs are excluded from the harness; AURA may import Jon's own
Suno download for DSP finishing). From D-21, amended: the A/B-arm question (Q7) is closed by declining the risk. The
enforcement mechanism is ADR-0036. Not legal advice.

Suno's 2026-09-03 terms forbid using its output "to power, enable or train other artificial intelligence and machine
learning models", and include a covenant against competing with Suno. They allow edit and process rights "to the
extent such use is incidental", a phrase they do not define. Suno takes a perpetual license to uploaded content, which
would include Jon's melody. On Pro and Premier, Suno assigns its rights in the output to Jon, and the assignment
survives cancellation.

**Decision.**

- Jon uses Suno through its official app only. AURA never calls a third-party "Suno API".
- AURA may **import Jon's own permitted Suno download** as an `imported_mix`, recording its source service and terms,
  and **DSP-finish** it: mix, master, format (feature A12, v1-studio). The finished result may be released. Suno's
  provenance marks are preserved, never removed or altered.
- A Suno import is **never** an audition arm, an evaluation reference, engine or conditioning input, the source of a
  generative edit (cover, repaint, extend), the source of a voice conversion, input to ML separation (Suno's own stems
  are the way to get stems), training data, or material used to develop or test AURA.
- Any further use needs a signed **risk acceptance** naming that use, which is an owner act.
- Re-performing from Jon's own melody and lyrics, which are his own submissions, is unaffected.
- AURA's UI does not imitate Suno's branding or look.

**Why.** O-08. The terms put using Suno audio to develop or test AURA at the highest risk, while DSP finishing of a
permitted download is allowed (C35, GAP-07).

## Consequences

Jon should know that uploading his melody to Suno grants Suno a perpetual license to it. The choice between Pro and
Premier stays Jon's and affects only his own use of Suno.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Jon may import his own Suno stems as one set and mix them non-generatively; placing a Suno import on a timeline beside AURA-generated audio is refused unless a risk acceptance names edit input. Free-plan output is not importable. The account holder is recorded, and a Suno import is llc-eligible only when the LLC holds the account or a written license.

**Reverse if:** Suno changes its terms, or Jon signs a risk acceptance for a named use (only engine, conditioning,
separation, edit or conversion input). A Suno arm, evaluation reference or anchor in the listening harness is excluded
by O-08 whatever is signed; it would need O-08 revisited and ADR-0010 amended first.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C22, C31, C35, C51, C52, GAP-07; §4.2; §6 D-21.
[evidence-register.json](../research/evidence-register.json) X-07, V-gap-7, V-suno-5, V-suno-6.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-08.
[feature-inventory.md](../research/feature-inventory.md) A12, G4.
