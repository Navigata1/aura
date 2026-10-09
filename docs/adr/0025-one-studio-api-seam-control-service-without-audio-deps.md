# One product seam: the Studio API, served by a control service with no audio or ML dependencies

Status: accepted (2026-10-09) with the v1 architecture (architecture.md §13.5). No owner decision touches it.

The browser, the CLI, the test harness, the eval harness and agents all need the same product behaviour. The control
service must run on three operating systems, while the engines need conflicting torch pins.

**Decision.**

- The control service's HTTP and SSE **Studio API** (`/api/v1/…`) is the only product seam. Every client uses it,
  including the eval harness, which has no private path to the store.
- Behind it sit six deep, in-process modules: **ProjectStore** (the durable truth), **Conductor** (durable jobs),
  **Registry** (what may run, in which lane, at what evidenced status), **Placement** (where it runs and what it costs,
  including the burst broker and ledger), **Score** (pure composition semantics) and **Audition** (blind,
  level-matched A/B). The API module itself is deliberately thin: it validates contracts at the edge and maps module
  errors to typed problem responses.
- **The control service carries no audio or ML dependencies.** All DSP and inference runs in worker processes, and
  analysis runs in the CPU-only analysis worker.
- The API binds 127.0.0.1, with a Host allowlist and an Origin check on every state change. Authority is split into
  owner-ui and automation scopes (ADR-0031). Secrets, worker tokens and burst URLs never cross the API.
- Tests target this seam: StudioHarness runs pytest against the real app on an ephemeral port. Fakes exist only at real
  boundaries: FakeEngine and the analysis worker as real subprocesses, FakeBurstProvider, recorded hardware probes and
  an injectable clock. No test mocks an internal collaborator.

**Why.** With one seam, every client exercises the same surface, and pure Score logic is reachable through it without a
second test seam. Keeping audio and ML out of the control service keeps it light, portable and free of torch pins.

## Consequences

A product feature that cannot be expressed as a Studio API resource plus a job does not exist. Playwright drives the
same seam through the browser; it is another way in, not another seam.

**Reverse if:** a feature needs in-process audio in the control service that a worker cannot provide. None does today.

Evidence: [architecture.md](../spec/architecture.md) §1, §4.1, §4.3–§4.7, §6.1, §13.1.
[RECONCILIATION.md](../research/RECONCILIATION.md) §2 C41; §6 D-12.
