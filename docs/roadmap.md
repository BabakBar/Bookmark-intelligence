# Development Roadmap

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Features](features.md) | [Reference](reference.md)

---

## Development Timeline Overview

**Total Duration:** 12 weeks to production-ready system

- **Phase 1 (Weeks 1-4):** MVP - Core bookmark management, auto-tagging, context surfacing
- **Phase 2 (Weeks 5-8):** Intelligence - Batch processing, project mode, engagement tracking
- **Phase 3 (Weeks 9-12):** Advanced - AI chat, ephemeral content, polish & launch

---

## Phase 1: MVP (Weeks 1-4)

### Week 1: Foundation

**Focus:** Infrastructure setup and basic authentication

- Set up development environment
- Initialize FastAPI backend
- Set up PostgreSQL + Qdrant databases
- Create basic data models
- User authentication (JWT)

**Key Deliverables:**
- Functional backend server
- Database schemas deployed
- User registration/login working

---

### Week 2: Core Backend

**Focus:** Bookmark CRUD and AI integration

- Bookmark CRUD API endpoints
- OpenAI embeddings integration
- Qdrant vector operations
- Basic search functionality
- Project management APIs

**Key Deliverables:**
- `/api/v1/bookmarks` endpoints functional
- Embedding generation pipeline working
- Vector search returning results

---

### Week 3: Browser Extension

**Focus:** Extension foundation and browser integration

- Chrome Extension scaffold (Manifest V3)
- Bookmark capture from browser
- Basic popup UI
- API client integration
- Context detection (URL + title)

**Key Deliverables:**
- Extension installable in Chrome
- Can save bookmarks to backend
- Basic UI functional

---

### Week 4: Context-Aware Surfacing

**Focus:** Core feature implementation

- Embedding generation on save
- On-demand context analysis triggered by bookmark saves
- Vector similarity search
- Sidebar UI with suggestions
- Testing and refinement

**Key Deliverables:**
- Context-aware suggestions working
- Sidebar displays similar bookmarks
- User can click suggestions to open

---

### MVP Deliverables (End of Week 4)

- ✅ Save bookmarks with auto-tagging
- ✅ Context-aware suggestions in sidebar
- ✅ Basic project management
- ✅ Manual tag editing

**Success Criteria:**
- User can save 10 bookmarks and get relevant suggestions
- Average suggestion latency < 2 seconds
- Zero critical bugs

---

## Phase 2: Intelligence Layer (Weeks 5-8)

### Week 5: Claude Integration

**Focus:** Advanced AI processing for content analysis

- Claude API client
- Summary generation
- Tag refinement
- Content type classification
- Real-time processing for new bookmarks

**Key Deliverables:**
- Bookmarks have AI-generated summaries
- Tags are semantic and high-quality
- Content types automatically classified

---

### Week 6: Batch Processing

**Focus:** Cost-optimized background processing

- Celery task queue setup
- Redis configuration
- Weekly batch job for clustering
- Daily ephemeral content processing
- Error handling and retry logic

**Key Deliverables:**
- Batch API working for weekly processing
- Clustering algorithm functional
- Scheduled jobs running reliably

---

### Week 7: Project Mode

**Focus:** Project-based filtering and organization

- Project embedding calculation
- Smart project suggestion on save
- Project filtering in sidebar
- Quick-switch keyboard shortcuts
- Active project indicator

**Key Deliverables:**
- Users can create/manage projects
- Project suggestions >80% acceptance
- Quick-switch (Alt+Shift+P) working

---

### Week 8: Engagement Tracking & Optimization

**Focus:** Usage analytics and performance tuning

- Implement bookmark engagement tracking (last_opened_at, open_count)
- Tab listener for passive URL matching
- "Dead Bookmarks" filter UI
- Enhanced relevance scoring with engagement boost
- Load testing (1000+ bookmarks)
- Embedding cache optimization
- UI/UX refinements
- Bug fixes
- Documentation

**Key Deliverables:**
- Engagement tracking functional
- "Dead Bookmarks" filter showing unused items
- System handles 1000+ bookmarks smoothly
- Performance targets met (see reference.md)

---

### Phase 2 Deliverables (End of Week 8)

- ✅ Intelligent auto-tagging and summarization
- ✅ Batch processing pipeline
- ✅ Full project mode functionality
- ✅ Bookmark engagement tracking
- ✅ Optimized performance

