# System Architecture

**Navigation**: [Overview](overview.md) | [Features](features.md) | [Roadmap](roadmap.md) | [Reference](reference.md)

---

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Data Flows](#data-flows)
- [Technology Stack](#technology-stack)
- [Database Schemas](#database-schemas)
- [API Endpoints](#api-endpoints)

---

## High-Level Architecture

```
┌─────────────────────────────────────┐
│   Browser Extension (Chrome/Brave)  │
│   - Context Detection               │
│   - UI/Sidebar                      │
│   - Bookmark Capture                │
│   - Engagement Tracking             │
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

---

## Data Flows

### Real-Time Flow (New Bookmark)

1. User saves bookmark in browser
2. Extension captures metadata (URL, title, DOM context)
3. Backend generates embedding via OpenAI API
4. AI generates summary + tags using Claude (real-time)
5. System suggests matching project
6. Data stored in PostgreSQL + Vector DB
7. User confirms/adjusts project assignment

### Batch Processing Flow (Daily/Weekly)

1. Celery scheduled job collects unprocessed bookmarks
2. Batch request submitted to Claude API (50% discount)
3. Results returned within 24 hours
4. Embeddings updated, clusters recalculated
5. Ephemeral content processed → Google Docs
6. Project contexts updated

### Context-Aware Surfacing Flow

1. User saves a bookmark or selects "Show related" for the current page
2. Extension captures a one-time context snapshot (URL, title, keywords, timestamp)
3. Backend generates an embedding from the snapshot
4. Vector search returns similar bookmarks, filtered by the user's active project when set
5. Sidebar surfaces the top 5-10 relevant bookmarks with relevance scores
6. User reviews suggestions alongside the save flow

### Engagement Tracking Flow

1. User opens a bookmarked page in browser
2. Extension detects URL matches existing bookmark via `chrome.tabs.onUpdated`
3. Event queued locally (batched every 5 minutes)
4. Backend updates `last_opened_at` and increments `open_count`
5. Weekly digest analyzes engagement patterns
6. System suggests archiving bookmarks with 0 opens after 6+ months

---

## Technology Stack

### Browser Extension

**Framework**: Chrome Extension Manifest V3

**Stack**:
- **Language**: TypeScript 5.x
- **UI Framework**: React 18.x with Hooks
- **Styling**: Tailwind CSS 3.x
- **State Management**: Zustand (lightweight, <1KB)
- **Build Tool**: Vite 5.x (faster than Webpack)
- **API Client**: Axios with interceptors

**Key Files**:
```
/extension
├── manifest.json (V3)
├── src/
│   ├── background/
│   │   ├── service-worker.ts (replaces background.js)
│   │   └── engagement-tracker.ts (tab monitoring)
│   ├── content/
│   │   └── context-detector.ts
│   ├── popup/
│   │   └── Popup.tsx
│   ├── sidebar/
│   │   └── Sidebar.tsx
│   └── utils/
│       ├── api.ts
│       ├── storage.ts
│       └── engagement-queue.ts (batch tracking)
└── public/
    ├── icons/
    └── styles/
```

**Manifest V3 Key Changes**:
- Service workers instead of persistent background pages
- `host_permissions` separated from `permissions`
- `declarativeNetRequest` API for request modification
- No remote code execution (all code bundled)

---

### Backend API

**Framework**: FastAPI 0.115+ (Python 3.11+)

**Stack**:
- **Server**: Uvicorn (ASGI server)
- **Database ORM**: SQLAlchemy 2.0 (async)
- **Migration Tool**: Alembic
- **Validation**: Pydantic v2 (built-in with FastAPI)
- **Authentication**: FastAPI Security + JWT
- **API Docs**: Auto-generated (Swagger UI / ReDoc)

**Project Structure**:
```
/backend
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── bookmarks.py
│   │   │   ├── projects.py
│   │   │   ├── search.py
│   │   │   └── engagement.py (tracking endpoints)
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
│   │   ├── engagement_service.py
│   │   └── vector_search.py
│   └── db/
│       └── database.py
├── migrations/
├── tests/
├── requirements.txt
└── .env
```

---

### Vector Database

**Selected**: Qdrant 1.7+

**Why**: Leading performance in 2025, excellent filtered search, open-source with cloud option, strong Python SDK

**Alternatives Considered**:
- **Pinecone**: Excellent but proprietary/expensive (~$70/month)
- **Milvus**: More complex setup, better for massive scale
- **Chroma**: Simpler but less performant at scale
- **Weaviate**: Good but larger resource footprint

**Qdrant Advantages**:
- High-performance filtered search (crucial for project filtering)
- Hybrid search (vector + keyword)
- Quantization support (reduce memory by 4x)
- Excellent SDK and docs
- Self-hostable or cloud ($0.50/GB/month)

**Schema**:
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
        "open_count": 0,
        "last_opened_at": "timestamp"
    }
}
```

**Performance Targets**:
- Search latency: <50ms (p95)
- Storage: ~10KB per bookmark (1536-dim embedding)
- Concurrent queries: 100+ QPS

---

### Metadata Database

**Selected**: PostgreSQL 16+

**Why**: Industry standard, excellent JSONB support, pgvector extension available (backup option)

**Schema Design**:

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
    context_keywords TEXT[],
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

### Job Queue & Task Scheduling

**Selected**: Celery 5.3+ with Redis 7.x

**Task Categories**:

1. **Daily Tasks (3 AM user timezone)**:
   - Process ephemeral bookmarks
   - Export to Google Docs
   - Clean up processed ephemeral bookmarks >30 days

2. **Weekly Tasks (Saturday 2 AM)**:
   - Batch processing: Generate embeddings for new bookmarks
   - Re-cluster all bookmarks
   - Update project embeddings
   - Send weekly digest email

3. **Real-time Tasks (triggered)**:
   - Generate embeddings for new bookmark (if not in batch)
   - Send Slack/email notifications (if enabled)

**Configuration**:
```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

app = Celery('bookmarkai')

app.conf.beat_schedule = {
    'process-ephemeral-daily': {
        'task': 'tasks.process_ephemeral',
        'schedule': crontab(hour=3, minute=0),
    },
    'batch-processing-weekly': {
        'task': 'tasks.batch_process_bookmarks',
        'schedule': crontab(day_of_week=6, hour=2),
    },
}
```

---

### AI Services

#### Embeddings: OpenAI text-embedding-3-small

**Model**: `text-embedding-3-small`

**Specs**:
- Dimensions: 1536 (can truncate to 512 or 768 if needed)
- Pricing: $0.02 per 1M tokens (~$0.00002 per 1K tokens)
- Performance: 62.3% on MTEB benchmark
- Max tokens: 8,191

**Usage Estimate**:
```
5-10 bookmarks/week (~40/month):
40 bookmarks × 500 tokens = 20K tokens
Cost: $0.0004/month
```

#### Content Analysis: Claude Sonnet 4.5

**Model**: `claude-sonnet-4-20250514`

**Pricing (Standard)**:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Pricing (Batch API - 50% discount)**:
- Input: $1.50 per 1M tokens
- Output: $7.50 per 1M tokens
- Turnaround: 24 hours max

**Real-Time (New Bookmark)**:
```
Input: 500 tokens (bookmark content + prompt)
Output: 150 tokens (summary + tags)
Cost per bookmark: $0.00375
```

**Batch Processing (Weekly - 40 bookmarks)**:
```
Input: 20K tokens (40 × 500)
Output: 6K tokens (40 × 150)
Cost: $0.08 (vs $0.15 real-time, 47% savings)
```

---

### External Integrations

#### Google Docs API
- **OAuth 2.0** for user authentication
- **Docs API v1** for appending content
- Scope: `https://www.googleapis.com/auth/documents`

#### Browser APIs (Chrome Extension)
- `chrome.tabs`: Tab monitoring for engagement tracking
- `chrome.bookmarks`: Bookmark CRUD
- `chrome.storage`: Local data persistence
- `chrome.sidePanel`: Sidebar UI (Manifest V3)

---

## API Endpoints

### Bookmarks
```
GET    /api/v1/bookmarks           # List all bookmarks
POST   /api/v1/bookmarks           # Create new bookmark
GET    /api/v1/bookmarks/:id       # Get bookmark details
PUT    /api/v1/bookmarks/:id       # Update bookmark
DELETE /api/v1/bookmarks/:id       # Delete bookmark
GET    /api/v1/bookmarks/dead      # Get never-opened bookmarks
DELETE /api/v1/bookmarks/dead      # Bulk delete dead bookmarks
```

### Projects
```
GET    /api/v1/projects            # List all projects
POST   /api/v1/projects            # Create new project
GET    /api/v1/projects/:id        # Get project details
PUT    /api/v1/projects/:id        # Update project
DELETE /api/v1/projects/:id        # Delete project
POST   /api/v1/projects/:id/suggest # Suggest project for bookmark
```

### Search
```
POST   /api/v1/search              # Semantic search
POST   /api/v1/search/similar      # Find similar bookmarks
POST   /api/v1/search/chat         # Natural language query
```

### Engagement
```
POST   /api/v1/engagement/track    # Batch track bookmark opens
GET    /api/v1/engagement/stats    # Get user engagement stats
GET    /api/v1/engagement/digest   # Get weekly engagement digest
```

### Authentication
```
POST   /api/v1/auth/register       # Register new user
POST   /api/v1/auth/login          # Login user
POST   /api/v1/auth/refresh        # Refresh JWT token
POST   /api/v1/auth/logout         # Logout user
```

---

**Next**: Explore [Feature Specifications](features.md) for detailed user flows and technical requirements.
