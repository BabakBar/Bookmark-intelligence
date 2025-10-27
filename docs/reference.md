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

### Per-User Monthly Costs (Self-Hosted on Hetzner VPS)

**Assumptions:**
- 1000 bookmarks in library
- 5-10 new bookmarks/week (~40/month)
- Context searches triggered only on saves (~40/month)
- Self-hosted infrastructure on Hetzner CX32 via Coolify

**Note:** On-demand surfacing (triggered only on bookmark saves) reduces vector search volume by ~95% compared to continuous monitoring approaches.

**Cost Breakdown:**

| Service | Usage | Cost |
|---------|-------|------|
| **OpenAI Embeddings** | 40 bookmarks × 500 tokens | $0.0004 |
| **Claude API (Real-time)** | 40 bookmarks/month × $0.00375 (Sonnet) | $0.15 |
| **Claude API (Alternative)** | 40 bookmarks/month × $0.001 (Haiku) | $0.04 |
| **Qdrant (Self-Hosted)** | Included in VPS | $0 |
| **PostgreSQL (Self-Hosted)** | Included in VPS | $0 |
| **Redis (Self-Hosted)** | Included in VPS | $0 |
| **Hetzner VPS CX32** | 8GB RAM, 80GB SSD | $13.00 |
| **Total (Sonnet)** | | **~$13.15/month** |
| **Total (Haiku)** | | **~$13.04/month** |

**With Optimizations:**
- Use Claude 3.5 Haiku instead of Sonnet: **73% AI cost savings**
- Batch processing (consolidate requests): Reduces latency overhead
- Qdrant quantization: 4x memory reduction, allows more bookmarks per GB

**Scalability:**
- Single VPS (CX32): ~100-200 concurrent users
- 10,000 users: ~$650/month (50 VPS instances + AI costs)
- 100,000 users: ~$6,500/month

---

### Infrastructure Costs (Self-Hosted on Hetzner)

**Development & MVP (1-50 users):**
- Hetzner VPS CX32 (8GB RAM, 80GB SSD): $13/month
- Domain: $12/year (~$1/month)
- Coolify (self-hosted): $0
- All databases (PostgreSQL, Redis, Qdrant): $0 (included in VPS)
- **Total:** ~$14/month

**Production (100-200 users):**
- Hetzner VPS CX32: $13/month
- Domain + CDN (Cloudflare free): $1/month
- Hetzner Storage Box (backups, 100GB): $3.50/month
- **Total:** ~$17.50/month ($0.09-0.18/user)
- **AI costs (per user):** ~$0.15/month (Claude Sonnet) or $0.04/month (Haiku)

**Production (1,000 users):**
- Hetzner VPS CX52 (16GB RAM, 160GB SSD): $25/month (upgrade from CX32)
- OR: 2× Hetzner VPS CX32 with load balancing: $26/month
- Hetzner Storage Box (1TB backups): $10/month
- Domain + CDN: $1/month
- **Total:** ~$36/month ($0.036/user + AI costs)

**Production (10,000 users):**
- 10× Hetzner VPS CX32 (distributed): $130/month
- OR: 2× Hetzner Dedicated AX52 (64GB RAM each): $120/month
- Hetzner Storage Box (5TB): $25/month
- Load balancer + CDN: $20/month
- **Total:** ~$175/month ($0.0175/user + AI costs)

**Cost Comparison: Self-Hosted vs. Cloud**

| Users | Cloud (from original) | Self-Hosted (Hetzner) | Savings |
|-------|-----------------------|-----------------------|---------|
| 100 | $155/month | $17.50/month | $137.50/month (89% savings) |
| 1,000 | $480/month | $36/month | $444/month (93% savings) |
| 10,000 | ~$3,000/month | $175/month | $2,825/month (94% savings) |

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

- [x] **Vector DB Choice:** Qdrant vs. Pinecone vs. pgvector? → **Qdrant 1.12+ (self-hosted)** ✓
  - Self-hosted on Hetzner VPS, significant cost savings
