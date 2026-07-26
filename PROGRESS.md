# Bookmark Intelligence Status

**Updated:** 2026-07-26

**Phase:** Phase 0C - Daily Memory Workflow Validation

**Deployment:** None; browser-local application

**Canonical store:** IndexedDB through Dexie

This is the canonical current status. Dated research and plans preserve
evidence, but verified application behavior overrides older delivery claims.

## Product Direction

Bookmark Intelligence is a private **Memory Desk**, not just a bookmark
catalog. It turns a large, aging collection into a small daily practice:

- show the full retained collection by default;
- explain why a record is resurfacing;
- preserve decisions and personal context;
- make high-volume cleanup safe and reversible;
- let AI and OpenClaw become optional helpers later, never owners of the data.

The July 2026 export contains 936 raw instances and 912 canonical retained
records. The older Dev/Cld default exposed only 540 records. `All Memory` is
now the default so the other 372 records are no longer silently hidden.

## Current Product

```text
browser bookmark HTML
  -> HTTP(S)-only parsing and canonicalization
  -> deterministic local signals
  -> transactional IndexedDB retention
  -> Today / Library / Mind Map / Duplicates / Review Queue
  -> versioned local backup and restore
```

### Today

The new landing surface creates a finite, deterministic daily flight of at
most six records. Every card includes a reason derived from retained evidence:

- time-sensitive decision;
- merge evidence;
- learning thread;
- missing personal context;
- useful record not opened through this workspace;
- unreviewed durable reference.

The exact daily deck, progress, action counts, and completion state persist
across reloads. Keep, Learning, Later, and Archive are transactional. Later
snoozes the record for three days. Opens initiated by the application record
only an honest local open event.

### Library and Review

- Full collection is the default scope; Dev, Cld, and Dev+Cld remain filters.
- Table, filters, saved views, mind map, duplicate review, and review queue
  remain available.
- Multi-select review supports Keep, Learning, and Archive for up to 1,000
  visible records at once.
- Bulk updates fail atomically if any selected record is missing.
- The most recent bulk action has one-step undo until reload or the next bulk
  action. Undo fails closed if any affected record changed afterward.
- Selection-bound detail editors prevent values leaking between records.

### Trust and Portability

- HTML imports and import history commit in one transaction.
- Only HTTP and HTTPS URLs without embedded credentials are retained.
- Import and backup files have a 25 MB application safety limit.
- Version 3 backups include bookmarks, import history, saved views, daily
  sessions, activity events, and metadata.
- Restore validates sizes, types, enums, URLs, unique keys, counts, and
  bookmark/import/session/event references before writing anything.
- Restore remaps import IDs and preserves existing local manual decisions when
  a backup overlaps a retained record.
- Local signal version 2 fixes the prior taxonomy defect that classified
  almost every HTTPS URL as networking.
- The heavy graph view is loaded only when Mind Map is opened.

## Verified Evidence

Current frontend gates:

```text
bun run test:unit   7 passed
bun run lint        passed
bun run build       passed; initial bundle 401.82 kB, map split separately
bun run test:e2e    7 passed
```

Browser acceptance covers:

- synthetic import with records outside Dev/Cld;
- all-memory and topic filters;
- saved views and version 3 backup export;
- map, duplicate, and review surfaces;
- cross-bookmark editor isolation across reload;
- malicious URL rejection and local-state-preserving restore;
- persistent finite daily flight;
- transactional bulk review and undo.

Desktop and 390 px mobile screenshots were visually inspected after importing
the synthetic fixture. The Memory Desk, Daily Flight, actions, and Collection
Pulse remained readable and operable at both sizes.

The preserved Python parser/extractor suite passes 18 tests. The legacy Python
backend still has 16 Ruff findings and a mypy duplicate-module configuration
failure; neither affects the supported browser-local runtime.

## Active Validation

The software slice is complete enough for real use. Development does not wait
on OpenClaw or a hosted backend. The next evidence comes from using the private
collection locally:

- complete daily flights and observe whether six cards is the right ceiling;
- measure five known-item retrievals;
- note useful rediscoveries and false-positive resurfacing reasons;
- perform a real backup, clear, and restore drill;
- identify repeated capture friction before adding an inbox;
- select a small, consented gold set before any paid AI enrichment.

Product tuning can continue from this evidence without an approval pause.
Destructive automation, external data transfer, deployment, and paid
collection-wide processing remain separate decisions.

## Privacy Boundary

Raw exports, JSON backups, notes, and activity history are private local data.
Do not commit them or place them in Telegram, Obsidian, OpenClaw sessions,
coding worktrees, or provider prompts. The committed E2E fixture is synthetic.

## OpenClaw Boundary

OpenClaw is optional future orchestration:

- Bookmark Intelligence owns canonicalization, retention, review, and storage.
- The first integration should be an append-only candidate inbox.
- OpenClaw may propose tags, summaries, or resurfacing candidates, but cannot
  directly mutate retained records.
- Private exports and backups do not enter OpenClaw.
- No OpenClaw dependency blocks local product work.

## Experimental Quarantine

`src/app/`, PostgreSQL, Qdrant, Valkey, Alembic, batch AI, the extension, and
Coolify deployment are preserved research paths, not the current runtime.
They are not production-ready and should not receive private data or provider
credentials without a new plan covering ownership, migrations, integration
tests, authentication, backups, rollback, privacy, and measured need.

## Current References

- Runbook: [`docs/run.md`](docs/run.md)
- Roadmap: [`docs/roadmap.md`](docs/roadmap.md)
- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Active plan:
  [`docs/dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md`](docs/dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md)
- Memory Desk implementation:
  [`docs/dev/implementation/2026-07-26-memory-desk-daily-flight.md`](docs/dev/implementation/2026-07-26-memory-desk-daily-flight.md)
