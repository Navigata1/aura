# Developing AURA

T01 now provides the package skeleton, CLI discovery, external-volume helpers and foundation checks. The web page is
explicitly a foundation placeholder; generation, the Studio API and playback are not implemented. A command marked
**(planned)** still belongs to a later ticket. Facts marked MEASURED-LOCAL were measured on the build Mac on 2026-10-09.
Everything else follows `docs/spec/architecture.md` and the ADRs it cites.

## Foundation commands available now

Work only in the external ticket worktree. The canonical checkout remains docs-only.

```sh
source ~/.config/studio/env.sh
export PATH="/Volumes/STUDIO/envs/node/22.22.3/bin:$PATH"
cd /Volumes/STUDIO/worktrees/01-foundation
source scripts/dev/studio-env.sh
python3 scripts/dev/preflight.py --estimate-gib 3
uv sync --frozen
pnpm install --frozen-lockfile
uv run --frozen studioctl --version
uv run --frozen studioctl doctor
uv run --frozen python scripts/ci/run.py --files-only
```

Use `--files-only` only while preparing uncommitted work. CI omits it and checks commit identities and the PR diff
using `--base <base-sha>`. `scripts/ci/clean_contracts.py` runs the contract, ticket and registry gates from a fresh
tracked-file copy, so an ignored local fixture cannot make a broken checkout pass. Stage new files before that
local gate; CI's checkout contains exactly the committed files.

Pinned toolchain: uv **0.11.8**, managed Python **3.12.13**, Node **22.22.3**, pnpm **11.1.2**. Exact dependency
versions and hashes live in `uv.lock` and `pnpm-lock.yaml`. These supersede the October 9 observations below.
`uv sync` installs all six workspace packages; `studio-control` currently has no third-party runtime dependencies.
The development license inventory is separate from the shipped control/web runtime inventory.

The Bash/Zsh helper refuses before exporting anything if STUDIO is absent, lacks ownership, is hosted internally,
is nested inside another disk image, or a cache/temp path resolves outside STUDIO through a symlink. On macOS
STUDIO_ROOT defaults to `/Volumes/STUDIO`; on Linux/Windows set it to the intended existing storage directory.
`STUDIO_PYTHON` may name the interpreter for sourcing the helper, useful with Git Bash on Windows.
`python3 scripts/dev/worktree.py <NN>-<slug>` uses the single external bare clone under `$STUDIO_ROOT/git` and creates
only under `$STUDIO_ROOT/worktrees`. It never clones or fetches automatically.

GitHub-hosted CI uses an explicitly disposable runner directory through `scripts/ci/bootstrap.py`; it does not use
the personal Mac volume adapter or claim physical storage qualification. CI tests the macOS adapter using synthetic
OS mount responses at the subprocess/filesystem boundary. Actual storage probes, playback, listening and paid runs
remain separate gates. Windows symlink privilege is not assumed; the escape test runs on the Unix runners.

T01 declared Linux PR checks plus macOS/Windows integration and nightly checks; since PR #12 (2026-11-06) every PR runs
on Linux, macOS and Windows, and the `integration` ruleset requires all three. A workflow definition is not an
executed check. Scheduled and manual workflows become available only when their definition reaches the default
branch; only Jon release-merges `integration` to `main`. Branch protection and owner prerequisites remain tracked
separately and must be satisfied before T01 closes.

## Toolchain

