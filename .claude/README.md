# Claude Code Workflow

Minimal development workflow for BookmarkAI: research → plan → implement

## Commands

### `/research <question>`
Investigate codebase and document findings.

**Use when:**
- Understanding how existing code works
- Finding patterns and conventions
- Exploring integration points

**Output:** `docs/dev/research/YYYY-MM-DD-topic.md`

---

### `/plan <what to build>`
Create phased implementation plan with verification criteria.

**Use when:**
- Starting new feature development
- Need structured approach to implementation

**Output:** `docs/dev/plans/YYYY-MM-DD-description.md`

**Process:**
1. Research current state
2. Get alignment on approach
3. Define phases with success criteria
4. Separate automated vs manual verification

---

### `/implement <plan-file>`
Execute plan phase by phase with verification.

**Use when:**
- Ready to build from an approved plan

**Process:**
1. Read plan completely
2. Implement phase by phase
3. Run automated verification
4. Pause for manual verification
5. Continue when approved

---

## Workflow Example

```bash
# 1. Research existing patterns
/research How does bookmark import work?

# 2. Create implementation plan
/plan Add AI tagging to bookmarks

# 3. Execute the plan
/implement docs/dev/plans/2025-01-29-ai-tagging.md
```

## Documentation Structure

```
docs/
├── features.md, architecture.md, etc.  # Project specs
└── dev/
    ├── research/   # Technical investigations
    └── plans/      # Implementation plans
```

## Key Principles

- **Read fully** - Always read files completely for context
- **Research first** - Understand before planning
- **Plan thoroughly** - No open questions before implementing
- **Verify progressively** - Check each phase before next
- **Document** - Track research and decisions

## Project Context

**BookmarkAI** - AI-powered bookmark manager
- Python 3.13 + FastAPI
- PostgreSQL + Qdrant + Valkey
- Self-hosted on Hetzner via Coolify
- OpenAI + Claude for AI features

See `docs/` for complete project specifications.
