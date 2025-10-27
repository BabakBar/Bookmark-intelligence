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
│      (FastAPI + Python 3.13+)       │
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
4. AI generates summary + tags using Claude API (real-time)
5. System suggests matching project
6. Data stored in PostgreSQL + Vector DB
7. User confirms/adjusts project assignment

### Batch Processing Flow (Daily/Weekly)

1. Celery scheduled job collects unprocessed bookmarks
2. Batch request submitted to Claude API or scheduled processing
3. Results processed asynchronously
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

**Framework**: FastAPI 0.115+ (Python 3.13+)

**Stack**:
- **Server**: Uvicorn 0.32+ (ASGI server)
- **Database ORM**: SQLAlchemy 2.0.36+ (async)
- **Migration Tool**: Alembic 1.14+
- **Validation**: Pydantic v2.10+ (built-in with FastAPI)
- **Authentication**: FastAPI Security + JWT
- **API Docs**: Auto-generated (Swagger UI / ReDoc)

**Deployment**: Coolify (self-hosted on Hetzner VPS)

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

**Selected**: Qdrant 1.12+ (Self-Hosted)

**Deployment**: Docker container on Hetzner VPS via Coolify

**Why**: Leading performance in 2025, excellent filtered search, fully open-source, strong Python SDK

**Alternatives Considered**:
- **Pinecone**: Excellent but proprietary/expensive (~$70/month)
- **Milvus**: More complex setup, better for massive scale
- **Chroma**: Simpler but less performant at scale
- **Weaviate**: Good but larger resource footprint
- **pgvector**: PostgreSQL extension, good backup option

**Qdrant Advantages**:
- High-performance filtered search (crucial for project filtering)
- Hybrid search (vector + keyword)
- Quantization support (reduce memory by 4x)
- Excellent SDK and docs
- Self-hostable with low resource footprint (2GB RAM)

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

**Selected**: PostgreSQL 17.x (Self-Hosted)

**Deployment**: Docker container on Hetzner VPS via Coolify

**Why**: Industry standard, excellent JSONB support, pgvector extension available (backup option), significant performance improvements in v17

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

**Selected**: Celery 5.4+ with Redis 7.4.x (Self-Hosted)

**Deployment**: Redis and Celery workers as Docker containers on Hetzner VPS via Coolify

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

#### Content Analysis: Claude 3.5 Sonnet (Anthropic)

**Model**: `claude-3-5-sonnet-20241022`

**Pricing (Standard)**:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

**Alternative**: Claude 3.5 Haiku (5x cheaper, faster, slightly lower quality)
- Input: $0.80 per 1M tokens
- Output: $4.00 per 1M tokens

**Real-Time (New Bookmark)**:
```
Input: 500 tokens (bookmark content + prompt)
Output: 150 tokens (summary + tags)
Cost per bookmark (Sonnet): $0.00375
Cost per bookmark (Haiku): $0.001
```

**Batch Processing (Weekly - 40 bookmarks)**:
```
Using Claude 3.5 Sonnet:
Input: 20K tokens (40 × 500)
Output: 6K tokens (40 × 150)
Cost: $0.15/week

Using Claude 3.5 Haiku:
Cost: $0.04/week (73% savings)
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

## Self-Hosted Deployment Architecture (Coolify)

### Infrastructure

**Hosting**: Hetzner VPS CX32
- **RAM**: 8GB
- **Storage**: 80GB SSD
- **CPU**: 4 vCPU AMD
- **Cost**: ~$13/month (€12.90)

**Deployment Platform**: Coolify (open-source, self-hosted Heroku alternative)
- Docker-based container orchestration
- Built-in SSL/TLS (Let's Encrypt)
- Zero-downtime deployments
- Integrated monitoring and logs

### Resource Allocation

```
Service                    RAM     Storage   Port(s)
─────────────────────────────────────────────────────
PostgreSQL 17              1.5GB   10GB      5432 (internal)
Redis 7.4                  512MB   500MB     6379 (internal)
Qdrant 1.12                2GB     5GB       6333 (internal)
FastAPI Backend            1GB     2GB       8000 → 443 (public)
Celery Worker              1GB     1GB       - (internal)
Celery Beat                256MB   500MB     - (internal)
Nginx (Coolify proxy)      256MB   1GB       80, 443 (public)
Coolify + Docker           1GB     5GB       8000 (admin)
OS (Ubuntu 24.04)          512MB   10GB      -
─────────────────────────────────────────────────────
TOTAL                      8GB     35GB
REMAINING BUFFER           0GB     45GB
```

### Coolify Services Configuration

#### 1. PostgreSQL
```yaml
image: postgres:17-alpine
environment:
  POSTGRES_DB: bookmarkai
  POSTGRES_USER: bookmarkuser
  POSTGRES_PASSWORD: ${DB_PASSWORD}
