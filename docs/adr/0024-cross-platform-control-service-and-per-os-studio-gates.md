# The control service and UI are portable across macOS, Windows and Linux; Studio playback is gated per OS; the Mac comes first

Status: accepted (2026-10-09). Owner decision O-11 (Jon selects platform and compute whenever necessary). From D-24,
option (b). Q13 is closed.

Jon wants AURA on Linux, Windows and macOS (X-46). Neither the Linux nor the Windows machine is reachable today. All
browser latency evidence comes from one 2021 MacBook Pro (X-49).

**Decision.**

- **The control service and localhost UI run on macOS, Windows and Linux**: Python and FastAPI, stdlib SQLite, uv, and
  React served to a Chromium-based browser. **The control service has no macOS-only dependency.** macOS-only code
  lives only in the sparse-bundle adapter of `StoreVolume` and in `scripts/store/`. MLX and Metal live only in Mac
  worker environments. On Windows and Linux the store is a plain directory with the same layout (ADR-0034).
- **Workers are per OS by capability**: the Mac for MLX profiles; Linux, or WSL2 on Windows, for CUDA profiles.
- **Studio playback is gated per OS** through the `studio.playback` capability (ADR-0013). It is computed
  `smoke-passed` only for an operating system whose own gate has passed. AURA is never called three-platform ready
  from one OS, and an OS stays labelled unverified until StudioHarness and the playback gate pass on a real host, not
  only in CI.
- **CI**: the control service's tests run on Linux for every PR and on macOS and Windows for integration and nightly
  builds, from the first tickets. A self-hosted Mac runner produces hardware evidence and never runs paid jobs.
  **Note (2026-11-07):** since PR #12 (2026-11-06) every pull request runs on Linux, macOS and Windows, and the
  `integration` ruleset requires all three (`docs/research/OWNER-DECISIONS-2026-11-07.md`). An OS still stays
  unverified until a real host passes.
- **Delivery order**: the Mac first, because it is the only reachable machine. Windows and Linux hosting is verified as
  soon as either machine is reachable (P6), followed by the DAW round trip (MG-E15) and the recovery test (MG-E16) on
  each OS.

**Why.** O-11 and X-46. The D-12 stack is already portable, so option (b) costs little now and avoids a later
rewrite. Full three-OS parity in v1, option (c), cannot be tested while the other machines are unreachable.

## Considered Options

- **(a) A Mac-only studio, with Linux and Windows as workers forever.** Rejected by O-11.
- **(b) A portable control service and UI, with Studio playback gated per OS.** Chosen.
- **(c) Full three-OS parity in v1.** Rejected: it cannot be verified today.

## Consequences

Every path, decoder and process call in the control service must work on all three operating systems; `afconvert`, for
example, is excluded from it. In v1 projects move between hosts only by backup and restore.

**Reverse if:** Jon says the studio host is always the Mac. CI on Windows and Linux would then cover only the workers.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C39; §4.9 (decoder row); §6 D-24.
[evidence-register.json](../research/evidence-register.json) X-46, X-49.
[feature-inventory.md](../research/feature-inventory.md) J19, J20.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-11. [architecture.md](../spec/architecture.md) §2
(`.github/workflows/`), §4.2 (`StoreVolume`), §6.1, §8.7, §11 (P0-6, P6).
