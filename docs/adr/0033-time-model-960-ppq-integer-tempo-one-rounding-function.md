# One time model: 960 PPQ, integer microseconds per quarter note, and one half-up rounding function, twinned in Python and TypeScript

Status: accepted (2026-10-09) with the v1 architecture.

The piano roll in the browser, Score in Python, MIDI import and export, the YuE2 ABC emitter and the timeline must agree
on every conversion between ticks and samples. Hashed records must not depend on how floats are formatted.

**Decision.** The TimeModel uses 960 PPQ, tempo as integer microseconds per quarter note (the Standard MIDI File unit),
meter segments, and **one** half-up rounding function for converting between ticks and frames. A TypeScript twin in
`contracts-ts` and the Python model both pass the same `contracts/fixtures/tempo` vectors, which the stdlib reference
implementation regenerates. Quantize is a reversible layer over played timing.

**Why.** Two runtimes that round differently would drift apart, one tick at a time, and an integer tempo is exact where
a decimal BPM is not.

## Considered Options

- **480 PPQ with a decimal BPM.** Rejected: not exact in Standard MIDI File terms.

## Consequences

Dragging a note in the piano roll needs no round trip to the server. MIDI round trips keep notes and ticks equal (the
TB4 golden fixture).

**Reverse if:** nothing foreseen reverses this.

Evidence: [architecture.md](../spec/architecture.md) §4.6, §5 (`melody-spec/1`), §6.3, §13.2, §13.3.
[RECONCILIATION.md](../research/RECONCILIATION.md) §5 (GPT 11); §6 D-13.
