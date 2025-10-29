# BookmarkAI Project

AI-powered bookmark manager with context-aware search and automatic organization.

## Tech Stack

- **Backend**: Python 3.13 + FastAPI (async/await, Pydantic v2)
- **Databases**: PostgreSQL 17 + Qdrant (vector) + Valkey (Redis fork)
- **AI**: OpenAI embeddings + Claude (Haiku for tagging/summarization)
- **Deployment**: Self-hosted on Hetzner VPS via Coolify

## Current Phase: Phase 0 - Bootstrap & Import (weeks 1-2)

Import and organize 800 existing bookmarks BEFORE building browser extension:

- Import bookmarks from HTML
- Batch AI processing (embeddings, tags, summaries)
- Clustering and project suggestions
- Web dashboard validation

**Why Phase 0 matters:** Proves AI organization of Bookmarks works correctly before committing to extension development.

## Development Workflow

Use Research -> Plan → Spec → Build → Test → Deploy for all features.

### `/research <question>`

Investigate codebase and document findings.

**Output:** `docs/dev/research/YYYY-MM-DD-topic.md`

**Process:**

1. Read mentioned files FULLY first (no limit/offset)
2. Spawn parallel agents (Explore subagent)
3. Read identified files completely
4. Document what EXISTS (not what should be)

### `/plan <what to build>`

Create phased implementation plan.

**Output:** `docs/dev/plans/YYYY-MM-DD-description.md`

**Process:**

1. Research current state (spawn agents for modern libraries/patterns)
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
4. **PAUSE** for manual verification
5. Update checkboxes in plan file
6. Get approval before next phase

## Testing Commands

```bash
# Run all checks
pytest tests/
mypy .
ruff check

# Or if Makefile exists
make test
make check
```

## Key Patterns

**AI Integration:**

- OpenAI text-embedding-3-small for embeddings
- Claude Haiku for cost-effective tagging/summarization
- Use Batch API for 50% cost savings on large operations

**Database:**

- SQLAlchemy 2.0+ async patterns
- Alembic for migrations
- Qdrant for vector similarity search

**Code Style:**

- Modern Python tooling (uv, pyproject.toml)
- Type hints on all function signatures
- FastAPI dependency injection
- Async/await throughout

## Important Principles

- **Read files fully** - never use limit/offset
- **Spawn parallel agents** - maximize efficiency
- **Use TodoWrite** - track progress
- **One phase at a time** - verify before continuing
- **Document decisions** - capture research and plans
- **Adapt intelligently** - communicate mismatches

## Project Docs

See `docs/` for complete specifications:

- `architecture.md` - System design
- `features.md` - Feature specifications
- `roadmap.md` - Development timeline
- `reference.md` - Costs, metrics, glossary
