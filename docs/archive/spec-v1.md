# Contextual Bookmark Intelligence System
## Product Specification Document v1.0
**Last Updated:** October 27, 2025  
**Project Codename:** BookmarkAI  

---

## Executive Summary

Contextual Bookmark Intelligence is an AI-powered browser extension and backend system designed to transform static bookmark collections into dynamic, context-aware knowledge management tools. The system addresses the "bookmark graveyard" problem by using machine learning to surface relevant bookmarks based on browsing context, automatically categorizing and tagging content, and providing natural language search capabilities.

### Key Value Propositions
- **Context-Aware Surfacing**: Surface relevant bookmarks when saving new pages to prevent duplicates and discover connections
- **Intelligent Organization**: AI-powered clustering and tagging eliminates manual folder management
- **Project-Based Workflows**: Dynamic workspaces that adapt to active projects
- **Natural Language Search**: Ask questions like "find docker tutorials from January" instead of navigating folder hierarchies
- **Cost-Optimized AI Processing**: 50% cost savings through batch processing for non-urgent tasks
- **Ephemeral Content Workflow**: Automated extraction of valuable insights from tweets/Reddit posts to Google Docs

### Target User
Cloud engineers, software developers, and knowledge workers managing 500+ bookmarks across multiple contexts (work, personal, learning) who frequently switch between projects.

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────┐
│   Browser Extension (Chrome/Brave)  │
│   - Context Detection               │
│   - UI/Sidebar                      │
│   - Bookmark Capture                │
└────────────┬────────────────────────┘
             │ REST API / WebSocket
             │
┌────────────▼────────────────────────┐
│      Backend API Server             │
│      (FastAPI + Python 3.11+)       │
│   - Authentication                  │
│   - Request Routing                 │
│   - Real-time Processing            │
└────────────┬────────────────────────┘
             │
   ┌─────────┴─────────┐
   │                   │
┌──▼────────────┐  ┌──▼──────────────┐
│  Job Queue    │  │  AI Processing  │
│  (Celery +    │  │  Layer          │
│   Redis)      │  │  - Claude API   │
│               │  │  - OpenAI Embed │
└───────────────┘  └─────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │                                     │
┌───────▼─────────┐              ┌───────────▼──────┐
│  Vector Store   │              │  Metadata Store  │
│  (Qdrant)       │              │  (PostgreSQL)    │
│  - Embeddings   │              │  - Users         │
│  - Similarity   │              │  - Bookmarks     │
│    Search       │              │  - Projects      │
└─────────────────┘              └──────────────────┘
```

### 1.2 Data Flow

#### Real-Time Flow (New Bookmark)
1. User saves bookmark in browser
2. Extension captures metadata (URL, title, DOM context)
3. Backend generates embedding via OpenAI API
4. AI generates summary + tags using Claude (real-time)
5. System suggests matching project
6. Data stored in PostgreSQL + Vector DB
7. User confirms/adjusts project assignment

#### Batch Processing Flow (Daily/Weekly)
1. Celery scheduled job collects unprocessed bookmarks
2. Batch request submitted to Claude API (50% discount)
3. Results returned within 24 hours
4. Embeddings updated, clusters recalculated
5. Ephemeral content processed → Google Docs
6. Project contexts updated

#### Context-Aware Surfacing Flow

1. User saves a bookmark or selects "Show related" for the current page
2. Extension captures a one-time context snapshot (URL, title, keywords, timestamp)
3. Backend generates an embedding from the snapshot
4. Vector search returns similar bookmarks, filtered by the user's active project when set
5. Sidebar surfaces the top 5-10 relevant bookmarks with relevance scores
6. User reviews suggestions alongside the save flow

---

## 2. Core Features Specification

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

## 3. Technology Stack (2025 Modern Standards)

### 3.1 Browser Extension

**Framework:** Chrome Extension Manifest V3  
**Why:** Required standard as of June 2025; V2 deprecated

**Stack:**
- **Language:** TypeScript 5.x
- **UI Framework:** React 18.x with Hooks
- **Styling:** Tailwind CSS 3.x
- **State Management:** Zustand (lightweight, <1KB)
- **Build Tool:** Vite 5.x (faster than Webpack)
- **API Client:** Axios with interceptors

**Key Files:**
```
/extension
├── manifest.json (V3)
├── src/
│   ├── background/
│   │   ├── service-worker.ts (replaces background.js)
│   │   └── engagement-tracker.ts (NEW - tab monitoring)
│   ├── content/
│   │   └── context-detector.ts
│   ├── popup/
│   │   └── Popup.tsx
│   ├── sidebar/
│   │   └── Sidebar.tsx
│   └── utils/
│       ├── api.ts
│       ├── storage.ts
│       └── engagement-queue.ts (NEW - batch tracking)
└── public/
    ├── icons/
    └── styles/
