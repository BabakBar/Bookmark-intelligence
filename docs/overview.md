# BookmarkAI - Product Overview

**Version:** 1.0
**Last Updated:** October 27, 2025
**Project Codename:** BookmarkAI

---

## Executive Summary

Contextual Bookmark Intelligence is an AI-powered browser extension and backend system designed to transform static bookmark collections into dynamic, context-aware knowledge management tools. The system addresses the "bookmark graveyard" problem by using machine learning to surface relevant bookmarks based on browsing context, automatically categorizing and tagging content, and providing natural language search capabilities.

---

## Key Value Propositions

- **Context-Aware Surfacing**: Surface relevant bookmarks when saving new pages to prevent duplicates and discover connections
- **Intelligent Organization**: AI-powered clustering and tagging eliminates manual folder management
- **Project-Based Workflows**: Dynamic workspaces that adapt to active projects
- **Natural Language Search**: Ask questions like "find docker tutorials from January" instead of navigating folder hierarchies
- **Self-Hosted & Private**: Fully self-hosted on your infrastructure via Coolify, complete data ownership
- **Cost-Effective**: 93% cheaper than cloud alternatives ($13/month vs $185/month for equivalent services)
- **Ephemeral Content Workflow**: Automated extraction of valuable insights from tweets/Reddit posts to Google Docs

---

## Target User

Cloud engineers, software developers, and knowledge workers managing 500+ bookmarks across multiple contexts (work, personal, learning) who frequently switch between projects.

### User Pain Points We Solve

1. **Bookmark Graveyard**: Saved hundreds of bookmarks but never open them
2. **Lost Knowledge**: Can't find that article you saved 3 months ago
3. **Context Switching**: Managing separate projects requires mental overhead
4. **Duplicate Saves**: Accidentally bookmark the same page multiple times
5. **Manual Organization**: Folder hierarchies become unwieldy and outdated

---

## Core Features at a Glance

| Feature | Priority | Description |
|---------|----------|-------------|
| **Context-Aware Surfacing** | P0 (MVP) | Surface similar bookmarks when saving to prevent duplicates |
| **Intelligent Auto-Tagging** | P0 (MVP) | AI generates semantic tags and summaries automatically |
| **Project Mode** | P0 (MVP) | Filter bookmarks by active project context |
| **Engagement Tracking** | P1 | Track usage to identify "dead" bookmarks |
| **AI Chat Interface** | P1 | Natural language search over your bookmarks |
| **Ephemeral Content** | P1 | Extract insights from tweets/Reddit to Google Docs |
| **Cross-Project Search** | P2 | Advanced search spanning multiple projects |

---

## How It Works (30-Second Version)

1. **Save a Bookmark** → Extension captures page context (URL, title, keywords)
2. **AI Processing** → Claude generates tags, summary, and suggests project
3. **Vector Search** → System finds similar bookmarks you already have
4. **Smart Suggestions** → "You already have 3 similar bookmarks" or "Add to FabrikTakt project?"
5. **Usage Tracking** → System learns which bookmarks you actually use
6. **Weekly Cleanup** → "You have 47 bookmarks never opened. Archive them?"

---

## Key Differentiators

### vs. Browser Native Bookmarks
- ❌ Browser: Static folders, no search, no context
- ✅ BookmarkAI: AI-powered search, automatic organization, context-aware

### vs. Raindrop.io / Pocket
- ❌ Competitors: Manual tagging, basic search, no project mode
- ✅ BookmarkAI: Automatic tagging, semantic search, project-based filtering

### vs. Notion / Obsidian
- ❌ Note tools: Requires manual note-taking, not browser-native
- ✅ BookmarkAI: One-click save, zero friction, automatic enrichment

---

## Technology Highlights

- **Frontend**: Chrome Extension (Manifest V3) with React + TypeScript
- **Backend**: FastAPI (Python 3.13+) with async/await
- **AI Models**:
  - OpenAI `text-embedding-3-small` for embeddings (~$0.0004/month per user)
  - Claude 3.5 Haiku for content analysis (~$0.04/month per user)
  - Claude 3.5 Sonnet available for premium quality (~$0.15/month per user)
- **Vector DB**: Qdrant 1.12+ (self-hosted) for sub-100ms similarity search
- **Metadata DB**: PostgreSQL 17.x (self-hosted) with JSONB support
- **Deployment**: Coolify on Hetzner VPS (self-hosted)
- **Cost**: **~$13.04/month total** (covers ~100-200 users)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to find bookmark | <5 seconds |
| Save-time suggestion relevance | 70%+ click-through |
| Project suggestion acceptance | 80%+ |
| User retention (30-day) | 70%+ |
| Dead bookmark cleanup adoption | 40%+ |

---

## Development Timeline

- **Phase 1 (Weeks 1-4)**: MVP - Bookmark save, auto-tagging, context surfacing
- **Phase 2 (Weeks 5-8)**: Intelligence - Batch processing, project mode, engagement tracking
- **Phase 3 (Weeks 9-12)**: Advanced - AI chat, ephemeral content, cross-project search

**Total**: 12 weeks to production-ready system

---

## Documentation Structure

- **[overview.md](overview.md)** ← You are here
- **[architecture.md](architecture.md)** - System design, tech stack, data flows
- **[features.md](features.md)** - Detailed feature specifications
- **[roadmap.md](roadmap.md)** - Development phases and timelines
- **[reference.md](reference.md)** - Costs, security, metrics, glossary

---

## Quick Links

- [Full Feature List](features.md)
- [System Architecture](architecture.md#high-level-architecture)
- [Development Roadmap](roadmap.md)
- [Cost Analysis](reference.md#cost-analysis)
- [Open Questions](reference.md#open-questions)

---

**Next**: Read [System Architecture](architecture.md) to understand how everything fits together.
