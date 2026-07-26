# Implementation: Dev/Cld Local-First Workspace

> **Implementation snapshot.** This records the state shipped on 2026-07-06.
> Current risks, priorities, and verification live in
> [`../../../PROGRESS.md`](../../../PROGRESS.md).

**Date:** 2026-07-06  
**Status:** Implemented and browser-smoke-tested  
**Scope:** Frontend live workspace for the large `Dev` and `Cld` bookmark folders

## Problem

The July 2026 bookmark export shows that `Dev` and `Cld` are now the main maintenance pressure:

- Raw export: 936 parsed bookmark instances
- `Dev`: 260 raw bookmark instances
- `Cld`: 285 raw bookmark instances
- Combined `Dev + Cld`: 545 raw bookmark instances

A folder tree alone is no longer enough because the same bookmark can matter by folder, domain, topic, provider, certification, project, and review state.

## Implemented Direction

The frontend now has a local-first Dev/Cld workspace.

The browser imports a bookmark HTML export directly, normalizes URLs, and stores retained bookmark records in IndexedDB. The UI updates live from that store through Dexie live queries.

This is intentionally separate from the future PostgreSQL/Qdrant backend. The current goal is fast, private, reviewable organization before cost-bearing AI enrichment or backend migration.

## Architecture

```text
Bookmark HTML export
        |
        v
Browser parser
        |
        v
Canonical URL normalization
        |
        v
Heuristic provider/topic/content inference
        |
        v
IndexedDB via Dexie
        |
        +--> Dev/Cld explorer table
        +--> Filtered live mind map
        +--> Duplicate/canonical review
        +--> Focused review queue
        +--> Bookmark detail + retention controls
        +--> User tags + saved filter views
        +--> JSON backup export/restore
```

## Data Model

Primary store: `bookmarks`

Key field:

- `canonicalUrl`: primary key

Retained fields:

- `url`
- `title`
- `titleLower`
- `domain`
- `addedAt`
- `sourceUrls`
- `rawInstanceCount`
- `topics`
- `userTags`
- `provider`
- `contentType`
- `reviewPriority`
- `inferredAt`
- `originalFolders`
- `folderPaths`
- `rootFolders`
- `firstSeenAt`
- `lastSeenAt`
- `importIds`
- `status`
- `reviewState`
- `userNote`
- `keepReason`
- `createdAt`
- `updatedAt`

Import history store: `imports`

- `id`
- `fileName`
- `importedAt`
- `totalCount`
- `devCount`
- `cldCount`

Saved view store: `savedViews`

- `id`
- `name`
- `filters`
- `createdAt`
- `updatedAt`

## Retention Behavior

Repeated imports upsert by `canonicalUrl`.

Preserved across imports:

- review state
- status
- user note
- keep reason
- first seen timestamp
- merged folder context

Updated on later imports:

- title
- domain
- current URL
- last seen timestamp
- import history
- original folders
- source URL variants
- raw instance count
- heuristic metadata (`topics`, `provider`, `contentType`, `reviewPriority`)
- user tags

## URL Canonicalization

The importer removes URL fragments, normalizes `www.`, sorts query params, trims trailing path slashes, and removes common tracking params such as `utm_*`, `fbclid`, `gclid`, `igshid`, `mc_cid`, `mc_eid`, `ref`, and `spm`.

For the July 2026 export this produces:

- 936 raw parsed bookmark instances
- 912 retained canonical records
- 259 retained `Dev` records
- 281 retained `Cld` records
- 540 retained `Dev + Cld` records

These numbers differ from raw folder counts because duplicate and tracking-variant URLs collapse into canonical retained records.

## UI

The first screen is the usable workspace:

- import bookmark HTML
- clear local workspace
- total, Dev, Cld, review, filtered, and multi-folder stats
- root scope filter: `Dev + Cld`, `Dev`, `Cld`
- text search
- folder/domain/review/status filters
- topic/provider/content-type filters
- user-tag filter
- top domain shortcuts
- saved views for recurring filter sets
- import history
- sortable bookmark table
- filtered live mind map
- duplicate/canonical review view
- focused review queue
- JSON backup export
- JSON backup restore
- bookmark detail panel
- retention controls:
  - `reviewState`
  - `status`
  - `keepReason`
- `userNote`
- `userTags`

## Mind Map Design

The mind map is intentionally filtered and bounded.

