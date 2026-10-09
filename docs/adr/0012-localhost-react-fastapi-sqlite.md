# A localhost browser app: Vite, React and TypeScript over a FastAPI control service with SQLite, durable jobs and SSE

Status: accepted (2026-10-09). From D-12, amended by the v1 architecture: JSON Schema is the source of truth, the
control service serves the built app, and jobs gain an `awaiting_approval` state. Requiring a Chromium-based browser for
the Studio is **proposed**, the owner-pending default (Q10).

AURA is a single-user tool on Jon's own machines. All three sources converged on a browser UI on localhost, FastAPI,
SQLite metadata and Python workers with SSE progress. Web Audio quality differs sharply by browser engine: WebKit
ignores `latencyHint` and has no `setSinkId`.

**Decision.**

- **UI**: Vite, React and TypeScript, with no SSR and no Next.js. The control service serves the built `dist/` from its
  own origin with COOP/COEP headers, so there is no CORS, no Node at runtime, and SharedArrayBuffer is available to the
  StudioEngine. The app uses only the generated typed client.
- **Control service**: Python 3.12, FastAPI, one uvicorn process, stdlib `sqlite3` in WAL mode, and **no audio or ML
  dependencies** (ADR-0025). It binds 127.0.0.1.
- **Contracts**: JSON Schema 2020-12 in `contracts/` is the source of truth. Pydantic and TypeScript types are
  generated from it, with a drift check in CI.
- **Jobs**: a durable SQLite `jobs` table with the states `queued`, `awaiting_approval`, `preparing`, `loading`,
  `generating`, `analyzing`, `ready`, `failed` and `cancelled`. Progress shows real steps; an index and total appear
  only when an engine reports real counters. Outputs commit atomically. SSE events resume with `Last-Event-ID`.
- **Workers**: Python processes, each engine in its own pinned `uv` project (ADR-0016), reached over the worker
  protocol (ADR-0026).
- **Browser**: a Chromium-based browser is required for the Studio (Q10 default). Safari and WKWebView are not
  supported for Studio playback.
- **UX**: listening-first, with a large audition area, level-matched A/B, progressive disclosure, and controls only
  where a profile implements them. No imitation of Suno's branding or look; standard names (Cover, Extend, Replace)
  where they help. The footer shows the public contact as text (ADR-0037).

**Why.** The sources agree on the shape (A7). An asyncio queue alone loses jobs on restart (C41). Next.js adds SSR and
routing that a local single-user tool does not need (C38). Chromium's audio stack is the only measured fit (C39). C49
sets the UX direction.

## Considered Options

- **Next.js 15 with Tailwind and shadcn** (Fable). Workable, but carries SSR and routing weight that nothing pays for.
- **A desktop app first.** Deferred (ADR-0014).
- **`asyncio.Queue` for jobs** (Kimi). Rejected: jobs vanish on restart.

## Consequences

Every product feature reaches the UI through one API (ADR-0025), so the browser, the CLI, the test harness and the eval
harness exercise the same surface. pnpm's store lives on the studio volume (ADR-0034).

**Reverse if:** an installable app is needed sooner (add the ADR-0014 shell), or Jon rejects the Chromium requirement
(Q10), which would bring a native or Electron Studio forward.

Evidence: [RECONCILIATION.md](../research/RECONCILIATION.md) §1 A7; §2 C38, C39, C41, C49; §4.7; §6 D-12.
[evidence-register.json](../research/evidence-register.json) V-ui-1, V-ui-2.
[architecture.md](../spec/architecture.md) §1, §2 (stack departures), §4.1, §4.11, §9.1.
