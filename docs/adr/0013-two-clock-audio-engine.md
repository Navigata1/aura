# Two clocks: bounded preview playback in the browser, and a separate deterministic offline render for export

Status: accepted (2026-10-09). From D-13, amended by the v1 architecture: the StudioEngine uses SharedArrayBuffer rings,
and a CPAL native engine is the only planned swap. Scope: v1-studio (phase P5).

Browser audio round-trip latency was measured on one 2021 MacBook Pro at 52.33 ms in Chrome, 100.02 ms in Safari and
38.89 ms in Firefox (WAC 2025, peer-reviewed). Windows and Linux are unmeasured (X-49). wavesurfer-multitrack is
dormant, breaks on wavesurfer 8, and keeps tracks in sync only to within 0.3 s.

**Decision.**

- **Preview playback** is the **StudioEngine**: an AudioWorklet graph with a SharedArrayBuffer ring per track, fed by
  a decode Web Worker that reads byte ranges of blobs. No inference, disk or network work runs on the render thread.
- **Export** is a separate offline render (the analysis worker's `export` task). Export never uses the StudioEngine.
- **Timeline**: integer sample positions in project frames, artifacts referenced at their native rate, MIDI in ticks,
  and a versioned tempo map (ADR-0033). Quantization is reversible.
- **Base**: evaluate waveform-playlist v16 (MIT) against a timeline of AURA's own. **Never wavesurfer-multitrack.**
  wavesurfer.js 8 core may draw single waveforms.
- **Time and pitch**: Signalsmith Stretch (MIT) first, SoundTouch (LGPL) as the fallback, only inside a separate worker
  process and never in the web bundle. Speed changes appear only after objective criteria and Jon's blind verdict pass. Rubber Band (GPL) is not
  bundled.
- **Recording into tracks** is deferred (v2). When it ships it is latency-compensated recording, not live monitoring.
- **Gate per operating system** (the `studio.playback` capability, ADR-0024): 8 tracks for 30 minutes with zero
  underruns according to Chrome's `playbackStats`, and UI p95 under 100 ms while a generation runs. 16 tracks is a
  stretch gate.

**Why.** GPT's two-clock model keeps blocking work out of the audio path (§5 GPT 11). Browser latency must be measured,
not assumed (C39). The dormant multitrack library cannot meet a sync requirement (C38).

## Consequences

Offline and real-time output must be shown equivalent before effects ship (v2). If the gate fails, only the
StudioEngine is replaced, behind the same timeline contract.

**Reverse if:** the gates fail in Chromium. A native engine on CPAL (Apache) then replaces the StudioEngine, with VST3
(MIT) for plugins later. JUCE only under its EULA.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C38, C39, C53; §4.6; §4.7; §5 (GPT 11); §6 D-13.
[evidence-register.json](../research/evidence-register.json) V-ui-1, V-ui-2, V-ui-3, X-35, X-49.
[feature-inventory.md](../research/feature-inventory.md) F1–F11, J20. [architecture.md](../spec/architecture.md) §4.11,
§11 (TB9, P5).
