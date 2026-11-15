# Bookmark Intelligence Project

Trusted personal bookmark memory with reviewable organization and later
context-aware resurfacing.

Read `PROGRESS.md` before acting. It is the canonical current status.

## Current Phase: Phase 0C - Daily Memory Workflow Validation

The supported product is the browser-local Memory Desk under `frontend/`:

- browser HTML import;
- canonical retained records in IndexedDB;
- finite daily flight over All Memory;
- Library, bounded bulk review, mind map, duplicate review, and review queue;
- notes, tags, status, sessions, activity, saved views, and backup/restore.

FastAPI, PostgreSQL, Qdrant, Valkey, paid AI processing, hosted sync, and the
browser extension are experimental or future work. Do not deploy or run
cost-bearing jobs without a new reviewed plan.

Raw bookmark exports and workspace backups are private local data. Never put
them in Git, chat, Obsidian, OpenClaw sessions, or coding worktrees.

## Development Workflow

Use Research -> Plan → Spec → Build → Test → Deploy for all features.

### `/research <question>`

Investigate codebase and document findings.

**Output:** `docs/dev/research/YYYY-MM-DD-topic.md`

**Process:**

1. Read the mentioned files first
2. Read identified files completely
3. Document what EXISTS (not what should be)

### `/plan <what to build>`

Create phased implementation plan.

**Output:** `docs/dev/plans/YYYY-MM-DD-description.md`

**Process:**

1. Research current state, including current libraries and patterns
2. Get alignment on approach
3. Define phases with success criteria (automated + manual)
4. Resolve ALL open questions before finalizing
5. Create Spec for each phase

**Critical:** No placeholders or "TBD" in final plan.

### `/implement <plan-file>`

Execute plan phase by phase with verification.

**Process:**

1. Read plan completely
2. Implement one phase at a time
3. Run automated verification (pytest, mypy, ruff)
4. Record manual verification when interaction quality needs it
5. Update checkboxes in the plan file
6. Continue safe local phases without an approval pause; stop for destructive,
   external, paid, privacy-expanding, or deployment decisions

## Testing Commands

```bash
# Current supported checks
uv run --extra dev pytest -q
cd frontend && bun run lint
cd frontend && bun run build
cd frontend && bun run test:unit
cd frontend && bun run test:e2e
```

## Key Patterns

**Future AI Integration:**

- OpenAI text-embedding-3-small for embeddings
- Claude Haiku for cost-effective tagging/summarization
- Use Batch API for 50% cost savings on large operations

**Experimental Backend:**

- SQLAlchemy 2.0+ async patterns
- Alembic for migrations
- Qdrant for vector similarity search

**Code Style:**

- Modern Python tooling (uv, pyproject.toml)
- Type hints on all function signatures
- FastAPI dependency injection
- Async/await throughout

## Important Principles

- **One phase at a time** - verify before continuing
- **Document decisions** - capture research and plans
- **Adapt intelligently** - communicate mismatches

## Project Docs

See `docs/` for complete specifications:

- `architecture.md` - System design
- `features.md` - Feature specifications
- `roadmap.md` - Development timeline
- `reference.md` - Costs, metrics, glossary
