# Development Roadmap

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Features](features.md) | [Reference](reference.md)

---

## Development Timeline Overview

**Total Duration:** 14 weeks to production-ready system

- **Phase 0 (Weeks 1-2):** Bootstrap - Import existing bookmarks, AI processing, infrastructure setup
- **Phase 1 (Weeks 3-6):** MVP - Browser extension for new bookmarks, auto-tagging, context surfacing
- **Phase 2 (Weeks 7-10):** Intelligence - Project mode optimization, engagement tracking
- **Phase 3 (Weeks 11-14):** Advanced - AI chat, ephemeral content, polish & launch

---

## Phase 0: Bootstrap & Import (Weeks 1-2)

**Critical First Step:** No user starts with zero bookmarks. This phase handles the cold-start problem by importing and organizing existing bookmark collections before building the browser extension.

### Week 1: Infrastructure & Import

**Focus:** Deploy infrastructure and import existing bookmarks

**Prerequisites:**
- Hetzner VPS CX32 provisioned
- Coolify deployment platform configured
- GitHub repository set up
- Bookmark export files ready (HTML, MD, JSON formats)

**Tasks:**
- Deploy PostgreSQL 17 container via Coolify
- Deploy Qdrant 1.12 container via Coolify
- Deploy Valkey 7.4 container via Coolify
- Initialize FastAPI backend with basic endpoints
- Set up user authentication (JWT)
- Implement HTML bookmark parser using `bookmarks-parser` library
- Create `/api/v1/import` endpoint for bookmark upload
- Build simple web interface for bookmark import

**Key Deliverables:**
- All infrastructure services running on Hetzner VPS
- Import API accepts HTML files (Chrome/Firefox/Safari formats)
- 800 bookmarks imported into PostgreSQL with zero data loss
- Progress tracking shows "Imported 800 of 800 bookmarks (100%)"

**Testing:**
- Export bookmarks from Chrome as HTML
- Upload to import endpoint
- Verify all 800 URLs and titles in database

---

### Week 2: AI Processing & Organization

**Focus:** Batch process all imported bookmarks with AI

**Tasks:**
- Integrate OpenAI Batch API for embeddings (50% cost savings)
- Integrate Anthropic Claude 3.5 Haiku for tagging and summarization
- Implement batch processing job: Generate embeddings for all 800 bookmarks
- Implement batch AI tagging: 3-7 tags per bookmark
- Implement batch AI summarization: 2-3 sentence summary per bookmark
- Implement clustering algorithm: MiniBatchKMeans with cosine similarity
- Generate 8-15 semantic clusters with descriptive names
- Implement project suggestion algorithm based on cluster analysis
- Build web dashboard for reviewing results

**Key Deliverables:**
- All 800 bookmarks have embeddings stored in Qdrant
- All 800 bookmarks have AI-generated tags and summaries
- 8-15 clusters created (e.g., "Docker & Containers", "Infrastructure as Code")
- 3-5 initial projects suggested (e.g., "FabrikTakt", "Personal Learning")
- Web interface shows organized bookmarks by cluster and project

**Success Criteria:**
- Processing completes within 24 hours
- Total cost: $40-60 for 800 bookmarks (~$0.06/bookmark)
- 85%+ of AI tags are acceptable without manual editing
- Clusters are semantically meaningful and cover 90%+ of bookmarks
- User can browse organized bookmarks in web interface

**Testing:**
- Search for "docker" and see relevant bookmarks
- View "FabrikTakt" project and see work-related bookmarks
- Browse "Infrastructure as Code" cluster and verify accuracy

---

### Phase 0 Deliverables (End of Week 2)

- ✅ Infrastructure fully deployed (PostgreSQL, Qdrant, Valkey, FastAPI, Celery)
- ✅ All 800 existing bookmarks imported and organized
- ✅ AI-generated tags, summaries, embeddings on every bookmark
- ✅ Semantic clusters created (8-15 topic groups)
- ✅ Initial projects suggested (3-5 workspaces)
- ✅ Web interface for browsing and validating organization
- ✅ System validated and ready for Phase 1 extension development

