# Hosted music services are optional, pinned references, outside v1-core

Status: accepted (2026-10-09). From D-22, which was titled "hosted provider lane"; renamed because "lane" means operator
lane.

Several hosted music APIs are live: Mureka (model pinnable to `mureka-9.5`, stems with MIDI, region edit), Gemini
Lyria 3.5 ($0.08 per song, SynthID-watermarked), Stability SA3 Large, and paid ElevenLabs Music. MiniMax's API is
closed to new users. AURA's premise is open weights on hardware Jon controls.

**Decision.** No hosted music service is in v1-core. A hosted service may be added later only as an optional, explicit,
model-pinned profile (never an `auto` model setting), with its billing and terms recorded per job, outside the
listening harness unless a preregistration names it, and never as a silent fallback.

**Why.** Hosted services do not serve the ownership premise, and an `auto` model setting drifts (C37, X-31).

## Consequences

v1 holds no music-service API keys, so none can leak into the client.

**Reverse if:** Jon wants a premium hosted fallback for the LLC lane.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C37; §4.2; §6 D-22.
[evidence-register.json](../research/evidence-register.json) V-suno-8, X-27, X-31.
[feature-inventory.md](../research/feature-inventory.md) L11.
