# SQLite is the system of record, and every immutable record and provenance sidecar is also content-addressed JSON, so the database can be rebuilt

Status: accepted (2026-10-09) with the v1 architecture. It amends ADR-0009 (D-09) and resolves tension T-01.

D-09 chose SQLite. A longevity proposal argued that objects should be the sole truth. The store sits on a single
spinning HDD that can be ejected uncleanly.

**Decision.**

- **SQLite is the system of record** that the control service reads and writes: WAL mode, numbered SQL migrations,
  `synchronous=FULL`, and `fullfsync=ON` plus `checkpoint_fullfsync=ON` on macOS. It holds projects, revision heads,
  the artifact index, jobs, events, sessions, quotes, approvals, burst runs, the ledger, verdicts and evidence. A
  `.backup` snapshot is taken nightly and after every keeper.
- **Records and sidecars.** Every immutable domain record (MelodySpec and SongSpec revisions, verdicts, keepers, export
  manifests, evidence, reference permissions, risk acceptances) is also written as **canonical JSON** under
  `records/sha256/…`, and every artifact blob has a `<sha>.prov.json` **provenance sidecar**, both in the same unit of
  work as their rows. Canonical JSON is UTF-8 with sorted keys, no insignificant whitespace and **integers only**.
  Non-integer quantities (LUFS, dBTP, cents, prices) are decimal strings with declared precision, so Python and
  TypeScript hash identically.
- **Unit of work**: blob, then sidecar or record, then rows and events, committed atomically. A crash leaves at most
  unreferenced blobs, which the startup recovery scan quarantines.
- **`reindex`** rebuilds artifact and record rows and revision heads from sidecars and records. Operational state
  (jobs, ledger, sessions) lives only in SQLite. A lost database loses only in-flight jobs, which fail on restart
  anyway, and ledger lines can be rebuilt from provider billing.
- A single-writer `LOCK` stops a second `serve`. `docs/FORMAT.md` documents the layout so a project is readable
  without AURA's code.

**Why.** It keeps D-09's simple system of record and still gets the main benefit of the objects-as-truth proposal: no
song is lost with the database.

## Considered Options

- **The store as the sole truth, with SQLite only an index.** Rejected: it needed an ADR fight before the first
  ticket, and writing records and sidecars in the same unit of work gives the same protection.
- **Merkle snapshot revisions, `.aurapack` packs, RFC 8785.** Rejected for now: P0 weight with nothing yet paying for
  it.

## Consequences

The P1 exit check deletes `studio.sqlite`, runs `reindex`, and compares the durable rows and heads for equality.

**Reverse if:** multi-user sharing needs a server store (ADR-0009).

Evidence: [architecture.md](../spec/architecture.md) §4.2, §8.2, §13.2, §13.3, §13.4 (T-01), §11 (P1-9).
[RECONCILIATION.md](../research/RECONCILIATION.md) §6 D-09.
