# NeutralVoice, AURA's own guide synth, renders the assembled melody, and SongForm turns phrases into a full-length song

Status: accepted (2026-10-09) with the v1 architecture. It resolves tension T-14 by replacing the UNVERIFIED MIDI synth
and soundfont on the v1-core path.

Route R2-synth needs a neutral render of the MelodySpec, but no MIDI synth or soundfont license has been verified, and
some soundfonts restrict rendered audio. Tests need hums whose true notes are known, and CI needs a fake microphone and
a fake engine that sound like singing.

**Decision.**

- **NeutralVoice** is a deterministic additive voice with formants, written and licensed by AURA, with vowel, vibrato
  and drift as parameters. It runs as the analysis worker's `guide` task. One synth does four jobs:
  1. the R2-synth conditioning input for ACE cover;
  2. ground-truth fixtures for transcription and adherence (±30 cents drift, onset jitter, vibrato, breath noise,
     rubato, and a line mixed under an accompaniment bed), generated at test time and never committed;
  3. FakeEngine's sound;
  4. the fake-microphone input for Playwright.
- **SongForm assembly** (`Score.assemble`) turns phrases, repeats and instrumental bars into a full-length `assembled`
  MelodySpec. The guide, R1's ABC and R2-raw's layout of hum slices (`assemble-audio`) all follow it.

**Why.** It keeps the core path license-clean, and it gives every test real ground truth.

## Consequences

Guides have the origin `rendered_guide` and are never candidates. Synthetic evidence from NeutralVoice can fail anything
but never promotes a profile to benchmarked (ADR-0027).

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The evidence this reverse-if reads is Jon's verdict on the NeutralVoice guide as a cover input, recorded in the first-real-pair ticket.

**Reverse if:** NeutralVoice fails Jon's ear as a cover input. A license-verified MIDI synth then becomes an alternative
renderer behind the same `guide` task, and NeutralVoice keeps its other three jobs.

Evidence: [architecture.md](../spec/architecture.md) §4.6, §4.9, §4.10, §12 (NeutralVoice risk), §13.4 (T-14).
[RECONCILIATION.md](../research/RECONCILIATION.md) §4.9 (MIDI synth row); §6 D-04.
