# Reference Documentation

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Features](features.md) | [Roadmap](roadmap.md)

---

## Table of Contents

- [Cost Analysis](#cost-analysis)
- [Security & Privacy](#security--privacy)
- [Success Metrics](#success-metrics)
- [Open Questions & Decisions](#open-questions--decisions)
- [Glossary](#glossary)
- [References & Resources](#references--resources)

---

## Cost Analysis

### Per-User Monthly Costs (Steady State)

**Assumptions:**
- 1000 bookmarks in library
- 5-10 new bookmarks/week (~40/month)
- Context searches triggered only on saves (~40/month)

**Note:** On-demand surfacing (triggered only on bookmark saves) reduces vector search volume by ~95% compared to continuous monitoring approaches.

**Cost Breakdown:**

| Service | Usage | Cost |
|---------|-------|------|
| **OpenAI Embeddings** | 40 bookmarks × 500 tokens | $0.0004 |
| **Claude API (Real-time)** | 40 bookmarks/month × $0.00375 | $0.15 |
| **Claude API (Batch)** | Weekly processing (~40 bookmarks) | $0.08 |
| **Qdrant Cloud** | 1GB storage | $0.50 |
| **PostgreSQL (Supabase)** | Free tier | $0 |
| **Redis (Upstash)** | Free tier | $0 |
| **Total** | | **~$0.73/month** |

**With Optimizations:**
- Batch-only processing (no real-time Claude): Saves $0.15/month → **$0.58/month**
- Prompt caching (90% discount on repeated prompts): Additional ~$0.10 savings → **$0.48/month**

**Scalability:**
- 10,000 users: $4,800/month (batch-only + caching)
- 100,000 users: $48,000/month

---

### Infrastructure Costs

**Development (Self-hosted):**
- DigitalOcean Droplet (4GB RAM): $24/month
- Qdrant Cloud (Starter): $20/month
- Domains + SSL: $15/year
- **Total:** ~$45/month

**Production (100 users):**
- Cloud Run (Backend): $50/month
- Qdrant Cloud: $50/month
- Supabase (PostgreSQL): $25/month
- Redis: $10/month
- CDN + Storage: $20/month
- **Total:** ~$155/month ($1.55/user)

**Production (1,000 users):**
- Cloud Run (Backend): $150/month
- Qdrant Cloud: $150/month
- Supabase (PostgreSQL): $100/month
- Redis: $30/month
- CDN + Storage: $50/month
- **Total:** ~$480/month ($0.48/user + AI costs)

---

## Security & Privacy

### Data Security

**Encryption:**
- At-rest: AES-256 (database)
- In-transit: TLS 1.3 (all API calls)
- API keys: Encrypted in database, never logged

**Authentication:**
- JWT tokens with 24-hour expiry
- Refresh tokens with 30-day expiry
- Password hashing: bcrypt (cost factor 12)

**API Security:**
- Rate limiting: 100 requests/minute per user
- CORS: Whitelist extension origin only
- Input validation: Pydantic schemas
- SQL injection protection: SQLAlchemy ORM with parameterized queries
- XSS prevention: Content Security Policy headers

---

### Privacy

**User Commitments:**
- Bookmark content never shared with third parties
- AI processing happens via direct API calls (no intermediate storage)
- User can export all data (GDPR compliance)
- User can delete account + all data permanently
- No analytics/tracking beyond error logging
- Engagement tracking is opt-in and can be disabled

**Data Retention:**
- Active bookmarks: Indefinite
- Ephemeral bookmarks (processed): 30 days
- Deleted bookmarks: Soft delete (30 days), then hard delete
- Logs: 7 days
- User sessions: 30 days (refresh token expiry)

**GDPR Compliance:**
- Right to access: `/api/v1/users/me/export` endpoint
- Right to deletion: `/api/v1/users/me/delete` endpoint
- Data portability: JSON export of all user data
- Privacy policy: Clear explanation of data usage
- Cookie consent: Extension requests permissions explicitly

---

## Success Metrics

### Product Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to find bookmark | <5 seconds | User testing |
| Save-time suggestion relevance | 70%+ | Click-through rate during save flow |
| Project suggestion acceptance | 80%+ | Acceptance rate |
| Daily active users | 60% of installed | Extension telemetry |
| Average bookmarks per user | 200+ | Database query |
| User retention (30-day) | 70%+ | Cohort analysis |
| Dead bookmark cleanup adoption | 40%+ | Feature usage tracking |
| Engagement tracking opt-in | 60%+ | Settings analytics |

---

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API latency (p95) | <200ms | APM (e.g., Sentry) |
| Vector search latency (p95) | <100ms | Qdrant metrics |
| Embedding generation latency (p95) | <500ms | Custom tracking |
| End-to-end save latency (p95) | <2s | Frontend → Backend → DB |
| Uptime | 99.5%+ | Status page |
| Error rate | <0.1% | Error tracking |
| Batch job completion | 95%+ within 24h | Celery monitoring |

---

### AI/ML Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Auto-tag acceptance | 85%+ | User edits vs. auto-generated |
| Clustering accuracy | 80%+ | User corrections |
| Project suggestion accuracy | 80%+ | Acceptance rate |
| Chat query relevance | 90%+ | User feedback |
| Ephemeral content processing | 95%+ | Success rate |

---

## Open Questions & Decisions

### Technical Decisions

- [ ] **Vector DB Choice:** Qdrant vs. Pinecone vs. pgvector? → **Qdrant** (cost + performance)
- [ ] **Hosting:** Self-hosted vs. Cloud Run vs. AWS Lambda?
  - Cloud Run: Best for MVP, auto-scaling, pay-per-use
  - AWS Lambda: More complex but potentially cheaper at scale
  - Self-hosted: Full control but requires DevOps effort
- [ ] **Chrome Web Store:** Free vs. $5 one-time fee?
  - Free: Better adoption, competitive with alternatives
  - Paid: Filters serious users, small revenue stream

---

### Product Decisions

- [ ] **Freemium Model?** Free tier (100 bookmarks) + Pro ($5/month)?
  - Free tier attracts users, Pro for power users
  - Alternative: Completely free during beta, monetize later
- [ ] **Ephemeral Content:** Google Docs only, or support Notion/Obsidian?
  - Start with Google Docs (OAuth simpler)
  - Add Notion/Obsidian based on user demand
- [ ] **AI Model Choice:** Claude Sonnet 4.5 vs. Haiku 4.5 for batch jobs?
  - Sonnet: Better quality, current choice
  - Haiku: 5x cheaper, test quality trade-off
- [ ] **Engagement Tracking Default:** Opt-in vs. Opt-out?
  - Opt-in: More privacy-friendly, better for Chrome Store approval
  - Opt-out: Higher adoption, more data for relevance scoring

---

### Go-to-Market

- [ ] **Target Audience:** Developers only, or broader knowledge workers?
  - Developers: Clear niche, easier to market
  - Knowledge workers: Larger market, harder to differentiate
- [ ] **Launch Strategy:** Product Hunt, Hacker News, or direct to Chrome Web Store?
  - Start with Hacker News (tech-savvy audience)
  - Follow up with Product Hunt (broader audience)
  - Chrome Web Store SEO for organic growth
- [ ] **Pricing:** Free beta → Paid launch, or free forever with optional Pro?
  - Recommendation: Free forever for individuals, Pro for teams
  - Monetization: Team features, API access, enterprise SSO

---

## Glossary

- **Batch Processing:** Asynchronous AI processing with 24-hour turnaround for cost savings (50% discount via Claude Batch API)
- **Context:** The browsing environment including URL, page content, time, and active project
- **Dead Bookmark:** A bookmark saved >6 months ago with 0 opens (engagement tracking metric)
- **Embedding:** A numerical vector (array of floats) representing semantic meaning of text (1536 dimensions for text-embedding-3-small)
- **Engagement Tracking:** Passive monitoring of bookmark opens to identify usage patterns and unused bookmarks
- **Ephemeral Bookmark:** Temporary bookmark (tweets, Reddit) meant for content extraction, not long-term storage
- **Project:** A collection of related bookmarks representing a work context or area of interest
- **Relevance Score:** Combined metric of vector similarity (60%), engagement (25%), and recency (15%)
- **Vector Search:** Finding similar items by comparing embeddings using cosine similarity

---

## References & Resources

### Official Documentation

- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Claude API Documentation](https://docs.anthropic.com/)
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
- [Celery Documentation](https://docs.celeryq.dev/)

---

### Tech Stack Rationale

- [FastAPI vs Flask vs Django (2025)](https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/)
- [Top Vector Databases 2025](https://www.datacamp.com/blog/the-top-5-vector-databases)
- [Claude Batch API Pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)
- [OpenAI Embedding Model Comparison](https://openai.com/index/new-embedding-models-and-api-updates/)
- [Chrome Extension Manifest V3 Migration](https://developer.chrome.com/docs/extensions/migrating/to-service-workers/)

---

### Learning Resources

**For Browser Extension Development:**
- [Chrome Extension Samples](https://github.com/GoogleChrome/chrome-extensions-samples)
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/migrating/)

**For Vector Search:**
- [Qdrant Quickstart](https://qdrant.tech/documentation/quick-start/)
- [Understanding Vector Embeddings](https://www.pinecone.io/learn/vector-embeddings/)

**For AI Integration:**
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [Claude Prompt Engineering Guide](https://docs.anthropic.com/en/docs/prompt-engineering)

---

### Related Projects & Inspiration

- **Raindrop.io:** Bookmark manager with tags and collections
- **Pocket:** Read-later app with recommendations
- **Hypothesis:** Web annotation tool with social features
- **Mem.ai:** AI-powered note-taking with auto-organization
- **Notion Web Clipper:** Save pages to Notion with metadata

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-27 | Initial specification |
| 1.1 | 2025-10-27 | Added engagement tracking feature |
| 1.2 | 2025-10-27 | Restructured into multi-doc format |

---

**Status:** Draft for Review
**Maintained By:** Project Team
**Last Updated:** October 27, 2025

---

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Features](features.md) | [Roadmap](roadmap.md)