```

**Manifest V3 Key Changes:**
- Service workers instead of persistent background pages
- `host_permissions` separated from `permissions`
- `declarativeNetRequest` API for request modification
- No remote code execution (all code bundled)

---

### 3.2 Backend API

**Framework:** FastAPI 0.115+ (Python 3.11+)  
**Why:** Leading modern Python framework in 2025; async-native, automatic OpenAPI docs, 3-5x faster than Flask/Django

**Stack:**
- **Server:** Uvicorn (ASGI server)
- **Database ORM:** SQLAlchemy 2.0 (async)
- **Migration Tool:** Alembic
- **Validation:** Pydantic v2 (built-in with FastAPI)
- **Authentication:** FastAPI Security + JWT
- **API Docs:** Auto-generated (Swagger UI / ReDoc)

**Key Features:**
- Type hints for automatic validation
- Async/await for high concurrency
- Dependency injection system
- WebSocket support for real-time features
- Request/response middleware

**Project Structure:**
```
/backend
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── bookmarks.py
│   │   │   ├── projects.py
│   │   │   ├── search.py
│   │   │   └── engagement.py (NEW - tracking endpoints)
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── bookmark.py
│   │   └── project.py
│   ├── schemas/
│   │   └── bookmark.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── embedding_service.py
│   │   ├── engagement_service.py (NEW)
│   │   └── vector_search.py
│   └── db/
│       └── database.py
├── migrations/
├── tests/
├── requirements.txt
└── .env
```

**Key API Endpoints:**
```python
# Engagement tracking
POST   /api/v1/engagement/track    # Batch track bookmark opens
GET    /api/v1/engagement/stats    # Get user engagement stats
GET    /api/v1/bookmarks/dead      # Get never-opened bookmarks
DELETE /api/v1/bookmarks/dead      # Bulk delete dead bookmarks
```

---

### 3.3 Vector Database

**Selected:** Qdrant 1.7+  
**Why:** Leading performance in 2025, excellent filtered search, open-source with cloud option, strong Python SDK

**Alternatives Considered:**
- **Pinecone:** Excellent but proprietary/expensive (~$70/month)
- **Milvus:** More complex setup, better for massive scale
- **Chroma:** Simpler but less performant at scale
- **Weaviate:** Good but larger resource footprint

**Qdrant Advantages:**
- High-performance filtered search (crucial for project filtering)
- Hybrid search (vector + keyword)
- Quantization support (reduce memory by 4x)
- Excellent SDK and docs
- Self-hostable or cloud ($0.50/GB/month)

**Schema:**
```python
# Collection: bookmarks
{
    "id": "uuid",
    "vector": [0.1, 0.2, ...],  # 1536 dimensions
    "payload": {
        "user_id": "uuid",
        "project_id": "uuid",
        "url": "string",
        "title": "string",
        "tags": ["tag1", "tag2"],
        "created_at": "timestamp",
        "content_type": "tutorial",
        "open_count": 0,  # For engagement-based filtering
        "last_opened_at": "timestamp"  # For recency filtering
    }
}
```

**Performance Targets:**
- Search latency: <50ms (p95)
- Storage: ~10KB per bookmark (1536-dim embedding)
- Concurrent queries: 100+ QPS

---

### 3.4 Metadata Database

**Selected:** PostgreSQL 16+  
**Why:** Industry standard, excellent JSONB support, pgvector extension available (backup option)

**Schema Design:**

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    google_doc_id VARCHAR(255), -- For ephemeral content
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    context_keywords TEXT[], -- PostgreSQL array
    last_active TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Bookmarks
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    cluster_id UUID,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    tags TEXT[],
    content_type VARCHAR(50),
    is_ephemeral BOOLEAN DEFAULT false,
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP,
    last_opened_at TIMESTAMP,
    first_opened_at TIMESTAMP,
    open_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, url)
);

CREATE INDEX idx_bookmarks_user_project ON bookmarks(user_id, project_id);
CREATE INDEX idx_bookmarks_created ON bookmarks(created_at);
CREATE INDEX idx_bookmarks_tags ON bookmarks USING GIN(tags);
CREATE INDEX idx_bookmarks_last_opened ON bookmarks(last_opened_at);
CREATE INDEX idx_bookmarks_engagement ON bookmarks(user_id, open_count DESC);

-- Clusters
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    representative_keywords TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bookmark-Cluster Junction (Many-to-Many)
CREATE TABLE bookmark_clusters (
    bookmark_id UUID REFERENCES bookmarks(id) ON DELETE CASCADE,
    cluster_id UUID REFERENCES clusters(id) ON DELETE CASCADE,
    similarity_score FLOAT,
    PRIMARY KEY (bookmark_id, cluster_id)
);
```