volumes:
  - postgresql_data:/var/lib/postgresql/data
networks:
  - internal
```

#### 2. Redis
```yaml
image: redis:7.4-alpine
command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
volumes:
  - redis_data:/data
networks:
  - internal
```

#### 3. Qdrant
```yaml
image: qdrant/qdrant:v1.12
environment:
  QDRANT__SERVICE__ENABLE_CORS: "false"
volumes:
  - qdrant_storage:/qdrant/storage
networks:
  - internal
```

#### 4. FastAPI Backend
```yaml
build: ./backend
environment:
  DATABASE_URL: postgresql+asyncpg://user:pass@postgresql:5432/bookmarkai
  REDIS_URL: redis://redis:6379/0
  QDRANT_URL: http://qdrant:6333
  OPENAI_API_KEY: ${OPENAI_API_KEY}
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
domains:
  - api.bookmarkai.yourdomain.com
networks:
  - public
  - internal
healthcheck:
  path: /health
  interval: 30s
```

#### 5. Celery Worker & Beat
```yaml
worker:
  build: ./backend
  command: celery -A app.tasks worker --loglevel=info --concurrency=2
  environment: [same as backend]
  networks:
    - internal

beat:
  build: ./backend
  command: celery -A app.tasks beat --loglevel=info
  environment: [same as backend]
  networks:
    - internal
  replicas: 1  # Singleton
```

### Network Architecture

```
Internet
   │
   ├─→ :443 (HTTPS) ─→ Nginx (Coolify Proxy) ─→ FastAPI Backend
   │                                              ↓
   └─→ :8000 (Admin) ─→ Coolify Dashboard        Internal Network
                                                  ├─→ PostgreSQL :5432
                                                  ├─→ Redis :6379
                                                  ├─→ Qdrant :6333
                                                  ├─→ Celery Worker
                                                  └─→ Celery Beat
```

**Security**:
- Only ports 80, 443, and 8000 (restricted) exposed to internet
- All databases on internal Docker network only
- SSL/TLS certificates auto-renewed via Let's Encrypt
- Environment secrets stored in Coolify vault

### Performance Optimizations

**PostgreSQL** (1.5GB RAM):
```sql
shared_buffers = 512MB
effective_cache_size = 1GB
work_mem = 8MB
max_connections = 100
```

**Qdrant** (2GB RAM with quantization):
```yaml
storage:
  on_disk_payload: true    # Store metadata on disk
quantization:
  scalar:
    type: int8             # 4x memory reduction
    always_ram: false
```

**Redis** (512MB):
```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
io-threads 2
```

### Backup Strategy

**Automated Daily Backups** (via Coolify or custom script):
```bash
# PostgreSQL
pg_dump bookmarkai | gzip > /backups/db-$(date +%Y%m%d).sql.gz

# Qdrant snapshots
curl -X POST http://localhost:6333/collections/bookmarks/snapshots

# Upload to Hetzner Storage Box or S3-compatible
rclone sync /backups remote:bookmarkai-backups/

# Retention: 7 daily, 4 weekly, 6 monthly
```

### Cost Comparison: Self-Hosted vs Cloud

| Component | Cloud (Monthly) | Self-Hosted | Savings |
|-----------|----------------|-------------|---------|
| Compute (Cloud Run) | $100 | $0 | $100 |
| Qdrant Cloud | $50 | $0 | $50 |
| PostgreSQL (Supabase) | $25 | $0 | $25 |
| Redis (Upstash) | $10 | $0 | $10 |
| **Infrastructure Total** | **$185** | **$13** (VPS) | **$172/mo** |
| **Annual Savings** | | | **$2,064/year** |

*AI costs (OpenAI/Anthropic) remain the same in both scenarios*

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
