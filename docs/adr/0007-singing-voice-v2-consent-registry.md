# No voice cloning in v1; own-voice conversion waits for a v2 consent-gated voice registry

Status: accepted (2026-10-09). Owner decision O-07 (own voice is v2). From D-07; its reverse condition ("Jon wants his
own voice on this first song") is closed by O-07.

ACE's maintainer says there is no direct voice cloning: `reference_audio` sets a global timbre or style (#776). RVC's
code is MIT, but the lj1995 base weights carry a "research use only" rider and rmvpe.pt is unlicensed and trained partly
on CC BY-NC-SA data (CONTESTED). Official RVC dropped macOS; the Applio fork runs on MPS. Seed-VC is archived and GPL.
Suno's own voice flow is a consent gate: a sung sample, then a spoken random phrase compared with the singing for the
same speaker, then a rights checkbox, for adults only.

**Decision.**

- **v1 has no voice cloning and no voice conversion.** v1 sings with the engines' own vocals. ACE `reference_audio`
  is offered (v1-studio) only as a "global timbre/style reference", labelled that way.
- **v2 adds a private voice registry with a consent gate modelled on Suno's.** The owner, or a singer he has
  authorized, records a sung sample and then speaks a displayed random phrase. Two checks follow: a speaker-embedding
  match between phrase and singing (pyannote WeSpeaker, CC-BY-4.0, or SpeechBrain ECAPA, Apache), and an ASR check of
  the phrase. Then a rights confirmation, `consent_at` and the permitted uses are recorded. The clean recording is the
  source of truth; embeddings are a cache.
- **v2 conversion** uses Applio or RVC as an optional, auditioned operation in a separate process. The contested
  weights license is recorded on every artifact, and the export manifest sets its converted-vocal flag. Jon decides
  per release whether a converted-vocal song is released.
- **Seed-VC is rejected.** DiffSinger stays research; commercial use would need a self-trained vocoder.

**Why.** O-07. ACE cannot clone a voice (C4). The conversion weights are contested (C24). A checkbox alone is weaker
than Suno's gate (C25).

## Consequences

The contested RVC and rmvpe weights stay out of v1 entirely. In v1 every export manifest carries
`converted_vocal: false`. The registry is not designed in v1 beyond keeping `conversion` in the artifact origin enum.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). O-07's global style reference reaches v1 through `ace-2b-base-mlx`, the only profile that declares `reference_timbre`; it has its own install-and-smoke ticket, and a style reference must carry a permission that grants conditioning.

**Reverse if:** the base-weights license resolves cleanly, or Jon wants his own voice earlier. Conversion would then
enter v1 for the individual lane only, still per-release.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C4, C24, C25; §4.4; §6 D-07.
[evidence-register.json](../research/evidence-register.json) V-voice-1, V-voice-2, V-voice-3, V-voice-4, X-32.
[feature-inventory.md](../research/feature-inventory.md) G1–G7.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-07.
