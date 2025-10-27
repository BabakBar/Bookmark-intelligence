# Feature Specifications

**Navigation**: [Overview](overview.md) | [Architecture](architecture.md) | [Roadmap](roadmap.md) | [Reference](reference.md)

---

## Table of Contents

- [Phase 0: Bootstrap & Import](#phase-0-bootstrap--import-prerequisite)
  - [Bookmark Import from Browser](#01-bookmark-import-from-browser)
  - [Batch AI Processing](#02-batch-ai-processing)
  - [Automatic Clustering](#03-automatic-clustering)
  - [Project Suggestions](#04-project-suggestions)
  - [Web Dashboard for Validation](#05-web-dashboard-for-validation)
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

## Phase 0: Bootstrap & Import (Prerequisite)

**Critical First Step:** No user starts with zero bookmarks. Phase 0 handles the cold-start problem by importing and organizing existing bookmark collections before building the browser extension. This phase proves the AI organization works correctly and delivers immediate value.

### 0.1 Bookmark Import from Browser

**Priority:** Phase 0 (Must complete before MVP)

**Description:**
Users export their existing bookmarks from their browser as an HTML file and upload it to the web interface. The system parses the HTML and imports all bookmarks with zero data loss, preserving URLs, titles, and original folder structure.

**User Flow:**
1. User navigates to Chrome → Bookmarks → Bookmark Manager → ⋮ → Export bookmarks
2. Browser saves `bookmarks_27_10_2025.html` file with 800 bookmarks
3. User opens BookmarkAI web interface at `app.bookmarkai.local`
4. User clicks "Import Bookmarks" and selects the HTML file
5. System parses HTML using `bookmarks-parser` library (supports Chrome/Firefox/Safari)
6. Progress bar shows "Importing: 342 of 800 bookmarks (43%)"
7. Import completes: "Successfully imported 800 bookmarks"
8. User sees list of all imported bookmarks in the web interface

**Technical Requirements:**
- HTML parser supports Netscape-Bookmark-file format (Chrome/Firefox standard)
- Handle duplicate URLs: Keep first occurrence, flag duplicates
- Preserve folder structure as preliminary tags
- Import status tracking with progress percentage
- Error handling for malformed HTML or invalid URLs
- Maximum file size: 50MB (~50,000 bookmarks)

**Success Metrics:**
- 100% import success rate (zero data loss)
- Processing time: <30 seconds for 1000 bookmarks
- Accurate URL and title extraction for all supported browsers

---

### 0.2 Batch AI Processing

**Priority:** Phase 0 (Must complete before MVP)

**Description:**
After import, the system automatically processes all bookmarks in batch mode to generate embeddings, AI tags, and summaries. Uses OpenAI Batch API for 50% cost savings and Claude 3.5 Haiku for fast, cost-effective analysis.

**User Flow:**
1. After import completes, user clicks "Start AI Processing"
2. System shows cost estimate: "$42 for 800 bookmarks (OpenAI: $8, Claude: $34)"
3. User confirms and processing begins
4. Progress dashboard shows:
   - "Generating embeddings: 456/800 (57%)"
   - "Creating tags & summaries: 234/800 (29%)"
   - "Estimated completion: 18 hours"
5. User receives email notification when complete
6. User reviews results: Every bookmark now has 3-7 tags and a 2-3 sentence summary

**Technical Requirements:**
- OpenAI Batch API integration (50% cost savings vs real-time)
- Claude 3.5 Haiku integration for tag generation
- Batch size: Process 100 bookmarks per API request
- Error handling: Mark failed bookmarks, continue processing others
- Retry logic for transient API failures
- Cost tracking and reporting
- Processing time: <24 hours for 1000 bookmarks

**Tag Generation Prompt:**
```
Analyze this bookmark and generate 3-7 semantic tags:

URL: {url}
Title: {title}
Content preview: {first_500_chars}

Return tags as JSON: {"tags": ["tag1", "tag2", ...], "content_type": "tutorial|documentation|article|video|tool", "summary": "2-3 sentence summary"}
```

**Success Metrics:**
- 100% of successfully imported bookmarks receive embeddings
- 95%+ of bookmarks receive AI-generated tags and summaries
- Processing cost: <$0.06 per bookmark
- 85%+ of AI-generated tags accepted without manual editing

---

### 0.3 Automatic Clustering

**Priority:** Phase 0 (Must complete before MVP)

**Description:**
After AI processing completes, the system automatically groups related bookmarks into semantic clusters using MiniBatchKMeans clustering on the embedding vectors. Generates descriptive cluster names using AI.

**User Flow:**
1. After AI processing, system automatically runs clustering
2. Algorithm creates 12 clusters from 800 bookmarks
3. User reviews suggested clusters in web interface:
   - "Docker & Containers" (34 bookmarks)
   - "Infrastructure as Code" (23 bookmarks: Terraform, Ansible, Pulumi)
   - "React Best Practices" (18 bookmarks)
   - "Kubernetes & Orchestration" (45 bookmarks)
   - "Python Web Development" (29 bookmarks)
   - ...and 7 more clusters
4. User can rename clusters (e.g., "Cloud Stuff" → "AWS Architecture")
5. User can merge similar clusters (e.g., "Docker" + "Containers" → "Docker & Containers")
6. User can view bookmarks in each cluster to verify accuracy

**Technical Requirements:**
- MiniBatchKMeans clustering (scalable for large datasets)
- Cosine similarity distance metric (better for text embeddings)
- Optimal K detection using elbow method (8-15 clusters typical)
- L2 normalization of embeddings before clustering
- Minimum cluster size: 3 bookmarks
- Cluster name generation using Claude based on representative keywords
- Silhouette score calculation for cluster quality assessment

**Clustering Algorithm:**
```python
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import normalize

# Normalize embeddings (L2-norm = 1)
embeddings_normalized = normalize(embeddings, norm='l2')

# Find optimal K using elbow method
silhouette_scores = []
for k in range(8, 16):
    kmeans = MiniBatchKMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(embeddings_normalized)
    score = silhouette_score(embeddings_normalized, labels, metric='cosine')
    silhouette_scores.append((k, score))

optimal_k = max(silhouette_scores, key=lambda x: x[1])[0]

# Final clustering
kmeans = MiniBatchKMeans(n_clusters=optimal_k, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings_normalized)
```

**Success Metrics:**
- 90%+ of bookmarks assigned to a cluster
- Clustering accuracy: 80%+ (measured by user corrections)
- Silhouette score: >0.3 (indicates decent cluster separation)
- Cluster coverage: 8-15 clusters for 500-1000 bookmarks

---

### 0.4 Project Suggestions

**Priority:** Phase 0 (Must complete before MVP)

**Description:**
Based on the created clusters, the system suggests 3-5 initial projects (high-level workspaces) that represent major topic areas. Users can accept, rename, or reject suggestions.

**User Flow:**
1. After clustering completes, system analyzes cluster patterns
2. System suggests 5 projects based on bookmark distribution:
   - "FabrikTakt Work" (187 bookmarks: Grafana, Docker, AWS, infrastructure)
   - "Personal Learning" (134 bookmarks: tutorials, courses, documentation)
   - "Web Development" (215 bookmarks: React, TypeScript, frontend)
   - "German Language" (89 bookmarks: Duolingo, grammar resources)
   - "Health & Fitness" (78 bookmarks: workout plans, nutrition)
3. User reviews project suggestions
4. User renames "Personal Learning" → "Tech Learning"
5. User rejects "Health & Fitness" (not relevant)
6. User accepts remaining 4 projects
7. System automatically assigns bookmarks to accepted projects based on cluster membership

**Technical Requirements:**
- Project suggestion based on cluster size and topic diversity
- Project embedding: Average of all member bookmark embeddings
- Suggest 3-5 projects covering 80%+ of all bookmarks
- Project name generation using Claude based on cluster themes
- User can manually adjust bookmark-to-project assignments
- Unassigned bookmarks remain in "Uncategorized" project

**Project Suggestion Algorithm:**
```python
def suggest_projects(clusters, min_projects=3, max_projects=5):
    # Group clusters by topic similarity
    cluster_groups = []
    for cluster in clusters:
        # Find existing group with similar theme
        matched = False
        for group in cluster_groups:
            similarity = cosine_similarity(cluster.embedding, group.embedding)
            if similarity > 0.75:
                group.add_cluster(cluster)
                matched = True
                break

        if not matched:
            cluster_groups.append(ProjectGroup([cluster]))

    # Generate project suggestions from groups
    projects = []
    for group in sorted(cluster_groups, key=lambda g: g.size, reverse=True)[:max_projects]:
        project_name = generate_project_name(group.clusters)
        projects.append({
            "name": project_name,
            "bookmark_count": group.size,
            "clusters": [c.name for c in group.clusters],
            "keywords": group.representative_keywords
        })

    return projects
```

**Success Metrics:**
- Suggested projects cover 80%+ of all bookmarks
- 70%+ of project suggestions accepted by users
- Project names are descriptive and meaningful
- Average 3-5 projects suggested per user

---

### 0.5 Web Dashboard for Validation

**Priority:** Phase 0 (Must complete before MVP)

**Description:**
Simple web interface (not the full extension) for browsing imported bookmarks, viewing clusters and projects, searching, and validating that the AI organization worked correctly before proceeding to Phase 1.

**User Flow:**
1. User logs into web dashboard at `app.bookmarkai.local`
2. Dashboard shows summary:
   - "800 bookmarks imported and organized"
   - "12 clusters created"
   - "4 projects suggested and accepted"
   - "Processing cost: $42"
3. User can:
   - Browse all bookmarks (grid or list view)
   - Search by keyword: "kubernetes" returns 45 results
   - Filter by cluster: View "Docker & Containers" (34 bookmarks)
   - Filter by project: View "FabrikTakt Work" (187 bookmarks)
   - Edit tags manually if AI got them wrong
   - Rename clusters or projects
   - View bookmark details (URL, title, tags, summary, cluster, project)
4. User validates organization is correct before committing to Phase 1 extension development

**UI Components:**
- **Dashboard Page:** Summary stats, recent imports, processing status
- **Bookmarks Page:** Grid/list view, search, filters (cluster, project, tags)
- **Clusters Page:** List of all clusters with bookmark counts, edit/merge/delete
- **Projects Page:** List of all projects with bookmark counts, manage assignments
- **Settings Page:** API keys, processing configuration, user profile

**Technical Requirements:**
- Simple React web app (not the extension)
- REST API integration with FastAPI backend
- Search: Full-text search across titles, URLs, tags, summaries
- Filters: Multi-select (cluster, project, tags)
- Pagination: 50 bookmarks per page
- Mobile-responsive design (Tailwind CSS)

**Success Metrics:**
- Page load time: <2 seconds for 1000 bookmarks
- Search results: <500ms
- Users can validate organization in <1 hour
- 90%+ of users proceed to Phase 1 after validation

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
2. Real-time: chatgpt generates tags in 2-3 seconds
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
Natural language search interface allowing users to query their bookmark library conversationally. Powered by semantic search + chatgpt for query understanding.

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
1. User query → chatgpt API for intent extraction
2. chatgpt returns structured search parameters:
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
5. Optional: chatgpt summarizes results

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
   - chatgpt extracts key insights (2-3 bullet points)
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