---

### 3.5 Job Queue & Task Scheduling

**Selected:** Celery 5.3+ with Redis 7.x  
**Why:** Industry standard for Python async tasks, reliable, scalable

**Task Categories:**
1. **Daily Tasks (3 AM user timezone):**
   - Process ephemeral bookmarks
   - Export to Google Docs
   - Clean up processed ephemeral bookmarks >30 days

2. **Weekly Tasks (Saturday 2 AM):**
   - Batch processing: Generate embeddings for new bookmarks
   - Re-cluster all bookmarks
   - Update project embeddings
   - Send weekly digest email

3. **Real-time Tasks (triggered):**
   - Generate embeddings for new bookmark (if not in batch)
   - Send Slack/email notifications (if enabled)

**Configuration:**
```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

app = Celery('bookmarkai')

app.conf.beat_schedule = {
    'process-ephemeral-daily': {
        'task': 'tasks.process_ephemeral',
        'schedule': crontab(hour=3, minute=0),  # 3 AM
    },
    'batch-processing-weekly': {
        'task': 'tasks.batch_process_bookmarks',
        'schedule': crontab(day_of_week=6, hour=2),  # Saturday 2 AM
    },
}
```

---

### 3.6 AI Services

#### 3.6.1 Embeddings: OpenAI text-embedding-3-small

**Model:** `text-embedding-3-small`  
**Why:** 5x cheaper than ada-002, better performance, 1536 dimensions

**Specs:**
- Dimensions: 1536 (can truncate to 512 or 768 if needed)
- Pricing: $0.02 per 1M tokens (~$0.00002 per 1K tokens)
- Performance: 62.3% on MTEB benchmark (vs 61% for ada-002)
- Max tokens: 8,191

**Usage Estimate:**
```
772 bookmarks × 500 tokens avg = 386K tokens
Cost: $0.00772 (initial load)

Monthly (10 new bookmarks/day):
300 bookmarks × 500 tokens = 150K tokens
Cost: $0.003/month
```

**Alternative:** `text-embedding-3-large` (3072 dim, better accuracy, $0.13/1M tokens)

---

#### 3.6.2 Content Analysis: Claude Sonnet 4.5

**Model:** `claude-sonnet-4-20250514`  
**Why:** Best coding/analysis model, excellent instruction following, 50% batch discount

**Pricing (Standard):**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Pricing (Batch API - 50% discount):**
- Input: $1.50 per 1M tokens
- Output: $7.50 per 1M tokens
- Turnaround: 24 hours max

**Usage Scenarios:**

**Real-Time (New Bookmark):**
```
Input: 500 tokens (bookmark content + prompt)
Output: 150 tokens (summary + tags)
Cost per bookmark: $0.00375
```

**Batch Processing (Weekly - 70 bookmarks):**
```
Input: 35K tokens (70 × 500)
Output: 10.5K tokens (70 × 150)
Cost: $0.131 (vs $0.262 real-time, 50% savings)
```

**Monthly Cost Estimate:**
- Real-time: 10 bookmarks/day × 30 days × $0.00375 = $1.13
- Batch: 4 weeks × $0.131 = $0.52
- **Total: ~$1.65/month** (excluding embeddings)

**Features Used:**
- Structured JSON output for tags/summaries
- Tool use for web scraping (if needed)
- Prompt caching for system prompts (90% savings on repeated context)

---

### 3.7 External Integrations

#### Google Docs API
- **OAuth 2.0** for user authentication
- **Docs API v1** for appending content
- Scope: `https://www.googleapis.com/auth/documents`

