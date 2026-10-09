# Quality is judged only by Jon's blind, level-matched auditions against his own reference standards; Suno output is not in the harness

Status: accepted (2026-10-09). Owner decisions O-05 (four feels, one reference standard each) and O-08 (reference
standards for listening only; Suno outputs excluded from the harness). From D-10, amended: the Suno target arm is
removed. Jon as the named gate owner and only voter is the owner-pending default (Q8).

No Suno v6.5 exists, so v6 is the operational reference for the ambition "Suno-v6-class". Every published quality
number for the candidate engines is VENDOR or COMPETITOR-RUN. Automatic scorers are biased (SongBench was trained on
Suno v4–v5 samples) or deaf above 8–12 kHz. Using Suno output to test AURA is the highest-risk reading of Suno's terms
(GAP-07), and Jon declined that risk.

**Decision.**

- **The target arm** is Jon's four **reference standards** (worship or acoustic ballad, cinematic or orchestral, R&B,
  soul or pop ballad, and a broad mix): human-made, owned or licensed, imported as `listening_only` references with a
  permission record. They are never engine input. A Suno import is never an audition arm or a reference (ADR-0021,
  ADR-0036). WildSongBench and Artificial Analysis numbers are external context only.
- **Audition mechanics.**
  - An audition opens over two or more candidates only when every arm is ready, so arrival order cannot leak.
  - Labels are drawn with a CSPRNG when the audition opens; only `sha256(mapping ‖ nonce)` is published.
  - Every arm is a 48 kHz, 24-bit preview. Gains are attenuation-only, down to the quietest arm's BS.1770-4
    integrated loudness (pyloudnorm, labelled as such), with true-peak headroom from AURA's own meter oversampling at
    least 4×. The remaining mismatch is at most 0.1 LU.
  - Audio is served by label with identical headers and no file name. Nothing but "unplayable" shows before the
    verdict.
  - Duration and sonic character cannot be hidden and are acknowledged as a residual leak.
- **Verdicts** are immutable owner acts: A, B, tie or neither, with optional axes, problem intervals and seconds
  listened per label. A reveal follows and must match the commitment.
- **Two kinds of listening.**
  - Everyday product verdicts are recorded as `listening-unregistered` evidence and shown per route ("kept n of m").
    They never change a status.
  - Only a **preregistered** set of eval auditions can promote or demote, through route-standing records the plan reads. First the **smoke set** of 12 briefs: hummed
    melody, MIDI chord seed, guide vocal with corrected lyrics, explicit no-vocal instrumental, three-reference role
    task, one-word replace, chorus-only replace with protected verses, a piece over 4 minutes, sparse acoustic
    worship, dense pop, rhythm-heavy, and a cinematic instrumental bed. Then the **benchmark set** of 48 (8 categories
    of 6), mapped to the four feels.
  - Protocol: the preregistration hash is committed before any run; equal-candidate and equal-compute tracks;
    uncertainty clustered by brief; about 10% hidden repeat pairs to measure listener consistency; rejects retained;
    each brief run in its own lane. A set of eval auditions short of its quota concludes `inconclusive` and promotes nothing. In
    evaluation mode a reference standard may be an anchor, acknowledged as recognizable.
- **Operational gates** sit beside listening: melody adherence, lyric error rate, edit preservation, export alignment
  and playback stability.
- **The preferred choice may lose.** Any route, YuE2 included, can be demoted by the records.

**Why.** Automatic and vendor numbers cannot carry the decision (C11, C13, C28, C29, C43). O-05 and O-08 define the bar
and exclude Suno. GAP-07 sets out the Suno risk Jon declined.

## Consequences

"Suno v6-class" is never claimed from a vendor figure, a leaderboard or a scorer. Thresholds are fixed at
preregistration, so the ambition can fail. Jon's listening minutes are the scarce input, and keeper cost records them.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The three-reference role task is not runnable in v1, because role-bound multi-reference conditioning (B11) is v2; one-word and chorus-only replace run once edit operations exist, and the MIDI chord seed once chord symbols exist. Every smoke brief resolves to a runnable plan or an explicit 'not yet runnable' record. A Suno arm would need O-08 revisited as well as this ADR amended; a risk acceptance can never name an audition arm or an evaluation reference or anchor.

**Reverse if:** nothing reverses the process; thresholds change only through a new preregistration. If Jon later
signs a risk acceptance for a Suno arm, this ADR must be amended before that arm enters.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §0; §2 C11, C13, C28, C29, C43, GAP-07; §4.2; §4.5;
§6 D-10. [evidence-register.json](../research/evidence-register.json) V-qe-2, V-qe-3, V-suno-2, V-gap-7, X-06, X-34,
X-47. [OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-05, O-08.
[architecture.md](../spec/architecture.md) §4.7, §5 (`audition/1`, `eval-brief/1`, `prereg/1`), §11 (TB8,
P4).