| Tool | Required | On the build Mac (MEASURED-LOCAL, 2026-10-09) | Notes |
|---|---|---|---|
| macOS | Apple Silicon studio host (compute tier 4) | macOS 26.6.2 (25G83), M5 Pro, 48 GiB unified memory | Metal `recommendedMaxWorkingSetSize` 37.44 GiB. |
| uv | one version for the repo, pinned (planned) | 0.11.8 (Homebrew) | Creates every Python environment and installs every interpreter onto the studio volume. |
| Python | per environment, below | `python3` on `PATH` is Homebrew's 3.14.7; 3.13 and the system 3.9.6 are also present; no 3.12 or 3.10 | Never build an AURA environment on a system or Homebrew interpreter. `uv python install 3.12 3.10` puts managed interpreters under `UV_PYTHON_INSTALL_DIR`. |
| Node | pinned in `package.json` `engines` (planned) | v26.8.2 (Homebrew) | Build time only. The control service serves the built web app, so no Node runs at runtime. |
| pnpm | pinned with `packageManager` (planned) | 11.1.2 | Takes its store and cache from `pnpm-workspace.yaml`, not `.npmrc` (see Environment). |
| Chromium-based browser | required for the Studio (ADR-0012, Q10 default) | Google Chrome 154.0.8037.98 | The playback gate reads Chrome's `playbackStats` (Chrome 146 and later). Safari is not supported for Studio playback. |
| ffmpeg | not on the v1-core path | 9.0.1 (Homebrew), configured with `--enable-gpl --enable-version3` | That is a **GPL-3.0 build**. It may only ever run as a separate process inside a worker: never linked, bundled or called by the control service. The decoder choice is an open license ticket (RECONCILIATION §4.9). Captures arrive as WAV, so the core path needs no decoder. |
| git | | 2.50.1 (Apple Git-155) | `~/Music Gen/aura` and `/Volumes/Backup Plus` contain spaces: always quote them. |
| gh | | 2.92.0 | Older than 2.94, so add sub-issues with the `gh api` fallback in `docs/agents/issue-tracker.md`. |
| `hdiutil`, `diskutil`, `tmutil`, `launchctl` | macOS built-ins | | Used only by the macOS store adapter and `scripts/store/`. |
| Containers | none on the Mac in v1 | Colima (Docker 29.4.1): an aarch64 VM with 32 GiB memory and a 100 GiB disk; `~/.colima` holds 33 GiB on the internal disk | Do not pull or build images into this VM, because its disk is internal. The yue2 image is built in CI or on a Linux host (planned). A running VM may hold unified memory that MLX needs (INFERRED); Jon decides whether to stop it during heavy jobs. |

### Python per environment

