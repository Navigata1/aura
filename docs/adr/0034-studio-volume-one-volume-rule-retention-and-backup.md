# One-volume rule, retention classes, and a hash-verified mirror of the irreplaceable closure

Status: accepted (2026-10-09) with the v1 architecture. It extends ADR-0015 (O-03). The backup destination device is
owner-pending.

Hardlinks and clones work only within one volume. The studio volume is a single spinning HDD with no second copy, and
neither APFS nor the sparse bundle gives a durability guarantee.

**Decision.**

- **One-volume rule.** Anything that hardlinks or clones lives on the same volume as its counterpart: the uv cache and
  the environments, the pnpm store and `node_modules`, the content-addressed store and the exports. `studioctl env`
  writes one env file that routes `HF_HOME`, `HF_XET_CACHE`, the `UV_*` variables, `PIP_CACHE_DIR`, `TORCH_HOME`,
  `XDG_CACHE_HOME`, `TMPDIR`, `PLAYWRIGHT_BROWSERS_PATH`, the MLX cache limit and the pnpm `store-dir` to the volume.
  The roots are configurable, but environments and the uv cache always move together.
- **Retention classes**, on every artifact and record:
  - `irreplaceable`: human recordings, imported MIDI and mixes, MelodySpec and SongSpec revisions with their
    correction logs, verdicts, keepers and their audio closures, references with permission records, risk acceptances,
    evidence records, export manifests and the latest database snapshot;
  - `derived`: other candidates and analysis outputs;
  - `reproducible`: weights, environments, caches, previews, scratch and export renders.
- **Backup.** `studioctl store backup <dest>` copies the irreplaceable closure in the same content-addressed layout to a
  second device, then re-hashes every file at the destination. `restore` rebuilds a fresh root, and `fsck` re-hashes
  it. `--include-derived` adds derived data. A weekly reminder prompts an `fsck` and a backup.
- **Other operating systems.** On Windows and Linux the store is a plain directory with the same layout: no symlinks or
  extended attributes, and short lowercase-hex paths. It works on any filesystem with atomic rename and fsync.

**Why.** Backup Plus is one physical HDD, so the second copy is the only real durability guarantee. Without the
one-volume rule, every hardlink and clone silently degrades into a full copy.

## Considered Options

- **`rsync` of `projects/`.** Rejected: it does not verify what it copied.
- **Small, hot environments on the internal SSD**, as the measurement note suggested. Rejected for now: internal free
  space reads as low as 2 GiB (timestamped in `docs/DEVELOPING.md`), and O-03 puts environments on the volume (T-10).

## Consequences

The P1 exit includes a backup, restore and fsck drill, and an fsck that detects a single flipped byte.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). The pnpm store is configured as `storeDir` and `cacheDir` in `pnpm-workspace.yaml` from `${STUDIO_ROOT}`, because pnpm 11 ignores `store-dir` in `.npmrc` and `npm_config_store_dir` (MEASURED-LOCAL). The env file also routes `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, `npm_config_cache` and `COREPACK_HOME`, and exports nothing when the volume is not mounted. Ticket worktrees come from a bare clone on the volume. Irreplaceable records include risk and license acceptances; export renders are reproducible while export manifests are irreplaceable.

**Reverse if:** a second physical store, an SSD or another host, becomes the primary. The classes and the mirror stay.

Evidence: [architecture.md](../spec/architecture.md) §8.2–§8.4, §8.6, §8.7, §13.4 (T-10, T-11), §11 (P1-9).
[RECONCILIATION.md](../research/RECONCILIATION.md) §6 D-15.
[measurements/2026-10-09-backup-plus-throughput.md](../research/measurements/2026-10-09-backup-plus-throughput.md).
[OWNER-DECISIONS](../research/OWNER-DECISIONS-2026-10-09.md) O-03.