**Success Criteria:**
- 85%+ auto-tags accepted without modification
- Batch processing costs 50% less than real-time
- Project suggestions 80%+ accurate
- Engagement tracking identifies dead bookmarks

---

## Phase 3: Advanced Features (Weeks 9-12)

### Week 9: AI Chat Interface

**Focus:** Natural language search

- Natural language query parsing
- Hybrid search implementation
- Chat UI in extension
- Query history
- Result ranking

**Key Deliverables:**
- Chat interface in popup
- Queries like "find docker tutorials" working
- Comparative queries supported

---

### Week 10: Ephemeral Content Workflow

**Focus:** Auto-extraction to Google Docs

- Google Docs OAuth integration
- Content extraction (Playwright)
- Batch processing for tweets/Reddit
- Auto-deletion of old ephemeral bookmarks

**Key Deliverables:**
- OAuth flow functional
- Tweets/Reddit extracted to Docs
- Ephemeral bookmarks auto-delete after 30 days

---

### Week 11: Cross-Project Search

**Focus:** Advanced search across projects

- Multi-project filtering
- Advanced query syntax
- Saved searches
- Search analytics

**Key Deliverables:**
- Users can search across multiple projects
- Saved searches feature working
- Analytics showing search patterns

---

### Week 12: Polish & Launch

**Focus:** Production readiness

- Web dashboard (optional)
- Onboarding flow
- User documentation
- Chrome Web Store submission
- Beta user testing

**Key Deliverables:**
- Extension submitted to Chrome Web Store
- Onboarding guides complete
- Beta users invited
- Documentation published

---

### Phase 3 Deliverables (End of Week 12)

- ✅ Full AI chat interface
- ✅ Ephemeral content → Google Docs
- ✅ Advanced search capabilities
- ✅ Production-ready system

**Success Criteria:**
- 90%+ of chat queries return relevant results
- 95%+ ephemeral content successfully processed
- Chrome Web Store approval received
- 20+ beta users testing

---

## Future Enhancements (Post-V1)

### Advanced AI Features
- **Bookmark Summarization:** Auto-generate weekly digests with engagement stats
- **Duplicate Detection:** Flag similar bookmarks across projects (>90% similarity)
- **Smart Recommendations:** "Users who bookmarked X also bookmarked Y" (collaborative filtering)
- **Learning Mode:** Flashcard generation from saved articles
- **Content Change Detection:** Alert when bookmarked pages are updated or deleted (404s)
- **Reading Time Estimates:** ML-based prediction of time to read each bookmark

### Collaboration Features
- **Shared Projects:** Team workspaces
- **Bookmark Sharing:** Share individual bookmarks with metadata
- **Social Layer:** See what your team bookmarks (opt-in)

### Platform Expansion
- **Firefox Extension:** Port from Chrome
- **Mobile Apps:** iOS/Android with sync
- **CLI Tool:** Command-line bookmark management
- **API Access:** Public API for third-party integrations

### Enterprise Features
- **SSO Integration:** SAML/OAuth for enterprise
- **Admin Dashboard:** Team analytics
- **Custom Models:** Fine-tuned embeddings for company data
- **On-Premise:** Self-hosted option

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Chrome Web Store rejection | High | Follow all Manifest V3 guidelines, clear privacy policy |
| Qdrant performance issues at scale | Medium | Load test early, have pgvector backup plan |
| Claude API rate limits | Medium | Implement batch processing, queue management |
| Embedding costs exceed budget | Low | Monitor usage, offer batch-only tier |

### Product Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Users don't adopt engagement tracking | Medium | Make value clear in onboarding, show dead bookmark count |
| Project suggestions inaccurate | Medium | Start with >80% confidence threshold, allow manual override |
| Context surfacing feels intrusive | High | User-triggered only, clear privacy messaging |

---

## Success Milestones

| Milestone | Week | Criteria |
|-----------|------|----------|
| MVP Feature Complete | 4 | All P0 features working |
| First Beta User | 8 | One external user successfully using system |
| Cost Targets Met | 8 | <$0.75/user/month confirmed |
| 10 Beta Users | 12 | 10 active users with feedback |
| Chrome Store Live | 12 | Extension publicly available |
| 100 Users | 16 (Post-launch) | First growth milestone |

---

**Next**: Review [Cost Analysis & Reference](reference.md) for detailed metrics and open questions.
