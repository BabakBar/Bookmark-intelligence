# Research: Bookmark Growth, Navigation, and Retention

**Date:** 2026-07-06  
**Source exports inspected:** `data/raw/bookmarks_29_10_2025.html`, `data/raw/bookmarks_17_12_2025.html`, `data/raw/bookmarks_04_01_2026.html`, `bookmarks_06_07_2026.html`  
**Status:** Investigation complete

## Situation

The project is still closest to a Phase 0 import and analysis tool. The parser, offline processing pipeline, FastAPI import route, and placeholder AI/navigation endpoints exist, but the current product surface is not yet a reliable retained knowledge base:

- `data/` is ignored by git, so private bookmark exports and generated analysis belong there.
- The new `bookmarks_06_07_2026.html` exists both at repo root and as `data/bookmarks_06_07_2026.html` with the same SHA-256 hash.
- The root-level export is untracked and should not stay at repo root if it contains private bookmark data.
- No `data/processed/` or `data/ai/` outputs currently exist.
- Alembic is configured, but there are no migration files under `alembic/versions/`.
- The React UI is still a basic upload screen, not a browser for retained bookmark intelligence.
- The API and frontend response shapes are currently inconsistent: the API returns `bookmarks_sample` with `original_folder`, while the frontend reads `bookmarks` and `folder_path`.

The reliable current capability is parsing and offline analysis of bookmark HTML exports.

## Current Data Snapshot

Latest export: `bookmarks_06_07_2026.html`

- Total parsed bookmarks: 936
- Parsed folders: 77
- Unique domains: 469
- Duplicate URL groups: 13
- Extra duplicate copies: 13
- Bookmark date range: 2022-12-07 to 2026-07-04

Normalized top-level folder counts, excluding Chrome's `Bookmarks bar` container:

| Folder | Bookmarks |
| --- | ---: |
| Cld | 285 |
| Dev | 260 |
| Sia | 245 |
| DE | 94 |
| H | 16 |
| TUI | 16 |
| Dcs | 14 |
| Root | 6 |

Dev and Cld together contain 545 bookmarks, or 58.2% of the whole export.

## Growth Since Prior Exports

| Export | Total | Dev | Cld | Sia | Dev + Cld |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2025-10-29 | 772 | 135 | 185 | 400 | 41.5% |
| 2025-12-17 | 871 | 153 | 233 | 429 | 44.3% |
| 2026-01-04 | 698 | 171 | 231 | 207 | 57.6% |
| 2026-07-06 | 936 | 260 | 285 | 245 | 58.2% |

Compared with the 2026-01-04 export, the latest export has 238 URLs not present in that snapshot:

- Dev: 89 new URLs
- Cld: 54 new URLs
- DE: 38 new URLs
- Sia: 38 new URLs
- TUI: 16 new URLs
- H: 3 new URLs

## Dev Folder Shape

Dev currently has 260 bookmarks, 27.8% of the total export.

Largest Dev areas:

| Folder | Count |
| --- | ---: |
| Dev > Tech-Blogs | 41 |
| Dev > Go | 39 |
| Dev > AI/Agents | 35 |
| Dev > Self-Host | 32 |
| Dev > Front&Desgn | 17 |
| Dev > Python > Pydantic | 16 |
| Dev > Tools-Utilities | 16 |
| Dev > Front&Desgn > Icons | 13 |
| Dev > Self-Host > AdGuard | 12 |
| Dev > Python | 9 |

Common Dev domains:

- `github.com`: 82
- `reddit.com`: 14
- `x.com`: 13
- `youtube.com`: 13

Observation: Dev mixes durable references, discovery feeds, tools, language/framework material, visual/design assets, and self-hosting operations. A plain folder tree cannot express overlap well, especially for items that are simultaneously `self-host`, `ai-agent`, `github`, `tutorial`, and `project-relevant`.

## Cld Folder Shape

Cld currently has 285 bookmarks, 30.4% of the total export.

Largest Cld areas:

| Folder | Count |
| --- | ---: |
| Cld | 46 |
| Cld > Dock/Kub | 27 |
| Cld > AWS > CCP | 24 |
| Cld > Azure | 23 |
| Cld > IaC/Terra | 23 |
| Cld > AWS | 18 |
| Cld > AZ104 | 15 |
| Cld > SysArch | 15 |
| Cld > NetWork | 13 |
| Cld > Cloud | 11 |
| Cld > obsv/mntr | 11 |
| Cld > Linux | 10 |
| Cld > CI/CD-DevOps | 9 |

Common Cld domains:

