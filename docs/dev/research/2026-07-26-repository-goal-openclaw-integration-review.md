# Research: Repository Goal, Current Condition, and OpenClaw Fit

**Date:** 2026-07-26

**Status:** Complete

**Scope:** Current repository, local-first workspace, legacy backend/AI path, and the integration boundary with `openclaw-ops`

> **Outcome update:** The integrity gaps identified below were repaired later
> on 2026-07-26, and the product expanded into the All Memory daily Memory
> Desk. See `../implementation/2026-07-26-memory-desk-daily-flight.md` and
> `../../../PROGRESS.md`. Findings below remain the pre-implementation snapshot.

## Goal

Bookmark Intelligence should turn Sia's bookmark collection into trusted,
active personal working memory:

- preserve why a bookmark matters;
- make known material quick to find;
- surface useful material in the context of current work;
- support review, archive, and duplicate decisions without losing history;
- use AI as a reviewable enrichment layer rather than an automatic owner of
  bookmark state.

The immediate product is personal and local-first. A multi-user service,
browser extension, synchronized backend, and hosted semantic search remain
possible future directions, not current implementation facts.

## Current Source of Truth

The working product is the browser-local Dev/Cld workspace in `frontend/`.

```text
Bookmark HTML
  -> browser parser
  -> canonical URL and local metadata
  -> IndexedDB via Dexie
  -> explorer, mind map, duplicate review, review queue
  -> notes, tags, status, saved views, JSON backup
```

The July 2026 export contains 936 raw bookmark instances. The local importer
retains 912 canonical records, including 540 records in the combined Dev/Cld
scope.

IndexedDB is authoritative for the current workspace. The private HTML export,
workspace backups, and generated analysis are user data and do not belong in
Git or an OpenClaw coding worktree.

## Repository Condition

### Working and verified

- Bookmark HTML parsing in the browser
- Canonical URL retention
- Dev/Cld filtering and table exploration
- Bounded mind map
- Duplicate review and prioritized review queue
- User notes, keep reasons, tags, status, and review state
- Saved views
- Versioned JSON backup and restore
- Python parser/extractor tests
- Frontend lint and production build
- One browser smoke test against the private July export

### Implemented but insufficiently protected

- Bookmark detail editing can retain uncontrolled input values when the
  selected bookmark changes, risking a write to the wrong record.
- Backup restore validates only the outer shape before overwriting records.
- Import history is written before the bookmark transaction completes.
- URL import accepts schemes beyond the intended web protocols.
- The browser test depends on a private untracked export and a manually started
  development server, so it is not portable to a clean clone or CI.

### Experimental and not deployable

The FastAPI, PostgreSQL, Qdrant, Valkey, and AI pipeline path is preserved as
an experiment. It is not the current product runtime.

Blocking findings include:

- backend import and parser field contracts do not match;
- no Alembic migration versions exist;
- AI runtime dependencies are not declared in the locked project;
- AI stage resume and export discovery are not reliable;
- backend ownership, authentication, upload limits, and integration tests are
  absent;
- Docker and health-check configuration do not constitute a production
  deployment boundary.

No backend deployment or cost-bearing AI run should start until a later plan
explicitly repairs and verifies those gates.

## Documentation Condition

The repository contains two generations of product direction:

1. the current local-first retention workspace;
2. an older hosted SaaS/browser-extension architecture.

`PROGRESS.md`, `docs/run.md`, `docs/roadmap.md`, and parts of
`docs/architecture.md` describe experimental or future work as complete.
Canonical documentation must distinguish current, experimental, and future
surfaces.

## OpenClaw Fit

OpenClaw should be the phone-facing control plane, not the bookmark datastore.

The current `openclaw-ops` repository reports:

- M1/M2 deployed for user context, GitHub reads, and create-only Obsidian inbox
  capture;
- M3 coder/reviewer staged but not deployed;
- only `sia-website` and `BoringHannover` approved for the first coder canaries.

Bookmark Intelligence must not be added to the coder worktree or push wrapper
until those canaries pass and Sia separately approves the new repository
authority.

The safe sequence is:

1. use current GitHub read and inbox capture as a project concierge;
2. keep private bookmark data outside OpenClaw workspaces;
3. stabilize the local workspace;
4. complete the existing OpenClaw coder canaries;
5. add Bookmark Intelligence as a separately reviewed coder module;
6. later expose an app-owned, append-only bookmark candidate boundary;
7. isolate untrusted webpage reading and cost-bearing enrichment in separate
   specialists.

OpenClaw may propose tags, summaries, review priorities, and candidates.
Bookmark Intelligence validates and owns all persisted state.

## Decision

The next development stage is:

> **Phase 0B - Local-First Retention Workflow Validation**

Work proceeds in small verified slices:

1. editor integrity and portable browser testing;
2. backup/import integrity;
3. real-use workflow validation;
4. bounded OpenClaw readiness;
5. small gold-set AI evaluation;
6. backend or synchronization only after measured need.
