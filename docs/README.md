# BookmarkAI Documentation

**Version 1.0** | **Last Updated:** October 27, 2025

Welcome to the BookmarkAI product documentation. This is an AI-powered browser extension and backend system that transforms static bookmark collections into dynamic, context-aware knowledge management tools.

---

## 📚 Documentation Structure

### [1. Overview](overview.md)
**Start here!** Executive summary, key value propositions, target users, and quick feature comparison.

**What you'll find:**
- 30-second product summary
- Key differentiators vs. competitors
- High-level technology stack
- Success metrics at a glance

**Read this if:** You want to understand what BookmarkAI is and why it exists.

---

### [2. System Architecture](architecture.md)
Complete system design including data flows, technology stack, database schemas, and API structure.

**What you'll find:**
- High-level architecture diagram
- Data flow diagrams (real-time, batch, engagement tracking)
- Technology stack with rationale
- Database schemas (PostgreSQL + Qdrant)
- API endpoint specifications
- AI services configuration

**Read this if:** You're implementing the system or need technical details.

---

### [3. Feature Specifications](features.md)
Detailed specifications for all features including user flows, technical requirements, and success metrics.

**What you'll find:**
- **P0 Features (MVP):**
  - Context-Aware Surfacing
  - Intelligent Auto-Tagging & Clustering
  - Project Mode
- **P1 Features (Post-MVP):**
  - AI Chat Interface
  - Ephemeral Content Workflow
  - Contextual Saving
  - Bookmark Engagement Tracking
- **P2 Features (Future):**
  - Cross-Project Search
- UI/UX specifications

**Read this if:** You need detailed feature requirements or user flows.

---

### [4. Development Roadmap](roadmap.md)
12-week development plan broken into three phases, with weekly milestones and deliverables.

**What you'll find:**
- **Phase 1 (Weeks 1-4):** MVP development
- **Phase 2 (Weeks 5-8):** Intelligence layer
- **Phase 3 (Weeks 9-12):** Advanced features & launch
- Risk mitigation strategies
- Success milestones
- Future enhancements

**Read this if:** You're planning development or tracking progress.

---

### [5. Reference](reference.md)
Cost analysis, security specifications, success metrics, glossary, and resources.

**What you'll find:**
- Cost breakdown for self-hosted deployment (~$13/month total for 100-200 users)
- Infrastructure costs comparison (93% savings vs cloud)
- Security & privacy specifications
- Product & technical metrics
- Open questions & decisions
- Glossary of terms
- Links to external resources

**Read this if:** You need cost projections, security details, or reference material.

---

## 🚀 Quick Start Paths

### For Product Managers
1. Read [Overview](overview.md) - Understand the product vision
2. Browse [Features](features.md) - Review feature specifications
3. Check [Roadmap](roadmap.md) - See development timeline

### For Engineers
1. Read [Architecture](architecture.md) - Understand system design
2. Review [Features](features.md) - Get technical requirements
3. Follow [Roadmap](roadmap.md) - Track implementation phases

### For Stakeholders
1. Start with [Overview](overview.md) - Get the big picture
2. Jump to [Reference](reference.md#cost-analysis) - Review costs
3. Check [Roadmap](roadmap.md#success-milestones) - See launch targets

---

## 🎯 Key Highlights

### Problem We're Solving
Users save hundreds of bookmarks but:
- Can't find them when needed
- Forget they exist
- Manually organize into folders that become outdated
- Accidentally save duplicates
- Never review 70%+ of saved bookmarks

### Our Solution
- **Context-Aware:** Surface similar bookmarks when saving (prevent duplicates)
- **AI-Powered:** Automatic tagging, summarization, and clustering
- **Project-Based:** Filter bookmarks by active work context
- **Engagement Tracking:** Identify "dead" bookmarks you never use
- **Privacy-First:** On-demand processing, no continuous monitoring

### Cost Efficiency
- **$13/month total** for self-hosted deployment (covers 100-200 users)
- **93% cost savings** vs cloud services ($13 vs $185/month)
- AI costs: $0.04-0.15/month per user depending on model choice
- Complete data ownership with self-hosted infrastructure

### Development Timeline
- **4 weeks:** MVP with core features
- **8 weeks:** Intelligence layer + engagement tracking
- **12 weeks:** Production-ready with advanced features

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Time to find bookmark | <5 seconds |
| Suggestion relevance | 70%+ click-through |
| User retention (30-day) | 70%+ |
| Dead bookmark cleanup adoption | 40%+ |

See [Reference > Success Metrics](reference.md#success-metrics) for complete list.

---

## 🛠️ Technology Stack Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| **Frontend** | Chrome Extension (Manifest V3) + React + TypeScript | Modern, required standard |
| **Backend** | FastAPI (Python 3.13+) | Async-native, 3-5x faster than alternatives |
| **Vector DB** | Qdrant 1.12+ (self-hosted) | Best filtered search, open-source, low resource footprint |
| **Metadata DB** | PostgreSQL 17.x (self-hosted) | Industry standard, JSONB support, v17 performance improvements |
| **Job Queue** | Celery 5.4+ + Redis 7.4+ | Reliable async tasks |
| **AI Models** | OpenAI embeddings + Claude 3.5 Haiku/Sonnet | Cost-effective, high quality |
| **Deployment** | Coolify on Hetzner VPS | Self-hosted, 93% cost savings vs cloud |

See [Architecture > Technology Stack](architecture.md#technology-stack) for details.

---

## 🤔 Open Questions

Key decisions still needed:
- Freemium model? (Free tier + Pro plan)
- Hosting choice? (Cloud Run vs. AWS Lambda)
- Pricing strategy? (Free beta vs. paid launch)
- Target audience? (Developers vs. knowledge workers)

See [Reference > Open Questions](reference.md#open-questions--decisions) for full list.

---

## 📖 Additional Resources

- **Original Spec:** [../spec-v1.md](../spec-v1.md) (legacy, superseded by this documentation)
- **Bookmark Cleaner:** [../README.md](../README.md) (companion tool for HTML bookmark cleanup)

---

## 📞 Contact & Feedback

For questions, suggestions, or contributions, please:
- Open an issue on GitHub
- Refer to specific documentation sections in discussions
- Follow the [Roadmap](roadmap.md) for implementation status

---

**Status:** Draft for Review
**Version:** 1.0
**Last Updated:** October 27, 2025

---

## Document Map

```
docs/
├── README.md          ← You are here (Index)
├── overview.md        → Product overview & value props
├── architecture.md    → System design & tech stack
├── features.md        → Detailed feature specs
├── roadmap.md         → Development timeline
└── reference.md       → Costs, security, metrics, glossary
```
