# Bookmark Intelligence Documentation

`../PROGRESS.md` is the canonical current status. Checkboxes and delivery claims
inside archived or dated plans are not implementation evidence.

## Document Map

| Classification | Documents |
| --- | --- |
| Current truth | [`../README.md`](../README.md), [`../PROGRESS.md`](../PROGRESS.md), [`run.md`](run.md) |
| Current roadmap | [`roadmap.md`](roadmap.md) |
| Current review | [`dev/research/2026-07-26-repository-goal-openclaw-integration-review.md`](dev/research/2026-07-26-repository-goal-openclaw-integration-review.md) |
| Active plan | [`dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md`](dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md) |
| Current implementation | [`dev/implementation/2026-07-26-memory-desk-daily-flight.md`](dev/implementation/2026-07-26-memory-desk-daily-flight.md) |
| Earlier implementation snapshot | [`dev/implementation/2026-07-06-devcld-local-workspace.md`](dev/implementation/2026-07-06-devcld-local-workspace.md) |
| Export evidence snapshot | [`dev/research/2026-07-06-bookmark-growth-navigation-retention.md`](dev/research/2026-07-06-bookmark-growth-navigation-retention.md) |
| Future product vision | [`overview.md`](overview.md), [`features.md`](features.md), future sections of [`architecture.md`](architecture.md), [`reference.md`](reference.md) |
| Experimental backend/AI | [`dev/DATABASE_SETUP.md`](dev/DATABASE_SETUP.md), dated plans under `dev/plans/`, and `specs/` |
| Archived | [`archive/`](archive/) |

## Current Product

The implemented product is the Phase 0C local-first Memory Desk:

```text
HTML import
  -> canonical retained records in IndexedDB
  -> finite daily flight over All Memory
  -> Library, bulk review, map, duplicates, review queue
  -> context, saved views, session/activity-aware backup and restore
```

FastAPI, PostgreSQL, Qdrant, Valkey, hosted synchronization, the extension,
and bulk AI processing are target or experimental architecture. They are not
current delivery status.

## Documentation Rules

- Update `../PROGRESS.md` when current stage, evidence, risks, or the exact next
  slice changes.
- Update `roadmap.md` when a gate opens or closes.
- Use dated research, plans, and implementation notes for evidence and history.
- Preserve old product plans under `archive/` rather than presenting them as
  current.
- Never put private exports, backups, or generated personal data in docs.

## Historical Material

- Original specification: [`archive/spec-v1.md`](archive/spec-v1.md)
- 2025 roadmap: [`archive/2025-10-27-roadmap-v1.md`](archive/2025-10-27-roadmap-v1.md)
- 2025 progress snapshot: [`archive/2025-12-03-progress.md`](archive/2025-12-03-progress.md)
- Backend-first run guide: [`archive/2025-12-03-run-v1.md`](archive/2025-12-03-run-v1.md)
