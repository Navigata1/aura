# Generation controls are capability-aware: record the creative intent and the actual parameters, never a universal slider

Status: accepted (2026-10-09). From D-18.

ACE turbo silently forces `guidance_scale` to 1.0 and needs `shift=3.0` set by hand. In a practitioner video, an
"instrumental" Suno generation picked up vocals because the style text still named them (GSV-14). Suno v6 exposes
Variety, Weirdness, Style Influence and Max Mode as separate controls (GSV-06).

**Decision.**

- Controls appear only where the selected profile implements them. Turbo hides CFG. Weirdness or Style Influence appear
  only where a profile maps them.
- Every generation records **intent** (what Jon set) and **actual** (what the engine received). Every SongSpec field
  records what was requested, what is supported and what was observed. `Registry.admit` maps intent to actual and
  returns both.
- Conflicts are resolved before submission. `Score.validate` flags, for example, an instrumental flag alongside vocal
  style words, or a field the chosen profile does not support.

**Why.** No slider should do nothing silently, and a result must be reproducible from what the engine actually got
(C4, GSV-06, GSV-14).

## Consequences

Comparing candidates across profiles uses intent; reproducing one uses actual.

**Reverse if:** nothing foreseen reverses this.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C4; §6 D-18.
[feature-inventory.md](../research/feature-inventory.md) B3, B5, B8, C5. [architecture.md](../spec/architecture.md)
§4.4 (`admit` steps 6–7), §4.6 (`validate`), §5 (`song-spec/1`).
