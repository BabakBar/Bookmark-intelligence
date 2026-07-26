# Implementation: Editor Integrity and Portable E2E

**Date:** 2026-07-26

**Plan phase:** Phase 1

**Status:** Complete; incorporated into the Memory Desk browser suite

## Problem

The bookmark detail fields used uncontrolled `defaultValue` inputs. React kept
the same input nodes when selection changed, so a newly selected bookmark could
display values from the prior record. A later blur could write that stale value
to the wrong canonical URL.

The only browser test also depended on Sia's private untracked bookmark export
and a separately started Vite server.

## Implementation

The detail component is keyed by the effective selected bookmark's
`canonicalUrl`. A selection change now remounts the detail editor with values
from the new retained record.

The browser acceptance path now:

- uses `frontend/e2e/fixtures/devcld-bookmarks.html`;
- contains synthetic Dev, Cld, AWS, tracking-parameter, and duplicate cases;
- starts Vite through `frontend/playwright.config.js`;
- runs through `bun run test:e2e`;
- verifies import, filters, saved views, backup export, map, duplicates, and
  review queue;
- edits two bookmarks and proves tags, keep reason, and notes remain isolated
  across selection changes and page reload.

## Files

- `frontend/src/App.jsx`
- `frontend/e2e/devcld-workspace.spec.js`
- `frontend/e2e/fixtures/devcld-bookmarks.html`
- `frontend/playwright.config.js`
- `frontend/package.json`

## Privacy Improvement

The automated test no longer reads `bookmarks_06_07_2026.html`.
`.gitignore` now protects root-level `bookmarks_*.html` exports. The existing
private export was not moved, changed, or deleted.

## Verification

```text
uv run --extra dev pytest -q
18 passed

cd frontend && bun run lint
passed

cd frontend && bun run build
passed; graph later code-split from the initial bundle

cd frontend && bun run test:e2e
7 passed in the expanded suite
```

## Continuation

This slice no longer has a manual approval gate. The editor regression remains
in the browser suite, and implementation continued through backup integrity,
daily sessions, and reversible bulk review. See
`2026-07-26-memory-desk-daily-flight.md`.
