# AURA v1 architecture

Status: **proposed**, 2026-10-09. This is the lead architect's synthesis of three judged proposals:

| Proposal | Lens | Owner-value judge | Engineering judge | Risk-evidence judge | Total |
|---|---|---|---|---|---|
| A | creator-first | 50 | 50 | 47 | **147** (winner) |
| C | longevity-first | 46 | 45 | 45 | 136 |
| B | evidence-first | 45 | 46 | 43 | 134 |

The base is the creator-first proposal. Every idea a judge endorsed is grafted on unless it adds a seam or a module without paying for that seam or module. §13 lists what came from each proposal, what was rejected and why, and how each tension was resolved.

**Binding inputs:** `docs/research/OWNER-DECISIONS-2026-10-09.md` (O-01…O-11) and the proposed decisions D-01…D-24 in `docs/research/RECONCILIATION.md` §6. Where this document amends a D-decision, it says so. The amended decision becomes an ADR (§13.4).

**Labels** follow RECONCILIATION.md: VENDOR, COMMUNITY, COMPETITOR-RUN, MEASURED-LOCAL, OWNER-REPORTED, INFERRED, UNVERIFIED. Nothing in this document has been built or run. Every claim below that a component "does" something is a design commitment. It is not a measurement.

**Fresh measurement** (MEASURED-LOCAL, `df -h` at 2026-10-09T16:56Z):

- Internal Data volume: **9.5 GiB free**. Readings across 2026-10-09 span 2.0–57 GiB (timestamped in `docs/DEVELOPING.md`, the one source for this range); every rule assumes the 2 GiB floor.
- `/Volumes/Backup Plus`: **1.1 TiB free**. It is exFAT over USB, and `diskutil` reports "Solid State: Info not available".
- `docs/research/measurements/2026-10-09-backup-plus-throughput.md` identifies the drive as a Seagate BUP Slim 2.5″ **spinning HDD**. It measured about 125 MB/s cold sequential read and about 70 MB/s synced sequential write (one run each, MEASURED-LOCAL). This design treats it as an HDD.

---

## 1. Shape

AURA v1 has five parts:

- **One control service.** It is portable, written in Python 3.12 with FastAPI, uses stdlib `sqlite3` in WAL mode, and has no audio or ML dependencies.
- **One worker SDK.** It is stdlib-only and runs on Python ≥3.10.
- **A small set of worker processes.** They do all DSP and inference.
- **A thin Vite/React web app.** The control service serves it from its own origin.
- **A content-addressed project store** on an APFS sparse bundle on Backup Plus.

The control service's HTTP+SSE **Studio API** is the only product seam. The browser, the CLI, the test harness and the eval harness are all clients of it. Behind it sit six deep modules:

- **ProjectStore**: the durable truth.
- **Conductor**: durable jobs.
- **Registry**: what may run, in which lane, at what evidenced status.
- **Placement**: where it runs and what it costs, including the paid-burst broker.
- **Score**: pure composition semantics.
- **Audition**: blind, level-matched A/B.

The control service reaches every engine through one HTTP **worker protocol**, and the control service is always the client. That protocol is the second, process-boundary seam. A localhost Mac worker, a tailnet CUDA box and a rented pod behind NAT all speak it unchanged. Assets move by SHA-256 and are never sent as paths or URLs.

The **creator path comes first**. A deterministic FakeEngine speaks the real protocol and sounds like **NeutralVoice**, AURA's own license-clean guide synth. With it, the whole hum/MIDI → MelodySpec → SongForm → 2 candidates → blind A/B → keeper → verified export path runs on three operating systems before any weights are downloaded. Real engines then arrive at the same seam: ACE-Step on the Mac first, then YuE2 on an approved, cap-bounded burst. Each one must pass install, conformance, smoke and evidence before it appears.

Two disciplines are taken from the runner-up proposals:

- **Registry status is computed from evidence records**, keyed by a pin-hash `profile_revision` and a `host_class`. It is never stored as a field.
- **Every immutable record is reconstructible from the store**, through content-addressed JSON records and per-blob provenance sidecars. Lane taint propagates only along audio-ancestry edges, never along analysis edges.

Narration is not precluded. The store, Conductor, Placement, Registry and SDK are domain-agnostic, `Artifact.origin` includes `tts_render`, and `Project.kind` reserves `narration`.

---

## 2. Repo layout

The repo is `Navigata1/aura`, private, all rights reserved until Q5. Following O-01, each ticket gets one issue, one branch and one PR into the integration branch. The product name appears only in `contracts/product.json` (O-10). Code identifiers are neutral: Python packages use `studio_*`, environment variables use `STUDIO_*`, the CLI is `studioctl` and the volume is `/Volumes/STUDIO`. The CLI is not called `studio` because Android Studio's JetBrains launcher installs that command name, and Jon also builds Android (JOVRA).

```
aura/
├── CLAUDE.md                     hard rules: evidence not claims; IDC Rule 07 (`hello@islanddevcrew.com` as text only,
│                                 never mailto, never a personal address, noreply commit identity); no secrets in client
│                                 code; no weights vendored; NC/copyleft only inside a worker process; lanes enforced;
│                                 never present a VENDOR number as measured; never fabricate quality
├── GLOSSARY.md                   Hum, Capture, MelodySpec, Phrase, SongForm, Guide, NeutralVoice, Route (R1 / R2-raw /
│                                 R2-synth / text), Engine profile, Profile revision, Host class, Candidate, Generation
│                                 request, Audition, Blind label, Verdict, Keeper, Export bundle, Operator lane, Eligible
│                                 lanes, Retention class, Compute tier, Compute profile, Session, Burst run, Quote,
│                                 Approval, Reservation, Reference standard, Badge, Evidence record, Owner act
├── README.md  LICENSE (pending Q5)  NOTICE
├── pyproject.toml + uv.lock      uv workspace: packages/contracts-py, packages/worker-sdk, services/control,
│                                 workers/analysis, workers/fake, workers/conformance (all py ≥3.12 except worker-sdk)
├── package.json + pnpm-workspace.yaml (storeDir and cacheDir from STUDIO_ROOT; pnpm 11 ignores .npmrc store-dir)   apps/web, packages/contracts-ts
├── contracts/                    LANGUAGE-NEUTRAL SOURCE OF TRUTH (JOVRA spec/ pattern, ADR-0001 there)
│   ├── product.json              {"productName": "AURA", "publicContactText": "hello@islanddevcrew.com"}
│   ├── schemas/*.schema.json     JSON Schema 2020-12; every record has `kind` + `schemaVersion`; no `$id`, relative refs
│   ├── registry/
│   │   ├── components.v1.json    license register, REGENERATED byte-identically from docs/research/evidence-register.json
│   │   ├── engine-profiles.v1.json   declarations only: tasks, limits, lanes, components, pins, gates, published claims.
│   │   │                             No status field (status is computed, §4.4)
│   │   ├── capabilities.v1.json  non-engine capabilities gated the same way (studio.playback per OS, capture.mic, …)
│   │   ├── lanes.v1.json         individual | llc | research, forbidden classes, propagation rule
│   │   ├── compute-tiers.v1.json tier rules 1–4 (O-02)
│   │   └── price-snapshots/<provider>-<date>.json   dated FALLBACK only; live rate is fetched at quote time
│   ├── fixtures/                 golden JSON only (no audio): melody ops, MIDI↔MelodySpec, tempo vectors (tick↔frame),
│   │   │                         SongForm assembly, MelodySpec→ABC (pickup, tuplet, tempo-change, language cases),
│   │   │                         lane checks (incl. analyzed_by non-propagation), tier recommendations from recorded
│   │   │                         hardware output, ledger arithmetic (month boundary, open reservations, settle at
│   │   │                         ceiling), audition gains, manifests, worker-protocol transcripts, negative cases
│   │   └── legacy/<schemaVersion>/   FROZEN at first release; must load (upcast on read) at HEAD forever
│   └── reference/studio_ref/     stdlib-only reference implementations of every pure rule + generate_fixtures.py
│                                 (deterministic bytes): tick↔frame, SongForm assembly, MelodySpec→ABC, recommend(),
│                                 ledger arithmetic, lane closure, audition gains
├── packages/
│   ├── contracts-py/             Pydantic v2 models generated from contracts/schemas (control service only); CI drift check
│   ├── contracts-ts/             generated TS record types + typed Studio API client (from FastAPI OpenAPI) + the
│   │                             TimeModel TS twin, tested against contracts/fixtures/tempo read in place
│   └── worker-sdk/               studio_worker, STDLIB ONLY, Python ≥3.10: protocol server (ThreadingHTTPServer + SSE +
│                                 polling), bundled stdlib JSON-Schema-subset checker over the same contracts/schemas,
│                                 asset cache, cancel, crash journal, parent-death watchdog, SDK-measured timings and
│                                 peak RSS, env-lock / commit / weights-manifest reporting
├── services/control/             studio_control (no audio or ML deps):
│   └── studio_control/{api, store, conductor, registry, placement, score, audition, cli}
│                                 placement/{probe, recommend, supervisor, burst/{runpod.py, fake.py}, ledger}
│                                 store/{volume_macos_sparsebundle.py, volume_plain_dir.py}
│                                 cli: studioctl setup | doctor | serve | env | store {create, attach, detach, compact,
│                                      backup, restore, fsck, reindex} | worker add | quote (never approve)
├── workers/                      each engine worker is a STANDALONE uv project with its own lock (torch pins conflict, A8)
│   ├── analysis/                 py3.12 CPU, every OS: transcribe (pYIN+HMM), measure, guide (NeutralVoice),
│   │                             assemble-audio, export render+verify, adherence, probe (MLX Metal working set on darwin-arm64)
│   ├── fake/                     FakeEngine (stdlib + numpy): deterministic, real protocol, fault knobs in test mode only
│   ├── conformance/              pytest suite: --worker URL --token; mutants/ (must each FAIL); --paid marker
│   ├── separate/                 internal vocal separator for analysis: Demucs 4.1.0 / demucs-mlx (individual + research
│   │                             lanes only); LLC-candidate separator added after its training-data check
│   ├── ace/                      ACE-Step 1.5 pinned main ≥ ca1e85fe9; extras darwin-arm64 (MLX/MPS) and linux-cuda
│   ├── yue2/                     Dockerfile (CUDA 12.8, torch 2.10.0, pinned YuE2 commit, NO weights) + uv.lock;
│   │                             image digest pinned in the registry; private GHCR
│   └── transcribe-bp/            Basic Pitch in its own py3.10 env (#203); hum-benchmark challenger only
├── apps/web/                     Vite + React + TS; built dist/ served by the control service with COOP/COEP;
│   ├── src/studio/engine/        StudioEngine (P5): AudioWorklet + SharedArrayBuffer rings + decode Web Worker
│   └── e2e/                      Playwright suite
├── eval/                         (P4) briefs/{smoke-12, full-48}, prereg/ (hash committed before any run), harness/
│                                 (a CLI client of the Studio API; no private path to the store)
├── scripts/
│   ├── spec/validate.py          schemas, fixtures, registry, reference re-run, legacy load; seeded-bad fixtures must fail
│   ├── spec/jsonschema_subset.py refuses keywords it does not implement (JOVRA pattern)
│   ├── registry/sync.py          evidence-register.json → contracts/registry/components.v1.json
│   ├── store/                    hdiutil helpers, band-size measurement
│   └── ci/                       Rule-07 lint (no mailto link, no address but `hello@islanddevcrew.com`, noreply author),
│                                 secret scan of the built web bundle, license deny-list (GPL/AGPL/NC) over the control
│                                 env and web bundle, no-weights check (size + extension), private-path lint (no home
│                                 that names an account, no home folder but a hidden one, Library or AppData; skips
│                                 docs/research/sources/; allowed forms listed beside the rule in check.py)
├── docs/{adr/, spec/, research/, agents/, evidence/, FORMAT.md, DEVELOPING.md}
│                                 FORMAT.md documents the store layout so a project is readable without AURA's code;
│                                 docs/evidence/ holds committed EvidenceRecord JSON + hashes (never audio)
└── .github/workflows/            pr.yml (Linux: contracts, control, fake + analysis conformance + mutants, Playwright
                                  headless, lints) · integration.yml / nightly (macOS + Windows matrix; Playwright on macOS
                                  Chromium with screenshots) · a self-hosted Mac runner for hardware evidence
```

**Stack.** The D-12 stack is unchanged: Vite + React + TS, FastAPI, SQLite, SSE, per-engine uv environments, Chromium required for Studio, and no Next.js. The departures, each justified:

1. **JSON Schema is the source of truth.** Generated Pydantic and TS types follow from it. The two runtimes share contracts, not code (JOVRA ADR-0001). The stdlib worker SDK validates against the same schemas with the bundled subset checker, so no worker imports the control service.
2. **One HTTP worker protocol, with the control service always the client.** D-03 left the transport open. HTTP is the only transport that works unchanged on localhost, over a tailnet, and to a rented pod the Mac cannot be called back from.
3. **The control service serves the built web app** from the same origin. That means no CORS, no Node at runtime, and COOP/COEP headers from P0, so the P5 StudioEngine can use SharedArrayBuffer.
4. **pnpm.** It is already installed, and its store sits on the same volume as the worktrees, so hardlinks work.
5. **YuE2 runs as an OCI image** rather than a bare uv env (D-16 allows containers). It must run identically on a RunPod pod and on a Linux or WSL2 box.
6. **Engine workers are standalone uv projects** outside the workspace lock (A8).
7. **`awaiting_approval` is a new job state** (O-09).

---

## 3. Processes and topology

### 3.1 Processes

