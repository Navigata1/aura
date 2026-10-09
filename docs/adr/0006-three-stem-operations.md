# Stems are three different operations: Isolate original, Re-perform this part, Create a new part

Status: accepted (2026-10-09). From D-06, with separator lanes per O-06. Isolate original is v1-studio; Re-perform and
Create a new part are v2 (feature inventory E1, E5, E6). Whether Logic Pro is a comparator is owner-pending (Q11);
until Jon says he owns it, it is not one.

Suno's stems are regenerated, not extracted: "Suno listens to it and regenerates each stem from scratch", with up to 12
stems from Auto Split. Open separators give 4–6 stems at best. The best open 6-stem checkpoint has an unknown license.
Demucs's pretrained weights are for research or personal use only, by their author's repeated statement (GAP-06).

**Decision.** Three operations, with separate contracts and labels:

- **Isolate original.** A separator stores the mixture, the stems **and the residual**. Gates: bleed and residual
  energy against thresholds committed in a gate record before the first real run, the sum-to-mixture integrity check on
  the stored and exported files (which can fail after a conversion), and Jon's listening verdict on stem, residual and
  rebuilt mix; until that verdict, stems read "separated · unreviewed". It runs on distinct `isolate` profiles, whose
  stems are exportable separated sources carrying the separator's lanes and release blockers, never on the internal
  `separate` profiles, whose output is analysis.
- **Re-perform this part.** Generative: ACE `extract`, repaint or cover on a stem, and later other engines. Always
  labelled a new performance. Its gates are notes, onsets and timbre identity, not residual. **ACE's `extract` is a
  re-perform, even though it is named "extract".**
- **Create a new part.** ACE `lego` or `complete` on base or XL-base. `lego` appears to return the new part on its own
  (medium confidence).

**Replacing a part means rebuilding the mix.** The replacement goes on its own track, and copying it to the main track
re-renders the mix from retained sources. It never layers over a mix that still contains the old part.

**Separators are lane-aware.** Demucs 4.1.0 (adefossez) htdemucs, and demucs-mlx on the Mac, are allowed in the
individual and research lanes only, downloaded at runtime and never bundled. The LLC lane needs a separator whose
weights and training data pass review; Kim Mel-Band-RoFormer (vocals) is the first candidate. RoFormer checkpoints come
only from an allow-list keyed on verified licenses.

The **internal separation** that feeds adherence and lyric-error checks (ADR-0005) is analysis, not this feature. Its
output is never exported as a stem, and its `analyzed_by` edge never carries its lane into the keeper (ADR-0029).

**Why.** Suno regenerates (C22). Open separators are limited and their checkpoints are often unlicensed (C23). Demucs
weights are research and personal only (GAP-06). Calling a regenerated part "isolated" would be a false claim.

## Consequences

The UI never calls a regenerated part isolated. Native generation stems are rare: only YuE1 writes separate vocal and
instrumental tracks, and YuE2 and MiniMax output one mix.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Kim Mel-Band-RoFormer's register row is individual and research until its training-data review passes; only then does a contract-fix PR widen it to llc. Whether Demucs-isolated stems may appear in a released individual song is owner-pending; until Jon answers, they are release-blocked in the manifest.

**Reverse if:** nothing reverses the three contracts. The separator choice is revisited by benchmark and license
review.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A9, A10; §2 C22, C23, GAP-06; §4.3; §5 (GPT 1, Fable
2); §6 D-06. [evidence-register.json](../research/evidence-register.json) V-sep-1, V-sep-2, V-sep-7, V-gap-6, X-10,
X-16. [feature-inventory.md](../research/feature-inventory.md) E1–E10.
[architecture.md](../spec/architecture.md) §3.1 (separator worker), §10.
