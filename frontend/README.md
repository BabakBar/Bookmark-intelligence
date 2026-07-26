# Memory Desk

The frontend is the current Bookmark Intelligence product. It imports browser
bookmark HTML, retains canonical records in IndexedDB, and provides a finite
daily flight, full Library, bounded bulk review, mind map, duplicate review,
review queue, saved views, and portable backup workflow.

## Run

```bash
bun install
bun run dev
```

Open `http://localhost:5173`.

## Verify

```bash
bun run lint
bun run build
bun run test:unit
bun run test:e2e
```

The E2E command starts its own Vite server and uses the synthetic
`e2e/fixtures/devcld-bookmarks.html` fixture. It does not require a private
bookmark export.

See [`../PROGRESS.md`](../PROGRESS.md) for current status and
[`../docs/run.md`](../docs/run.md) for the complete runbook.