| Process | Runs on | Responsibilities |
|---|---|---|
| **Browser** (Chromium-based, Q10 default) | The studio host | Renders the web app. It captures the hum as raw float32 PCM at the device rate through an AudioWorklet. Echo cancellation, noise suppression and auto gain are off, verified with `getSettings()`. It hashes the capture with SubtleCrypto and uploads it as WAV, which keeps the UNVERIFIED m4a decoder off the core path. It records live MIDI through Web MIDI and plays auditions through GainNodes using server-computed gains. It talks only to the control origin. It holds no secrets and no edit logic. |
| **Control service** (`studioctl serve`, one uvicorn process) | The studio host: the Mac in tier 4; the Mac or the CUDA host in tiers 1–3. macOS, Windows or Linux (D-24). | Runs the Studio API, the Conductor's asyncio loop, the worker supervisor, the burst client, the ledger and the reaper. It refuses to start unless the store is mounted, `store.json` identity matches and the store `LOCK` is free. It reads secrets (RunPod API key, HF token for gated models, tailnet pairing secrets) from the OS keychain through `keyring`. It binds 127.0.0.1. Binding to the tailnet is opt-in and token-gated. It sets every cache and temp variable for the workers it spawns (§8.4). |
| **Analysis worker** | Local to the control service, every OS, CPU only | Tasks: `transcribe`, `measure`, `guide` (NeutralVoice), `assemble-audio`, `export` (render and verify), `adherence`, `probe`. Spawned by the supervisor with TMPDIR set to `scratch/<job_id>/`. |
| **Separator worker** | Mac (demucs-mlx or Demucs MPS, chosen by smoke); CUDA host later | Runs the internal vocal separation that adherence and PER need. Its outputs are analysis artifacts and are never exported as stems. It is individual and research lanes only until an LLC-clean separator passes its check. |
| **ACE worker** | Mac (MLX/MPS) in tier 4; local CUDA host in tiers 1–3 | Tasks: `cover` (R2-raw, R2-synth), `text_to_song`, and later `repaint`. Spawned on demand. At most one heavy model is resident per device. It unloads when idle. |
| **FakeEngine worker** | Dev machines and CI on Linux, macOS and Windows | Produces deterministic candidates over the real protocol. It also impersonates a burst pod for FakeBurstProvider. It is enabled only when `STUDIO_ENV` is `dev` or `test`. |
| **CUDA worker host** (tiers 1–3; hardware owner-pending, Q1) | A Linux box, or WSL2 on the Windows box (`.wslconfig` memory ≥24 GB) | `studio-worker` services run the yue2 container and ACE on CUDA, plus HeartMuLa or MiniMax later. They bind only to the tailnet interface. They are registered once with `studioctl worker add <url>` plus a pairing token. They report nvidia-smi facts in `/v1/describe`. They never call the control service. |
| **Rented burst pod** | RunPod GPU pod (secure cloud preferred over community hosts for unreleased melody and lyrics), 24 GB class with a fallback list | Started from the pinned yue2 image digest. It exists only after Jon's approval and a written ledger reservation. Weights download at boot onto pod disk under a recorded license acceptance. A network volume is adopted only if measurements show it is cheaper (§7.6). The pod serves the worker protocol through the provider's HTTPS proxy with a per-lease bearer token. The control service polls it. An in-image deadline (`shutdown -h` at the lease's hard maximum) backs up the control-side reaper. The pod is tagged `studio-burst` plus the run id. |
| **Store mount** | macOS (`hdiutil`), with an optional LaunchAgent at login | `studioctl store attach` mounts the sparse bundle. `detach` stops the control service and workers first. An unclean-detach marker triggers `diskutil verifyVolume`. `compact` runs offline. |
| **Eval harness CLI** (P4+) | The studio host | A Studio API client. It runs preregistered briefs, opens eval-mode audition sessions and posts EvidenceRecords. It can request quotes but never approve them. |
| **CI runners** | GitHub Actions (Linux, macOS and Windows on every PR since PR #12, integration and nightly) plus a self-hosted Mac runner | Contract gate, StudioHarness suite, conformance against fake and analysis workers plus mutants, Playwright, and the lints. The self-hosted Mac runner produces hardware evidence. It never runs paid jobs. |

### 3.2 Topology per compute tier

The **studio host** runs the browser, the control service, the store and the analysis worker. **Worker hosts** run engine workers. The tier decides placement (§7). It never changes a project.

```
TIER 4  (current recommendation: M5 Pro, 48 GiB)
┌──────────────────────── Mac (studio host) ────────────────────────┐          ┌──────── RunPod pod (burst) ────────┐
│ Chromium ──HTTP+SSE──▶ control service ──HTTP (token)──▶ analysis  │  HTTPS   │ yue2 worker (pinned image digest)  │
│                         │  ProjectStore on /Volumes/STUDIO         │──proxy──▶│ weights on pod disk; per-lease     │
│                         ├──HTTP──▶ ACE worker (MLX/MPS)            │ (polls)  │ token; in-image deadline           │
│                         └──HTTP──▶ separator worker (individual)   │          └────────────────────────────────────┘
└────────────────────────────────────────────────────────────────────┘  only after quote → UI approval → reservation

TIER 1 / 2  (NVIDIA 24–32 GB / 24 GB; owner-pending Q1)
 Option A: Mac stays studio host ──tailnet HTTP──▶ CUDA worker host (Linux, or WSL2 on Windows): ACE CUDA + yue2 local
 Option B: Linux box is studio host (control + store as a plain directory + Chromium), workers local on the same box
 Windows box as studio host: control service runs natively on Windows; CUDA workers run in WSL2 on localhost
 forwarding (whether WSL2 localhost forwarding works on Jon's box is UNVERIFIED). Burst stays available as overflow,
 still with per-run approval.

TIER 3  (NVIDIA 11.5–23.5 GiB at compute capability ≥ 8.0; O-02 names 12–16 GB)
 Same as tiers 1/2. ACE 2B (XL only with offload after a smoke run). YuE2 runs locally ONLY after a smoke record on
 that exact card (A4 open); until then it resolves to burst.
```

On every host, workers bind loopback or the tailnet interface, require a bearer token and expose no shell (§9.2). A non-Apple host without a qualifying GPU (compute capability below 8.0, or none) is burst only: CUDA profiles take tier-4 placements and MLX profiles are unavailable off the Mac. Separation runs only on the Mac (MPS or MLX) until a CUDA separator profile exists, so individual-lane adherence on a Linux or Windows studio host reads "unmeasured" until then.

---

## 4. Deep modules

Each module is listed with its interface, what it hides, and its internal seams. "Interface" means everything a caller must know (codebase-design vocabulary). The control service's modules are all in-process. Only the Studio API and the worker protocol are external seams.

### 4.1 Studio API (`studio_control.api`): the one product seam (thin by design)

**Responsibility.** HTTP + SSE resources, the built web app, and range-served audio. It validates contracts at the edge and maps module errors to typed problem responses. It holds no music logic.

**Interface (v1 resources).**

| Area | Resources |
|---|---|
| System and compute | `GET /api/v1/system` (store mount, per-volume free space vs margin, versions, product name) · `GET /api/v1/compute/detect` → HardwareSnapshot + Recommendation · `POST /api/v1/compute/recommend` (pure what-if) · `POST /api/v1/sessions {tier \| ComputeProfile}` · `PATCH /api/v1/sessions/{id}` (switch) |
| Projects and capture | `POST /api/v1/projects {name, operator_lane}` · `GET /api/v1/projects/{id}` → ProjectView · `POST /api/v1/projects/{id}/captures` (PCM WAV with client sha256 → Artifact + transcribe Job; or `.mid`, or a live-MIDI event list → MelodySpec) · `POST /api/v1/projects/{id}/lane` (**owner act**; re-checks every artifact) |
| Melody and song | `POST /api/v1/melodies/{id}/revisions {base_rev, ops[]}` (409 on a stale base; each op is timestamped and logged) · `GET /api/v1/melodies/{id}/{rev}/as/{midi\|abc\|guide}` → bytes, a Job, or `Ineligible{reasons}` · `PUT /api/v1/projects/{id}/song` → SongSpec + `Validation{conflicts, unsupported_by_profile}` |
| Generation and jobs | `POST /api/v1/projects/{id}/generations {song_rev, mode: auto\|explicit, routes?}` → GenerationRequest{plan with reasons, declined routes, jobs, quotes} (409 `profile_not_promoted` before any load) · `POST /api/v1/jobs/{id}/cancel` · `GET /api/v1/events?after=seq` (SSE, resumable with `Last-Event-ID`) |
| Paid runs | `GET /api/v1/quotes/{id}` · `POST /api/v1/quotes/{id}/challenge` → `{nonce, expires_at}` (**owner-ui scope only**) · `POST /api/v1/quotes/{id}/approve {nonce, quote_sha256}` (**owner act**) · `GET /api/v1/budget` · `POST /api/v1/budget/overruns/{id}/acknowledge` (**owner act**) |
| Audition and keepers | `POST /api/v1/generations/{id}/auditions` and `POST /api/v1/projects/{id}/auditions {candidate_ids}` (several requests, a re-roll beside an earlier candidate) → Audition (labels only; opens only when every arm is ready and every arm's audio allows `audition_arm`) · `GET /api/v1/auditions/{audition_id}/audio/{label}` · `POST /api/v1/auditions/{audition_id}/verdict` (**owner act**) · `POST /api/v1/auditions/{audition_id}/reveal` · `POST /api/v1/projects/{id}/keepers {candidate_id, verdict_id}` |
| Export | `POST /api/v1/keepers/{id}/exports {formats}` → export Job · `GET /api/v1/exports/{id}` (bundle and zip) |
| References and imports | `POST /api/v1/references` (audio + permission record; **owner act**) · `POST /api/v1/imports` (imported_mix with source service, attested terms, contained studio exports and detected marks; **owner act**) · `POST /api/v1/risk-acceptances` (**owner act**; engine, conditioning, separation, edit or conversion input only) |
| Registry and evidence | `GET /api/v1/registry?audience=product\|lab` (published claims and local results in separate fields) · `POST /api/v1/evidence` (EvidenceRecord; Registry checks the gate rules) · `POST /api/v1/licenses/{component}/accept` (**owner act**, `license-acceptance/1`, before any weights download, gated or not) |

**Auth and local hardening.**

- Binds 127.0.0.1, with a Host allowlist (DNS-rebinding defence) and an Origin check on every state change.
- `studioctl serve` prints a one-time launch token, only to an interactive terminal and never to a log (`serve --open` hands it to the browser directly). The browser exchanges it for a `SameSite=Strict` cookie with the **owner-ui** scope. Test mode mints owner-ui sessions only on a temporary store marked `test_store`, with FakeBurstProvider forced and keyring reads off.
- The CLI, the eval harness and agents use an **automation** token from a local token file. That scope can do everything except **owner acts**: approve a quote, change the cap, acknowledge an overrun or a reconciliation adjustment, change a project lane, submit a verdict, accept a risk, accept a model license, record a reference permission, attest an import.
- An owner act requires the owner-ui cookie. A paid approval also requires the challenge nonce rendered in the dialog. An automation token gets 403 on every owner act.
- Secrets, worker tokens and burst URLs never cross the API.

**Depth rationale.** The module is deliberately thin because it is the seam, not the depth. Putting the highest seam here means the browser, StudioHarness and the eval harness all exercise the same surface. Pure Score logic is reachable through the render and what-if endpoints, so golden fixtures need no second test seam.

### 4.2 ProjectStore (`studio_control.store`): the durable truth

**Responsibility.**

- **Content-addressed blobs.** SHA-256, staged in `tmp/` on the same volume, fsync, rename, then read-only (0444). Native-rate originals are always kept.
- **Content-addressed records.** Every immutable domain record is also written as canonical JSON under `records/`, in the same unit of work as its SQLite row: MelodySpec and SongSpec revisions, verdicts, keepers, export manifests, evidence records, reference permissions, risk acceptances. Canonical JSON means UTF-8, sorted keys, no insignificant whitespace and integers only. Non-integer quantities (LUFS, dBTP, cents, prices) are decimal strings with declared precision (the JOVRA pattern). Python and TS therefore hash identically with no float canonicalization.
- **Provenance sidecars.** Each artifact blob has a `<sha>.prov.json` sidecar beside it.
- **SQLite metadata** (D-09 kept as the system of record the service reads and writes): WAL mode, numbered SQL migrations, `synchronous=FULL`, and `fullfsync=ON` plus `checkpoint_fullfsync=ON` on macOS. It holds projects, revision heads, the artifact index, jobs, events, sessions, quotes, approvals, burst runs, the ledger, verdicts and evidence. A `.backup` snapshot is taken nightly and after every keeper.
- **Unit of work.** Blob, then sidecar or record, then SQLite rows and events, all committed atomically. Outputs therefore appear only together, and a crash leaves at most unreferenced blobs, which the recovery scan quarantines.
- **Write-path rules.** Committing an artifact into a project whose lane is not in its `eligible_lanes` is rejected. Records must be schema-valid and provenance-complete.
- **Provenance closure** walks typed edges (§10).
- **Retention class** on every artifact: `irreplaceable`, `derived` or `reproducible` (§8.6).
- **Disk preflight on every volume** (§8.5).
- **Recovery scan at startup.** Removes stale tmp files, quarantines blobs without rows, flags rows without blobs, and runs `PRAGMA integrity_check`.
- **`reindex`.** Rebuilds the artifact and record rows and the revision heads (each head is the tip of its parent chain) from sidecars and records.
- **`backup` / `restore` / `fsck`.** A hash-verified mirror of the irreplaceable closure (§8.6).
- **Single writer.** A process lock on `LOCK` stops a second `serve` on the same store.
- **Mount watch.** If the volume disappears, new jobs are refused and in-flight jobs become `failed(store_unavailable)`. On reattach the service re-runs integrity checks before reopening.
- **Sleep assertion.** On macOS the service holds an idle-sleep assertion while a unit of work or a download is writing.

**Interface.**

- `ingest(stream, AssetMeta) -> Artifact` verifies a declared hash.
- `path(sha) -> Path` (read-only).
- `with unit_of_work() as uow: uow.put(record); uow.emit(Event)` (atomic).
- `head(project_id, kind)`; `set_head(project_id, kind, rev, expected_rev)` (optimistic concurrency).
- `closure(sha, edges={derived_from, converted_from}) -> ProvenanceGraph`.
- `reserve(bytes_by_volume) -> Reservation | InsufficientSpace(volume, free, needed, margin)`.
- `events(after_seq) -> Iterator[Event]`.
- `recover() -> RecoveryReport`; `reindex() -> ReindexReport`; `fsck() -> FsckReport`; `backup(dest) -> BackupReport`; `restore(src) -> RestoreReport`.

**Hides.** The CAS layout, canonical JSON, fsync/rename crash safety on APFS, NTFS, ext4 and exFAT, migrations, WAL, the sparse-bundle free-space trap, sidecars and reindex, the mount watch and the recovery scan.

**Internal seam.** `StoreVolume` has two adapters: the macOS sparse bundle (`hdiutil`, host-free query) and a plain directory (Linux, Windows, CI). macOS-only code lives only in that adapter and in `scripts/store/`.

### 4.3 Conductor (`studio_control.conductor`): durable jobs

**Responsibility.** The durable job queue and its honest state machine (§9.1). It owns the only WorkerClient.

- **Dispatch.** It submits first, with `job_id` as the idempotency key; the worker admits or refuses the job before any asset moves. It then pushes inputs by hash: `HEAD`, then `PUT` only if the worker lacks the asset, accepted only for that admitted job. It mirrors worker steps into events without inventing percentages. It pulls outputs by hash into the store.
- **Child jobs.** `generate` spawns child `measure` and `adherence` jobs (adherence where the lane allows it), each registered as one file under `conductor/children/`. On a compute-profile switch, undispatched jobs are re-resolved under the new profile with a logged event, and running jobs keep their placement.
- **Residency.** One heavy model per device, enforced with a device semaphore and `/v1/unload`.
- **Cancel** with a deadline.
- **Retries.** Only for retryable errors on free placements. A paid job never auto-retries: a retry needs a new quote and a new approval.
- **Restart reconciliation.** Local workers die with the control service through the SDK's parent-death watchdog, so their in-flight jobs become `failed(worker_lost)`. Remote and burst jobs are re-queried by `job_id`. They resume if the worker still runs them, and otherwise become `failed(worker_lost)`. A lost job is never marked `ready`.
- **Egress record.** For every job that leaves the studio host, it records the asset hashes and the destination.

**Interface.**

- `submit(JobSpec) -> Job`. Calls `Registry.admit` and then `Placement.resolve`. It raises `profile_not_promoted | lane_forbidden | use_forbidden | insufficient_space | worker_refused(code)`, all before any model loads. A paid placement returns the job in `awaiting_approval` with a Quote.
- `on_approved(job_id, approval) -> Job`. Called by Placement after the reservation is written.
- `cancel(job_id) -> Job`.
- `run()`: the asyncio lifecycle owned by `serve`.

State is observed only through store events.

**Hides.** Transport, SSE versus polling per placement, asset transfer, residency, timeouts, retry policy, crash reconciliation and the atomic commit. Every product feature is a JobSpec: transcribe, guide, assemble-audio, generate, measure, adherence, separate, export, probe, and later repaint, isolate, dsp-finish, dsp-edit and offline-render (plus a reserved `tts` kind for the later narration service).

### 4.4 Registry (`studio_control.registry`): what may run, in which lane, at what evidenced status

**Responsibility.**

- **Engine profiles.** Declaration only: tasks, limits, languages, backend, host OS, lanes, components, pins, gates, published claims labelled VENDOR, COMMUNITY or COMPETITOR-RUN, and a `test_only` flag. A **schema rule rejects `MEASURED-LOCAL` inside `claims_published`**. Every `results_local` entry must reference an `evidence_id`.
- **Component license register.** Generated from `evidence-register.json` (§2).
- **Lane policy.** Lanes are individual, llc and research. NC and research-only components are allowed only in individual and research.
- **Use policy.** Reference permissions: a `listening_only` reference is never engine input. The Suno boundary rule (§10) also lives here.
- **Computed status.** `profile_revision = sha256(code commit + weights manifest + env lock or image digest + SDK version)`. Status is a pure fold over EvidenceRecords for `(profile_revision, host_class)`:
  - `declared → installed` needs an install record and a conformance pass at that revision and host class.
  - `installed → smoke-passed` needs the profile's declared smoke gate: a smoke record listing every check the gate declares, each passing, with `owner_not_garbled` answered by an owner-ui verdict on that revision's own smoke candidates.
  - `smoke-passed → benchmarked` needs a preregistered benchmark gate.
  - Any later failing record on the same revision and host class gives `disabled`.
  - A pin change produces a new revision. With no records at that revision it computes to `declared`; it reaches `installed` only after its own install and conformance records.
- **Synthetic evidence** (fixtures generated by NeutralVoice or FakeEngine) may satisfy a smoke gate only where the profile's gate says so. Examples are the transcriber's synthetic-band floor and every `test_only` profile. It **never** satisfies a benchmark gate.
- **Unregistered listening.** Product verdicts are recorded as evidence of kind `listening-unregistered`. They are shown per route ("kept n of m"). They never change status, because promotion to `benchmarked` needs a preregistered set of eval auditions (D-10).
- **System of record.** The store holds evidence. `docs/evidence/` holds hash-checked exports of it (each record with the canonical JSON of the verdicts and preregistrations it cites), and the contract gate runs every reference rule over those exports.

**Interface.**

- `admit(JobSpec, project) -> Admission{profile_revision, actual_params, license_chain, eligible_lanes, obligations} | Refusal[reasons]`. It checks, in order:
  1. The status at the target host class is at least smoke-passed (`test_only` profiles count only when `STUDIO_ENV` is `dev` or `test`).
  2. The task, duration, language and channels are within the profile's limits.
  3. Every component lists the project lane.
  4. Every `derived_from` or `converted_from` input includes the lane in its `eligible_lanes`.
  5. Every input's `allowed_uses` includes the task.
  6. Intent maps to actual parameters (turbo hides CFG, D-18).
  7. Prompt conflicts are flagged (B5).
- `view(audience) -> list[ProfileCard]`. The product view omits anything below smoke-passed, shows unproven routes only as "needs smoke", and never shows a published claim as measured.
- `status(profile_id, host_class) -> Status`.
- `record(EvidenceRecord) -> StatusChange | Rejected`. This is the only write. It rejects records whose gate needs a preregistration hash that is unknown, whose listening gate lacks owner verdicts, that are synthetic but aim at a benchmark gate, or that claim a smoke pass without every declared check or its owner verdict.
- `eligible_lanes(chain) -> set[Lane]`.

**Hides.** The task matrix per checkpoint, 131 component license rows (122 from the evidence register plus 9 supplement rows), lane closure, the use policy, host-class availability and the evidence lifecycle. The UI, Conductor, export and eval never re-implement any of it.

### 4.5 Placement (`studio_control.placement`): where it runs and what it costs

**Responsibility.**

- **Compute.** Hardware detection (§7.1). Tier recommendation, as a pure, golden-tested function. ComputeProfile selection at install and at every session start. Switching at any time.
- **Endpoint resolution.** A profile resolves to an endpoint: a supervised local worker, a registered tailnet worker, or a burst.
- **Worker supervisor.** Spawns each profile's uv env on a random 127.0.0.1 port with a per-spawn token. Runs health checks. Unloads idle workers.
- **Burst broker.** A `BurstProvider` port with a RunPod adapter and a FakeBurstProvider adapter. It covers quotes, approvals, reservations, provisioning, the reaper and settlement (§7.5).
- **BudgetLedger.** Append-only. Month-to-date equals settled actuals plus open reservations at ceiling plus fixed monthly lines, and it must stay ≤ $25.00 (O-09).

**Interface.**

- `detect() -> HardwareSnapshot`.
- `recommend(snapshots) -> Recommendation{tier, reasons, warnings, per_tier_evidence}`.
- `select(session_id, tier | ComputeProfile) -> Session`.
- `resolve(profile_id, session) -> Ready(endpoint) | Paid(Quote) | Unavailable(reason, remedy)`.
- `challenge(quote_id) -> Nonce`; `approve(quote_id, nonce, quote_sha256) -> Approval` (owner act; writes the reservation, then provisions).
- `release(endpoint, outcome) -> Settlement`.
- `reap() -> ReapReport`.

**Hides.** Process supervision, provider APIs, live rates and dated fallbacks, budget arithmetic, the tier presets and per-OS probes.

**Internal seams.** `BurstProvider` (RunPod and Fake) and `HardwareProbe` (real commands and recorded-output fixtures). Each has two adapters, so each is a real seam.

### 4.6 Score (`studio_control.score`; pure, no I/O)

**Responsibility.** Composition semantics.

- **Build a MelodySpec** from transcribed notes, keeping per-note confidence.
- **Edit ops**: move, resize, transpose, split, merge, add, delete, set tempo, meter or key, mark phrase, quantize. Quantize is a reversible layer. Each op set creates a new immutable revision and appends to the **correction log**, which is timestamped from TB1. The log is the correction-effort metric.
- **TimeModel**: 960 PPQ, tempo as integer microseconds per quarter (the SMF unit), meter segments, and one half-up rounding function for tick↔frame. Its TS twin lives in `contracts-ts`, and both pass the same `contracts/fixtures/tempo` vectors.
- **MIDI import and export** via `mido`. The license row must be recorded before adoption.
- **SongForm assembly**: phrases, repeats and instrumental bars become a full-length `assembled` MelodySpec.
- **YuE2 ABC emission** in its strict two-voice dialect: fixed header, one integer tempo, full bars, no tuplets or pickups. Pickups are padded with rests and tuplets are re-quantized. Typed ineligibility covers anything not representable, lyrics in a language other than zh or en, and lengths over about 6 minutes. Lyrics bind by section tags and order, with the syllable plan as a sidecar.
- **SongSpec validation.** For example, an instrumental flag alongside vocal style words, or fields a profile does not support. Each field is recorded as requested, supported and observed (B8).
- **Candidate plan.** Route × profile × seed for a given lane, compute profile and set of eligible choices. The default is the first two eligible routes in the plan-rules order (R1 only without a burst or with Jon's opt-in for that request, then R2-synth, R2-raw, text), adjusted only by route-standing records from concluded preregistered sets. Reasons say "first in the default order (unbenchmarked)", never "best". It is labelled **"unbenchmarked routes"** until a benchmark record exists (completing the benchmark set is post-v1). `render_mode` is `whole_form` by default; `per_section` renders each SongForm section with one profile and seed and stitches them at the markers.
- **ExportManifest assembly** from a closure.

**Interface.**

- `apply(melody, ops) -> melody'`.
- `assemble(melody, form) -> melody`.
- `from_midi(bytes) / from_midi_events(events) -> melody`; `to_midi(melody, form) -> bytes`.
- `to_abc(assembled, song) -> Abc | Ineligible(reasons)`.
- `validate(song, profiles) -> Validation`.
- `plan(song, lane, choices, compute) -> CandidatePlan`.
- `manifest(closure, chain, files) -> ExportManifest`.

**Depth.** This is the largest body of music logic, behind a handful of pure functions. Every case is a golden JSON fixture, re-run against the stdlib reference in `contracts/reference`.

### 4.7 Audition (`studio_control.audition`): blind, level-matched A/B

**Responsibility.**

- **Opening an audition.** An audition opens over 2 or more candidates, from one request or several (a re-roll beside an earlier candidate), **only when every arm is ready** and every arm's audio allows `audition_arm`, so arrival order cannot leak which arm is which. In eval mode a listening-only reference standard can be added as an anchor (honestly labelled: its identity is not blind). A Suno import is **never** an arm (O-08).
- **Labels.** Assigned with a CSPRNG at open time, independent of job order. Only `sha256(mapping ‖ nonce)` is published.
- **Previews and gains.** All arms are previews rendered by `measure` at a common 48 kHz / 24-bit. Gains are **attenuation-only**: louder arms are lowered to the quietest arm's BS.1770-4 integrated loudness (measured with pyloudnorm and labelled as such), with true-peak headroom from AURA's own ≥4× oversampled meter. Residual mismatch must be ≤ 0.1 LU.
- **Serving.** Audio is served by label with identical headers, no filename and no-store caching.
- **What is hidden.** While a blind audition is open, the jobs drawer shows candidates only by ordinal and never by route or profile. Before reveal only an "unplayable" flag shows; every other badge waits for the reveal.
- **Residual leak.** Duration and sonic character are inherent, cannot be hidden, and are acknowledged as a residual leak.
- **Verdicts.** Each verdict is immutable and an owner act: preferred A, B, tie or neither; optional axes; problem intervals; seconds listened per label. Then reveal, which must match the commitment. The keeper is the preferred arm; after a tie either arm may be kept; after neither, none.
- **Neither.** A "neither" verdict re-rolls with new seeds and counts toward candidates per keeper (C9).
- **Eval mode.** About 10% hidden repeat pairs measure listener consistency. A set of eval auditions that falls short of its preregistered quota concludes as `inconclusive` and promotes nothing.

**Interface.**

- `open(request_ids | candidate_ids | brief_id, mode) -> Audition`.
- `audio(audition_id, label) -> Stream`.
- `verdict(audition_id, Verdict) -> Verdict`.
- `reveal(audition_id) -> Reveal{mapping, nonce}`.
- `keep(candidate_id, verdict_id) -> Keeper`.

### 4.8 Worker SDK (`packages/worker-sdk`, `studio_worker`)

**Responsibility.** The worker protocol (§9.2), implemented once.

- It is stdlib-only and runs on Python ≥3.10, so it installs into the Basic Pitch py3.10 env and every torch-pinned env without dependency fights.
- It validates messages against the shared schemas with the bundled subset checker.
- It keeps an asset cache, a crash journal, honest steps, a cancellation token, and a parent-death watchdog for local spawns.
- It hashes outputs and reports their audio metadata.
- **It measures timings and peak memory itself, never trusting engine code.** A speed number is therefore MEASURED-LOCAL by construction.
- It refuses jobs before loading anything. It unloads when idle and runs one job at a time for heavy profiles.
- It has no shell endpoint and never executes or interpolates free-form strings.

**Adapter contract.** An engine author writes four methods:

- `describe() -> [ProfileDescription]`
- `prepare(profile_id, ctx)`
- `run(task, ctx)`, where `ctx` offers `input(role) -> Path`, `step(name, index?, total?)`, `check_cancel()`, `emit(role, path, meta)` and `actual(params)`
- `unload()`

FakeEngine, the analysis worker, the separator, ACE, YuE2 and Basic Pitch are all adapters at this seam.

### 4.9 Analysis worker (`workers/analysis`) and NeutralVoice

**Responsibility.** All DSP and analysis runs here, so the control service stays light and portable. It runs on Python 3.12, CPU only, on every OS. Its tasks are discovered from `workers/analysis/tasks/<task>.py`, and it decodes only through soundfile (WAV and FLAC), never `librosa.load` on a path (whose audioread fallback would shell out to whatever ffmpeg is on PATH). Its host class on the Mac is `cpu/m5pro`, so its profiles need install, conformance and smoke records there, not only on Linux CI. Tasks:

- **`transcribe`.** v0 is pYIN F0 (librosa, ISC, no weights) plus AURA's own HMM note segmentation via `librosa.sequence.viterbi`. It is LLC-clean.
- **`measure`.** Checks that the file decodes, duration, non-silence and clipping. Measures integrated loudness with pyloudnorm (labelled "BS.1770-4 (pyloudnorm)" until the -4 versus -5 diff ticket closes, X-47), and true peak with AURA's own ≥4× oversampled meter. Writes the common 48 kHz / 24-bit audition preview.
- **`guide` (NeutralVoice).** A deterministic, AURA-licensed additive voice with formants. Vowel, vibrato and drift are parameters. It renders an assembled MelodySpec.
- **`assemble-audio`.** Lays R2-raw hum slices out per the SongForm.
- **`adherence`.** The separator worker's vocal goes through SwiftF0, with pYIN as a cross-check, then DTW. Outputs are median cents error, octave-error rate, onset F1 and contour correlation, judged against thresholds committed in a gate record before any real adherence evidence. It appears on real candidates only while the `adherence.real-separator.<os>` capability is smoke-passed (the golden under a NeutralVoice bed and an ACE bed with reverb and doubling, through the real separator); a fake-separate validation never unlocks it.
- **`export`.** A bit-exact native copy. A 48k/24-bit deliverable with TPDF dither seeded from the export id (so it is deterministic), only when the native rate differs. MIDI and specs come from Score. The task then re-decodes and re-hashes everything for verification.
- **`probe`.** Reads the Metal `recommendedMaxWorkingSetSize` via MLX on darwin-arm64 only.

**NeutralVoice is one synth doing four jobs:**

1. The R2-synth conditioning input for ACE cover.
2. Ground-truth fixtures for transcription and adherence tests (drift ±30 cents, onset jitter, vibrato, breath noise, rubato, and a line mixed under an accompaniment bed).
3. FakeEngine's sound.
4. The fake-mic input for Playwright.

It also replaces the UNVERIFIED MIDI synth and soundfont (§4.9 of RECONCILIATION) on the v1-core path.

### 4.10 Engine adapters

**FakeEngine.**

- Profiles: `fake-route-a`, `fake-route-b`, `fake-burst`, `fake-nc` (declares an NC component, lanes individual and research) and `fake-separate` (returns the exact vocal it embedded), plus the pre-seeded `fake-repaint`, `fake-isolate`, `fake-reference-timbre`, `fake-tts`, `fake-asr` and `fake-diagnostic`.
- All are `test_only`.
- Output: the NeutralVoice guide plus a pad derived from the key, seeded and deterministic within a platform.
- Fault knobs, only when `STUDIO_ENV=test`: `driftCents`, `octaveErrorRate`, `onsetJitterMs`, `clipDb`, `silence`, `failAtStep`, `crashAt`, `wrongOutputHash`, `slowLoadMs`, `ignoreCancel`, `refuse`.
- Outputs carry `synthetic_test=true`, which is shown on screen ("Synthetic test output") and in the manifest.

**ACE.**

- Profiles: `ace-2b-turbo-mlx` (draft) and `ace-2b-sft-mlx` (render), then `ace-xl-sft-mlx` after its own smoke run and the diffusers bf16 loader check, and `ace-2b-base-mlx`, the only profile with `reference_timbre` (O-07's global style reference), after its own smoke run. CUDA twins exist for tiers 1–3.
- Tasks: `cover` (R2-raw, R2-synth; sweeps `audio_cover_strength` 0.8–1.0 and `cover_noise_strength`) and `text_to_song`, then `repaint` in P5.
- Allowed in every lane.

**YuE2.**

- Profile `yue2-3b-score`, task `score_to_song` (`abc=`, `cot='melody'|'full'`, lyrics by section tags).
- Lyrics in English or Chinese only. Length ≤ about 6 minutes.
- Lanes: individual and research only. The worker refuses `llc` before loading.

**Basic Pitch.** A py3.10 env, used only as a hum-benchmark challenger; individual and research until its training-data provenance review.

**Weights sources.** A profile's weights come from a Hugging Face revision, a pinned URL with sha256 (Demucs's torch.hub checkpoint) or a file inside a pinned package (SwiftF0's and Basic Pitch's bundled models); every source downloads only after Jon's license acceptance (`license-acceptance/1`).

### 4.11 Web app (`apps/web`) and StudioEngine

**Web app.** Listening-first and thin. Screens:

- **Session**: snapshot, recommended tier with reasons, all four tiers, and per-tier evidence.
- **Capture**: AudioWorklet recorder with a level meter, MIDI file drop, and Web MIDI live input.
- **Melody**: a piano roll over revisions, with phrase marks and an oscillator preview. It uses the TimeModel TS twin so a drag does not need a round trip.
- **Song**: lyrics, SongForm and style, with conflicts shown inline.
- **Generate**: the plan with reasons, plus the approval card, which shows the provider, GPU class, live rate and its timestamp, the ceiling, month-to-date, the cap, and exactly which assets leave the machine.
- **Jobs drawer**, driven by SSE.
- **Audition**: synced A/B with an instant switch and short crossfade, loop region and keyboard control, with no label leak in the DOM.
- **Reveal / Keeper**, **Export**, and **Registry & Budget** (published and measured figures in separate columns).

The footer shows `hello@islanddevcrew.com` as text. The app consumes only the generated typed client. Each screen's container ticket declares its own named slots; filler tickets register into them.

**StudioEngine (P5).** AudioWorklet playback with a SharedArrayBuffer ring per track, fed by a decode Web Worker that reads blob byte ranges. No inference, disk or network work runs on the render thread. Offline export never uses it. If the per-OS gates fail, only this module is replaced, by a CPAL native engine behind the same timeline contract (D-13 reverse-if).

---

## 5. Contracts

Every contract is a JSON Schema 2020-12 record with `kind` and `schemaVersion` (the contracts author writes them).

- **Minor versions are additive.** A major version is upcast on read and stored objects are never rewritten.
- **Frozen legacy fixtures** must load at HEAD.
- **Integers only in hashed records.** Every other quantity is a decimal string.

| Contract | One-line purpose |
|---|---|
| `product/1` | The single rename constant (O-10) and the public contact text. |
| `store/1` (`store.json`) | Store identity, layout version, band size, last clean detach. A future reader opens a store from this file plus `docs/FORMAT.md`. |
| `melody-spec/1` | The owned, editable melody from a hum, singing, MIDI file or live MIDI: 960 PPQ, an integer µs-per-quarter tempo map, meter, key, notes with confidence and origin, phrases, transcription method with the transcriber's eligible lanes and license chain, `content_sha256`. Revisions are immutable, and every revision inherits the transcriber's lanes. `spec_kind: assembled` is the full-song guide timeline. |
| `correction-log/1` | Timestamped piano-roll ops per revision chain, used as the correction-effort metric. |
| `song-spec/1` (with SongForm) | What Jon asked for: approved lyrics (kept separate from any ASR transcript) with BCP-47 language, style and excludes, vocal mode, form sections (vocal or instrumental, phrase refs, bars, repeats), duration target, references and candidate count (2). Each field records requested, supported and observed. |
| `project/1` | The versioned container: kind (`song`, or `narration`, reserved), operator lane (default `individual`), heads, requests, keepers, exports. |
| `artifact/1` + `provenance-sidecar/1` | Every stored blob with full provenance. Origin enum: `generated_mix`, `separated_source`, `regenerated_part`, `new_part`, `human_recording`, `rendered_guide`, `rendered_midi`, `tts_render`, `conversion`, `imported_mix`, `analysis`, `preview`. Typed parent edges (`derived_from`, `converted_from`, `analyzed_by`). Producing job, profile revision, weights, code commit, env lock or image digest, intent and actual params, seed, host and host class, compute profile, timings, operator lane, `eligible_lanes`, license chain, `allowed_uses`, retention class, `synthetic_test`. |
| `job/1` + `event/1` | The durable unit of work (the id is the idempotency key) with honest states, steps, placement, outputs, typed error, cost and egress, plus the resumable event stream. |
| `generation-request/1` + `candidate/1` | One request yields 2 candidates. Each records route, profile revision, seed and placement, and is never hidden. Declined routes carry reasons. Measures and badges are attached. |
| `engine-profile/1` | Declaration only (D-01): tasks, limits, languages, backend, host OS, allowed lanes, components, pins, gates (`smoke`, `benchmark`), `test_only`, `claims_published` (labelled; MEASURED-LOCAL forbidden) and `results_local` (each with an `evidence_id`). |
| `capability/1` | A non-engine capability (`studio.playback`, `capture.mic`, `capture.midi-live`, `adherence.real-separator`) gated per OS by evidence, the same way as profiles, each check with its measurement definition. |
| `component/1` | One license-register row: code, weights and output terms, obligations, allowed lanes, process-boundary flag, verification status. |
| `lane-policy/1` | Lane semantics as data: forbidden classes per lane and the propagation rule (§10). |
| `hardware-snapshot/1` | Detected facts per host, with the raw command outputs kept. |
| `compute-profile/1` + `session/1` | The chosen tier preset and its placements per profile, and the session record that pins the choice and logs switches (O-02). |
| `quote/1` + `approval/1` | A priced, hashed job list (`quote_sha256`) with the live rate and its timestamp, the ceiling and the egress list. The approval is single-use, owner-only, nonce-bound and expires in 15 minutes. |
| `burst-run/1` + `ledger-entry/1` | Every paid run is logged against the cap before it starts. The ledger is append-only: reserve, settle, release, overrun, fixed line, reconcile adjustment, cap change, overrun acknowledged. |
| `reference/1` | Jon's reference standards and style references, each with a permission record (O-05, O-08). A `listening_only` reference is never engine input. |
| `import-terms/1` + `risk-acceptance/1` + `license-acceptance/1` | The source service, attested terms, contained studio exports and detected marks of an `imported_mix` (an owner act); Jon's signed acceptance of a named risk (the Suno boundary, §10); his acceptance of a component's license documents before any weights download. |
| `audition/1` + `verdict/1` + `reveal/1` | Blind level-matched comparison, committed before reveal. This is the acceptance gate (D-05, D-10). |
| `eval-brief/1` + `prereg/1` | The smoke-12 and full-48 briefs, mapped to O-05's four categories, and a preregistration hashed before any run. |
| `evidence/1` | The only way a status changes or a gate passes. It holds the check, subject, profile revision, host class, result, measured values labelled MEASURED-LOCAL, the per-check results its gate declares (with the owner verdict that answered a listening check), a synthetic flag, hashed attachments and a preregistration hash where needed. |
| `export-manifest/1` | A self-describing export bundle: files with hashes, roles, rates and frames; human contributions; model and license chain; lane; eligible lanes; AI-disclosure flag and reasons; `converted_vocal: false`; imported-source terms; a loudness report naming its standard and meter version; closure hash; release blockers and whether it is release-clear (never for research exports); `synthetic_test`; verification time. |
| `edit-operation/1` (v1-studio) | A scoped generative edit that stays a proposal until accepted, with the byte-identical preservation report (D-17). |
| `timeline/1` (v1-studio) | Tracks, clips in project frames, artifact source frames at native rate, MIDI clips in ticks, markers. |
| Worker protocol (`worker-describe/1`, `task-request/1`, `task-status/1`, `refusal/1`) | The process-boundary contract every worker speaks, locally, over the tailnet and on a pod. |

---

## 6. Test seams

There are two behaviour seams, and both are as high as they can be. A data gate and the real-world evidence gates complete them. No test mocks an internal collaborator. Fakes exist only at real boundaries.

### 6.1 Studio API: the one product seam (StudioHarness, pytest)

**What it tests.** Every product behaviour, as Jon would observe it:

- **Compute.** Detect and recommend from golden snapshots. Select and switch: queued jobs are re-planned, and jobs awaiting approval are re-quoted, which invalidates the old approval.
- **Store.** Preflight refusal on every volume, mount loss, the LOCK, recovery, reindex (delete the DB, reindex, diff), and backup and restore.
- **Capture.** Ingest and hash verification.
- **Melody.**
  - Transcription produces a MelodySpec.
  - Edit ops land, a stale revision gets 409, and the correction log grows.
  - MIDI round trip.
  - SongForm assembly.
  - ABC emission, with typed ineligibility.
  - The guide renders.
  - SongSpec conflicts are flagged.
- **Plans.** Candidate plans per lane and tier.
- **Registry.**
  - `profile_not_promoted` before any load.
  - A pin change resets status.
  - Promotion without evidence is rejected.
  - Synthetic evidence never reaches `benchmarked`.
- **Jobs.**
  - Honest state sequences, SSE resume and cancel.
  - Restart reconciliation: SIGKILL during `generating` gives `failed(worker_lost)` with no partial artifact visible.
- **Paid gate** (FakeBurstProvider):
  - An over-cap quote is refused.
  - The reservation event precedes the provision event.
  - An automation token gets 403 on approve.
  - A reused or expired nonce is refused.
  - A changed job list needs a new quote.
  - The orphan reaper runs, and a run without billing data settles at ceiling.
  - An overrun blocks new leases.
  - There is no automatic paid retry.
- **Audition.**
  - No label, profile, route, seed or file name in any response before the verdict.
  - Common preview rate, attenuation-only gains, match ≤ 0.1 LU.
  - The reveal matches the commitment.
  - An automation-scope verdict gets 403.
- **Keeper and export.** The bundle re-decodes, its hashes match a schema-valid manifest, and the export is deterministic.
- **Lanes** (§10). Each enforcement point has a negative test.
- **Suno boundary.** An imported Suno mix is refused as cover input and as an audition arm.

**Fakes and fixtures.**

- The real control app on an ephemeral port.
- A temp store root: a plain directory on Linux and Windows, and on macOS a 2 GB temp APFS sparse bundle for the preflight and mount cases.
- A registry overlay enabling the `fake-*` profiles.
- **FakeEngine** and the **analysis worker** as real subprocesses, launched through the real supervisor.
- **FakeBurstProvider**: in-process at the `BurstProvider` port, with programmable rates, provisioning latency, billing, lost pods and terminate failures.
- **HardwareProbe fixtures**: recorded `sysctl`, `system_profiler`, `nvidia-smi` and `wsl.exe` output for an M5 Pro 48 GB, a 3090, a 4090, a 5090, a 16 GB card and a no-GPU host.
- An injectable clock.
- NeutralVoice hum fixtures generated at test time from golden MelodySpecs, so ground truth is known. They are never committed.
- Golden JSON from `contracts/fixtures`.

Tests wait on event `seq`, never on sleeps. The suite runs on Linux, macOS and Windows for every PR (since PR #12), integration and nightly, with a PR budget of 10 minutes or less.

**Browser entry to the same seam (Playwright, not a new seam).** It covers:

- The UI drives the API correctly.
- No blind label or hash appears in the DOM or in network responses.
- The approval card copy is correct, as are "Synthetic test output" and "ACE-only: burst declined".
- Accessibility audit and keyboard-only operation.

Chromium runs with `--use-fake-device-for-media-stream --use-file-for-fake-audio-capture=<NeutralVoice hum>.wav`. It runs headless on Linux per PR, and on macOS Chromium nightly with screenshots attached as evidence.

### 6.2 Worker protocol conformance (the process-boundary seam)

**What it tests.**

- `describe` is schema-valid and matches the registry declaration.
- **Refuse-before-load** for an unsupported task, a forbidden lane, an over-limit duration, an unsupported language, missing weights and insufficient memory, with no `loading` step and no model import.
- A hash mismatch is rejected, and submit is idempotent on `job_id`.
- Steps are honest (an index or total appears only when declared).
- Cancel takes effect within 5 s.
- Outputs hash-match and carry complete provenance (weights manifest, env lock or image digest, commit, seed, `params_actual`).
- A restart reports the job lost, never `ready`.
- One heavy model is resident, and `/v1/unload` frees it.
- Auth is required, and every undeclared route returns 404.

**Mutant workers the suite must fail** (CI asserts each failure, which proves the suite is not vacuous):

1. Loads before the refuse check.
2. Misdeclares the sample rate.
3. Returns a wrong output hash.
4. Ignores cancel.
5. Fabricates a percentage.
6. Goes silent on heartbeat or health.
7. Answers an undeclared route (a shell surface).

**Where it runs.**

- FakeEngine and analysis on every PR.
- ACE on the self-hosted M5 Pro runner, producing an EvidenceRecord.
- YuE2 on a pod, only through the `--paid` marker, which goes through the real quote → UI approval → reservation flow.
- Request and response transcripts are golden fixtures.

### 6.3 Contract gate (data, not behaviour)

`scripts/spec/validate.py` checks the following:

- Schemas use only keywords the bundled checker implements.
- Every fixture and registry file validates.
- The stdlib reference re-run matches expected outputs exactly: tick↔frame, SongForm, ABC, `recommend()`, ledger arithmetic, lane closure, audition gains.
- Hand-written assertions hold, which guards against tautological fixtures.
- Seeded-bad fixtures fail.
- `components.v1.json` regenerates byte-identically.
- Every `legacy/` fixture loads.
- `claims_published` never contains MEASURED-LOCAL.

The TS twin runs the tempo vectors in vitest.

### 6.4 Evidence gates (real checks, not test seams)

These are what no fake can show:

- ACE, YuE2 (on its burst host class) and the analysis worker (on `cpu/m5pro`) install, conformance and smoke on real host classes, with cold and warm timings.
- Jon's recorded "not garbled" checks.
- Store throughput, IOPS and band size on Backup Plus.
- Jon's blind verdicts.
- The per-OS Chrome `playbackStats` gate (8 tracks × 30 min).
- The ledger reconciled against provider billing.
- The hum benchmark on Jon's hums.

Each produces an EvidenceRecord with hashed attachments. Results are labelled MEASURED-LOCAL. Synthetic results are recorded but never promote anything to `benchmarked`.

---

## 7. Compute profiles

### 7.1 Detection

`studioctl doctor` and `GET /api/v1/compute/detect` build a HardwareSnapshot per reachable host and keep the raw command output.

- **macOS.** `sysctl -n hw.memsize machdep.cpu.brand_string`, `system_profiler SPHardwareDataType SPDisplaysDataType -json`, and the Metal `recommendedMaxWorkingSetSize` through the analysis worker's `probe` task (MLX on darwin-arm64; a verifier read 37.44 GiB on this M5 Pro, MEASURED-LOCAL).
- **Linux, Windows and WSL2.** `nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader`, total RAM, and `/proc/version` (WSL2 detection). On Windows also `wsl.exe -l -v` and the `.wslconfig` memory.
- **Remote hosts** report the same facts in `/v1/describe`.
- **Store facts.** APFS free, exFAT host free, sequential MB/s and random 4K IOPS. The IOPS figure tells an HDD from an SSD, because `diskutil` says "Info not available".
- **Stray caches.** `doctor` also audits stray caches on the internal disk (`~/.cache/huggingface`, `~/.cache/uv`, `~/Library/Caches/pnpm`, `ms-playwright`) and reports their sizes. The owner decides what to delete.

An unreachable host has no snapshot and so cannot qualify for a tier. Linux and Windows are unknown today (Q1).

### 7.2 Recommendation (pure, golden-tested)

`recommend(snapshots)` over `compute-tiers.v1.json` returns:

| Hardware | Tier |
|---|---|
| Apple Silicon | 4 |
| NVIDIA ≥23.5 GiB, compute capability ≥8.9 (4090/5090 class) | 1 |
| NVIDIA ≥23.5 GiB, compute capability 8.0–8.6 (3090/A5000) | 2 |
| NVIDIA 11.5–23.5 GiB, compute capability ≥8.0 | 3 (O-02 names 12–16 GB; 16–23.5 GiB cards are a deliberate extension, with a warning, pending Jon's confirmation) |
| Any NVIDIA card below compute capability 8.0, or no accelerator | burst only (tier-4 placements for CUDA profiles; MLX profiles unavailable off the Mac), with a warning |

**Warnings:**

- Host RAM under 24 GiB for YuE2.
- Driver below 570.26 (Linux) or 570.65 (Windows) for cu128.
- A Blackwell card paired with cu126.
- WSL2 memory under 24 GiB.

For **each tier** it lists which profiles have evidence on a matching `host_class` and marks the rest "needs smoke". A 16 GB card never gets YuE2 until its own smoke record exists (A4). It never qualifies a tier from hardware it has not probed. **This Mac recommends tier 4.**

### 7.3 Tier presets (`compute-tiers.v1.json`)

| Tier | ACE | YuE2 (individual lane) | Burst | Analysis and separation |
|---|---|---|---|---|
| 1 | `ace-xl-sft-cuda` local | local | overflow, per-run approval | studio host; separation on the Mac only until a CUDA separator profile exists |
| 2 | `ace-2b-sft-cuda`; XL with offload after a smoke run | local | overflow | studio host |
| 3 | `ace-2b-sft-cuda`; XL only on 16 GB with offload, after a smoke run | local only after a smoke run on that card; otherwise burst | fallback | studio host |
| 4 | `ace-*-mlx` on the Mac | burst | per-run approval | Mac |

Metal ports of YuE2 or HeartMuLa become placeable only after a parity check plus the smoke gate (D-03 reverse-if). They are then simply another host class. `compute-tiers.v1.json` uses the glossary's placement terms (`local`, `worker_host`, `burst`), with any smoke precondition in `condition`; `ace-2b-base-mlx` is placed when stems, lego, complete or reference timbre are needed.

### 7.4 Selection and switching

- **At install,** `studioctl setup` writes the default ComputeProfile from the recommendation.
- **At every session start** (each `serve` start, or the first UI load after an idle gap), the Session screen shows the snapshot, any change since last time (for example "Linux box now reachable"), the recommendation with its reasons, warnings and per-tier evidence, and all four tiers. One click keeps the profile. Jon may pick any tier, host or platform (O-02, O-11). A tier the hardware cannot satisfy is allowed: its profiles resolve to `burst` or `Unavailable(reason, remedy)`, and the plan says so **before** submit. Nothing is ever substituted silently.
- **Switching** (`PATCH /sessions/{id}`) works at any time and is logged:
  - Jobs not yet dispatched are re-planned.
  - Jobs awaiting approval are re-quoted, which invalidates the old approval.
  - Running jobs finish where they are unless Jon cancels them.
  - Every Job and Artifact records its compute profile, placement and host class.
  - Projects never change.

### 7.5 Burst provisioning: the $25/month cap and per-run approval (O-09)

1. **Quote.**
   - Jobs whose placement is `burst` get a Quote. Its basis is the **live** provider rate fetched at quote time, with its timestamp. A dated snapshot from `price-snapshots/` is used only as a fallback labelled with its date.
   - `max_minutes` = boot + weights download + Σ job estimates + teardown margin. Each estimate is measured history on that GPU class where it exists, labelled MEASURED-LOCAL. Otherwise it is the VENDOR figure × 3, labelled "unmeasured".
   - **Ceiling** = `max_minutes` × the highest rate in the GPU-class fallback list, plus fixed lines.
   - The quote also lists, by hash, exactly which assets leave the Mac (for R1: the ABC, the lyrics plan and the job params; never Suno audio, never reference standards). It includes the lane check result.
   - `quote_sha256` covers all of the above.
   - Pod rates are **UNVERIFIED** today: the research verified only serverless rates. As an example, a 20-minute ceiling at the serverless 4090 PRO's $1.10/h is about $0.37 (INFERRED, illustrative only). The hard maximum is always computed by the formula above, never hard-coded; until the YuE2 smoke record supplies measured boot, download and run times it is labelled INFERRED. The GPU-class fallback list names only GPU classes with a smoke-passed record for that profile revision.
2. **Cap check.**
   - Month-to-date (UTC calendar month) = settled actuals + open reservations at ceiling + fixed monthly lines + reconcile adjustments.
   - If month-to-date plus the ceiling would exceed $25.00, the quote is refused, with no override in the flow.
   - Raising the cap is an owner act in Settings and is recorded.
3. **Approval** (owner act, UI only). The dialog fetches a challenge nonce and shows:
   - provider, GPU class, rate and timestamp
   - the job list
   - the ceiling, month-to-date, the cap and the remainder
   - the egress list

   Jon's click posts the nonce and `quote_sha256`. The approval is single-use, bound to the quote hash, and expires 15 minutes after the quote. The CLI, the eval harness, `--paid` conformance and agent tokens can quote but never approve. Any change to the job list needs a new quote and a new yes. One approval covers one run (one request's burst jobs).
4. **Reservation before provisioning.** The approval writes a ledger `reserve` entry at ceiling (fsynced, timestamped) in the same transaction as the cap check. Provisioning starts only after that.
5. **Provision.**
   - A RunPod pod starts from the pinned yue2 image digest (private GHCR; the pull credential is stored at the provider, never in AURA's client).
   - Tags: `studio-burst` plus the run id.
   - It gets a one-run 256-bit bearer token (only its hash is stored locally), the hard maximum duration, an in-image `shutdown -h` deadline, and enough container disk for weights, outputs and a margin.
   - Weights download at boot from HF at the pinned revision under the recorded license acceptance.
   - The worker runs a conformance ping before the first job.
6. **Run.** The Conductor polls the pod through the HTTPS proxy with short status requests rather than long-lived streams. Whether the proxy holds long connections is UNVERIFIED, so the design does not depend on it.
7. **Settle.**
   - On a terminal state or at the hard maximum, the pod is terminated, and termination is confirmed through the provider API.
   - Settlement uses the provider-reported cost. If that is unavailable, it settles **at the ceiling**, labelled `settled_at_ceiling`. Monthly reconciliation against the invoice may lower only an amount settled at the ceiling. Any invoice charge the ledger never saw (a machine the reaper missed, stopped-machine storage, a revised cost, network-volume fees) becomes a `reconcile_adjustment` entry that counts toward the cap and blocks new leases until Jon acknowledges it (an owner act).
   - An actual cost above the reservation writes an `overrun` entry and blocks new leases until Jon acknowledges it.
8. **Reaper** at startup and every 5 minutes. It terminates any tagged pod without an open run, and any open run past its hard maximum, then settles it.

**Backstops.**

- The in-image deadline. Whether an in-container shutdown stops RunPod billing is **UNVERIFIED** (spike ticket). Until verified it is a second lock, not a guarantee.
- A provider-side spend limit that Jon sets by hand. Its exact mechanism on pods is UNVERIFIED.
- Monthly reconciliation against the invoice, upward included.
- A prepaid balance kept at or below the remaining cap, with auto top-up off: the external backstop.
- The RunPod API key lives in a presence-gated keychain item that the self-hosted runner's dedicated user cannot read, and hardware workflows run only by `workflow_dispatch` or from protected branches.

Every step is exercised for $0 by FakeBurstProvider in CI.

### 7.6 Burst weights and cold start

v1 downloads YuE2 weights (7.30 GB + 0.53 GB VAE, VENDOR sizes) per lease onto pod disk, and the quote includes that time.

A network volume holding the HF cache is adopted only when measured boot-plus-download time across settled runs shows it is cheaper. Its GB-month fee would then be a fixed ledger line, and its region lock would be recorded as a GPU-availability risk. Both the fee and the lock are UNVERIFIED today.

The provider is RunPod secure cloud first. A Vast adapter behind the same port is considered only if ledger evidence shows the saving matters, weighed against marketplace-host trust for unreleased material.

---

## 8. Storage

### 8.1 The volume

`studioctl setup` creates the volume once. It prints any command that needs admin rights for Jon to run, and never runs `sudo` itself.

```
hdiutil create -type SPARSEBUNDLE -fs APFS -volname STUDIO -size 900g \
  -imagekey sparse-band-size=<measured> "/Volumes/Backup Plus/STUDIO.sparsebundle"
hdiutil attach -nobrowse -owners on -mountpoint /Volumes/STUDIO "/Volumes/Backup Plus/STUDIO.sparsebundle"
```

- **Size.** 900g is a logical cap (owner may change it). It leaves room for Jon's other backups on the 1.1 TiB-free drive. The host's free space is the real limit, and `hdiutil resize` can raise the cap later.
- **Band size.** P0 measures the default 8 MiB (16384 sectors) against 64 MiB (131072 sectors) on this HDD: attach time, sequential read and random 4K read. Fewer, larger bands are kinder to exFAT directories. Until then the choice is UNVERIFIED.
- **`-owners on`** keeps POSIX permissions, so uv envs keep their exec bits. APFS restores symlinks (the HF cache leaves its degraded mode), hardlinks and `clonefile` (O-03). Setup probes all four and records the result.
- **Spotlight.** Setup writes `.metadata_never_index` at the root. Whether current macOS honours it is UNVERIFIED, so setup also prints `mdutil -i off /Volumes/STUDIO` as an owner action.
- **Time Machine.** A sticky `tmutil addexclusion` (no root needed). The real backup of irreplaceable data is `studioctl store backup` (§8.6).
- **Unclean-detach marker.** The next attach runs `diskutil verifyVolume`.
- **Compaction.** Deleting inside the bundle frees no host space until `studioctl store compact` runs offline (`hdiutil compact`). Preflight reports reclaimable bands separately.
- **Volume name.** It is neutral (`STUDIO`), so renaming AURA touches no path. Doctor checks for a mount-point collision.

### 8.2 Layout

```
/Volumes/STUDIO/
  store.json                 store_id, layout_version, band size, created_at, last_clean_detach
  LOCK                       single-writer lock held by `studioctl serve`
  projects/                  STUDIO_STORE_ROOT (the project store by default, O-03; configurable)
    db/studio.sqlite         WAL (+ -wal/-shm), synchronous=FULL, fullfsync=ON
    db/snapshots/            nightly and post-keeper `.backup` copies
    cas/sha256/ab/cd/<hex>             immutable blobs (0444)
    cas/sha256/ab/cd/<hex>.prov.json   provenance sidecar (artifact truth; DB rows are rebuildable from these)
    records/sha256/ab/cd/<hex>.json    canonical JSON domain records (MelodySpec/SongSpec revisions, verdicts,
                                       keepers, manifests, evidence, permissions, risk acceptances)
    tmp/                     same-volume staging for temp-then-rename
    quarantine/
    exports/<project_id>/<export_id>/  APFS clones of CAS blobs (`clonefile`, zero copy) + manifest
  models/
    hf/                      HF_HOME (hub; HF_XET_CACHE beneath it)
    other/                   non-HF downloads (SwiftF0 ONNX, Basic Pitch) with pin files {url, sha256}
    licenses/<component>.json  license-acceptance/1 records: each document's url, revision and sha256, the weights
                               source, lanes, obligations, any release permission, accepted_at (owner act); voided when a
                               document changes
    manifests/<profile>/<revision>.json   pinned file list + sha256 (feeds profile_revision)
  envs/
    python/                  UV_PYTHON_INSTALL_DIR
    uv-cache/                UV_CACHE_DIR (same volume as the envs, so uv clones instead of copying)
    workers/<env>/<lock_sha>/  UV_PROJECT_ENVIRONMENT per engine worker, keyed by lock hash, shared by worktrees
  caches/
    pnpm-store/  pip/  torch/  mlx/  xdg/  ms-playwright/
  worktrees/<ticket>/        git worktrees for ticket agents (node_modules and .venv inside)
  scratch/<job_id>/          worker working dirs and TMPDIR; deleted when the job ends (class: reproducible)
  logs/
  evidence/                  hashed captures awaiting commit to docs/evidence/
```

The internal disk holds only the OS, the browser, the canonical git checkout (docs and coordination, no dependencies installed), `~/.config/studio/` (a few KB: volume path, roots, automation token), and keychain entries.

### 8.3 The one-volume rule

Anything that hardlinks or clones lives on the same volume as its counterpart: the uv cache and envs, the pnpm store and `node_modules`, the CAS and exports. Otherwise each silently degrades to full copies.

### 8.4 Environment

`studioctl env` writes one env file. Every `studioctl` command and every worker spawn sources it, and the control service also sets these variables per spawn:

- `HF_HOME`, `HF_XET_CACHE`
- `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR`, `UV_PROJECT_ENVIRONMENT`
- `PIP_CACHE_DIR`, `TORCH_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`
- `UV_TOOL_DIR`, `UV_TOOL_BIN_DIR`, `npm_config_cache`, `COREPACK_HOME`
- `TMPDIR`
- `PLAYWRIGHT_BROWSERS_PATH`
- an MLX cache limit for demucs-mlx
- the pnpm store: `storeDir` and `cacheDir` in `pnpm-workspace.yaml` from `${STUDIO_ROOT}` (pnpm 11 ignores `store-dir` in `.npmrc` and `npm_config_store_dir`; MEASURED-LOCAL)

The env file exports nothing and returns non-zero when the volume is not mounted, so a missing STUDIO never silently falls back to `/tmp` on the internal disk. Ticket worktrees are added from a bare clone at `$STUDIO_ROOT/git/aura.git`, so their git objects never land in the canonical checkout's `.git`.

**HDD consequence** (INFERRED from the measured ~125 MB/s): a cold ACE turbo load (about 6.34 GB) takes roughly 50 s, and an XL bf16 load (about 11 GB) roughly 90 s. Imports and installs from envs on a spinning disk are slower still. So workers keep one heavy model resident and report cold and warm times separately (D-23).

The measurement note suggests putting small hot envs on the internal SSD. O-03 binds the envs to the bundle, and internal free space reads as low as 2 GiB (the range is timestamped in `docs/DEVELOPING.md`), so the envs stay on the bundle. The roots are configurable: if Jon frees internal space, `studioctl setup --envs-root` moves the envs **and** the uv cache together, keeping the one-volume rule.

### 8.5 Disk preflight

Every download, install, env build, job and export declares its estimated bytes per volume before it starts.

- **The STUDIO volume.** Effective free = min(APFS free inside the bundle, exFAT host free) − band overhead. Refused if effective free − estimate < **10 GiB** (D-15, configurable). The refusal names the volume, the free figure, the amount needed and the margin.
- **Internal volume.** No planned writes are accepted. Heavy jobs are **blocked** while internal free space is under **2 GiB**, because swap lives there.
- **Remote hosts.** A worker host's root is checked from the free space it reports in `describe`. A pod's container disk is sized at quote time.
- **Estimates.** Selective `allow_patterns` downloads with a size dry run: ACE turbo + encoder + VAE ≈ 6.34 GB, LM 1.7B ≈ 3.76 GB, XL only as diffusers bf16 (≈ 11.1–11.5 GB) once loader support is verified, YuE2 7.30 + 0.53 GB on CUDA hosts and pods only. Outputs are budgeted at 92,160,000 bytes (about 87.9 MiB) per 4-minute stereo float32 stem.
- **Runtime watch.** A running job fails honestly with `failed(disk_low)` if free space falls below half the margin.
- **Integrity.** Install verifies downloaded bytes against the manifest and every LFS sha256.

### 8.6 Retention classes, backup and restore

| Class | Contents | Backup |
|---|---|---|
| `irreplaceable` | Human recordings (hums, sung lines), imported MIDI and mixes, MelodySpec and SongSpec revisions with correction logs, verdicts, keepers and the audio closure of every keeper, reference audio with permission records, risk acceptances, evidence records, export manifests, and the latest DB snapshot | Mirrored |
| `derived` | Non-keeper candidates and analysis outputs: kept in the store, not reproducible bit-for-bit, not essential | Mirrored only with `--include-derived` |
| `reproducible` | Weights, envs, caches, previews, scratch, and export renders (deterministic from the closure) | Never backed up |

`studioctl store backup <dest>` copies the irreplaceable closure in the same CAS layout (blobs, sidecars, records and a DB snapshot) to a second device, then re-hashes every file at the destination. The destination is owner-pending. `restore` rebuilds a fresh root, and `fsck` re-hashes it. A weekly reminder prompts `fsck` and a backup. Backup Plus is a single physical HDD, so the second copy is the real durability guarantee. Neither the sparse bundle nor APFS provides one.

### 8.7 Other operating systems

On Windows and Linux the `StoreVolume` adapter is a plain directory on a native filesystem (`STUDIO_ROOT`) with the same layout, and preflight checks that one volume. The store format uses no symlinks or xattrs and keeps paths short (lowercase hex), so it works anywhere with atomic rename and fsync. In v1, projects move between hosts only through `backup` and `restore`.

---

## 9. Job lifecycle and worker protocol

### 9.1 Job lifecycle

```
queued ──▶ awaiting_approval ──(owner approval + reservation)──▶ preparing
   │            │ (quote expired / declined / re-quoted on tier switch)
   └────────────┴──────────────────────────────────────────────▶ preparing ──▶ loading ──▶ generating ──▶ analyzing ──▶ ready
                                                                     any state ──▶ failed{code, retryable} | cancelled
```

- **States.**
  - `preparing`: the job is submitted and admitted by the worker, then its assets are pushed by hash.
  - `loading`: the model is loading. Cold versus warm is recorded.
  - `generating`: the engine is running.
  - `analyzing`: the child `measure` and, where allowed, `adherence` jobs are running.
  - `ready`: outputs are committed atomically.

  Steps carry `index/total` only when the engine reports real counters. No percentages are invented.
- **Submit order.** `Registry.admit` → `ProjectStore.reserve` (preflight) → `Placement.resolve` → (paid: quote → `awaiting_approval`) → dispatch. Every refusal happens before any load or spend.
- **Atomic commit.** Outputs are pulled to `tmp/` and their hashes verified. The `measure` child confirms they decode and that their declared media facts (rate, channels, frames) match. A single unit of work then commits all artifacts, sidecars and events. No partial artifact is ever visible.
- **Failure codes:** `worker_lost`, `worker_refused(code)`, `hash_mismatch`, `decode_failed`, `media_mismatch`, `timeout`, `disk_low`, `store_unavailable`, `budget_refused`, `quote_expired`, `cancelled_by_owner`, `internal`.
- **Retries.** Automatic only for `retryable` errors on free placements, with a bounded count. Never for paid jobs.
- **Residency.** A device semaphore keeps one heavy profile resident per device. Light profiles (analysis) run beside it. `/v1/unload` runs on idle timeout or when another heavy profile needs the device.
- **Cancel.** `POST /v1/jobs/{id}/cancel` must take effect within 5 s. If it does not, a local worker is killed and a burst pod is terminated. The job ends `cancelled` with no partial output.
- **Restart.** See §4.3. Local work becomes `failed(worker_lost)`. Remote and burst work is re-queried. The reaper settles burst work.

### 9.2 Worker protocol v1

**Auth.** Every route requires `Authorization: Bearer <token>`:

- per spawn, for local workers
- per pairing, for tailnet hosts (`studioctl worker add`)
- per lease, for burst pods

Tokens never reach the browser. Workers bind 127.0.0.1, the tailnet interface, or sit behind the provider's HTTPS proxy. Workers never call the control service.

**Routes** (the complete list; anything else returns 404, and conformance checks this):

| Route | Purpose |
|---|---|
| `GET /v1/describe` | Capability discovery: `worker_id`, protocol and SDK version, host facts (OS, arch, backend, device, memory, free disk, nvidia-smi or Metal facts), env lock sha256 or image digest, code commit, and per profile its tasks, limits, lanes, `weights_present` and weights manifest sha256. The control service computes `profile_revision` from these and admits the worker only if the revision has an installed record. |
| `GET /v1/health` | `{state: idle\|loading\|busy, resident_profile, mem}` |
| `PUT \| HEAD \| GET /v1/assets/{sha256}` | **Assets by reference, after admission.** A PUT is accepted only for a hash an admitted `job_id` lists, so a refused request never receives a byte. The control service HEADs first and PUTs only if missing. The worker verifies the hash on PUT and enforces a per-profile size cap. Workers never receive paths or URLs and never fetch arbitrary URLs. The only network fetch a worker makes is the weights download from its profile's pinned source (a Hugging Face revision, a pinned URL with sha256, or a file in a pinned package). |
| `POST /v1/jobs` | `{job_id, profile_id, task, lane, inputs[{role, sha256, media_type, bytes}], params (typed per task), seed, deadline_s}` → `202 awaiting_inputs` (the job starts once its inputs are present), or `422 Refused{code}` **before anything loads or any asset moves**. Codes: `unsupported_task`, `lane_forbidden`, `over_limit`, `language_unsupported`, `weights_missing`, `insufficient_memory`, `insufficient_disk`, `busy`. Idempotent on `job_id`. |
| `GET /v1/jobs/{id}` | Status: state, steps, outputs `[{role, sha256, audio_meta}]`, `params_actual`, SDK-measured timings (queue, load, cold flag, run) and peak memory, error. Used for burst polling. |
| `GET /v1/jobs/{id}/events` | SSE mirror of status, used locally and over the tailnet. |
| `GET /v1/jobs/{id}/outputs/{role}` | Output bytes. The control service re-hashes them. |
| `POST /v1/jobs/{id}/cancel` | Cooperative cancel through `ctx.check_cancel()`. |
| `POST /v1/unload` | Frees the resident model. |

**Safety.** There is no shell. Params are validated against per-task schemas and never interpolated into command lines. For example, the YuE2 adapter writes the ABC to a scratch file and calls the Python API with that path. Workers write only inside their scratch directory, and the SDK journals in-flight jobs for crash reporting.

---

## 10. Operator-lane enforcement

**The rule (O-06, D-11).** Every project has a lane, `individual` by default, with `llc` for Sabbath Echo and every IDC venture, plus `research`. Every artifact carries `eligible_lanes`. That set is the intersection of the allowed lanes of every component in its license chain and the `eligible_lanes` of its **`derived_from` and `converted_from`** parents.

**`analyzed_by` edges never propagate.** A Demucs separation used only to measure an ACE keeper's adherence cannot taint that keeper. However, the analysis job itself is still admitted in the project's lane, so Demucs analysis cannot run at all in an LLC project.

| # | Enforcement point | What it checks | Negative test |
|---|---|---|---|
| 1 | **Project lane** (owner act) | The lane is set at creation. A change re-checks every artifact and every lane-carrying record (a MelodySpec drafted by a lane-restricted transcriber) and fails if any lacks the new lane. | Moving an individual project holding a YuE2 artifact, or a melody drafted by an individual-only transcriber, to `llc` is refused. |
| 2 | **Admission** (`Registry.admit` at `Conductor.submit`) | Every component of the profile lists the lane. Every audio-ancestry input's `eligible_lanes` includes it. Every input's `allowed_uses` includes the task. | An LLC request for `yue2-3b-score` returns `lane_forbidden` with no `loading` event. An LLC adherence job on `separate-demucs` is refused, and the badge reads "adherence unmeasured (no LLC separator yet)". |
| 3 | **Worker refuse-before-load** | The request's lane must be in the profile's declared lanes. | A direct protocol call with `lane: llc` to the yue2 or `fake-nc` worker gets `422 lane_forbidden` and the worker loads nothing. |
| 4 | **Store write path** (unit of work) | No artifact or melody record enters a project whose lane is not in its `eligible_lanes`. An import's lanes come from its owner-attested terms; a DAW bounce inherits the lanes and license chains of the studio exports it contains. | A forced commit of an individual-only artifact into an LLC project is rejected; a DAW bounce of an individual-only export is refused in an LLC project. |
| 5 | **Export** (closure over `derived_from` and `converted_from`) | The manifest's `eligible_lanes` must contain the project lane. The license chain, release blockers and AI-disclosure obligations come from audio ancestry only; a research export is never release-clear. | An LLC export of a closure containing `fake-nc` is refused. An LLC export of an ACE keeper that was `analyzed_by` an individual-only separator is **allowed**. |
| 6 | **Eval** | Each brief runs in its own lane, so LLC briefs never touch YuE2, Demucs or NC scorers. | An LLC brief plan naming YuE2 fails preregistration validation. |
| 7 | **Burst egress** | The quote shows the lane check and the egress list. | A quote for an LLC project's YuE2 job is never created; it is refused at point 2. |

**Use policy, enforced at the same points.**

- **Reference standards.** A `listening_only` reference is refused as engine input and is never an arm in a product audition, only an eval anchor (O-05, O-08).
- **Imports** are owner acts whose uses follow their source: Suno `[listen, loudness_measure, dsp_finish]` (Pro or Premier only; llc only with the LLC's account or a written license), owned purchases `[listen, loudness_measure, eval_anchor]`, licensed imports only what their license grant names, never training. Ingest detects Suno's embedded marks (forcing source Suno) and AURA's own export tags (which a bounce must name).
- **The Suno boundary** (D-21, O-08). An `imported_mix` whose source is Suno has `allowed_uses = [listen, loudness_measure, dsp_finish]`; an owner-signed risk acceptance can add only engine, conditioning, separation, edit or conversion input. It is never an audition arm, an eval reference or anchor, a reference, training data or test material, whatever is signed, and never separated by an ML model. DSP finishing preserves its embedded provenance metadata.

**Lane-aware components in v1.**

| Component | Lanes |
|---|---|
| pYIN+HMM transcriber, NeutralVoice, ACE | all lanes |
| SwiftF0 | individual and research until its provenance review (its ONNX model was trained on CC BY-NC-SA data), so LLC adherence uses pYIN only, once an LLC separator exists |
| Basic Pitch | individual and research until its provenance review (its training datasets' terms are unchecked) |
| Kim Mel-Band-RoFormer | individual and research until its training-data review, then llc by contract-fix PR |
| Non-commercial scorers (SongEval, MuQ, CMI-RM, TuneJury) | individual and research (O-06), diagnostics only; SongBench research only |
| Any component whose license is UNVERIFIED | research only (individual and llc forbid it) |
| Demucs and demucs-mlx | individual and research only |
| YuE2 | individual and research only |
| HeartMuLa and MiniMax (P6) | LLC-eligible, with MiniMax's AUP #11 disclosure carried into the manifest |

---

## 11. Tracer-bullet order and phase plan

Each tracer bullet is a narrow, complete path through contracts, store, jobs, workers, UI and tests. TB1 is split into slices that each fit one fresh context window. The skeleton is **MIDI-first**, so it never depends on transcriber quality.

| Order | Tracer bullet | Path |
|---|---|---|
| TB0 | **Store, doctor, session** | `studioctl setup` creates and attaches the bundle, writes `store.json`, `LOCK` and the env file, and points HF, uv, pnpm, Playwright and TMPDIR at the bundle. `doctor` writes a HardwareSnapshot plus store throughput, IOPS and band-size measurements as EvidenceRecords. `serve` refuses to start without a mounted, matching, unlocked store. `/system` and `/compute/detect` feed the Session screen (tier 4 recommended, with reasons). A session row persists across reloads. The mount watch is live. COOP/COEP headers are served. |
| TB1a | **MIDI → measured fake pair** | A MIDI fixture becomes MelodySpec rev1 (Score.from_midi). PUT song (English lyrics, style, SongForm) → `Score.assemble` → plan `[fake-route-a, fake-route-b]` → FakeEngine ×2 over the real protocol → child `measure` (loudness, true peak, 48k/24 preview) → two `ready` candidates labelled "Synthetic test output". |
| TB1b | **Blind audition → keeper → verified export** | `Audition.open` (opens only when all arms are ready; attenuation-only gains; commitment) → owner verdict → reveal → keep → export job (native copy, 48k/24 if needed, MIDI, specs, manifest; re-decode and re-hash) → bundle verified and downloadable. |
| TB1c | **Capture → ingest** | The browser AudioWorklet records with EC/NS/AGC off (verified with `getSettings()`), hashes the capture client-side, and POSTs it. `ingest` creates a `human_recording` (irreplaceable). Playwright supplies the fake-mic NeutralVoice hum. |
| TB1d | **Transcribe → piano roll** | The `transcribe` job (pYIN+HMM) produces a MelodySpec draft with per-note confidence. Piano-roll ops create rev2+, with a timestamped correction log. The synthetic-band floor runs (blocked by the mir_eval license ticket), and the transcriber is labelled "unverified on real hums". |
| TB2 | **Paid-run gate on FakeBurstProvider** | Plan with `fake-burst` → Quote at ceiling from a fake live rate → `awaiting_approval` → challenge nonce → owner approve → ledger reservation fsynced → provision → run → terminate → settle. Variants: over cap, automation-token approve (403), reused or expired nonce, job-list change, SIGKILL mid-run (the reaper settles at ceiling and the job becomes `failed(worker_lost)` with no retry), overrun block. |
| TB3 | **First real pair: ACE on the Mac (R2-synth + R2-raw)** | `guide` (NeutralVoice over the full SongForm) and `assemble-audio` (hum slices) → the ACE env is created lazily on the bundle → preflight → license acceptance (owner act) → selective download verified against the manifest → conformance on the M5 Pro → smoke gate (decode, non-silence, duration, Jon's "not garbled") → computed `smoke-passed` → sequential cover jobs on Jon's own hum → blind A/B → keeper → export (ACE MIT chain, eligible lanes all). |
| TB4 | **MIDI in and out, including live** | Web MIDI live input becomes a MelodySpec through `from_midi_events`. MIDI export carries the tempo map and section markers. A golden round trip (MIDI → MelodySpec → MIDI) keeps notes and ticks equal. |
| TB5 | **Adherence (pulled forward from TB6)** | The separator worker (Demucs or demucs-mlx, individual lane) → SwiftF0 with a pYIN cross-check → DTW → metrics, validated first on a NeutralVoice line mixed under an accompaniment bed, with tolerances fixed in the fixture. The P2 ACE pair then carries adherence badges (after reveal) once the real-separator capability passes, and gives R2-raw versus R2-synth numbers as an input to the preregistered route comparison, which alone decides the D-04 reverse-if. |
| TB6 | **Hum benchmark (P2 parallel track, not blocking TB3)** | Jon records N hums plus the same melodies played on MIDI as ground truth. N is set at preregistration, and the hash is committed before scoring. Basic Pitch (py3.10 env), SwiftF0 `segment_notes` and pYIN+HMM are scored with mir_eval COn/COnP/COnPOff, plus blind correction effort from the correction log. The result is an EvidenceRecord that decides the default transcriber. "Manual entry wins" is an allowed outcome. |
| TB7 | **Not ACE-only: YuE2 on an approved burst (R1)** | `Score.to_abc` in the YuE2 dialect (validated with the YuE skill's `abc_tools.py`; typed ineligibility) → YuE2 smoke on its burst host class (weights verified in the image, Jon's "not garbled") → lane check → quote (the smoke-passed 24 GB class, a hard maximum computed from boot, download, run and teardown, egress = ABC + lyrics plan) → Jon opts in and approves in the UI → reservation → burst machine from the pinned digest → conformance → R1 candidate beside an R2 candidate on the Mac → measure and adherence → blind A/B → keeper → export (YuE2 CC BY-NC chain, eligible lanes individual and research) → terminate → settle ≤ ceiling. The same request in an LLC project is refused at submit. If Jon declines, the plan is labelled "ACE-only: burst declined". |
| TB8 | **Reference standards and preregistered smoke-12** | Jon's four reference standards are imported as `listening_only` with permission records. The eval harness commits the preregistration hash, runs smoke-12 (hum and MIDI fixtures included, each brief in its lane, equal candidate count) and holds eval auditions with reference anchors and hidden repeat pairs. Results get uncertainty clustered by brief. Promotions and demotions happen only through records. Lyric PER (ASR + verified G2P) joins the badges. |
| TB9 | **First studio slice: section replace** | EditOperation (mask, crossfade, locked context) → ACE repaint (main's chunk mask) → two candidates, each composited (original outside the mask and crossfades, ACE inside) → audition → accept → preservation check (PCM byte-identical outside the mask in the declared domain, on the composite; ACE's raw deviation recorded separately) → new keeper revision. StudioEngine timeline playback gate on the Mac via Chrome `playbackStats`. |

### Phase plan and exit evidence

Every exit criterion is a check that could fail, recorded as an EvidenceRecord or a CI run id.

**P0 Ground (TB0).** Store on the bundle, hardware truth, contracts v1 and CI on three operating systems, all before any model.

1. `studioctl doctor --json` output is hashed into a host-inventory record. `recommend()` goldens pass over at least 6 recorded snapshots and return tier 4 for this Mac.
2. Store probes pass: owners on, symlink, chmod, hardlink and `clonefile`. A second `serve` is refused by `LOCK`.
3. Preflight negatives:
   - A 250 MB write into a 200 MB temp bundle is refused.
   - A fixture where APFS free exceeds exFAT host free is refused on host free.
   - A planned internal write is refused.
4. Store throughput, IOPS and the 8 vs 64 MiB band-size measurement are recorded as MEASURED-LOCAL, and the band size is chosen from them.
5. `validate.py` passes. Every seeded-bad fixture fails. The reference re-run matches. `components.v1.json` regenerates byte-identically. The TS twin passes the tempo vectors. The codegen drift check is green.
6. Control-service tests are green on Linux, macOS and Windows runners.
7. Lints fail on each planted violation: a mailto link, a personal address, a non-noreply author, a 50 MB dummy `.safetensors`, a GPL dependency in the control env, a secret in the web bundle.
8. Mount watch: detaching the volume under `serve` refuses new jobs and marks running ones `failed(store_unavailable)`.
9. License-verification ticket nodes are closed or left explicitly open: mir_eval, mido, pyloudnorm, librosa, FastAPI, uv, React, Vite, SQLite, keyring, the codegen tools. Until a row is verified, it is research-only in the register.

**P1 Walking skeleton (TB1a–d, TB2).** The whole creator path and the paid-run gate run on FakeEngine and FakeBurstProvider.

1. The StudioHarness end-to-end test (MIDI and fake-mic hum → verified export) passes on all three operating systems.
2. Playwright passes on Chromium with the NeutralVoice fake mic, with screenshots attached.
3. Conformance is green against FakeEngine and the analysis worker, and each of the 8 mutants fails (including one that accepts assets before admission).
4. Crash: SIGKILL during `generating`, then restart, gives `failed(worker_lost)` with zero partial artifacts visible.
5. Paid gate: every TB2 case behaves as specified, upward reconciliation included, including the reservation event preceding the provision event and the 403 on an automation approve.
6. Blinding: no mapping, profile, route, seed or file name appears in any response or in the DOM before the verdict. Previews share a rate. Gains are attenuation-only and match within 0.1 LU. The reveal matches the commitment.
7. Registry:
   - An unpromoted profile is absent from the product view.
   - A generation naming it returns 409 before any load.
   - Promotion without evidence is rejected.
   - A pin change gives a new revision at `declared`, which reaches `installed` only with its own install and conformance records.
   - A smoke record without every declared check or its owner verdict does not promote, in the API and in the contract gate over `docs/evidence`.
   - A synthetic record aimed at a benchmark gate is rejected.
8. Suno boundary: the negative tests pass (a stand-in import refused as cover input, audition arm, separation input and evaluation reference, whatever risk acceptance exists; an import posted by an automation token refused). The seven-point lane suite moved to P4 in the design review, because two of its points (preregistration, quotes) exist only from P2 and P4; P1 keeps the admission, write-path and export negatives its tickets already carry.
9. Durability:
   - Delete `studio.sqlite`, run `reindex`, and the durable rows and heads diff equal.
   - `backup` to a second directory with hashes verified at the destination, then `restore` into a fresh root, then `fsck`, comes back clean.
   - A single flipped byte is detected by `fsck`.
10. Transcription floor: pYIN+HMM COnP F1 on NeutralVoice hums is at or above the preregistered floor. A miss keeps the transcriber disabled. The record is marked synthetic and satisfies only the transcriber's smoke gate.

**P2 First real pair (TB3–TB6).** Jon hums on the Mac and auditions 2 real ACE candidates that carry adherence numbers. MIDI goes in and out. The hum benchmark runs as a parallel track.

1. ACE conformance passes on `mlx/m5pro`, with the log hashed.
2. Cold and warm timings are recorded in `results_local` as MEASURED-LOCAL. The smoke record lists every declared check (manifest match, conformance, decode, non-silence, duration) and Jon's "not garbled" verdict. `smoke-passed` is computed, not set. The analysis profiles have their own install, conformance and smoke records on `cpu/m5pro`.
3. Install: the downloaded bytes equal the manifest, every LFS sha256 verifies, the license acceptance is recorded, and the preflight estimate is within 10% of the actual size.
4. Adherence is validated on the NeutralVoice-under-bed golden within its committed thresholds, and then through the real separator under a NeutralVoice bed and an ACE bed (the `adherence.real-separator.darwin` capability), before it is shown on real candidates.
5. Jon's first verdict on real candidates from his own hum is recorded. The keeper's bundle re-decodes, and its hashes match a schema-valid manifest (ACE MIT chain; the Demucs analysis edge does not taint it).
6. R2-raw and R2-synth adherence numbers on Jon's hum are recorded as an input to the preregistered route comparison; only that comparison decides the D-04 reverse-if.
7. The MIDI round-trip golden passes, and live Web MIDI capture produces a MelodySpec; `capture.mic.darwin` and `capture.midi-live.darwin` compute from Jon's microphone check and keyboard.
8. Hum benchmark: the preregistration hash is committed before scoring, and the record holds three transcribers' scores plus blind correction effort on Jon's hums. The default transcriber changes only through that record.

**P3 Not ACE-only (TB7).** The individual-lane melody pair becomes mixed-engine through an approved, cap-bounded burst (O-02, O-09).

1. The ABC converter goldens pass YuE's `abc_tools.py` validation.
2. The yue2 image builds, and its digest is pinned in the registry.
3. RunPod spikes are recorded, each pass or fail: pod HTTPS-proxy reachability and limits, the live-rate API, in-container shutdown stopping billing, the provider spend limit, and private-registry pull.
4. YuE2 is smoke-passed on its burst host class (weights verified against the pinned manifest in the image, Jon's "not garbled"), and conformance passes on each burst before its first job.
5. Ledger: `reservation_at < provisioned_at`, actual ≤ ceiling, the provider API lists zero `studio-burst` pods afterwards, and the egress record lists only the ABC and lyrics-plan hashes.
6. An LLC-lane YuE2 request is refused at submit and by the worker (two tests).
7. Jon's verdict on a mixed pair is recorded.
8. The month's ledger total is ≤ $25.00 and reconciled against provider billing.

**P4 Measurement (TB8).** Route defaults change only on evidence. Completing the 48-brief benchmark is post-v1; the benchmark set is authored and preregistrable in v1.

1. The preregistration hash is committed before the first smoke run, and CI checks the commit order.
2. Smoke-12 verdicts are recorded with brief-clustered uncertainty and repeat-pair consistency. A short quota concludes `inconclusive`.
3. Promotions and demotions are computed through records only: a concluded preregistered set writes route-standing records that the plan reads. Any route may lose, and the "unbenchmarked routes" label drops only for routes with a benchmark record.
4. A `listening_only` reference is refused as engine input.
5. The G2P license is verified, and lyric PER is validated on NeutralVoice and on sung vocals whose words Jon verified, before it is shown.
6. The BS.1770-4 versus -5 stereo diff is recorded (X-47).
7. The seven-point lane suite passes, one named negative test per enforcement point of §10, with `fake-nc` and `fake-separate` standing in for the real NC components (moved here from P1-8).

**P5 Studio, v1-studio (TB9 onward).** Timeline, section replace and extend, Isolate original with residual (lane-aware), stems, MIDI and tempo-map export, the Mac playback gate, and DSP finishing of an imported Suno download.

1. Chrome `playbackStats` shows 0 underruns for 8 tracks × 30 minutes on the Mac, and UI p95 stays under 100 ms while a generation runs. `studio.playback` is computed `smoke-passed` for `darwin` only.
2. The preservation check shows byte-identical PCM outside the mask on every accepted edit's composite, a planted one-sample change fails, and ACE's raw chunk-mask deviation on the Mac is recorded against a rule committed in advance.
3. Undo restores the prior artifact by hash, with no regeneration run recorded.
4. Isolate original: the sum-to-mixture integrity check holds on stored and exported files, bleed and residual energy meet the committed thresholds on a real separation, and Jon's listening verdict lifts "separated · unreviewed".
5. A DAW import of the aligned stems is verified with screenshots: zero start, equal frame counts.
6. A Suno DSP-finish export manifest of a synthetic stand-in carries the imported terms, and any generative op on that import is refused. Real Suno audio is never test material (O-08).
7. StudioHarness and the recovery test pass against the real STUDIO volume on the Mac, recorded as darwin per-OS evidence.

**P6 Lanes and hosts beyond the Mac.** This phase can be pulled forward the day a CUDA host is reachable, because it uses the same protocol.

1. A tailnet CUDA worker passes conformance on its own `host_class`. Tier 1–3 recommendations are made from its real snapshot.
2. StudioHarness passes on a real Linux or Windows studio host, not only in CI, and the per-OS playback gate passes. Until each passes, that OS is labelled unverified.
3. LLC engine smoke (HeartMuLa and/or MiniMax) passes with license-chain checks. The LLC separator is allow-listed after its training-data check, which turns LLC adherence on.
4. Narration dry-run: a `tts_render` artifact flows through the store, jobs and the export manifest with no schema change.

---

## 12. Risks

| Risk | Mitigation |
|---|---|
| **Backup Plus is a single spinning HDD on exFAT over USB** (MEASURED-LOCAL: about 125 MB/s read, about 70 MB/s write). Model loads are slow, an unclean eject can corrupt the bundle, the APFS volume over-reports free space, and there is no second copy. | Doctor measures throughput and IOPS. Preflight uses host free space. An unclean-detach marker triggers verifyVolume. An idle-sleep assertion is held while writing. SQLite runs with `fullfsync` and snapshots after each keeper. Sidecars and records allow `reindex`. `store backup` makes a hash-verified mirror of the irreplaceable closure on a second device. Weights and envs are re-downloadable. D-15 reverse-if: move to an APFS SSD when Jon frees space or buys one. |
| **No route keeps a hummed melody.** ACE cover scored Hit@1 2.4% (COMPETITOR-RUN), maintainer #972, user report #1100. YuE2's 71.3% is self-reported on SHS100K. | R2-synth uses the clean NeutralVoice guide with strength and noise sweeps. R1 covers the individual lane. Adherence is measured from P2. The keeper badge says "melody not kept" honestly. Jon's ear is the gate. D-04 reverse-if applies in either direction. |
| **NeutralVoice is a poor ACE cover input** (new DSP on the critical path). | R2-raw runs beside it in the same request. P2 records adherence for both. NeutralVoice's other three jobs (fixtures, fake sound, fake mic) do not depend on cover quality. If it fails Jon's ear, the evaluated MIDI-synth candidate (license-verified first) becomes an alternative guide renderer behind the same `guide` task. |
| **Hum transcription is poor.** COMMUNITY F1 is 0.27–0.43, and no clean transcriber is benchmarked on hums. | Piano-roll correction is mandatory. MIDI file and live MIDI are first-class. The synthetic floor runs before real use. The P2 benchmark on Jon's own hums uses correction effort as a metric, and "manual entry wins" is allowed. |
| **Burst costs leak or breach the cap**: orphan pods, cold start, fees, rate drift. | The live rate is taken at quote time. The reservation at ceiling precedes provisioning. Approval is single-use and owner-only. There is a hard maximum, an in-image deadline, a tag reaper at startup and every 5 minutes, no automatic paid retry, settlement at ceiling when billing is missing, an overrun block, fixed lines counted, a provider spend limit set by hand, and monthly invoice reconciliation. CI covers it all with FakeBurstProvider. |
| **RunPod specifics are UNVERIFIED**: pod rates, proxy behaviour, in-container shutdown billing, spend limits, private registry auth. | Each is its own spike ticket in P3, with a recorded pass or fail. The design polls with short requests rather than relying on long-lived proxy streams. A Vast adapter behind the same port is a fallback only on evidence. |
| **Cold start dominates YuE2 cost**, or the GPU class is unavailable. | A slim image with no weights. A GPU-class fallback list. Cold and warm timings per run are shown beside the ceiling. A network volume is adopted only when measurements show it is cheaper. |
| **Lane leakage**: NC YuE2 or research-only Demucs output reaches LLC work, directly, through a melody drafted by an NC-data transcriber, or through a DAW bounce of an individual-only export. | Seven enforcement points (§10), each with a negative test. Typed edges stop analysis from tainting keepers without opening a hole, because analysis itself is still lane-admitted. Transcribed melodies carry their transcriber's lanes; imports are owner-attested and a bounce inherits the lanes of the exports it contains. |
| **Evidence ceremony slows the first song.** | Evidence is computed, not hand-promoted. Product requests are not Lab plans. TB1 runs end to end on fakes within P1. ACE needs install, conformance, smoke and promote, and no new architecture. |
| **Single-seam suite becomes slow or flaky** (subprocess workers, SSE timing). | Zero-latency FakeEngine, an injectable clock, waits on event seq and never sleeps, parallel harness instances on separate store roots, a PR budget of 10 minutes or less, and pure Score logic on golden fixtures. |
| **Localhost exposure**: CSRF or DNS rebinding against a service that can spend money and record verdicts, or an agent performing an owner act. | Binds 127.0.0.1. Host and Origin allowlists. A launch token exchanged for a `SameSite=Strict` owner-ui cookie. Owner acts are refused for automation tokens, and paid approval also needs the dialog nonce. No secrets, tokens or burst URLs reach the browser. The design does not claim to defeat a compromised local machine. |
| **ACE pin regressions**: XL-SFT garble #1259; XL F32 downloads of 19.95 GB. | Pin main ≥ ca1e85fe9. A pin change gives a new `profile_revision`, which computes to `declared` until its own install and conformance records exist. Start with 2B. Allow XL only after its own smoke run, preflight and the diffusers bf16 loader check. |
| **The internal disk (as low as 2 GiB free) fills** from stray caches or swap pressure. | The env file routes every cache to the bundle. Doctor audits stray caches. Heavy jobs are blocked under 2 GiB internal. Builds run only in worktrees on the bundle. |
| **Blinding leaks**: arrival order, sample rate, loudness, the jobs drawer, duration. | The audition opens only when every arm is ready. Labels are drawn at open time. Previews share a rate, and gains are attenuation-only within 0.1 LU. The jobs drawer shows ordinals only. Leak tests run at P1. Duration and character are an acknowledged residual leak. |
| **Format churn**: schemas frozen too early, or upcasters that grow unmanageable. | Small v1 schemas. Additive minor versions. Majors upcast on read, never rewritten. Frozen legacy fixtures make a break visible in CI. Snapshot records avoid tying old projects to old replay code. |
| **SongForm assembly sounds repetitive**, or ACE misbehaves over rests and instrumental sections. | The form editor supports instrumental sections. `render_mode: per_section` (each section with one profile and seed, stitched at the markers) is built with the R2 routes, so P4 smoke compares whole-form against per-section renders. Jon's verdicts decide the default. |
| **Windows and Linux hosting claimed from CI alone.** | Labelled unverified until a real host passes StudioHarness and the playback gate (P6). AURA is never called three-platform ready from one OS. |
| **CI minutes** on a private repo (macOS and Windows multipliers; current rates UNVERIFIED). | Since PR #12 all three OSes run on every PR, integration and nightly; the repository is public for the build so hosted CI stays free (2026-11-07). A self-hosted Mac runner produces hardware evidence. |

---

## 13. Where each part came from

### 13.1 Taken from creator-first (the base)

These are kept essentially as proposed:

- The single Studio API seam.
- The HTTP worker protocol with the control service always the client.
- The six control modules: ProjectStore, Conductor, Registry, Placement, Score, Audition.
- The control service carries no audio or ML dependencies.
- NeutralVoice in four roles, and SongForm assembly.
- AudioWorklet PCM capture that keeps the m4a decoder off the core path.
- FakeEngine on the real protocol, and FakeBurstProvider.
- StudioHarness, waiting on event seq.
- Lanes enforced at submit, at the worker and at export, extended here to seven points.
- Reserve-before-provision, the hard maximum, a 5-minute reaper and no automatic paid retry.
- The `awaiting_approval` state.
- Disk preflight on min(APFS free, exFAT host free), with heavy jobs blocked under 2 GiB internal.
- The one-volume rule and the cache env file.
- Neutral identifiers.
- The tier recommendation thresholds and warnings.
- The tracer-bullet spine: ACE on the Mac before any burst, then YuE2.
- Synthetic evidence never promotes to `benchmarked`.

### 13.2 Grafted from the runners-up

| Graft | From | Where |
|---|---|---|
| Provenance edges split: `derived_from` and `converted_from` propagate; `analyzed_by` never does | longevity | §5, §10 |
| Retention classes plus a hash-verified mirror of the irreplaceable closure, with a restore drill in P1 | longevity | §8.6, P1-9 |
| Provenance sidecars plus canonical JSON records; `reindex` rebuilds SQLite; `docs/FORMAT.md` | evidence + longevity | §4.2, §8.2 |
| Frozen legacy fixtures; MEASURED-LOCAL banned in `claims_published`; `results_local` must cite evidence | longevity | §2, §4.4, §6.3 |
| Computed status: a fold over evidence keyed by `profile_revision × host_class`; product view only at smoke-passed or above; 409 `profile_not_promoted` | evidence | §4.4 |
| Mutant workers the conformance suite must fail | evidence + longevity | §6.2 |
| Approval single-use, nonce-bound, quote-hash-bound, 15-minute expiry, UI-only; automation can quote but not approve | evidence + longevity | §4.1, §7.5 |
| Live rate at quote time, snapshot as a dated fallback; per-job egress record; secure cloud preferred | evidence | §7.5 |
| In-image `shutdown -h` deadline as a second lock; settle at ceiling when billing is missing; overrun blocks leases | longevity + evidence | §7.5 |
| Adherence pulled forward to P2, validated on synthetic ground truth first; default plan labelled "unbenchmarked routes" | evidence | TB5, §4.6 |
| Correction-op log as the correction-effort metric; hum benchmark on Jon's hums with "manual entry wins" allowed, moved to a P2 parallel track | evidence | §4.6, TB6 |
| Audition hardening: opens only when all arms are ready, common 48k/24 previews, ≤0.1 LU, hidden repeat pairs, `inconclusive` | evidence | §4.7 |
| 960 PPQ with integer µs per quarter, one half-up rounding function, a TS twin | longevity | §4.6 |
| COOP/COEP from P0; StudioEngine on SharedArrayBuffer rings, with CPAL as the only swap | longevity | §2, §4.11 |
| Every UNVERIFIED dependency as a ticket node; band size measured in P0; `fullfsync` | evidence | P0, §8 |
| Mount watch and sleep assertion | evidence + longevity | §4.2 |
| Suno boundary enforced in admission and the store | longevity | §10 |
| Per-tier evidence shown on the Session card; a 16 GB card gets YuE2 only after its own smoke run | evidence | §7.2 |
| Network volume adopted only on measured evidence | evidence | §7.6 |
| Stdlib-only worker SDK on Python ≥3.10; SDK-measured timings | evidence + longevity | §4.8 |
| TB1 split into window-sized MIDI-first slices | engineering judge | §11 |
| stdlib reference implementations; `components.v1.json` regenerated byte-identically | evidence | §2, §6.3 |
| FakeEngine fault knobs; analysis golden with a line under an accompaniment bed | evidence + longevity | §4.10, TB5 |
| Single-writer `LOCK` | longevity | §4.2 |
| Capability entries (`studio.playback` per OS) gated like profiles | evidence | §5 |

### 13.3 Rejected, and why

| Rejected | From | Why |
|---|---|---|
| Two worker transports (stdio NDJSON locally plus a WebSocket worker host remotely) | evidence | They double the protocol and conformance surface. One HTTP protocol reaches loopback, tailnet and a pod. The stdio benefits (crash as EOF, no ports) are covered by the parent-death watchdog and per-spawn tokens. |
| Every product request as a preregistered Lab plan; `/lab` as the first screen | evidence | It puts statistics ceremony on the creator path and delays the first song to P5. Product verdicts are recorded as `listening-unregistered` evidence instead: shown, but never promoting. |
| Hum benchmark serialized before the first real engine | evidence | It blocks hardware work behind recording sessions. It is now a P2 parallel track. |
| Tone-only FakeEngine audio | evidence | NeutralVoice gives a voiced, ground-truth guide that also serves R2-synth and the fake mic. |
| Internal disk under 2 GiB only warns | evidence | Swap lives there. Heavy MLX jobs are blocked instead. |
| `own_suno_download` as a basis for a reference permission | evidence, longevity | It conflicts with O-08: Suno audio is excluded from the harness. |
| FakeEngine profiles promoted into the product view with no synthetic flag | evidence | `test_only` profiles are visible only in dev and test, and their outputs carry `synthetic_test`. |
| The store as the sole truth and SQLite only as operations plus index (overturning D-09) | longevity | It needs an ADR fight before the first ticket. Its benefit (no data lost with the DB) is had by writing records and sidecars in the same unit of work, while D-09's SQLite stays the system of record. |
| Merkle snapshot revisions, `.aurapack` packs, RFC 8785, AURA's own RIFF/RF64 codec | longevity | P0 weight with no current payer. Immutable revision records already avoid replay coupling. Integer-only canonical JSON avoids float canonicalization with the stdlib alone. The backup mirror uses the CAS layout itself. Workers use proven WAV I/O behind the process boundary. Cross-host packs wait until a second host is reachable (Q1). |
| Two real burst adapters at once (Vast plus RunPod); Tailscale inside pods | longevity | Prove one adapter first. Tailscale in provider containers is an UNVERIFIED spike on the paid path. Vast becomes an adapter only on ledger evidence. |
| MediaRecorder capture | longevity | Compressed capture needs the UNVERIFIED decoder. AudioWorklet PCM does not. |
| Settlement at INFERRED runtime × snapshot price | creator-first | Settle at ceiling (conservative) until reconciled. |
| Stored status plus `promote()` | creator-first | Replaced by computed status. A pin bump can no longer keep a stale `smoke-passed`. |
| Quote from a stored price snapshot | creator-first | The live rate is used, with the snapshot as a dated fallback. |
| `POST /jobs/{id}/approve` open to any authenticated client | creator-first | Approval is now an owner act with a nonce. Agents can quote only. |
| PPQ 480 with `bpm_decimal` | creator-first | Replaced by 960 PPQ and integer µs per quarter (SMF-exact), with a TS twin. |
| `rsync` backup of `projects/` | creator-first | Replaced by a hash-verified mirror of the irreplaceable closure. |
| Adherence and the hum benchmark in P4; the promotion-without-evidence test in P4 | creator-first | Moved to P2 and P1. |
| Monolithic TB1 | creator-first | Split into TB1a–d. |
| TTY y/N approval in the CLI | evidence | There is one approval path, the UI, to keep the owner-act surface minimal. |
| CLI named `studio` | creator-first | Possible collision with Android Studio's launcher. Renamed `studioctl`. |

### 13.4 Tensions resolved

| # | Tension | Resolution |
|---|---|---|
| T-01 | Is SQLite the truth (D-09), or are objects the truth (longevity)? | SQLite stays the system of record. Every immutable record and every artifact's provenance is also written as content-addressed JSON in the same unit of work, so the DB can be rebuilt (`reindex`). Operational state (jobs, ledger, sessions) lives only in SQLite, with `fullfsync` and snapshots. A lost DB loses only in-flight jobs (which fail on restart anyway), and ledger lines can be rebuilt from provider billing. D-09 is **amended**, not overturned. |
| T-02 | Does lane taint flow through analysis? | No. Only `derived_from` and `converted_from` edges propagate. Analysis jobs are still lane-admitted, so Demucs never runs in LLC. LLC adherence shows "unmeasured" until an LLC separator is allow-listed. |
| T-03 | Can a smoke gate be met with synthetic evidence? | Only where the profile's declared gate says so (transcriber floor, `test_only` profiles). Benchmark gates never accept synthetic evidence. A smoke-passed transcriber is labelled "unverified on real hums" until benchmarked. |
| T-04 | Do product verdicts count as evidence? | They are recorded (`listening-unregistered`) and shown per route ("kept n of m"). They cannot change status. Only a preregistered set of eval auditions can (D-10). |
| T-05 | Is the hum benchmark in P2 (risk judge) or P4 (owner judge)? | P2, as a parallel track (TB6) that does not block the first ACE pair (TB3). |
| T-06 | Restart: re-query workers (creator-first) or fail everything (evidence-first)? | Local workers die with the control service through the parent-death watchdog, so their jobs fail. Remote and burst jobs are re-queried and resume or fail. Paid work never auto-retries. |
| T-07 | Settlement when billing is missing: INFERRED runtime × rate, or the ceiling? | The ceiling, labelled `settled_at_ceiling`. Reconciliation can lower only that amount, and books any unseen invoice charge as a reconcile adjustment that counts toward the cap. |
| T-08 | Approval channel: UI only, or UI plus TTY? | UI only, with a nonce. The CLI and harness quote, then wait for the UI approval. |
| T-09 | Month boundary for the cap? | UTC calendar month, shown in local time. The ledger arithmetic is fixture-tested. |
| T-10 | Envs on the HDD bundle (O-03) or the internal SSD (measurement note)? | The bundle, per O-03, because internal space reads as low as 2 GiB. The roots are configurable, and envs and the uv cache move together. |
| T-11 | Bundle size 1t vs 900g? | 900g, leaving room on a shared backup drive. Owner may change it. Preflight uses host free in every case. |
| T-12 | What happens if Jon declines a burst? | Per run, the plan is labelled "ACE-only: burst declined". Nothing changes silently. The no-CUDA owner sign-off (Q14) is closed by O-02. |
| T-13 | Network volume for burst weights? | Not in v1. Download per lease, then adopt only on measured cost (§7.6). |
| T-14 | MIDI synth/soundfont for R2-synth vs NeutralVoice? | NeutralVoice in v1-core. The MIDI synth stays an `evaluate` ticket (license-gated) for F6 instrument rendering in v1-studio. |
| T-15 | `test_only` fakes vs "nothing reaches the UI without evidence"? | Fakes appear only when `STUDIO_ENV` is `dev` or `test`, with synthetic labels on every surface. |
| T-16 | Product name vs code identifiers vs on-disk names? | The product name lives only in `product.json`. Code, CLI, volume and store format use `studio`. A rename touches one constant and no path. |

### 13.5 Proposed ADRs on top of D-01…D-24

D-01…D-24 become `0001`–`0024` as RECONCILIATION.md suggests, with D-09 marked amended by 0028. New ADRs:

- `0025-one-studio-api-seam-control-service-without-audio-deps.md`
- `0026-worker-protocol-v1-http-control-always-client-stdlib-sdk.md`
- `0027-registry-status-computed-from-evidence.md`
- `0028-sqlite-of-record-plus-content-addressed-records-and-reindex.md`
- `0029-provenance-edge-types-and-lane-propagation.md`
- `0030-paid-runs-quote-owner-approval-reservation-settle-at-ceiling.md`
- `0031-owner-acts-and-automation-tokens.md`
- `0032-neutralvoice-guide-synth-and-songform-assembly.md`
- `0033-time-model-960-ppq-integer-tempo-one-rounding-function.md`
- `0034-studio-volume-one-volume-rule-retention-and-backup.md`
- `0035-neutral-identifiers-and-the-single-product-constant.md`
- `0036-suno-boundary-enforced-at-admission.md`
- `0037-public-contact-rule-07-and-noreply-identity.md`

---

## 14. Design review log (2026-10-09)

Five review lenses produced 128 findings (2 critical, 43 high, 55 medium, 28 low). All 128 were applied; one was applied
only in part, and 9 were applied in a different form than proposed, each noted below. Where a finding conflicted with
the owner decisions (O-01…O-11) or the verified evidence, those won. Gates after the review: `python3
scripts/spec/validate.py` PASSED (59 reference rules, 300 fixture files) and `python3 scripts/spec/tickets.py --check`
PASSED (105 tickets, depth 19, critical path weight 49).

**Renumbering.** The ticket set grew from 88 to 105 tickets and was renumbered in topological order, so the findings'
ticket numbers are the old ones. Old → new: T12→T13, T13→T14, T14→T15, T15→T16, T16→T17, T17→T19, T18→T20, T19→T22,
T20→T25 … T32→T37, T33→T65, T34→T38, T35→T39, T36→T40, T37→T42, T38→T43, T39→T44, T40→T46 … T47→T53, T48→T55,
T49→T56, T50→T58 … T52→T60, T53→T62, T54→T64, T55→T69 … T64→T78, T65→T79, T66→T81, T67→T82, T68→T84, T69→T85,
T70→T87 … T88→T105 (T01–T11 keep their numbers). New tickets: T12 unlock,
T18 store-facts-and-mount-watch, T21 harness-skeleton, T23 song-page, T24 player-bar, T41 paid-run-approval-dialog,
T45 analysis-on-mac, T54 training-data-provenance, T57 chord-symbols, T61 yue2-smoke-on-burst, T63 route-comparison,
T66 references, T67 reference-timbre, T68 ace-base-on-mac, T80 repaint-on-mac, T83 time-stretch-listening,
T86 stems-listening, plus precondition P01 (interim volume and GitHub email privacy, which blocks T01).

**Traceability (29 applied).** Per-section rendering is built (`render_mode` in the contract ticket, the stitch path
in the routes ticket); the three-reference role task is "not runnable in v1" (B11 is v2) and the MIDI chord seed runs
on the new chord-symbols ticket; ACE base and O-07's style reference get their own install-and-smoke ticket and the
tier-4 preset names reference timbre; Kim Mel-Band-RoFormer is individual and research until its review; the Suno
boundary is closed in the risk-acceptance schema, CLAUDE.md rule 6, GLOSSARY and the imports ticket; the first-song
ticket no longer uses Jon's Suno download as evidence; the shared job contract reserves `tts`; `integration` is named
everywhere; recording a reference permission is an owner act; SwiftF0 and Basic Pitch get a provenance-review ticket;
ADR-0016 and story 348 name the smoke gate; live MIDI and the Mac's StudioHarness and recovery test have real-host
evidence; switch re-planning belongs to the Conductor; the contract ticket's declaration list is complete; D1 and L4 are
traced; the default route order is a plan-rules default; smoke-12 waits for lyric PER; `ready-for-human` means "needs
Jon"; ACE installs one profile at a time; the low items (five evidence kinds, product.json, scope labels, checker
coverage, P1-8, HumTrans, tier-3 extension, one disk range) are applied.

**DAG slicing (22 applied).** Missing edges added (aligned export after export; PER validation after ACE; paid spikes
and the CUDA host after the real store; install after first run; the evaluation harness after imports and the
commit-order check); owner gates moved off the agent chain by splitting section replace and isolate original; the web
shell, studio-volume lifecycle, projects, paid-run gate and references tickets are split; container tickets declare
their slots and fillers descend from them; API routes, CLI subcommands, doctor sections, analysis tasks, child jobs,
job states, placement strategies and plan route providers register by file; the contract and license tickets no longer
touch the same files; the stack rows (SQLite, keyring, MLX, numpy, scipy, soundfile, codegen tools) moved to the
foundation ticket; a deep-module integration skeleton lands at depth 8; the first-song ticket no longer deadlocks on a
declined burst; LLC challengers get images; `tickets.py` now fails on path conflicts between parallel tickets and on slot
fillers outside their container's descendants.

**Evidence honesty (27 applied, 1 in part).** `evidence/1` carries per-check results and the status fold promotes a
smoke record only when every declared check passes with Jon's verdict (new vectors, scenarios and an invalid fixture);
`validate.py` runs every reference rule over `docs/evidence` exports; YuE2 earns smoke-passed on its burst host class;
the analysis worker earns its own records on `cpu/m5pro`; adherence on real candidates waits for the
`adherence.real-separator.darwin` capability and committed thresholds; a preregistered route comparison alone decides
ADR-0004's reverse-if; "best" is gone from plan copy; route-standing records carry demotions; "Check this microphone"
breaks the capture deadlock; isolation, repaint, time-stretch and lyric PER each get a check that can fail; the
precondition is a tracked item; the burst hard maximum is computed; capability checks carry measurement definitions.
In part: the deliverable-style criteria were rewritten as checks, but the proposed prose lint (an AC "only recorded"
must name a pass rule; a non-owner ticket mentioning a real keeper must say test-mode) was not added, because matching
prose that way is fragile; reviewers keep that rule.

**Licensing safety (24 applied).** Imports are owner acts whose uses follow their source, DAW bounces inherit the lanes
and license chains of the exports they contain, and detected Suno marks force source Suno (`use.import_terms`);
`license-acceptance/1` records every weights acceptance, gated or not, with YuE2's four pinned documents (amended 2026-11-07); weights sources cover
pinned URLs and packages (`license.weights_pin`); individual and llc forbid an UNVERIFIED license; transcribed melodies
carry lanes (`lane.record_eligible`); manifests carry release blockers (`release.manifest_blockers`); internal
`separate` and exportable `isolate` profiles are distinct; owner-ui sessions cannot leak to agents (TTY-only token, test
store guards); the RunPod key is out of the runner's reach and the prepaid balance is a backstop; reconciliation can
raise the ledger (`reconcile_adjustment`); NC scorers follow O-06; the license lint is an allowlist; the Rule-07 lint is
exact; the worker protocol admits before any asset moves; Basic Pitch is narrowed; DSP finishing follows O-08 and covers
Suno stems; secrets are scanned repo-wide; the env script refuses an unmounted volume and git objects stay on STUDIO.

**Cross-document consistency (25 applied).** A pin change computes to `declared`; the spec's shape blocks follow the
schemas; `audition-session/1` became `audition/1` with `audition_id`; either arm may be kept after a tie; tier rules,
placement terms, badge strings, figure labels, the benchmark-set wording, job kinds, `stream:*` labels, the pnpm
`storeDir`, auditions across requests, the preservation check, ADR filenames and row counts, retention classes and the
quote refusal reasons now agree everywhere.

**Applied in a different form than proposed (9).** (1) RoFormer and Basic Pitch were narrowed in the register overlay
with a new `unverified_training_data` blocker class (forbidden in llc only), not in `evidence-register.json`, which stays
the verified research record. (2) The real repaint check runs as an agent ticket on a temporary store with a real ACE
render and a test-mode verdict (labelled "hardware, non-listening"), not on Jon's keeper, so it needs no owner gate.
(3) `studioctl` discovery lives in the foundation ticket, not the durability ticket, because only the foundation ticket
is an ancestor of every CLI ticket. (4) The paid-run gate's split keeps the approval API with the reservation it guards;
only the O2 dialog, the decline label and `studioctl quote` moved. (5) The integration skeleton stops at admission,
dispatch, measurement and closure, because auditions, keepers and exports do not exist until later tickets. (6) Enum
additions (`tts`, `isolate`, `dsp-finish` and the other tasks), `render_mode`, route-standing and plan rules go to the
contract ticket as additive changes; contracts that were wrong were corrected now. (7) The store-export hash check is
part of `studioctl evidence export` (registry ticket), since `validate.py` has no store. (8) WhisperX's row was not
split; the LLC alignment profile declares English only. (9) Jon's acceptance of the spec and of ADR-0025…0037 cannot be
recorded by an agent, so the ticket set is labelled a draft until he gives it.

**For Jon.** Accept or amend the spec and ADR-0025…0037; decide whether Demucs-isolated stems may be released; confirm
tier 3 for 16–23.5 GiB cards and the plan-rules route order; run P01; note that agents still run as his macOS user, so
the presence-gated keychain item, the runner's separate user and the prepaid-balance backstop are the controls on the
RunPod key.

Contact for the project, as text only: `hello@islanddevcrew.com`