#### Browser APIs (Chrome Extension)
- `chrome.tabs`: Tab monitoring
- `chrome.bookmarks`: Bookmark CRUD
- `chrome.storage`: Local data persistence
- `chrome.sidePanel`: Sidebar UI (Manifest V3)

---

## 4. User Interface Design

### 4.1 Extension Popup

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

### 4.2 Sidebar Panel

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

### 4.3 Web Dashboard (Optional)

**URL:** `app.bookmarkai.com`  
**Tech:** React + Tailwind CSS

**Pages:**
1. **Dashboard:** Overview stats, recent activity
2. **Bookmarks:** Grid/list view, advanced filters
3. **Projects:** Manage projects, bulk operations
4. **Analytics:** Usage patterns, tag cloud
5. **Settings:** API keys, Google Docs integration

---

## 5. Development Roadmap

### Phase 1: MVP (Weeks 1-4)

**Week 1: Foundation**
- Set up development environment
- Initialize FastAPI backend
- Set up PostgreSQL + Qdrant databases
- Create basic data models
- User authentication (JWT)

**Week 2: Core Backend**
- Bookmark CRUD API endpoints
- OpenAI embeddings integration
- Qdrant vector operations
- Basic search functionality
- Project management APIs

**Week 3: Browser Extension**
- Chrome Extension scaffold (Manifest V3)
- Bookmark capture from browser
- Basic popup UI
- API client integration
- Context detection (URL + title)

**Week 4: Context-Aware Surfacing**
- Embedding generation on save
- On-demand context analysis triggered by bookmark saves
- Vector similarity search
- Sidebar UI with suggestions
- Testing and refinement

**MVP Deliverables:**
- ✅ Save bookmarks with auto-tagging
- ✅ Context-aware suggestions in sidebar
- ✅ Basic project management
- ✅ Manual tag editing

---

### Phase 2: Intelligence Layer (Weeks 5-8)

**Week 5: Claude Integration**
- Claude API client
- Summary generation
- Tag refinement
- Content type classification
- Real-time processing for new bookmarks

**Week 6: Batch Processing**
- Celery task queue setup
- Redis configuration
- Weekly batch job for clustering
- Daily ephemeral content processing
- Error handling and retry logic

**Week 7: Project Mode**
- Project embedding calculation
- Smart project suggestion on save
- Project filtering in sidebar
- Quick-switch keyboard shortcuts
- Active project indicator

**Week 8: Engagement Tracking & Optimization**
- Implement bookmark engagement tracking (last_opened_at, open_count)
- Tab listener for passive URL matching
- "Dead Bookmarks" filter UI
- Enhanced relevance scoring with engagement boost
- Load testing (1000+ bookmarks)
- Embedding cache optimization
- UI/UX refinements
- Bug fixes
- Documentation

**Phase 2 Deliverables:**
- ✅ Intelligent auto-tagging and summarization
- ✅ Batch processing pipeline
- ✅ Full project mode functionality
- ✅ Bookmark engagement tracking
- ✅ Optimized performance

---

### Phase 3: Advanced Features (Weeks 9-12)

**Week 9: AI Chat Interface**
- Natural language query parsing
- Hybrid search implementation
- Chat UI in extension
- Query history
- Result ranking

**Week 10: Ephemeral Content Workflow**
- Google Docs OAuth integration
- Content extraction (Playwright)
- Batch processing for tweets/Reddit
- Auto-deletion of old ephemeral bookmarks

**Week 11: Cross-Project Search**
- Multi-project filtering
- Advanced query syntax
- Saved searches
- Search analytics

**Week 12: Polish & Launch**
- Web dashboard (optional)
- Onboarding flow
- User documentation
- Chrome Web Store submission
- Beta user testing

**Phase 3 Deliverables:**
- ✅ Full AI chat interface
- ✅ Ephemeral content → Google Docs
- ✅ Advanced search capabilities
- ✅ Production-ready system

---

## 6. Cost Analysis

### 6.1 Per-User Monthly Costs (Steady State)

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

### 6.2 Infrastructure Costs

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

---

## 7. Security & Privacy

### 7.1 Data Security

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

---

### 7.2 Privacy

**User Commitments:**
- Bookmark content never shared with third parties
- AI processing happens via direct API calls (no intermediate storage)
- User can export all data (GDPR compliance)
- User can delete account + all data permanently
- No analytics/tracking beyond error logging

