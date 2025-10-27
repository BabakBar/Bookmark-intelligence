# Feature Specifications

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Roadmap](roadmap.md) | [Reference](reference.md)

---

## Table of Contents

- [P0 Features (MVP Critical)](#p0-features-mvp-critical)
  - [Context-Aware Surfacing](#21-context-aware-surfacing)
  - [Intelligent Clustering & Auto-Tagging](#22-intelligent-clustering--auto-tagging)
  - [Project Mode](#23-project-mode)
- [P1 Features (Post-MVP)](#p1-features-post-mvp)
  - [AI Chat Interface](#24-ai-chat-interface)
  - [Ephemeral Content Workflow](#25-ephemeral-content-workflow)
  - [Contextual Saving](#26-contextual-saving-smart-project-detection)
  - [Bookmark Engagement Tracking](#27-bookmark-engagement-tracking)
- [P2 Features (Future)](#p2-features-future)
  - [Cross-Project Search](#28-cross-project-search)
- [User Interface Design](#user-interface-design)

---

## P0 Features (MVP Critical)

### 2.1 Context-Aware Surfacing

**Priority:** P0 (MVP Critical)

**Description:**
Browser extension captures the current page context when the user saves a bookmark or explicitly requests related items, then surfaces relevant saved bookmarks in a persistent sidebar. The feature avoids continuous background monitoring and instead reacts to the user's save workflow.

**User Flow:**
1. User selects "Save bookmark" while on `kubernetes.io/docs`
2. Extension captures context at save time: `domain: kubernetes.io, keywords: ["kubernetes", "container", "orchestration"]`
3. System generates an embedding from the captured context
4. Vector search returns similar bookmarks
5. Sidebar surfaces suggestions such as:
  - "Kubernetes Tutorial (saved 2 months ago)"
  - "Your company's K8s setup guide (FabrikTakt project)"
  - "Helm charts best practices"

**Technical Requirements:**
- Context snapshot captured on bookmark save or manual "Show related" action (no continuous polling)
- Embedding generation: <500ms (p95)
- Vector search: <100ms (p95)
- End-to-end latency: <2s from save action to sidebar render (p95)
- Sidebar renders top 5 results
- Click tracking for relevance feedback

**Alternative Trigger:**
User can manually click "Show Related Bookmarks" button in the extension popup while browsing (without saving) to see similar bookmarks for the current page. This provides on-demand discovery without committing to save the page.

**Success Metrics:**
- 70%+ of bookmark save sessions with suggestions lead to a click within 5 min
- Average time to find a related bookmark reduced by 60% vs. manual search
- 30%+ of "Show Related" manual queries result in opening a suggested bookmark

---

### 2.2 Intelligent Clustering & Auto-Tagging

**Priority:** P0 (MVP Critical)

**Description:**
AI automatically analyzes bookmark content to generate semantic tags and cluster related bookmarks. Initial processing happens on save (real-time), with deeper analysis in weekly batch jobs.

**User Flow:**
1. User saves article: "Getting Started with Terraform on AWS"
2. Real-time: Claude generates tags in 2-3 seconds
   - Tags: `#terraform`, `#aws`, `#infrastructure-as-code`, `#devops`
   - Content type: `tutorial`
   - Difficulty: `beginner`
3. Weekly batch: System identifies this clusters with 12 other IaC bookmarks
4. User sees suggested cluster: "Infrastructure as Code" (13 bookmarks)
5. User can accept, rename, or ignore cluster suggestion

**Technical Requirements:**
- Tag generation: 3-7 tags per bookmark
- Clustering algorithm: K-means with auto-K detection (elbow method)
- Minimum cluster size: 3 bookmarks
- Re-clustering frequency: Weekly
- Tag suggestion confidence threshold: 0.7

**Data Schema:**
```
Bookmark {
  id: UUID
  url: string
  title: string
  tags: string[]
  content_type: enum [tutorial, documentation, article, video, tool]
  summary: string (2-3 sentences)
  embedding: float[] (1536 dimensions)
  cluster_id: UUID (nullable)
  last_opened_at: timestamp (nullable)
  first_opened_at: timestamp (nullable)
  open_count: integer (default: 0)
  created_at: timestamp
  user_id: UUID
}

Cluster {
  id: UUID
  name: string
  bookmark_ids: UUID[]
  representative_keywords: string[]
  created_at: timestamp
}
```

**Success Metrics:**
- 85%+ of auto-tags accepted without modification
- Clustering accuracy: 80%+ (measured by user corrections)

---

### 2.3 Project Mode

**Priority:** P0 (MVP Critical)

**Description:**
Users create Projects (e.g., "FabrikTakt", "German Learning") that act as filtered workspaces. When a project is active, only its bookmarks are visible. AI suggests which project new bookmarks belong to based on content similarity.

**User Flow:**
1. User creates project "FabrikTakt" and adds existing bookmarks manually
2. Next day, user saves article: "Grafana Dashboard Design Patterns"
3. System analyzes article content + existing FabrikTakt bookmarks
4. Suggests: "This looks like it belongs in FabrikTakt project (85% confidence)"
5. User confirms
6. Extension icon badge updates to show active project

**Project Types:**
- **Active Projects:** User is currently working on (max 3 simultaneous)
- **Archived Projects:** Completed or on-hold
- **Auto-Archived:** No interaction for 30 days → system suggests archiving

**Technical Requirements:**
- Project embedding: Average of all bookmark embeddings in project
- Suggestion threshold: >70% cosine similarity
- Quick-switch menu: Keyboard shortcut (Alt+Shift+P)
- Project context includes: name, description, keywords, last_active_date

**Data Schema:**
```
Project {
  id: UUID
  name: string
  description: string
  is_active: boolean
  bookmark_ids: UUID[]
  context_keywords: string[]
  embedding: float[] (1536 dimensions)
  last_active: timestamp
  user_id: UUID
}
```

**UI Elements:**
- Extension icon badge: Shows active project abbreviation (e.g., "FT" for FabrikTakt)
- Sidebar: Project filter dropdown
- Context menu: "Add to project..." option

**Success Metrics:**
- 80%+ project suggestions accepted
- Average bookmarks per project: 20-50
- Time to find project-specific bookmark: <5 seconds

---

## P1 Features (Post-MVP)

### 2.4 AI Chat Interface

**Priority:** P1 (Post-MVP)

**Description:**
Natural language search interface allowing users to query their bookmark library conversationally. Powered by semantic search + Claude for query understanding.

**Example Queries:**
```
User: "show me all docker tutorials I saved"
System: [Returns 8 bookmarks with "docker" + "tutorial" semantics]

User: "what kubernetes links did I save in January?"
System: [Filters by date range + keyword]

User: "find that reddit post about Grafana alerting"
System: [Searches ephemeral bookmarks, finds Reddit post]

User: "compare the terraform tutorials I saved"
System: [Generates comparison table of 4 tutorials]
```

**Technical Architecture:**
1. User query → Claude API for intent extraction
2. Claude returns structured search parameters:
   ```json
   {
     "keywords": ["docker", "tutorial"],
     "date_range": null,
     "project": null,
     "content_type": "tutorial"
   }
   ```
3. Backend executes hybrid search:
   - Vector search on query embedding (semantic)
   - Metadata filters (date, tags, project)
4. Results ranked by relevance score
5. Optional: Claude summarizes results

**Technical Requirements:**
- Query latency: <2 seconds (p95)
- Support for temporal queries: "last month", "this year", "after January 1"
- Support for comparative queries: "compare X and Y"
- Chat history: Last 10 exchanges per session (client-side)

**Success Metrics:**
- 90%+ queries return relevant results (user feedback)
- Average results per query: 3-8 bookmarks

---

### 2.5 Ephemeral Content Workflow

**Priority:** P1 (Post-MVP)

**Description:**
Special handling for "read later" content like tweets and Reddit posts. System automatically extracts key insights and appends to a designated Google Doc, preventing bookmark accumulation.

**User Flow:**
1. User sees interesting tweet, clicks "Bookmark" with "Read Later" tag
2. System marks bookmark as `ephemeral=true`
3. Daily batch job runs:
   - Fetches tweet content via API/scraping
   - Claude extracts key insights (2-3 bullet points)
   - Appends to user's Google Doc: "Tech Insights - October 2025"
   - Marks bookmark as `processed=true`
4. After 30 days, processed ephemeral bookmarks auto-delete

**Google Docs Output Format:**
```markdown
## [Tweet Title] - @username
**Source:** [Tweet URL]
**Saved:** October 27, 2025

**Key Insights:**
- Insight point 1
- Insight point 2
- Insight point 3

---
```

**Technical Requirements:**
- Content extraction: Playwright for dynamic sites
- Processing frequency: Daily (3 AM user timezone)
- Google Docs API integration with OAuth 2.0
- Batch processing: Up to 50 ephemeral items per day
- Auto-delete threshold: 30 days post-processing

**Data Schema:**
```
Bookmark (extended) {
  ...
  is_ephemeral: boolean
  processed: boolean
  processed_at: timestamp (nullable)
  google_doc_id: string (nullable)
  last_opened_at: timestamp (nullable)
  first_opened_at: timestamp (nullable)
  open_count: integer (default: 0)
}
```

**Success Metrics:**
- 95%+ ephemeral content successfully processed
- Average processing time: <12 hours
- User satisfaction: 80%+ find extracted insights valuable

---

### 2.6 Contextual Saving (Smart Project Detection)

**Priority:** P1 (Post-MVP)

**Description:**
When saving a new bookmark, system analyzes its content against existing projects and suggests the best match. Reduces manual categorization.

**User Flow:**
1. User saves article: "FastAPI Performance Optimization"
2. System generates embedding, compares with all project embeddings
3. Results:
   - "OrX" project: 87% match (contains FastAPI/Python content)
   - "Personal Website" project: 23% match
4. UI shows: "Suggested for OrX project" with confidence badge
5. User confirms or selects different project

**Technical Implementation:**
```python
async def suggest_project(bookmark_embedding):
    projects = get_user_projects()
    similarities = []

    for project in projects:
        # Project embedding = average of all bookmark embeddings
        project_embedding = np.mean([b.embedding for b in project.bookmarks])
        similarity = cosine_similarity(bookmark_embedding, project_embedding)
        similarities.append((project, similarity))

    # Return top 2 suggestions with >70% confidence
    return [s for s in sorted(similarities, reverse=True)[:2] if s[1] > 0.7]
```

**Success Metrics:**
- Suggestion accuracy: 85%+ (measured by user acceptance)
- Suggestions provided: 90%+ of new bookmarks

---

### 2.7 Bookmark Engagement Tracking

**Priority:** P1 (Post-MVP)

**Description:**
Track when users actually open their bookmarks to identify "dead" bookmarks that were saved but never used. Surfaces engagement patterns to help users clean up their library and prioritize relevant content.

**User Flow:**
1. User clicks on a bookmarked link from sidebar/popup
2. Extension tracks `last_opened_at` timestamp and increments `open_count`
3. Weekly digest shows engagement insights:
   - "You opened 12 bookmarks this week"
   - "47 bookmarks saved >6 months ago have never been opened"
4. User sees "Dead Bookmarks" filter showing unused bookmarks
5. Bulk actions: Archive or delete unused bookmarks

**Engagement-Based Features:**
- **Smart Sorting:** Sidebar can sort by "Most Used" vs "Recently Saved"
- **Relevance Boosting:** Frequently-opened bookmarks rank higher in search
- **Stale Content Warnings:** "You saved this 8 months ago but never opened it. Still relevant?"
- **Archive Suggestions:** System suggests archiving bookmarks with 0 opens after 6+ months

**Technical Requirements:**
- Passive tracking via `chrome.tabs.onUpdated` listener
- URL matching: Check if opened tab matches any bookmark URL
- Privacy-preserving: Only tracks opens, not browsing behavior
- Batch updates: Queue tracking events, sync every 5 minutes to reduce API calls

**Data Schema Updates:**
```sql
ALTER TABLE bookmarks ADD COLUMN last_opened_at TIMESTAMP;
ALTER TABLE bookmarks ADD COLUMN open_count INTEGER DEFAULT 0;
ALTER TABLE bookmarks ADD COLUMN first_opened_at TIMESTAMP;

CREATE INDEX idx_bookmarks_last_opened ON bookmarks(last_opened_at);
CREATE INDEX idx_bookmarks_engagement ON bookmarks(user_id, open_count DESC);
```

**Enhanced Relevance Scoring:**
```python
def calculate_relevance(bookmark, query_embedding, current_time):
    vector_score = cosine_similarity(bookmark.embedding, query_embedding)

    # Recency decay: newer bookmarks get small boost
    days_old = (current_time - bookmark.created_at).days
    recency_score = 1 / (1 + days_old / 30)  # Decays over ~30 days

    # Engagement boost: frequently-used bookmarks rank higher
    engagement_score = min(bookmark.open_count / 10, 1.0)  # Cap at 10 opens

    # Weighted combination
    return (
        0.6 * vector_score +      # Semantic relevance (primary)
        0.25 * engagement_score +  # Usage frequency
        0.15 * recency_score       # Freshness
    )
```

**UI Components:**
- Sidebar: "Most Used This Week" section
- Popup: Badge showing "3 unread" (saved but never opened)
- Settings: Toggle engagement tracking on/off
- Analytics page: Heatmap of bookmark usage over time

**Success Metrics:**
- 40%+ of users enable "Dead Bookmarks" cleanup feature
- Average library size reduced by 20% after 3 months (healthier collections)
- Engagement-boosted search results: 15% higher click-through rate

---

## P2 Features (Future)

### 2.8 Cross-Project Search

**Priority:** P2 (Future)

**Description:**
Advanced search that spans multiple projects simultaneously. Useful for finding patterns or connections across different work contexts.

**Example Query:**
```
"find all Grafana-related bookmarks across FabrikTakt and Personal projects"
```

**Technical Implementation:**
Extends AI Chat Interface (#2.4) with multi-project filtering.

---

## User Interface Design

### Extension Popup

**Dimensions:** 400px × 600px
**Trigger:** Click extension icon

**Components:**
- **Search Bar:** Natural language query input
- **Active Project Badge:** Shows current project (if any)
- **Quick Actions:**
  - "Add Current Page"
  - "Show Related Bookmarks" (triggers context search without saving)
  - "Switch Project"
  - "Open Chat"
- **Recent Bookmarks:** Last 5 saved (with thumbnails)
- **Settings Icon:** Opens options page

---

### Sidebar Panel

**Position:** Right side of browser
**Width:** 320px (resizable)
**Trigger:** User opens sidebar as needed (can be collapsed); suggestions refresh when a bookmark is saved or the user selects "Show related"

**Sections:**

1. **Context Suggestions** (Top) — refreshes right after a bookmark is saved or "Show related" is requested
  - "Relevant to this saved page:"
   - 5 bookmark cards with:
     - Title
     - Tags (pills)
     - Relevance score (%)
     - Project badge

2. **Active Project Bookmarks** (Middle)
   - Filtered list if project is active
   - Search bar (project-scoped)

3. **Quick Filters** (Bottom)
   - Recent (24h)
   - This Week
   - Most Used (sorted by open_count)
   - Never Opened (open_count = 0)
   - Dead Bookmarks (saved >6mo, never opened)
   - Untagged
   - Ephemeral

---

### Web Dashboard (Optional)

**URL:** `app.bookmarkai.com`
**Tech:** React + Tailwind CSS

**Pages:**
1. **Dashboard:** Overview stats, recent activity
2. **Bookmarks:** Grid/list view, advanced filters
3. **Projects:** Manage projects, bulk operations
4. **Analytics:** Usage patterns, tag cloud
5. **Settings:** API keys, Google Docs integration

---

**Next**: Review the [Development Roadmap](roadmap.md) for implementation phases and timelines.