- `reddit.com`: 51
- `github.com`: 49
- `youtube.com`: 16
- `x.com`: 9
- `docs.google.com`: 9
- `learn.microsoft.com`: 7

Observation: Cld has more certification/provider/task orientation. It needs faceted navigation more than deeper folders: provider, cert, skill area, tool, learning status, and operational usefulness are separate axes.

## Retention Risks

The main retention problem is not only bookmark count. It is loss of context across imports.

Current schema and generated files do not yet preserve enough user-specific context to trust cleanup decisions:

- No stable import history is currently materialized in the repo data outputs.
- No retained per-bookmark notes, decisions, last-reviewed state, archive status, or keep/drop reason.
- No canonical URL normalization policy beyond basic domain extraction.
- No dedupe/merge policy for same URL across folders or same resource with tracking/query variants.
- No migration exists to create the database schema.
- AI outputs, if generated later, are file-based under ignored `data/ai/`, not yet first-class retained records.

Before any automatic reorganization, the project needs a retention model that can distinguish:

- keep as permanent reference
- keep as active project resource
- keep as learning queue
- archive but searchable
- delete candidate
- duplicate/merged into canonical record

## Navigation Options

### Option 1: Folder Health Dashboard

Build a local dashboard over the parsed export: folder counts, stale/new items, duplicate groups, top domains, and oversized folders.

Pros:

- Fastest useful next step.
- Uses existing parser and analysis code.
- Helps decide where cleanup is needed before adding AI.

Cons:

- Still folder-first.
- Does not solve cross-category relationships.

Best for: immediate control over Dev/Cld growth.

### Option 2: Faceted Bookmark Explorer

Import bookmarks into a retained store and browse by folder, domain, inferred topic, content type, provider, technology, added date, and review status.

Pros:

- Better fit for Dev/Cld than folders alone.
- Supports cleanup workflows and retention state.
- Can start without embeddings.

Cons:

- Requires schema and UI work.
- Needs a canonical bookmark identity policy.

Best for: turning this into a dependable personal knowledge base.

### Option 3: Live Mind Map

Create an interactive graph where nodes are folders, domains, tags, technologies, and bookmarks. Edges connect bookmarks to all applicable concepts.

Pros:

- Useful for seeing overloaded areas and hidden relationships.
- Good for Dev/Cld because resources naturally belong to multiple contexts.
- Can reveal clusters without forcing immediate folder changes.

Cons:

- Graphs get noisy quickly at 936 bookmarks.
- Needs filtering and progressive disclosure, or it becomes visual clutter.
- Should be an exploration view, not the source of truth.

Best for: discovery and sense-making after retained metadata exists.

### Option 4: AI Clustering and Project Suggestions

Use embeddings and summaries to cluster bookmarks, suggest topics/projects, and recommend folder or tag changes.

Pros:

- Matches the original project intent.
- Strong for cross-folder themes and project grouping.

Cons:

- Should not run before retention/dedupe identity is settled.
- AI output should be reviewable, not directly applied.
- Current AI config/code has drifted from older docs and needs verification before cost-bearing runs.

Best for: second phase after a reliable import/explorer baseline.

## Recommended Direction

Do not start with a full live mind map as the first implementation. Start with retained import + faceted explorer, then add the mind map as a view over the same data.

Practical sequence:

1. Move the fresh export into ignored raw data storage and avoid keeping private bookmark files at repo root.
2. Fix baseline dev workflow: document `uv run --extra dev pytest -q` as the working test command.
3. Add migrations or choose a simpler local-first store for Phase 0. The current database story is incomplete without migrations.
4. Define bookmark identity and retention fields:
   - `canonical_url`
   - `first_seen_at`
   - `last_seen_at`
   - `source_import_id`
   - `original_folders`
   - `status`
   - `review_state`
   - `user_note`
   - `keep_reason`
5. Build a Dev/Cld-first explorer:
   - folder tree
   - table/list view
   - domain facet
   - added-date facet
   - duplicate groups
   - status/review controls
6. Add graph/mind-map view using the same retained records:
   - start with folders, domains, and inferred topics
   - hide individual bookmark nodes until zoom/filter
   - support filtering to `Dev`, `Cld`, provider, technology, or review state
7. Only then run AI enrichment and clustering.

## Verification

Commands run:

```bash
uv run --extra dev pytest -q
```

Result:

```text
18 passed in 0.31s
```

The earlier plain command failed:

```bash
uv run pytest -q
```

Reason: dev dependencies are not installed by default; use the `--extra dev` command for the current repo.