- [x] **Hosting:** Self-hosted vs. Cloud Run vs. AWS Lambda? → **Self-hosted on Hetzner via Coolify** ✓
  - Cost: $13/month vs $185+/month cloud services (93% savings)
  - Full control, predictable costs, excellent performance
  - Coolify provides easy deployment and management
- [ ] **Chrome Web Store:** Free vs. $5 one-time fee?
  - Recommendation: **Free** (better adoption, offset by low hosting costs)

---

### Product Decisions

- [ ] **Freemium Model?** Free tier (unlimited bookmarks) + Pro for advanced features?
  - With self-hosted costs at $13/month, can offer generous free tier
  - Pro features: Team collaboration, advanced analytics, API access
  - Alternative: Completely free for individuals, charge for teams/enterprises
- [ ] **Ephemeral Content:** Google Docs only, or support Notion/Obsidian?
  - Start with Google Docs (OAuth simpler)
  - Add Notion/Obsidian based on user demand
- [x] **AI Model Choice:** Claude 3.5 Sonnet vs. Haiku for content analysis? → **Start with Haiku** ✓
  - Haiku: 73% cheaper ($0.04 vs $0.15 per 40 bookmarks), fast, good quality
  - Upgrade to Sonnet for users who need premium quality
  - OpenAI GPT-4o-mini as alternative if Claude unavailable
- [x] **Engagement Tracking Default:** Opt-in vs. Opt-out? → **Opt-in** ✓
  - More privacy-friendly, better for Chrome Store approval
  - Clear value proposition: "Enable to get insights and dead bookmark alerts"

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

- **Batch Processing:** Asynchronous AI processing for cost optimization and efficient resource usage
- **Coolify:** Open-source, self-hosted Platform-as-a-Service (PaaS) for deploying applications via Docker
- **Context:** The browsing environment including URL, page content, time, and active project
- **Dead Bookmark:** A bookmark saved >6 months ago with 0 opens (engagement tracking metric)
- **Embedding:** A numerical vector (array of floats) representing semantic meaning of text (1536 dimensions for text-embedding-3-small)
- **Engagement Tracking:** Passive monitoring of bookmark opens to identify usage patterns and unused bookmarks
- **Ephemeral Bookmark:** Temporary bookmark (tweets, Reddit) meant for content extraction, not long-term storage
- **Project:** A collection of related bookmarks representing a work context or area of interest
- **Quantization:** Technique to reduce vector storage size by 4x (e.g., float32 → int8) with minimal accuracy loss
- **Relevance Score:** Combined metric of vector similarity (60%), engagement (25%), and recency (15%)
- **Vector Search:** Finding similar items by comparing embeddings using cosine similarity

---

## References & Resources

### Official Documentation

- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Anthropic Claude API Documentation](https://docs.anthropic.com/)
- [PostgreSQL 17 Documentation](https://www.postgresql.org/docs/17/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Coolify Documentation](https://coolify.io/docs)
- [Hetzner Cloud Documentation](https://docs.hetzner.com/)

---

### Tech Stack Rationale

- [FastAPI vs Flask vs Django (2025)](https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/)
- [Top Vector Databases 2025](https://www.datacamp.com/blog/the-top-5-vector-databases)
- [Anthropic Claude Pricing](https://www.anthropic.com/pricing)
- [OpenAI Embedding Model Comparison](https://openai.com/index/new-embedding-models-and-api-updates/)
- [Chrome Extension Manifest V3 Migration](https://developer.chrome.com/docs/extensions/migrating/to-service-workers/)
- [Coolify vs Heroku vs Railway](https://coolify.io/)
- [Hetzner vs DigitalOcean vs AWS Cost Comparison](https://www.hetzner.com/cloud)

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
- [Anthropic Claude Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

**For Self-Hosting:**
- [Coolify Getting Started](https://coolify.io/docs/introduction)
- [Docker Compose for Development](https://docs.docker.com/compose/)
- [Hetzner Cloud Best Practices](https://docs.hetzner.com/cloud/)

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
