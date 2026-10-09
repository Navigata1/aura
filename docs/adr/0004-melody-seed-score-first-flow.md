# The north-star flow is score-first: a hum or MIDI becomes a corrected MelodySpec before any route renders it

Status: accepted (2026-10-09). Owner decision O-04 (hum or sing into a mic, and MIDI). From D-04, amended by the v1
architecture: AudioWorklet PCM capture, a weights-free v0 transcriber, NeutralVoice for R2-synth (ADR-0032), SongForm
assembly and a MIDI-first walking skeleton. English lyrics are the owner-pending default (Q6).

Jon starts from a melody in his head. No source designed the whole path. No transcriber is both license-clean and
benchmarked on humming (GAP-01). ACE cover is not note-for-note (maintainer, #972) and scored Hit@1 2.4% in a
competitor's test (COMPETITOR-RUN). YuE2's score route is self-reported (VENDOR).

**Decision.** The first end-to-end flow:

1. **Capture.** A hum or sung line recorded in the browser as raw float32 PCM through an AudioWorklet, with echo
   cancellation, noise suppression and auto gain off (verified with `getSettings()`), hashed in the browser and
   uploaded as WAV. Or a MIDI file, or live Web MIDI. Captures are irreplaceable human recordings. This keeps the
   m4a/AAC decoder, whose license is UNVERIFIED, off the core path; a phone voice memo enters as WAV until that ticket
   closes.
2. **Transcribe.** v0 is pYIN F0 (librosa, ISC, no weights) plus AURA's own HMM note segmentation. It is LLC-clean,
   gives every note a confidence, and is labelled "unverified on real hums". A hum benchmark on Jon's own hums
   decides the default: Basic Pitch (in its own Python 3.10 environment), SwiftF0 `segment_notes` and pYIN+HMM, scored
   with mir_eval COn/COnP/COnPOff plus correction effort. "Manual entry wins" is an allowed outcome.
3. **Correct** in a piano roll. The result is the **MelodySpec** (ADR-0033): 960 PPQ, an integer
   microseconds-per-quarter tempo map, meter, key, phrases, and notes with confidence and origin. Every set of edits is
   a new immutable revision and is logged with its time; the log is the correction-effort metric.
4. **SongSpec and SongForm.** Approved lyrics with their BCP-47 language (kept apart from any ASR transcript), style
   and exclusions, vocal mode, references with permissions, duration, candidate count (2), and a SongForm of vocal and
   instrumental sections built from phrases. `Score.assemble` lays the MelodySpec out along the SongForm as the
   full-length melody (ADR-0032).
5. **Routes.**
   - **R1, YuE2 score route** (CUDA, individual lane only). The assembled melody becomes YuE2's strict two-voice ABC:
     fixed header, one integer tempo, full bars, pickups padded with rests, tuplets re-quantized. It is sent as `abc=`
     with `cot='melody'` (chord symbols stripped) or `cot='full'`. Lyrics bind by section tags and order, with the
     syllable plan as a sidecar. English or Chinese lyrics only; about 6 minutes maximum. Anything else returns a typed
     `Ineligible`. It is conditioning, not exact rendering: 84% exact pitch on edited scores (VENDOR).
   - **R2-raw, ACE cover of the hum**, with the hum slices laid out along the SongForm.
   - **R2-synth, ACE cover of the NeutralVoice guide**, sweeping `audio_cover_strength` from 0.8 to 1.0 and
     `cover_noise_strength`.
   - **R3** (a DiffSinger guide vocal, then ACE `complete`) stays research.
6. **Measure** every candidate's melody adherence (ADR-0005).
7. **Fan out.** A preregistered route comparison runs R1, R2-raw and R2-synth at an equal candidate count per hum
   fixture, against the adherence thresholds committed in a gate record before any real adherence evidence. In the
   product each request shows **2 candidates**, by default one from each of the first two eligible routes in the
   project's lane in the plan-rules order (R1 only where it runs without a burst or when Jon opts in for that request,
   then R2-synth, R2-raw, text; no quality claim), adjusted only by route-standing records from concluded preregistered
   sets, labelled "unbenchmarked routes" until a benchmark record exists. With only one eligible route, both
   candidates come from it with different seeds. In the LLC lane only R2 exists today. Route, profile and seed stay
   hidden until the reveal. Jon's ear decides.

**Why.** A human-corrected symbolic stage makes the tune explicit, editable, owned and testable, so it survives engine
drift. Suno itself moved toward MIDI clips as prompts (Studio 2.0).

## Considered Options

- **ACE cover at high strength on the raw hum** (Fable). Kept as R2-raw, but not the only route.
- **Hum to MIDI to a sampler** (Kimi). Rejected: it gives an instrument part, not a song.
- **Suno Studio 2.0's MIDI clips as prompts.** Rejected: hosted, and outside the Suno boundary (ADR-0021).

## Consequences

The walking skeleton is MIDI-first, so it never depends on transcriber quality. SheetSage2, YuE2's own transcriber, is
non-commercial and is never loaded. Basic Pitch (Python 3.10) and librosa 1.0 (Python 3.12 or later) live in separate
environments. When adherence fails, the keeper's badge says "melody not kept".

**Reverse if:** the preregistered route comparison (its record alone; the first real pair's numbers are only an input)
shows R2 within the committed adherence thresholds. The Mac-only R2 path then becomes the default
and R1 becomes optional. If NeutralVoice proves a poor cover input, a license-verified MIDI synth replaces it behind the
same `guide` task.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A11, A12; §2 C8, C52, GAP-01, GAP-02; §4.3; §4.9;
§6 D-04. [evidence-register.json](../research/evidence-register.json) V-ace-8, V-sep-4, V-gap-1, V-gap-2, X-13.
[feature-inventory.md](../research/feature-inventory.md) A1–A7, A11.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-04. [architecture.md](../spec/architecture.md) §3.1,
§4.6, §4.9, §11 (TB1a–TB7).