**Cost Breakdown:**
- OpenAI embeddings: 800 bookmarks × 500 tokens = 400K tokens = $8
- Claude 3.5 Haiku: 800 bookmarks × (500 input + 150 output) tokens = $32
- **Total AI cost: ~$40 (one-time bootstrap)**
- Infrastructure: $13/month (Hetzner VPS)

**Why This Matters:**
Without Phase 0, users would need to manually re-save 800 bookmarks through the browser extension one by one. This phase delivers immediate value by organizing existing bookmarks, and proves the AI organization works correctly before committing to extension development.

---

## Phase 1: MVP (Weeks 3-6)

### Week 3: Foundation

**Focus:** Infrastructure validation and browser extension scaffold

- Validate Phase 0 infrastructure is stable
- Initialize Chrome Extension project (Manifest V3)
- Set up extension development environment
- Create basic extension popup UI
- Integrate extension with existing FastAPI backend

**Key Deliverables:**
- Functional backend server
- Database schemas deployed
- User registration/login working

---

### Week 4: Core Backend for Extension

**Focus:** Bookmark CRUD for real-time extension use

- Extend bookmark API for extension (already exists from Phase 0)
- Real-time embedding generation for new bookmarks
- Real-time AI tagging for new bookmarks (Claude 3.5 Haiku)
- Context-aware similarity search endpoint
- Project assignment suggestions

**Key Deliverables:**
- `/api/v1/bookmarks` endpoints support real-time saves from extension
- Real-time embedding generation (<500ms)
- Real-time AI tagging (<3s total)
- Similarity search returns related bookmarks for context surfacing

---

### Week 5: Browser Extension

**Focus:** Extension foundation and browser integration

- Chrome Extension scaffold (Manifest V3)
- Bookmark capture from browser
- Basic popup UI
- API client integration with Phase 0 backend
- Context detection (URL + title)

**Key Deliverables:**
- Extension installable in Chrome
- Can save bookmarks to backend
- Basic UI functional

---

### Week 6: Context-Aware Surfacing

**Focus:** Core feature implementation

- On-demand context analysis triggered by bookmark saves
- Vector similarity search against existing 800+ bookmarks
- Sidebar UI with suggestions
- Integration with Phase 0 projects and clusters
- Testing and refinement

**Key Deliverables:**
- Context-aware suggestions working (searches across existing organized bookmarks)
- Sidebar displays similar bookmarks with relevance scores
- User can click suggestions to open
- Suggestions filtered by active project if set

---

### MVP Deliverables (End of Week 6)

- ✅ Save NEW bookmarks with auto-tagging via browser extension
- ✅ Context-aware suggestions in sidebar (searches 800+ existing bookmarks)
- ✅ Project management (extends Phase 0 projects)
- ✅ Manual tag editing
- ✅ Working with existing organized bookmark collection from Phase 0

**Success Criteria:**
- User can save 10 new bookmarks and get relevant suggestions from existing 800
- Average suggestion latency < 2 seconds
- Zero critical bugs
- Extension integrates seamlessly with Phase 0 organized bookmarks

---

## Phase 2: Intelligence Layer (Weeks 7-10)

### Week 7: Enhanced AI Integration

**Focus:** Refine AI processing quality

- Optimize Claude 3.5 Haiku prompts for better tag quality
- Implement tag confidence scores
- Add content type classification improvements
- Enhance summary quality based on Phase 0 learnings

**Key Deliverables:**
- Improved tag quality (95%+ acceptance)
- Better summaries based on user feedback from Phase 0
- Content type classification accuracy >90%

---

### Week 8: Continuous Clustering

**Focus:** Extend Phase 0 clustering to handle new bookmarks

- Incremental clustering: add new bookmarks to existing clusters
- Cluster rebalancing algorithm
- New cluster creation threshold
- Cluster merge/split suggestions based on growth

**Key Deliverables:**
- New bookmarks automatically added to appropriate clusters
- Clusters stay balanced as collection grows
- UI shows cluster growth over time

---

### Week 9: Project Mode Enhancement

**Focus:** Improve project-based filtering and organization

