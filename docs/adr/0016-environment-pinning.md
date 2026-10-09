# Every engine profile gets its own pinned environment, and "latest" is never a version

Status: accepted (2026-10-09). From D-16, amended by the v1 architecture: engine workers are standalone uv projects
outside the workspace lock, and YuE2 ships as an OCI image.

Torch pins conflict across engines: ACE 2.7.1 or 2.10.0, YuE2 2.10.0, HeartMuLa below 2.11, SGLang-Omni 2.13.0, and
Shao NGC's 2.7.0a0. cu128 wheels ended at torch 2.11, so Blackwell needs cu128 (torch 2.11 or earlier) or cu130 and
later with R580+ drivers. ACE XL-SFT and base output was garbled on Apple Silicon until a fix landed on main after
v0.1.8.

**Decision.**

- One `uv` project per engine worker, each with its own lock and outside the workspace lock. The YuE2 worker is an OCI
  image (CUDA 12.8, torch 2.10.0, a pinned YuE2 commit, **no weights**) whose digest is pinned in the registry.
  Containers are used only where required (SGLang-Omni; Shao, which is research-only).
- Pins are recorded in the registry and folded into the profile revision (ADR-0027):
  - **ACE**: main at or after `ca1e85fe9430179831e6bc6be790c332190a3866`, or v0.1.8 (`dce62140…`) with
    `dcw_enabled=False, shift=1.0` for non-turbo models.
  - **YuE2**: torch 2.10.0 on Linux or WSL2, cu128 (driver 570.26 or later on Linux, 570.65 or later on Windows).
    Raising torch to 2.13 for the MPS fix (#176) would push Blackwell cards onto cu130 and R580+ drivers.
  - **MiniMax**: diffusers 0.40.0 or later, not the old PR commit.
  - **Basic Pitch**: its own Python 3.10 environment, because 0.4.0 does not install under 3.12 on macOS (#203).
    librosa 1.0 needs Python 3.12 or later.
  - **CUDA wheel by GPU generation**: Blackwell on cu128 (torch 2.11 or earlier) or cu130 and later with R580+;
    Turing to Ada on any; Pascal on cu126 only.
- The worker SDK is stdlib-only and runs on Python 3.10 and later, so it installs into every pinned environment without
  dependency fights (ADR-0026).
- **Upgrades are admitted only after the new revision passes its own smoke gate** on that host class (ADR-0027); until
  then the product keeps the last smoke-passed revision. A new revision computes to `declared` with no records.

**Why.** Conflicting pins make a shared environment impossible (A8, C46). Pin regressions are real and silent (C3).

## Consequences

A pin bump is a new profile revision and starts again at `installed`, so an upgrade never inherits a stale
`smoke-passed`. Environments are keyed by lock hash on the studio volume and shared by worktrees.

**Reverse if:** nothing foreseen reverses this.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A8; §2 C3, C46, GAP-03; §4.8; §6 D-16.
[evidence-register.json](../research/evidence-register.json) V-ace-3, V-cost-4.
[architecture.md](../spec/architecture.md) §2 (`workers/`), §4.8, §8.2.