For broad scopes, it shows top roots, folders, and domains. It only shows individual bookmark nodes when the current filter narrows the result set to 35 or fewer records. This avoids a 500-node visual tangle while still supporting live exploration.

## Duplicate Review

The `Duplicates` view lists canonical records that need a merge or retention decision.

A record appears when any of these are true:

- it appears in multiple folders
- it has multiple source URL variants
- the latest import contained multiple raw instances collapsed into one canonical URL

The view shows:

- duplicate reason
- canonical URL
- raw instance count
- merged folder list
- source URL variants

Actions:

- `Keep`: sets `reviewState=keep` and `status=active`
- `Archive`: sets `reviewState=archive` and `status=archived`
- `Delete candidate`: sets `reviewState=delete-candidate` and `status=delete-candidate`

## Backup And Restore

The workspace can export and restore its retained local state as JSON.

Backup format:

```json
{
  "schema": "bookmark-intelligence-workspace",
  "version": 2,
  "exportedAt": "2026-07-06T00:00:00.000Z",
  "counts": {
    "bookmarks": 912,
    "imports": 1,
    "savedViews": 1
  },
  "bookmarks": [],
  "imports": [],
  "savedViews": []
}
```

Restore validates the schema/version and upserts retained records into IndexedDB. Version 1 backups are still accepted, with no saved views. This preserves review work across browser profiles or before clearing local data.

## Heuristic Inference

The workspace now infers lightweight metadata without AI calls:

- `topics`: examples include `aws`, `azure`, `kubernetes`, `terraform`, `ai-agents`, `python`, `go`, `self-hosting`, `certification`
- `provider`: examples include `AWS`, `Azure`, `Google Cloud`, `GitHub`, `Reddit`, `YouTube`, `HashiCorp`
- `contentType`: examples include `repository`, `video`, `discussion`, `course`, `documentation`, `tool`, `reference`
- `reviewPriority`: `merge-review`, `time-sensitive`, `durable-reference`, or `normal`

These fields are derived from title, URL, domain, and folder path. They are intended as a fast local triage layer before AI enrichment. Existing local records are backfilled when the app opens.

## Review Queue

The `Review Queue` view sorts current filtered records for practical cleanup:

1. canonical merge/duplicate candidates
2. time-sensitive certification or interview material
3. durable references such as docs and repositories
4. normal records

It excludes records already marked as delete candidates and keeps quick actions visible:

- `Keep`
- `Learning`
- `Archive`
- `Delete candidate`

## User Tags And Saved Views

User tags are editable per bookmark in the detail panel. They are comma-separated, normalized to lowercase, indexed in IndexedDB, included in search, and preserved across future bookmark imports.

Saved views persist the active filter state:

- root scope
- folder
- domain
- topic
- provider
- content type
- user tag
- review state
- status
- search query

This supports repeat workflows such as `AWS cert cleanup`, `Self-hosting review`, or `AI agents keep/archive` without reconfiguring filters every session.

## Key Files

- `frontend/src/App.jsx`
- `frontend/src/bookmarkImport.js`
- `frontend/src/db.js`
- `frontend/src/bookmarkSignals.js`
- `frontend/src/BookmarkTable.jsx`
- `frontend/src/BookmarkMap.jsx`
- `frontend/src/DuplicateReview.jsx`
- `frontend/src/ReviewQueue.jsx`
- `frontend/src/App.css`
- `frontend/e2e/devcld-workspace.spec.js`

## Dependencies

Runtime:

- `dexie`
- `dexie-react-hooks`
- `@tanstack/react-table`
- `@xyflow/react`

Verification:

- `@playwright/test`

## Verification

Commands:

```bash
cd frontend
bun run lint
bun run build
bunx playwright test e2e/devcld-workspace.spec.js
```

Results on 2026-07-06:

- lint passed
- build passed
- Playwright smoke test passed

Build note:

Vite reports one chunk above 500 kB after adding the table and graph stack. This is acceptable for the current local tool. If production performance becomes a priority, split the map view with a dynamic import.

## Next Steps at Time of Implementation

1. Add a small saved-view dashboard with counts and stale-view warnings.
2. Add optional bulk actions for the current filtered set.
3. Add AI enrichment only after review and retention workflows feel right.
4. Consider syncing IndexedDB records into PostgreSQL when multi-device access matters.
