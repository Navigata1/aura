# Post-production is measurement first: BS.1770-4 loudness, AURA's own true-peak meter, a dry export, and no generative enhancement by default

Status: accepted (2026-10-09). From D-19.

Matchering is GPL-3.0. pyloudnorm implements BS.1770-4, not -5, and has no true-peak meter. Apollo is CC BY-SA 4.0 and
restores 44.1 kHz MP3 losses; it is not a 48 kHz upsampler. AudioSR synthesizes the top octave. Upsampling changes the
container, not the information.

**Decision.**

- **v1 measurement**: integrated loudness with pyloudnorm, labelled "BS.1770-4 (pyloudnorm)", plus AURA's own true-peak
  meter oversampling at least 4×. A ticket compares BS.1770-4 with -5 for stereo programme (X-47); until it closes,
  every report names the revision actually used. A dry export is always kept. Loudness targets depend on the
  destination and are never applied silently.
- **Export**: a bit-exact copy at the native rate; a 48 kHz, 24-bit deliverable with TPDF dither seeded from the export
  id (so it is deterministic), only when the native rate differs; every file decoded and hashed again before the bundle
  is offered.
- **v2**: optional mastering through Matchering in a separate process, only after a blind audition shows it improves
  keepers without hiding defects.
- **No generative super-resolution by default.** DeepFilterNet runs on speech only, never on music.
- A **codec round-trip ceiling study** (ACE VAE, HeartCodec, SA3 SAME) runs before any enhancement or training claim.

**Why.** Every proposed mastering and enhancement tool in the sources was either copyleft, mislabelled or generative
(C27), and automatic scorers cannot validate super-resolution (X-15).

## Consequences

Every loudness number carries its standard and meter version into the manifest. "Remaster" is not a v1 feature.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). DSP finishing means O-08's non-generative mixing, mastering and format, on one mix or a set of Jon's own stems; a target is never applied silently and the dry export is always kept.

**Reverse if:** a blind audition shows that a mastering stage improves keepers without hiding defects.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C27; §4.6; §5 (GPT 5); §6 D-19.
[evidence-register.json](../research/evidence-register.json) V-qe-4, V-qe-5, X-15, X-47.
[feature-inventory.md](../research/feature-inventory.md) I3, I6, I7, J13. [architecture.md](../spec/architecture.md)
§4.9 (`measure`, `export`).
