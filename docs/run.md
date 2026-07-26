# Run and Verify Bookmark Intelligence

The supported product is the local-first frontend. The backend and AI pipeline
are experimental and are not required for normal use.

## Requirements

- Bun
- A Chromium browser for Playwright verification
- Python 3.13 and uv for parser/extractor tests

## Start the Workspace

```bash
cd frontend
bun install
bun run dev
```

Open `http://localhost:5173`.

## Use the Workspace

1. Import a browser bookmark HTML export.
2. Start on **Today** and complete or defer the finite daily flight.
3. Use **Library** for all-memory search, optional Dev/Cld scopes, and bulk review.
4. Use Mind Map, Duplicates, and Review Queue for deeper exploration.
5. Select a bookmark to edit tags, state, status, keep reason, or notes.
6. Save recurring filters as views.
7. Export a JSON backup before clearing browser data or changing profiles.

The browser stores retained records in IndexedDB. Re-importing a newer browser
export updates records by canonical URL while preserving manually entered
retention state.

## Private Data

Raw exports, workspace backups, IndexedDB dumps, and generated AI outputs are
private user data.

- Keep raw exports under ignored `data/` storage.
- Do not commit them to Git.
- Do not place them in Telegram, Obsidian, OpenClaw sessions, or coder
  worktrees.
- The committed E2E fixture is synthetic and contains no private bookmark data.

## Verification

From the repository root:

```bash
uv run --extra dev pytest -q
```

From `frontend/`:

```bash
bun run lint
bun run build
bun run test:unit
bun run test:e2e
```

`bun run test:e2e` starts and stops its own Vite server. It uses
`e2e/fixtures/devcld-bookmarks.html`, so it works without Sia's private export.
If Playwright Chromium is not installed, run `bunx playwright install chromium`
once.

## Local Trust Drill

```bash
cd frontend
bun run dev
```

Then import the synthetic fixture and check Today, Library selection,
multi-select plus undo, refresh persistence, and backup export/restore. The
automated browser suite covers these flows; the local drill is for interaction
quality rather than a phase approval gate.

For the responsive check, inspect Today at both a normal desktop width and a
390 x 844 browser viewport. Confirm the tab strip remains scrollable, the
Daily Flight actions use two usable columns, Collection Pulse remains legible,
and the page itself has no horizontal overflow.

## Experimental Backend and AI

The following surfaces are preserved for research but are not supported run
paths:

- `src/app/`
- `alembic/`
- `docker-compose.yml`
- `src/bookmark_intelligence/ai/`
- `scripts/process_ai.py`

Do not treat `docker compose up`, `alembic upgrade head`, FastAPI health output,
or the AI CLI as proof of a working system. Current blockers include missing
migrations, a broken parser/API contract, undeclared AI dependencies, no
authentication or ownership boundary, and no database/AI integration tests.

Do not run a paid collection-wide AI job. The current roadmap requires a
consented, measured sample of approximately 20 reviewed bookmarks first.

See:

- [`../PROGRESS.md`](../PROGRESS.md)
- [`roadmap.md`](roadmap.md)
- [`dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md`](dev/plans/2026-07-26-local-first-stabilization-openclaw-readiness.md)
