# Workers speak one HTTP protocol, the control service is always the client, and the worker SDK is stdlib-only

Status: accepted (2026-10-09) with the v1 architecture. It gives D-03's job protocol a transport.

The same engine must run as a local subprocess on the Mac, on a tailnet CUDA box, and on a rented pod behind NAT that
the Mac cannot be called back from. Engines need conflicting Python and torch versions.

**Decision.**

- **One HTTP worker protocol, v1**, with versioned contracts `worker-describe/1`, `task-request/1`, `task-status/1` and
  `refusal/1`. The complete route list is `GET /v1/describe`, `GET /v1/health`, `PUT|HEAD|GET /v1/assets/{sha256}`,
  `POST /v1/jobs`, `GET /v1/jobs/{id}`, `GET /v1/jobs/{id}/events`, `GET /v1/jobs/{id}/outputs/{role}`,
  `POST /v1/jobs/{id}/cancel` and `POST /v1/unload`. Anything else returns 404.
- **The control service is always the client.** Workers never call it. Through a provider's proxy it polls with short
  requests.
- **Submit first, then assets.** `POST /v1/jobs` comes first: the worker checks lane, task, limits, weights and memory
  and returns `202 awaiting_inputs` or a `422` refusal before any asset moves. Then the control service PUTs only the
  missing assets (HEAD first), each accepted only for an admitted `job_id` that lists its hash, and the job starts once
  its inputs are present. A refused request never receives a byte, so a control-side admission bug cannot leak an llc
  project's melody to a rented machine.
- **Assets move by reference**: inputs and outputs travel by SHA-256, never as paths or URLs. A worker's only network
  fetch is its profile's pinned weights (a Hugging Face revision, a pinned URL with sha256, or a file in a pinned
  package).
- **Refuse before load**: `422 Refused{code}` for `unsupported_task`, `lane_forbidden`, `over_limit`,
  `language_unsupported`, `weights_missing`, `insufficient_memory`, `insufficient_disk` or `busy`, before any model is
  imported. Submitting is idempotent on `job_id`.
- **No shell.** Parameters are validated per task and never interpolated into command lines. Workers write only inside
  their scratch directory.
- **Auth**: a bearer token per spawn (local), per pairing (tailnet) and per lease (burst). Tokens never reach the
  browser. Workers bind loopback or the tailnet interface, or sit behind the provider's HTTPS proxy.
- **The worker SDK** (`studio_worker`) is stdlib-only on Python 3.10 and later, so it installs into every pinned
  environment, including Basic Pitch's Python 3.10. It validates messages against the shared schemas with a bundled
  subset checker, keeps an asset cache and a crash journal, honours cancel within 5 s, runs a parent-death watchdog for
  local spawns, and **measures timings and peak memory itself**, so a speed number is MEASURED-LOCAL by construction.
  An engine author writes four methods: `describe`, `prepare`, `run` and `unload`.
- **Conformance** runs against every worker, and seven mutant workers must each fail it: one that loads before
  refusing, one that misdeclares its sample rate, one that returns a wrong output hash, one that ignores cancel, one
  that fabricates a percentage, one that goes silent, and one that answers an undeclared route.

**Why.** HTTP is the only transport that works unchanged on loopback, over a tailnet and to a pod behind NAT. A
stdlib-only SDK is the only way one protocol implementation fits every pinned environment.

## Considered Options

- **Two transports**, stdio NDJSON locally plus WebSocket remotely. Rejected: it doubles the protocol and conformance
  surface. The parent-death watchdog and per-spawn tokens cover stdio's advantages.
- **Workers calling back to the control service.** Rejected: a pod behind NAT cannot be reached that way.
- **Workers importing the control service's models.** Rejected: it would drag the control service's dependencies into
  every torch environment.

## Consequences

FakeEngine, the analysis worker, the separator, ACE, YuE2 and Basic Pitch are all adapters at this seam. Conformance
transcripts are golden fixtures.

**Amended in the 2026-10-09 design review** (architecture.md, "Design review log"). Conformance gains an eighth mutant that accepts assets before admission, and a test that a lane-forbidden request receives no asset bytes.

**Reverse if:** a provider offers no HTTPS ingress at all. The pod-reachability spike in P3 decides.

Evidence: [architecture.md](../spec/architecture.md) §1, §2 (stack departure 2), §4.8, §6.2, §9.2, §13.3.
[RECONCILIATION.md](../research/RECONCILIATION.md) §5 (GPT 6); §6 D-03.
