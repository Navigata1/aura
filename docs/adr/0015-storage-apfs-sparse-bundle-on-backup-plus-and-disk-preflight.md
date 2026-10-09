# AURA's store lives in an APFS sparse bundle on the Backup Plus drive, and a disk preflight guards every volume

Status: accepted (2026-10-09). Owner decision O-03. From D-15, amended: O-03 answers D-15's "nothing installs until Jon
picks a volume", and an APFS sparse bundle avoids exFAT's limits without reformatting. The bundle's logical size
(900g) is Jon's to change. The band size is UNVERIFIED until measured in P0. Retention and backup: ADR-0034.

Measured on 2026-10-09 (MEASURED-LOCAL): the internal Data volume read between 2.0 and 57 GiB free across the day (timestamped readings in `docs/DEVELOPING.md`,
the one source for this range; every rule assumes the 2 GiB floor) and
fluctuates. `/Volumes/Backup Plus` is a Seagate BUP Slim 2.5″ spinning HDD, exFAT over USB, with about 1.1–1.2 TiB free,
about 125 MB/s cold sequential read and about 70 MB/s synced sequential write (one run each). exFAT has no symlinks or
POSIX permissions, so the Hugging Face cache would run in its degraded no-symlink mode and uv environments would lose
their exec bits.

**Decision.**

- **The volume.** `studioctl setup` creates `"/Volumes/Backup Plus/STUDIO.sparsebundle"` with `hdiutil create -type
  SPARSEBUNDLE -fs APFS -volname STUDIO -size 900g` and attaches it at `/Volumes/STUDIO` with `-owners on -nobrowse`.
  It prints any command needing admin rights for Jon to run and never runs `sudo` itself. Setup probes ownership,
  symlinks, chmod, hardlinks and `clonefile`, and records the result.
- **What lives there**: models (`HF_HOME` and the xet cache, other downloads with pin files, license acceptances,
  manifests), engine environments and the uv cache, caches (pnpm, pip, torch, MLX, XDG, Playwright), worktrees,
  scratch, logs, evidence captures and, by default, the project store. The internal disk holds only the OS, the
  browser, the canonical docs checkout, `~/.config/studio/` and keychain entries.
- **Disk preflight on every volume**, before every download, install, environment build, job and export, from an
  estimate declared per volume:
  - **STUDIO**: effective free = min(APFS free inside the bundle, exFAT free on the host) minus band overhead. Refused
    if effective free minus the estimate is under **10 GiB** (configurable). The refusal names the volume, the free
    space, the amount needed and the margin.
  - **Internal**: no planned writes are accepted, and heavy jobs are blocked while free space is under **2 GiB**,
    because swap lives there.
  - **Remote hosts**: checked from the free space a worker reports in `describe`. A pod's disk is sized at quote time.
  - A running job fails honestly with `failed(disk_low)` if free space drops below half the margin.
- **Selective downloads** (`allow_patterns`) with a size dry run: ACE turbo plus encoder and VAE ≈ 6.34 GB; the 1.7B LM
  ≈ 3.76 GB; XL only as diffusers bf16 (≈ 11.1–11.5 GB) once the loader is verified; YuE2's 7.30 + 0.53 GB only on CUDA
  hosts and pods. Outputs are budgeted at 92,160,000 bytes (about 87.9 MiB) per 4-minute stereo float32 stem. Install
  checks downloaded bytes against the manifest and every LFS sha256.
- **Hygiene**: Spotlight off (`.metadata_never_index`, plus `mdutil -i off` printed as an owner action), a sticky Time
  Machine exclusion, an unclean-detach marker that triggers `diskutil verifyVolume`, offline `compact`, a mount watch
  that refuses new jobs if the volume disappears, and an idle-sleep assertion while writing.

**Why.** O-03. exFAT breaks symlinks and permissions. The internal disk cannot safely hold even one ACE bundle.

## Consequences

Cold loads are slow on the HDD (INFERRED: about 50 s for ACE turbo and 90 s for XL bf16), so workers keep one heavy
model resident and report cold and warm times separately. Deleting inside the bundle frees host space only after
`compact`. Backup Plus is a single physical HDD, so the real durability guarantee is the backup mirror (ADR-0034).

**Reverse if:** Jon frees about 60 GB internally or buys an APFS SSD. The roots are configurable, and environments and
the uv cache always move together.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §2 C2, C47; §6 D-15.
[measurements/2026-10-09-backup-plus-throughput.md](../research/measurements/2026-10-09-backup-plus-throughput.md).
[evidence-register.json](../research/evidence-register.json) V-cost-1, X-02, X-05, X-20.
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-03. [architecture.md](../spec/architecture.md)
§8.1–§8.5, §11 (P0-2, P0-3, P0-4).
