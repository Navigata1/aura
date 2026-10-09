# Engines sit behind engine profiles in a capability registry

Status: accepted (2026-10-09). From D-01, amended by the v1 architecture: profile status is computed from evidence
(ADR-0027), and the registry also enforces operator lanes and allowed uses (ADR-0011, ADR-0029).

AURA must run several engines whose abilities differ by checkpoint, by backend and by license. The owner's rule is that
nothing is presented as working until a check that could fail has passed.

**Decision.** AURA never addresses an engine or a model, only an **engine profile**: one checkpoint on one backend
with a declared task set. A profile declares:

- **tasks**: `text_to_song`, `cover`, `score_to_song`, `repaint`, `extend`, `extract`, `lego`, `complete`,
  `instrumental`, `reference_timbre`;
- **limits**: maximum duration, sample rate, channels and lyric languages (YuE2 takes English and Chinese only);
- **backend and host OS**;
- **components, pins and gates** (smoke, benchmark), and the operator lanes its components allow;
- **`claims_published`**, each labelled VENDOR, COMMUNITY or COMPETITOR-RUN, and **`results_local`**, each pointing at
  an evidence record. A schema rule rejects MEASURED-LOCAL inside `claims_published`;
- a `test_only` flag for fakes.

Declarations live in `contracts/registry/engine-profiles.v1.json` with **no status field**. Status (`declared →
installed → smoke-passed → benchmarked`, or `disabled`) is computed (ADR-0027). `Registry.admit` refuses a job before
anything loads, in this order:

1. the status on the target host class is below smoke-passed;
2. the task, duration, language or channels fall outside the declaration;
3. a component does not allow the project's lane;
4. an audio-ancestry input does not allow the lane;
5. an input's allowed uses exclude the task;
6. intent is mapped to actual parameters (ADR-0018);
7. prompt conflicts are flagged.

Workers repeat the refusal before loading (ADR-0026). The first profiles are `ace-2b-turbo-mlx` (draft) and
`ace-2b-sft-mlx` (render), then `ace-xl-sft-mlx` after its own smoke run, CUDA twins for tiers 1–3, and
`yue2-3b-score`. Non-engine capabilities (`studio.playback` per OS, `capture.mic`) are gated the same way in
`capabilities.v1.json`.

**Why.** Task support differs by checkpoint. ACE base and XL-base do every task; SFT and turbo do only text-to-music,
cover and repaint; turbo silently forces guidance to 1.0 (C4). Mac behaviour differs by checkpoint: XL-SFT output was
garbled until a fix landed on main (C3). Licenses differ by component (§4). A single "engine URL" would hide all three.

## Considered Options

- **One engine wired in** (Fable). Rejected: it cannot meet the owner's "not ACE-only" requirement.
- **One engine URL or abstraction** (Fable, Kimi). Rejected: task and license differences stay hidden inside the
  engine.
- **Profiles plus a capability registry** (GPT). Chosen.

## Consequences

The product view lists only profiles at smoke-passed or better on the session's host class. Unproven routes show as
"needs smoke". A published figure never appears in a measured column. Adding an engine means adding a worker adapter
and declarations, never a UI branch.

**Reverse if:** a single profile passes every task gate at accepted quality. None does today.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C3, C4; §4.1; §5 (GPT 2); §6 D-01.
[evidence-register.json](../research/evidence-register.json) V-ace-3, V-ace-4, X-10, X-11.
[architecture.md](../spec/architecture.md) §4.4, §4.10, §5 (`engine-profile/1`, `capability/1`). Pattern: JOVRA
ADR-0004.
