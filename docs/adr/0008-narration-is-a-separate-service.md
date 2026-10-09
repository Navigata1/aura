# Narration is a separate service with its own spec; music v1 only keeps the shared contracts open for it

Status: accepted (2026-10-09) for the boundary: owner note on Q9 ("out of scope for the music v1 spec … gets its own
spec later") and O-06 (Sabbath Echo is `llc`). The narration design itself (engines, the Scripture rule, voices,
languages, priority) is **proposed** and owner-pending (Q9). From D-08.

Sabbath Echo narration is the other workload Jon has in mind, and its targets differ from music: long-form text,
consented narrator voices, and cost per approved hour. No independent long-form evaluation of the open TTS engines
exists, and an independent paper shows Qwen3-TTS and VoxCPM2 degrading badly past about 1,500 words. ElevenLabs'
Prohibited Use Policy §9(j)(k)(l) bars using its renders as ML input or training data.

**Decision.**

- The **narration service** is detachable and gets its own spec and tickets later. It is out of scope for the music
  v1 spec.
- It shares only the artifact, provenance, job and storage contracts, and music v1 must not preclude it:
  `Artifact.origin` includes `tts_render`, `Project.kind` reserves `narration`, and the store, Conductor, Placement,
  Registry and worker SDK stay domain-agnostic. Phase P6 includes a dry run: a `tts_render` artifact flows through the
  store, jobs and export manifest with no schema change.
- Sabbath Echo is an **llc** project (O-06), so YuE2 and every non-commercial component are excluded from its
  narration and its music beds. This settles the presumption recorded as X-50.
- **Proposed for the narration spec** (owner-pending, Q9):
  - a pilot on approved, permitted text and consented voices with VoxCPM2 (Apache, official MPS), Qwen3-TTS (Apache),
    Chatterbox (MIT, watermarked), CosyVoice3 (Apache) and Kokoro as a baseline;
  - ranking by cost per approved finished hour against ElevenLabs list prices, with Eleven v4 as the quality bar;
  - chunking at semantic boundaries with ASR verify-and-regenerate per chunk, because long-form is a core requirement;
  - voice continuity seeded only from original human recordings;
  - excluded: OmniVoice, F5-TTS, Fish S2-Pro, VibeVoice;
  - the Scripture boundary waits for Jon.

**Why.** Jon pinned narration separately. Its evaluation targets would distort the music spec, while a shared store
and job system avoid building everything twice.

## Consequences

Music v1 has no narration UI, engine or worker. The ElevenLabs baseline (about $4.0–4.6 per finished hour at list
price, INFERRED) and the roughly $25k historical spend (OWNER-REPORTED, UNVERIFIABLE) inform the narration spec, not
this one.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The shared job contract reserves a `tts` worker task and job kind, so the later narration service fits without a schema change; v1 builds no narration UI, engine or worker.

**Reverse if:** Jon makes narration the priority. It then becomes the first spec, with music second.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C48, C54, C55, GAP-08; §4.4; §6 D-08.
[evidence-register.json](../research/evidence-register.json) V-voice-5, V-voice-7, V-gap-8, X-17, X-18, X-19, X-48,
X-50. [feature-inventory.md](../research/feature-inventory.md) H1–H8.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-06 and the Q9 note.
[architecture.md](../spec/architecture.md) §1, §5, §11 (P6-4).