| Environment | Python | Why |
|---|---|---|
| uv workspace: `packages/contracts-py`, `services/control`, `workers/analysis`, `workers/fake`, `workers/conformance` | 3.12 | librosa 1.0 (pYIN, DTW) needs 3.12 or later. The control service has no audio or ML dependencies; FakeEngine is stdlib plus numpy. |
| `packages/worker-sdk` (`studio_worker`) | 3.10 or later, stdlib only | It installs into every pinned engine environment without dependency fights (ADR-0026). |
| `workers/transcribe-bp` | 3.10 | Basic Pitch 0.4.0 does not resolve on macOS arm64 with 3.12 (#203). Hum-benchmark challenger only. |
| `workers/ace` | set by the ticket that creates it, from ACE's own requirement | Standalone uv project, ACE main at or after `ca1e85fe9`, extras for darwin-arm64 (MLX/MPS) and linux-cuda. Upstream torch pins: 2.10.0+cu128 on Linux, 2.7.1+cu128 on Windows (VENDOR). |
| `workers/separate` | set by its ticket | Demucs 4.1.0 or demucs-mlx 1.6.1, individual and research lanes only. |
| `workers/yue2` | 3.12 inside the image (VENDOR: "3.12 (3.10+)") | OCI image: Linux, CUDA 12.8, torch 2.10.0, a pinned YuE2 commit, **no weights**. Its digest is pinned in the registry. |

## The studio volume (ADR-0015, ADR-0034)

Per the October 29 owner amendment, everything heavy lives in a dedicated APFS sparse bundle on **Extreme SSD**,
mounted as `/Volumes/STUDIO`:
models, the Hugging Face, uv, pnpm, pip, torch and Playwright caches, Python interpreters, engine environments,
worktrees, scratch, logs, evidence captures and, by default, the project store. The internal disk holds only the OS,
the browser, the canonical docs checkout at `~/Music Gen/aura` (nothing installed), `~/.config/studio/` and keychain
entries.

Why: the internal Data volume read between 2.0 and 57 GiB free on 2026-10-09 (MEASURED-LOCAL). It fluctuates, and the
57 GiB reading at 17:29Z relaxes no rule. Backup Plus is a Seagate 2.5″ spinning HDD, exFAT over USB, with about
1.1 TiB free, about 125 MB/s cold sequential read and about 70 MB/s synced write
(`docs/research/measurements/2026-10-09-backup-plus-throughput.md`). exFAT has no symlinks and no POSIX permissions,
so nothing is written to it directly. The APFS volume inside the bundle provides both.

Caches already on the internal disk, from before AURA (MEASURED-LOCAL, 2026-10-09T17:30Z): `~/.colima` 33 GiB,
`~/Library/pnpm/store` 4.4 GiB, `~/.cache/uv` 3.3 GiB, `~/Library/Caches/pnpm` 290 MiB, `~/.local/share/uv` 189 MiB.
Report them. Jon decides what to delete. `studioctl doctor` audits them (planned).

### Create it once

The volume is created once, by Jon or with his go-ahead, because it reserves up to 900 GiB of his backup drive.
`studioctl setup` will do every step below and print the commands that need admin rights (planned). Until it lands,
run them by hand.

1. **Choose the band size.** It is fixed when the image is created and cannot be changed in place. P0 measures the
   default 8 MiB bands (`16384` sectors) against 64 MiB (`131072` sectors) on this HDD (attach time, sequential read
   and write, random 4K read) and records the result as evidence before the real image exists (planned, in
   `scripts/store/`). Until that record exists the choice is UNVERIFIED.
2. **Create and attach.**

   ```sh
   BAND_SECTORS=16384   # replace with the measured choice; 16384 sectors = 8 MiB, hdiutil's default
   hdiutil create -type SPARSEBUNDLE -fs APFS -volname STUDIO -size 900g \
     -imagekey sparse-band-size="$BAND_SECTORS" "/Volumes/Extreme SSD/STUDIO.sparsebundle"
   hdiutil attach -nobrowse -owners on -mountpoint /Volumes/STUDIO "/Volumes/Extreme SSD/STUDIO.sparsebundle"
   mount | grep ' on /Volumes/STUDIO '            # expect: apfs, local, nobrowse
   diskutil info /Volumes/STUDIO | grep Owners    # expect: Enabled
   ```

   900g is a logical cap that leaves room for Jon's other backups; he may change it. `hdiutil resize -size <new>` on
   the detached bundle raises it later. The host's free space is the real limit either way.
3. **Lay out the volume.** `store.json`, `LOCK` and `projects/db/` are written by `studioctl` (planned); never write
   them by hand.

   ```sh
   cd /Volumes/STUDIO && mkdir -p projects scratch logs evidence worktrees \
     models/hf models/other models/licenses models/manifests envs/python envs/uv-cache envs/workers \
     caches/pnpm-store caches/pnpm-cache caches/pip caches/torch caches/mlx caches/xdg caches/ms-playwright
   touch /Volumes/STUDIO/.metadata_never_index
   ```

4. **Probe it.** Ownership, symlinks, exec bits, hardlinks and `clonefile` must all work (P0-2):

   ```sh
   cd /Volumes/STUDIO/scratch && echo probe > p && chmod 755 p && ln -s p p.link && ln p p.hard \
     && cp -c p p.clone && ls -l p p.link p.hard p.clone && rm -f p p.link p.hard p.clone
   ```

5. **Spotlight and Time Machine** (Jon runs the `sudo` line):

   ```sh
   sudo mdutil -i off /Volumes/STUDIO                              # Spotlight off; .metadata_never_index alone is UNVERIFIED
   tmutil isexcluded /Volumes/STUDIO                               # expect [Excluded]
   tmutil addexclusion "/Volumes/Extreme SSD/STUDIO.sparsebundle"  # sticky exclusion on the image itself
   ```

What has been checked, and where (MEASURED-LOCAL, 2026-10-09T17:29Z, macOS 26.6.2, on a 1 GiB probe image hosted on
the **internal** APFS disk and then deleted, not on Backup Plus): `sparse-band-size=16384` gives 8 MiB bands;
`hdiutil attach -nobrowse -owners on -mountpoint /Volumes/<name>` works without `sudo` and reports Owners Enabled;
symlinks, `chmod` exec bits, hardlinks and `cp -c` clones all work, and the clone took no extra space;
`diskutil verifyVolume` works on the mounted volume and `hdiutil compact` on the detached bundle. `tmutil addexclusion`
on the mounted volume failed with `Invalid argument` (the image's volume already reported `[Excluded]`), while
`tmutil addexclusion` on the bundle path succeeded. That is why step 5 targets the bundle, which refines the
"sticky `tmutil addexclusion`" of architecture §8.1. Every one of these behaviours is UNVERIFIED with Backup Plus's
exFAT as the host until P0 records it there.

### Attach at login

`studioctl store attach` (planned) adds the identity check, the unclean-detach check and the mount watch. Until it
lands, this optional LaunchAgent attaches the bundle at login and whenever a volume appears (Backup Plus being plugged
in, for example). Save it as `~/Library/LaunchAgents/local.studio.attach.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>local.studio.attach</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>-c</string>
    <string>B="/Volumes/Extreme SSD/STUDIO.sparsebundle"; [ -d "$B" ] &amp;&amp; ! /sbin/mount | /usr/bin/grep -q ' on /Volumes/STUDIO ' &amp;&amp; /usr/bin/hdiutil attach -nobrowse -owners on -mountpoint /Volumes/STUDIO "$B"; exit 0</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>WatchPaths</key>
  <array>
    <string>/Volumes</string>
  </array>
</dict>
</plist>
```

```sh
plutil -lint ~/Library/LaunchAgents/local.studio.attach.plist
launchctl bootstrap gui/"$(id -u)" ~/Library/LaunchAgents/local.studio.attach.plist
launchctl bootout gui/"$(id -u)"/local.studio.attach    # to remove it
```

This plist passes `plutil -lint` and its script passes `sh -n` (MEASURED-LOCAL). The agent has not been loaded on this
Mac yet.

### Detach, verify, compact, back up

```sh
hdiutil detach /Volumes/STUDIO                                  # stop `studioctl serve` and every worker first
diskutil verifyVolume /Volumes/STUDIO                           # after an unclean eject (drive pulled, sleep mid-write)
hdiutil compact "/Volumes/Extreme SSD/STUDIO.sparsebundle"      # offline only; deletes free no host space until this runs
```

`studioctl store detach` stops the service and workers before detaching, and an unclean-detach marker makes the next
attach run `verifyVolume` (planned). Backup Plus is a single physical HDD, so the real durability guarantee is the
hash-verified mirror of the irreplaceable closure made by `studioctl store backup <dest>` on a second device (planned;
the destination is owner-pending).

**Never `mkdir` or write under `/Volumes/STUDIO` while it is not mounted.** That writes to the internal disk and leaves
a directory squatting on the mount point.

## Environment (ADR-0034)

`scripts/dev/studio-env.sh` is implemented. Source it in Bash/Zsh from an external worktree. It delegates to
`environment.py` and `preflight.py`, validates the actual studio volume/backing device, and exports the HF, uv,
Python/tool, pip, torch, XDG, npm, Corepack, pnpm and Playwright paths plus TMPDIR/TMP/TEMP under STUDIO.
It emits no exports on failure. It refuses a globally inherited UV_PROJECT_ENVIRONMENT and refuses symlink escapes.
`studioctl env` and supervisor per-spawn environment setup remain planned.

```sh
source scripts/dev/studio-env.sh
python3 scripts/dev/preflight.py --estimate-gib 3
```

**`UV_PROJECT_ENVIRONMENT` is never exported in the shell.** If it were, every `uv sync` would share one environment.

- **The workspace** (control, analysis, fake, conformance, contracts-py, worker-sdk): leave it unset. `uv sync` builds
  `.venv` inside the worktree, which is on the volume, so each ticket gets its own and uv clones from the cache.
- **Engine workers** (`workers/ace`, `workers/separate`, `workers/transcribe-bp`) are standalone uv projects. The
  supervisor sets `UV_PROJECT_ENVIRONMENT=$STUDIO_ROOT/envs/workers/<env>/<lock_sha256>/` per spawn (planned), so
  every worktree with the same `uv.lock` shares one environment, and a lock change builds a new one (and a new profile
  revision). To build one by hand, after the disk preflight:

  ```sh
  cd "$STUDIO_ROOT/worktrees/<NN>-<slug>/workers/ace"
  UV_PROJECT_ENVIRONMENT="$STUDIO_ROOT/envs/workers/ace/$(shasum -a 256 uv.lock | cut -c1-64)" uv sync --frozen
  ```

**pnpm.** pnpm 11.1.2 ignores `store-dir` in `.npmrc` and ignores `npm_config_store_dir`: with either set,
`pnpm store path` still printed `~/Library/pnpm/store/v11` on the internal disk (MEASURED-LOCAL). It honours `storeDir`
and `cacheDir` in `pnpm-workspace.yaml`, substitutes `${VAR}` there, and refuses to run when the variable is unset
("Failed to replace env in config"), which fails safe. So the repo's `pnpm-workspace.yaml` carries (planned, with the
web scaffold):

```yaml
packages:
  - apps/web
  - packages/contracts-ts
storeDir: ${STUDIO_ROOT}/caches/pnpm-store
cacheDir: ${STUDIO_ROOT}/caches/pnpm-cache
```

Check it with `pnpm store path`, which must print a path under `/Volumes/STUDIO/caches/pnpm-store`. This departs from
architecture §2, which names `.npmrc` as the place for the store directory. The intent is unchanged: the store sits on
the same volume as `node_modules`, so pnpm hardlinks instead of copying. (`pnpm_config_store_dir` also works as an
environment variable.)

**Git worktrees** live at `$STUDIO_ROOT/worktrees/<NN>-<slug>/`, with their `.venv` and `node_modules` inside.

## Disk preflight (ADR-0015)

Every download, install, environment build, job and export declares its estimated bytes per volume before it starts.

- **The studio volume.** Effective free = min(APFS free inside the bundle, exFAT free on Extreme SSD) minus band
  overhead. Refuse if effective free minus the estimate is under **10 GiB** (configurable). The APFS volume reports
  its 900 GiB logical cap, not what the drive can hold, so always read the host too.
- **The internal disk.** No planned writes at all. Heavy jobs are blocked while it is under **2 GiB** free, because swap
  lives there.
- **Remote hosts.** A worker host is checked from the free disk it reports in `/v1/describe`. A pod's disk is sized at
  quote time.
- A running job fails honestly with `failed(disk_low)` if free space falls below half the margin. Every refusal names
  the volume, its free space, the amount needed and the margin.

Estimates (VENDOR sizes): ACE turbo with encoder and VAE ≈ 6.34 GB; the 1.7B LM ≈ 3.76 GB; ACE XL only as diffusers
bf16 (≈ 11.1–11.5 GB) once its loader is verified; YuE2 7.30 + 0.53 GB, on CUDA hosts and pods only. Outputs are
budgeted at 92,160,000 bytes (about 87.9 MiB) per 4-minute stereo float32 stem.

`studioctl doctor` computes all of this (planned). Until it lands, read the numbers by hand and put them in your
report:

```sh
studio_free_gib() { df -k "$1" | awk 'NR==2 { printf "%.1f", $4 / 1048576 }'; }
for v in /System/Volumes/Data /Volumes/STUDIO "/Volumes/Extreme SSD"; do
  [ -d "$v" ] && printf '%-22s %8s GiB free\n' "$v" "$(studio_free_gib "$v")"
done
```

Go ahead only if the smaller of the `/Volumes/STUDIO` and `/Volumes/Extreme SSD` figures, minus the estimate, leaves at
least 10 GiB, and nothing you are about to do writes to `/System/Volumes/Data`.

## Repository workflow

The November 6 owner amendment requires green current-head CI and independent review against the current integration base before a ticket merge. The November 7 decision (`docs/research/OWNER-DECISIONS-2026-11-07.md`) makes the repository public during the build, so `CLAUDE.md` hard rule 10 governs everything posted. Rulesets now enforce PR-only, squash-only merges into `integration`, the three `checks / foundation (…)` jobs and an up-to-date branch. The independent review stays procedural and is bound to the PR's patch (`git diff <merge-base>...<head> | git patch-id --stable`), and `main` takes only Jon's release merge. See also `docs/research/OWNER-DECISIONS-2026-11-06.md`.

Ticket worktrees come from a bare clone on the volume, so their commits, indexes and fetched packs never land in the
canonical checkout's `.git` on the internal disk (`~/Music Gen/aura` stays the docs checkout only).

```sh
# once, after the volume exists
GH_TOKEN="$(gh auth token --user Navigata1)" gh repo clone Navigata1/aura "$STUDIO_ROOT/git/aura.git" -- --bare
# per ticket
git -C "$STUDIO_ROOT/git/aura.git" fetch origin
git -C "$STUDIO_ROOT/git/aura.git" worktree add "$STUDIO_ROOT/worktrees/<NN>-<slug>" -b "ticket/<NN>-<slug>" integration
cd "$STUDIO_ROOT/worktrees/<NN>-<slug>"
git config user.email         # must end in @users.noreply.github.com (Rule 07)
```

If the identity is missing, derive the noreply address and set it in the repo config:

```sh
git config user.email "$(GH_TOKEN="$(gh auth token --user Navigata1)" gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"
```

Run every `gh` command for this repo with `GH_TOKEN="$(gh auth token --user Navigata1)"`, never `gh auth switch`. The
PR targets `integration` (O-01; `main` advances only by Jon's release merge) and its body carries `Closes #<issue>`.
Merge only after `gh pr checks <pr> --watch` passes, with `gh pr merge --squash --author-email <your noreply address>`
so the squash commit GitHub creates carries no personal address. Package manifests carry no author email (create uv
projects with `--author-from none`). Afterwards:

```sh
git -C "$STUDIO_ROOT/git/aura.git" worktree remove "$STUDIO_ROOT/worktrees/<NN>-<slug>"
```

Worker environments under `envs/workers/` stay: other worktrees with the same lock share them.

## Commands

Run from a worktree with the env file sourced.

| Command | What it does |
|---|---|
| `uv sync` | Builds the workspace `.venv` in the worktree. |
| `pnpm install` | Installs `apps/web` and `packages/contracts-ts` against the store on the volume. |
| `uv run studioctl setup` | Creates and attaches the volume (printing admin commands for Jon), probes it, and writes `store.json`, `LOCK`, the env file and the default compute profile from the tier recommendation. |
| `uv run studioctl doctor [--json]` | HardwareSnapshot, the recommended tier with reasons, free space per volume against the margin, store throughput, random IOPS and band size, stray internal caches and a `/Volumes/STUDIO` mount-point collision. Writes evidence records. |
| `uv run studioctl env` | Writes the env file above. |
| `uv run studioctl serve` | Starts the control service on 127.0.0.1: the Studio API plus the built web app, with COOP/COEP headers. Refuses to start unless the store is mounted, `store.json` matches and `LOCK` is free. Prints the one-time launch token that the browser exchanges for the owner-ui cookie. |
| `uv run studioctl store {create, attach, detach, compact, backup, restore, fsck, reindex}` | Volume and store lifecycle (ADR-0028, ADR-0034). |
| `uv run studioctl worker add <url>` | Registers a tailnet worker host with a pairing token. |
| `uv run studioctl quote …` | Requests a quote for a burst job. It never approves: Jon approves in the Studio UI. |
| `pnpm --dir apps/web build` | Builds `dist/`, which `serve` serves from its own origin. |

**FakeEngine.** With `STUDIO_ENV=dev` or `test`, a registry overlay enables the `test_only` profiles `fake-route-a`,
`fake-route-b`, `fake-burst`, `fake-nc` and `fake-separate` (and, once the contract ticket pre-seeds them,
`fake-repaint`, `fake-isolate`, `fake-reference-timbre`, `fake-tts`, `fake-asr` and `fake-diagnostic`), and the supervisor spawns `workers/fake` as a real
subprocess speaking the real worker protocol. Its output is the NeutralVoice guide over a key-derived pad, always
labelled "Synthetic test output". Fault knobs (`driftCents`, `crashAt`, `ignoreCancel`, …) work only with
`STUDIO_ENV=test`. FakeBurstProvider runs the whole quote → approval → reservation → settlement flow for $0. Nothing
fake is visible outside `dev` and `test`.

## Tests and validators

These run today with any `python3` 3.11 or later and the standard library only, from the canonical checkout or a
worktree:

| Command | What it gates |
|---|---|
| `python3 scripts/spec/validate.py` | The contract gate (below). |
| `python3 contracts/reference/generate_fixtures.py` | Regenerates the golden fixtures deterministically. Contract tickets only. |
| `python3 scripts/registry/sync.py` | Regenerates `contracts/registry/components.v1.json` and the open-source-readiness register in `docs/research/licenses/`; `--check` also fails when a release blocker is missing from that register. |
| `python3 scripts/spec/tickets.py --check` | The ticket DAG: shape, edges, reduction, story and inventory traceability, owner gates, path conflicts and slot ancestry. |

The rest are planned and land with the tickets that build them:

| Command | What it gates |
|---|---|
| `uv run python scripts/spec/validate.py` | The contract gate: schemas use only keywords the bundled checker implements, every fixture and registry file validates, the stdlib reference re-run matches exactly, seeded-bad fixtures fail, `components.v1.json` regenerates byte-identically, every `legacy/` fixture loads, and `claims_published` holds no MEASURED-LOCAL. |
| `uv run python contracts/reference/generate_fixtures.py` | Regenerates the golden fixtures deterministically. Contract tickets only. |
| `uv run python scripts/registry/sync.py` | Regenerates `contracts/registry/components.v1.json` from `docs/research/evidence-register.json` and the register overlay, and the open-source-readiness register from the same rows. |
| `uv run pytest services/control` | StudioHarness: the real app on an ephemeral port, a temp store (a 2 GB temp sparse bundle on macOS for the preflight and mount cases), FakeEngine and the analysis worker as real subprocesses, FakeBurstProvider, recorded hardware probes and an injectable clock. Ten minutes or less on a PR. |
| `uv run pytest workers/conformance --worker <url> --token <token>` | Worker-protocol conformance. Each of the eight mutants in `workers/conformance/mutants/` must fail it. The `--paid` marker goes through the real quote, Jon's UI approval and the reservation; an agent never starts it. |
| `pnpm --dir apps/web test` | vitest, including the TimeModel twin against `contracts/fixtures/tempo`. |
| `pnpm --dir apps/web exec playwright test` | Chromium with `--use-fake-device-for-media-stream --use-file-for-fake-audio-capture=<NeutralVoice hum>.wav`: the UI drives the API, no blind label or hash reaches the DOM or the network, the approval-card copy, keyboard-only operation and an accessibility audit on every screen. |
| `scripts/ci/` | The Rule-07 lint (no `mailto:`, no address but the public contact, no bare address in Markdown prose, noreply authors only, no author email in a package manifest; on every PR and every push to `integration`), a repo-wide secret scan (tracked files, the PR diff, `docs/evidence/**`) plus a scan of the built web bundle, the license allowlist over the control environment and the web bundle (unknown fails; LGPL, GPL, AGPL, NC, CC-BY-SA, SSPL and BUSL denied), and the no-weights check (size and extension). Each must fail on a planted violation (P0-7). |

Run the stdlib scripts with `uv run python`, so they use the workspace's 3.12 rather than whichever `python3` is first
on `PATH`.

CI: since PR #12, `pr.yml`, `integration.yml` and the nightly all run the foundation checks on Linux, macOS and Windows.
Planned additions join as their tickets land: fake and analysis conformance with the mutants, headless Playwright on
every PR, and Playwright on macOS Chromium with screenshots attached in the nightly. A self-hosted Mac runner produces hardware evidence and never runs paid jobs.

## Per-OS notes

### macOS: the studio host today (tier 4)

- The only OS with the sparse-bundle `StoreVolume` adapter; macOS-only code lives there and in `scripts/store/`. MLX and
  Metal live only in Mac worker environments (ACE's darwin-arm64 extra, demucs-mlx, the analysis worker's `probe`).
- The volume is a spinning HDD. A cold ACE turbo load takes about 50 s and an XL bf16 load about 90 s (INFERRED from the
  measured throughput), and imports from environments on the HDD are slow too. Workers keep one heavy model resident
  and report cold and warm times separately.
- The tailnet holds two macOS nodes and no Linux or Windows host (MEASURED-LOCAL, `tailscale status`).

### Windows

- The control service runs natively (Python 3.12 through uv, a Chromium browser). The store is a plain directory on
  NTFS with the same layout. Set the same variables (`STUDIO_ROOT` and the rest) in the session that runs `studioctl`;
  the store format uses no symlinks or extended attributes and keeps paths short.
- CUDA workers run in **WSL2**, not natively: YuE2 on native Windows needs unmerged patches. Give WSL2 at least 24 GB,
  YuE2's host-RAM recommendation (VENDOR), in `%UserProfile%\.wslconfig`:

  ```ini
  [wsl2]
  memory=24GB
  ```

- cu128 wheels need NVIDIA driver 570.65 or later on Windows. A Blackwell card on cu128 needs torch 2.11 or earlier;
  otherwise cu130 with an R580+ driver.
- Whether WSL2's localhost forwarding reaches the workers on Jon's box is UNVERIFIED. Binding the workers to the tailnet
  interface is the alternative.
- The GPU, RAM and WSL2 details are owner-pending (Q1). Windows stays unverified until StudioHarness and the playback
  gate pass on the real machine (P6).

### Linux

- Either the studio host (control service, a plain-directory store, Chromium) or a worker host only.
- cu128 wheels need driver 570.26 or later. YuE2 runs from the pinned image under an OCI runtime with GPU access; ACE
  on CUDA uses torch 2.10.0+cu128 (VENDOR).
- Owner-pending (Q1), and unverified until P6.

### Worker hosts and burst

- Workers bind loopback or the tailnet interface, require a bearer token, expose no shell and never call the control
  service. A tailnet host joins with `studioctl worker add <url>` and is admitted per profile only after its own
  conformance and smoke evidence on its host class.
- Burst pods (RunPod secure cloud) exist only after a quote, Jon's approval in the UI and a ledger reservation, and
  never from a dev shell. Pod rates, proxy behaviour, in-container shutdown billing, spend limits and private-registry
  pulls are UNVERIFIED until the P3 spikes record them.

## Evidence

A ticket is done when a check that could have failed has passed (CLAUDE.md rule 1).

- **The PR carries the proof**: the commands run, exit status, test counts, CI run ids, the host class (for example
  `mlx/m5pro`), the profile revision for any real engine, Playwright screenshots, and SHA-256 hashes of every attached
  file.
- **Five kinds of result, reported under separate PR headings**, never merged:
  - **CI on fakes**: FakeEngine, NeutralVoice fixtures and FakeBurstProvider. They are synthetic: they can fail
    anything, meet a smoke gate only where that gate allows it, and never meet a benchmark gate.
  - **Hardware**: per profile revision and host class. Install, conformance, smoke (every check its gate declares), and
    cold and warm timings from the worker SDK, labelled MEASURED-LOCAL.
  - **Listening**: Jon's verdicts only. Everyday verdicts are `listening-unregistered` and never change a status; only a
    preregistered set of eval auditions promotes or demotes. An agent never writes a listening result. It links the one
    Jon recorded.
  - **Paid**: quotes, Jon's approvals, reservations, settlements and the reconciled ledger.
  - **Per-OS**: StudioHarness, the playback gate and the recovery test on a real host of each operating system.
- **Evidence records** (`evidence/1`) hold the check, subject, profile revision, host class, result, MEASURED-LOCAL
  values, the per-check results the gate declares (with the owner verdict that answered a listening check), a synthetic
  flag, hashed attachments and, where needed, the preregistration hash. They reach the registry only through
  `POST /api/v1/evidence`; the store is the system of record. `studioctl evidence export` writes a hash-checked export
  of a record and of every verdict and preregistration it cites (no audio) to `docs/evidence/`, and the contract gate
  runs every reference rule over those exports; raw captures wait in
  `$STUDIO_ROOT/evidence/`. Never audio, never secrets. Until `evidence/1` and the endpoint land (planned), save raw
  output under `$STUDIO_ROOT/evidence/<NN>-<slug>/`, hash each file with `shasum -a 256`, and list the hashes in the PR.
- **Design-informing local measurements** go in `docs/research/measurements/<date>-<topic>.md`, saying exactly how
  they were taken. The Backup Plus throughput note is the pattern.
- **Label every number** with its figure label, and say what is planned, what is measured and what is unverified.
  "Works on Windows" is never written from a Mac or from CI alone.