**Data Retention:**
- Active bookmarks: Indefinite
- Ephemeral bookmarks (processed): 30 days
- Deleted bookmarks: Soft delete (30 days), then hard delete
- Logs: 7 days

---

## 8. Success Metrics

### 8.1 Product Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to find bookmark | <5 seconds | User testing |
| Save-time suggestion relevance | 70%+ | Click-through rate during save flow |
| Project suggestion acceptance | 80%+ | Acceptance rate |
| Daily active users | 60% of installed | Extension telemetry |
| Average bookmarks per user | 200+ | Database query |
| User retention (30-day) | 70%+ | Cohort analysis |

### 8.2 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API latency (p95) | <200ms | APM (e.g., Sentry) |
| Vector search latency (p95) | <100ms | Qdrant metrics |
| Uptime | 99.5%+ | Status page |
| Error rate | <0.1% | Error tracking |
| Batch job completion | 95%+ within 24h | Celery monitoring |

---

## 9. Future Enhancements (Post-V1)

### 9.1 Advanced AI Features
- **Bookmark Summarization:** Auto-generate weekly digests with engagement stats
- **Duplicate Detection:** Flag similar bookmarks across projects (>90% similarity)
- **Smart Recommendations:** "Users who bookmarked X also bookmarked Y" (collaborative filtering)
- **Learning Mode:** Flashcard generation from saved articles
- **Content Change Detection:** Alert when bookmarked pages are updated or deleted (404s)
- **Reading Time Estimates:** ML-based prediction of time to read each bookmark

### 9.2 Collaboration Features
- **Shared Projects:** Team workspaces
- **Bookmark Sharing:** Share individual bookmarks with metadata
- **Social Layer:** See what your team bookmarks (opt-in)

### 9.3 Platform Expansion
- **Firefox Extension:** Port from Chrome
- **Mobile Apps:** iOS/Android with sync
- **CLI Tool:** Command-line bookmark management
- **API Access:** Public API for third-party integrations

### 9.4 Enterprise Features
- **SSO Integration:** SAML/OAuth for enterprise
- **Admin Dashboard:** Team analytics
- **Custom Models:** Fine-tuned embeddings for company data
- **On-Premise:** Self-hosted option

---

## 10. Open Questions & Decisions Needed

### 10.1 Technical Decisions
- [ ] **Vector DB Choice:** Qdrant vs. Pinecone vs. pgvector? → **Qdrant** (cost + performance)
- [ ] **Hosting:** Self-hosted vs. Cloud Run vs. AWS Lambda?
- [ ] **Chrome Web Store:** Free vs. $5 one-time fee?

### 10.2 Product Decisions
- [ ] **Freemium Model?** Free tier (100 bookmarks) + Pro ($5/month)?
- [ ] **Ephemeral Content:** Google Docs only, or support Notion/Obsidian?
- [ ] **AI Model Choice:** Claude Sonnet 4.5 vs. Haiku 4.5 for batch jobs?

### 10.3 Go-to-Market
- [ ] **Target Audience:** Developers only, or broader knowledge workers?
- [ ] **Launch Strategy:** Product Hunt, Hacker News, or direct to Chrome Web Store?
- [ ] **Pricing:** Free beta → Paid launch, or free forever with optional Pro?

---

## 11. Glossary

- **Context:** The browsing environment including URL, page content, time, and active project
- **Embedding:** A numerical vector (array of floats) representing semantic meaning of text
- **Ephemeral Bookmark:** Temporary bookmark (tweets, Reddit) meant for content extraction, not long-term storage
- **Project:** A collection of related bookmarks representing a work context or area of interest
- **Vector Search:** Finding similar items by comparing embeddings (cosine similarity)
- **Batch Processing:** Asynchronous AI processing with 24-hour turnaround for cost savings

---

## 12. References & Resources

### Documentation
- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Claude API Documentation](https://docs.anthropic.com/)

### Tech Stack Rationale
- [FastAPI vs Flask vs Django (2025)](https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/)
- [Top Vector Databases 2025](https://www.datacamp.com/blog/the-top-5-vector-databases)
- [Claude Batch API Pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)
- [OpenAI Embedding Model Comparison](https://openai.com/index/new-embedding-models-and-api-updates/)

---

**End of Document**  
**Version:** 1.0  
**Last Updated:** October 27, 2025  
**Status:** Draft for Review