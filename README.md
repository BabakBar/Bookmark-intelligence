# Bookmark Intelligence

Trusted personal bookmark memory for preserving context, reviewing what should
stay, and rediscovering useful material when it matters.

## Current Phase

**Phase 0C - Daily Memory Workflow Validation**

The supported product is the browser-local Memory Desk in `frontend/`.
It does not require the experimental backend or paid AI services.

- Import browser bookmark HTML directly in the browser
- Retain canonical bookmark records in IndexedDB
- Start with a finite, explainable daily flight across all retained memory
- Preserve daily progress, review state, status, notes, and keep reasons
- Explore all records or optional `Dev` and `Cld` scopes
- Review duplicate/canonical URL merges and export/restore local review state as JSON
- Triage with local topic/provider/content inference and a prioritized review queue
- Apply bounded bulk decisions with one-step undo until reload or the next action
- Add personal tags, save recurring views, and track app-mediated opens locally

Current stack: React 19, Vite 7, Dexie/IndexedDB, TanStack Table, React Flow,
and Playwright.

## Privacy Boundary

Raw bookmark exports and workspace backups are private local data. Do not
commit them or place them in chat, Obsidian, OpenClaw sessions, or coding
worktrees.

## Experimental Path

FastAPI, PostgreSQL, Qdrant, Valkey, batch AI enrichment, a browser extension,
and hosted synchronization are preserved as experimental/future work. They are
not the current runtime and are not ready for deployment.

OpenClaw may later orchestrate append-only capture and review proposals, but
it is optional. Bookmark Intelligence remains the owner of canonical records
and retention state.

## Start Here

- Current status: [`PROGRESS.md`](PROGRESS.md)
- Run and verification: [`docs/run.md`](docs/run.md)
- Current roadmap: [`docs/roadmap.md`](docs/roadmap.md)
- Review evidence:
  [`docs/dev/research/2026-07-26-repository-goal-openclaw-integration-review.md`](docs/dev/research/2026-07-26-repository-goal-openclaw-integration-review.md)
- Active implementation plan:
  [`docs/dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md`](docs/dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md)
- Current implementation:
  [`docs/dev/implementation/2026-07-26-memory-desk-daily-flight.md`](docs/dev/implementation/2026-07-26-memory-desk-daily-flight.md)