- Enhanced project embedding (Phase 0 projects + new bookmarks)
- Smart project suggestion on save (integrates with existing projects)
- Project filtering in sidebar (shows Phase 0 + new bookmarks)
- Quick-switch keyboard shortcuts (Alt+Shift+P)
- Active project indicator in extension badge

**Key Deliverables:**
- Project suggestions >85% acceptance (improved from Phase 0 baseline)
- Quick-switch working seamlessly
- Extension badge shows active project

---

### Week 10: Engagement Tracking & Optimization

**Focus:** Usage analytics and performance tuning

- Implement bookmark engagement tracking (last_opened_at, open_count)
- Tab listener for passive URL matching
- "Dead Bookmarks" filter UI (identify unused bookmarks from Phase 0 + new ones)
- Enhanced relevance scoring with engagement boost
- Load testing (1000+ bookmarks from Phase 0 + new additions)
- Embedding cache optimization
- UI/UX refinements
- Bug fixes
- Documentation

**Key Deliverables:**
- Engagement tracking functional
- "Dead Bookmarks" filter showing unused items from original 800 + new saves
- System handles 1000+ bookmarks smoothly
- Performance targets met (see reference.md)

---

### Phase 2 Deliverables (End of Week 10)

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

## Phase 3: Advanced Features (Weeks 11-14)

### Week 11: AI Chat Interface

**Focus:** Natural language search over organized bookmarks

- Natural language query parsing with Claude
- Hybrid search implementation (semantic + filters)
- Chat UI in extension popup
- Query history (last 10 exchanges)
- Result ranking with engagement scores

**Key Deliverables:**
- Chat interface in popup searches across Phase 0 + new bookmarks
- Queries like "find docker tutorials from FabrikTakt project" working
- Comparative queries supported ("compare these terraform tutorials")

---

### Week 12: Ephemeral Content Workflow

**Focus:** Auto-extraction to Google Docs

- Google Docs OAuth integration
- Content extraction (Playwright for dynamic sites)
- Batch processing for tweets/Reddit
- Auto-deletion of old ephemeral bookmarks

**Key Deliverables:**
- OAuth flow functional
- Tweets/Reddit extracted to Docs
- Ephemeral bookmarks auto-delete after 30 days

---

### Week 13: Cross-Project Search & Analytics

**Focus:** Advanced search and insights

- Multi-project filtering
- Advanced query syntax
- Saved searches
- Search analytics dashboard
- Bookmark usage heatmaps

**Key Deliverables:**
- Users can search across multiple projects simultaneously
- Saved searches feature working
- Analytics showing bookmark usage patterns over time

---

### Week 14: Polish & Launch

**Focus:** Production readiness

- Enhance web dashboard (Phase 0 interface → full dashboard)
- Onboarding flow for new users
- User documentation and video tutorials
- Chrome Web Store submission
- Beta user testing and feedback incorporation

**Key Deliverables:**
- Extension submitted to Chrome Web Store
- Onboarding guides complete (including import flow for new users)
- Beta users invited (can start with Phase 0 import)
- Documentation published

---

### Phase 3 Deliverables (End of Week 14)

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
| chatgpt API rate limits | Medium | Implement batch processing, queue management, fallback to Haiku |
| Embedding costs exceed budget | Low | Monitor usage, self-hosted deployment reduces infrastructure costs by 93% |
| VPS resource exhaustion | Medium | Monitor resource usage, scale to CX52 or add instances via Coolify |

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
| **Phase 0 Complete** | **2** | **800 bookmarks imported, organized, and validated** |
| First User (Sia) Using System | 2 | Can browse organized bookmarks in web interface |
| MVP Feature Complete | 6 | Browser extension working with organized bookmarks |
| First Beta User | 10 | One external user successfully using system (with their own import) |
| Cost Targets Met | 10 | <$0.75/user/month confirmed (post-bootstrap) |
| 10 Beta Users | 14 | 10 active users with feedback |
| Chrome Store Live | 14 | Extension publicly available |
| 100 Users | 18 (Post-launch) | First growth milestone |

---

**Next**: Review [Cost Analysis & Reference](reference.md) for detailed metrics and open questions.
