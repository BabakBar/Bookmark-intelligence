# Data Model: Phase 0 Bootstrap Import

**Feature**: Phase 0 Bootstrap Import
**Date**: October 27, 2025
**Database**: PostgreSQL 17
**ORM**: SQLAlchemy 2.0 (Async)

## Overview

This document defines the database schema for Phase 0, which handles importing and organizing existing bookmarks. The schema supports users, bookmarks, projects, clusters, and import job tracking.

---

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
└──────┬───────┘
       │
       │ 1:N
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│  bookmarks   │      │  projects    │
└──────┬───────┘      └──────┬───────┘
       │                     │
       │ N:M                 │ 1:N
       ├────────┐            │
       │        │            │
       ▼        ▼            ▼
┌──────────────┐      ┌──────────────┐
│   clusters   │      │   bookmarks  │
└──────────────┘      └──────────────┘
       │
       │ N:M
       ▼
┌────────────────────┐
│ bookmark_clusters  │ (junction table)
└────────────────────┘

       ┌──────────────┐
       │ import_jobs  │ (tracks import progress)
       └──────────────┘
```

---

## Schema Definitions

### 1. Users Table

Stores user authentication and profile information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
```

**Fields**:
- `id`: UUID primary key
- `email`: Unique email address for authentication
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's display name (optional)
- `is_active`: Account status (for soft delete)
- `is_superuser`: Admin flag (for future multi-user support)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Password must be >= 8 characters before hashing
- Email must be unique (enforced by database)

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="user", cascade="all, delete-orphan")
    import_jobs = relationship("ImportJob", back_populates="user", cascade="all, delete-orphan")
```

---

### 2. Bookmarks Table

Stores imported bookmarks with AI-generated metadata.

```sql
CREATE TABLE bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    -- Original bookmark data
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    original_folder TEXT,  -- Browser folder path (e.g., "Work/DevOps")
    add_date TIMESTAMP WITH TIME ZONE,  -- Original browser bookmark date

    -- AI-generated metadata
    tags TEXT[] DEFAULT '{}',
    summary TEXT,
    content_type VARCHAR(50),  -- tutorial, documentation, article, video, tool
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP WITH TIME ZONE,

    -- Import tracking
    import_job_id UUID REFERENCES import_jobs(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_url UNIQUE(user_id, url),
    CONSTRAINT valid_content_type CHECK (content_type IN ('tutorial', 'documentation', 'article', 'video', 'tool'))
);

-- Indexes for common queries
CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_project ON bookmarks(project_id) WHERE project_id IS NOT NULL;
CREATE INDEX idx_bookmarks_tags ON bookmarks USING GIN(tags);  -- Full-text search on tags
CREATE INDEX idx_bookmarks_created ON bookmarks(created_at DESC);
CREATE INDEX idx_bookmarks_processed ON bookmarks(processed) WHERE processed = false;
CREATE INDEX idx_bookmarks_import_job ON bookmarks(import_job_id) WHERE import_job_id IS NOT NULL;
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `project_id`: Optional foreign key to projects table (NULL if not assigned)
- `url`: Bookmark URL (unique per user)
- `title`: Bookmark title (from browser or page title)
- `original_folder`: Browser folder path preserved from import
- `add_date`: Original bookmark creation date from browser export
- `tags`: Array of AI-generated semantic tags (e.g., ["docker", "devops"])
- `summary`: 2-3 sentence AI-generated summary
- `content_type`: Classification (tutorial/documentation/article/video/tool)
- `processed`: Whether AI processing completed
- `processed_at`: When AI processing completed
- `import_job_id`: Which import job created this bookmark
- `created_at`: When bookmark was imported
- `updated_at`: Last modification timestamp

**Validation Rules**:
- URL must be valid HTTP/HTTPS format
- URL must be unique per user (enforced by constraint)
- Tags array: 3-7 items, lowercase, hyphenated
- Summary: 100-500 characters
- Content type: Must be one of the 5 valid types

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    # Original data
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    original_folder = Column(Text, nullable=True)
    add_date = Column(DateTime(timezone=True), nullable=True)

    # AI metadata
    tags = Column(ARRAY(String), default=list)
    summary = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=True)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Import tracking
    import_job_id = Column(UUID(as_uuid=True), ForeignKey("import_jobs.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookmarks")
    project = relationship("Project", back_populates="bookmarks")
    import_job = relationship("ImportJob", back_populates="bookmarks")
    clusters = relationship("Cluster", secondary="bookmark_clusters", back_populates="bookmarks")

    # Constraints
    __table_args__ = (
        CheckConstraint("content_type IN ('tutorial', 'documentation', 'article', 'video', 'tool')", name="valid_content_type"),
        UniqueConstraint("user_id", "url", name="unique_user_url"),
    )
```

**Note**: Embedding vectors are NOT stored in PostgreSQL. They are stored in Qdrant vector database for efficient similarity search. The bookmark `id` serves as the foreign key to link PostgreSQL records with Qdrant vectors.

---

### 3. Projects Table

Stores user-defined projects (workspaces) for organizing bookmarks.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Project metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    context_keywords TEXT[] DEFAULT '{}',

    -- Project suggestion metadata
    is_suggested BOOLEAN DEFAULT false,  -- Was this AI-suggested?
    suggestion_confidence FLOAT,  -- 0.0-1.0 confidence if suggested
    suggestion_accepted BOOLEAN,  -- Did user accept the suggestion?

    -- Activity tracking
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_user_project_name UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_active ON projects(is_active) WHERE is_active = true;
CREATE INDEX idx_projects_suggested ON projects(is_suggested, suggestion_accepted) WHERE is_suggested = true;
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `name`: Project name (unique per user)
- `description`: Optional project description
- `is_active`: Whether project is currently active/in use
- `context_keywords`: Array of keywords representing project theme
- `is_suggested`: Whether this was an AI-generated project suggestion
- `suggestion_confidence`: AI confidence score (0.0-1.0) if suggested
- `suggestion_accepted`: Whether user accepted the suggestion
- `last_active`: Last time project was accessed/modified
- `created_at`: Project creation timestamp
- `updated_at`: Last modification timestamp

**Validation Rules**:
- Name: 1-255 characters, unique per user
- Description: Optional, max 1000 characters
- Context keywords: 3-10 items
- Suggestion confidence: 0.0-1.0 if is_suggested=true

**SQLAlchemy Model**:
```python
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    context_keywords = Column(ARRAY(String), default=list)

    is_suggested = Column(Boolean, default=False)
    suggestion_confidence = Column(Float, nullable=True)
    suggestion_accepted = Column(Boolean, nullable=True)

    last_active = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="projects")
    bookmarks = relationship("Bookmark", back_populates="project")

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_project_name"),
    )
```

**Note**: Project embeddings are calculated dynamically as the average of all member bookmark embeddings. They are NOT stored in the database but computed on-demand and cached in memory/Redis for performance.

---

### 4. Clusters Table

Stores AI-generated semantic clusters of related bookmarks.

```sql
CREATE TABLE clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Cluster metadata
    name VARCHAR(255) NOT NULL,
    representative_keywords TEXT[] DEFAULT '{}',
    bookmark_count INTEGER DEFAULT 0,

    -- Cluster quality metrics
    silhouette_score FLOAT,  -- Clustering quality (0.0-1.0)
    avg_similarity FLOAT,  -- Average similarity within cluster

    -- User actions
    is_accepted BOOLEAN DEFAULT false,  -- User reviewed and accepted
    is_renamed BOOLEAN DEFAULT false,  -- User changed the name
    original_name VARCHAR(255),  -- AI-generated name (if renamed)

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_clusters_user ON clusters(user_id);
CREATE INDEX idx_clusters_accepted ON clusters(is_accepted);
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `name`: Cluster name (AI-generated or user-edited)
- `representative_keywords`: Top 3-5 keywords representing cluster theme
- `bookmark_count`: Number of bookmarks in cluster (denormalized for performance)
- `silhouette_score`: Clustering quality metric (0.0-1.0, >0.3 is good)
- `avg_similarity`: Average cosine similarity within cluster
- `is_accepted`: Whether user reviewed and accepted this cluster
- `is_renamed`: Whether user changed the AI-generated name
- `original_name`: Original AI-generated name (preserved if renamed)
- `created_at`: Cluster creation timestamp
- `updated_at`: Last modification timestamp

**Validation Rules**:
- Name: 1-255 characters
- Representative keywords: 3-5 items
- Silhouette score: 0.0-1.0
- Bookmark count: Must match actual bookmark count in junction table

**SQLAlchemy Model**:
```python
class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    representative_keywords = Column(ARRAY(String), default=list)
    bookmark_count = Column(Integer, default=0)

    silhouette_score = Column(Float, nullable=True)
    avg_similarity = Column(Float, nullable=True)

    is_accepted = Column(Boolean, default=False)
    is_renamed = Column(Boolean, default=False)
    original_name = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="clusters")
    bookmarks = relationship("Bookmark", secondary="bookmark_clusters", back_populates="clusters")
```

---

### 5. Bookmark_Clusters Junction Table

Many-to-many relationship between bookmarks and clusters.

```sql
CREATE TABLE bookmark_clusters (
    bookmark_id UUID NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
    cluster_id UUID NOT NULL REFERENCES clusters(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,  -- How similar is this bookmark to cluster centroid

    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    PRIMARY KEY (bookmark_id, cluster_id)
);

-- Indexes
CREATE INDEX idx_bookmark_clusters_bookmark ON bookmark_clusters(bookmark_id);
CREATE INDEX idx_bookmark_clusters_cluster ON bookmark_clusters(cluster_id);
CREATE INDEX idx_bookmark_clusters_similarity ON bookmark_clusters(similarity_score DESC);
```

**Fields**:
- `bookmark_id`: Foreign key to bookmarks table
- `cluster_id`: Foreign key to clusters table
- `similarity_score`: Cosine similarity to cluster centroid (0.0-1.0)
- `assigned_at`: When bookmark was added to cluster

**Validation Rules**:
- Similarity score: 0.0-1.0
- Each bookmark can belong to multiple clusters (but typically 1-2)

**SQLAlchemy Association Table**:
```python
from sqlalchemy import Table, Column, Float

bookmark_clusters = Table(
    "bookmark_clusters",
    Base.metadata,
    Column("bookmark_id", UUID(as_uuid=True), ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("cluster_id", UUID(as_uuid=True), ForeignKey("clusters.id", ondelete="CASCADE"), primary_key=True),
    Column("similarity_score", Float, nullable=False),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now())
)
```

---

### 6. Import_Jobs Table

Tracks HTML import and AI processing jobs.

```sql
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Job metadata
    filename VARCHAR(255),
    file_size_bytes INTEGER,
    total_bookmarks INTEGER DEFAULT 0,

    -- Progress tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,  -- 0-100 percentage

    -- Processing stages
    imported_count INTEGER DEFAULT 0,
    embeddings_generated INTEGER DEFAULT 0,
    tags_generated INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,

    -- Cost tracking
    total_cost_usd DECIMAL(10, 4) DEFAULT 0.00,
    openai_cost_usd DECIMAL(10, 4) DEFAULT 0.00,
    claude_cost_usd DECIMAL(10, 4) DEFAULT 0.00,

    -- Error tracking
    error_message TEXT,
    error_details JSONB,

    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('pending', 'importing', 'processing', 'clustering', 'completed', 'failed'))
);

-- Indexes
CREATE INDEX idx_import_jobs_user ON import_jobs(user_id);
CREATE INDEX idx_import_jobs_status ON import_jobs(status);
CREATE INDEX idx_import_jobs_created ON import_jobs(created_at DESC);
```

**Fields**:
- `id`: UUID primary key
- `user_id`: Foreign key to users table
- `filename`: Original uploaded HTML filename
- `file_size_bytes`: File size in bytes
- `total_bookmarks`: Total bookmarks found in HTML file
- `status`: Job status (pending/importing/processing/clustering/completed/failed)
- `progress`: Overall progress percentage (0-100)
- `imported_count`: Bookmarks successfully imported
- `embeddings_generated`: Embeddings successfully generated
- `tags_generated`: Tags/summaries successfully generated
- `failed_count`: Bookmarks that failed processing
- `total_cost_usd`: Total AI processing cost
- `openai_cost_usd`: OpenAI embedding cost
- `claude_cost_usd`: Claude tagging cost
- `error_message`: Human-readable error (if failed)
- `error_details`: Structured error data (JSONB)
- `started_at`: When job started
- `completed_at`: When job completed
- `created_at`: Job creation timestamp

**State Transitions**:
```
pending → importing → processing → clustering → completed
                                              ↓
                                           failed
```

**SQLAlchemy Model**:
```python
from sqlalchemy.dialects.postgresql import JSONB
from decimal import Decimal

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    filename = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    total_bookmarks = Column(Integer, default=0)

    status = Column(String(50), nullable=False, default="pending")
    progress = Column(Integer, default=0)

    imported_count = Column(Integer, default=0)
    embeddings_generated = Column(Integer, default=0)
    tags_generated = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    total_cost_usd = Column(Numeric(10, 4), default=Decimal("0.00"))
    openai_cost_usd = Column(Numeric(10, 4), default=Decimal("0.00"))
    claude_cost_usd = Column(Numeric(10, 4), default=Decimal("0.00"))

    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="import_jobs")
    bookmarks = relationship("Bookmark", back_populates="import_job")

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'importing', 'processing', 'clustering', 'completed', 'failed')", name="valid_status"),
    )
```

---

## Database Initialization

### Migration Strategy (Alembic)

```bash
# Initialize Alembic
alembic init migrations

# Create initial migration
alembic revision --autogenerate -m "Initial schema: users, bookmarks, projects, clusters, import_jobs"

# Apply migration
alembic upgrade head
```

### Seed Data (Development Only)

```python
# Create test user
test_user = User(
    email="sia@example.com",
    hashed_password=hash_password("testpass123"),
    full_name="Sia Test User"
)

# No bookmarks initially (Phase 0 starts with import)
```

---

## Performance Considerations

### Indexes Strategy:
- **GIN indexes** on `tags` arrays for fast tag filtering
- **Composite indexes** on `(user_id, created_at)` for user-scoped time-based queries
- **Partial indexes** on boolean flags (`WHERE is_active = true`) to reduce index size

### Query Optimization:
- **Eager loading** relationships with `selectinload()` to avoid N+1 queries
- **Batch operations** for bulk inserts (import 800 bookmarks at once)
- **Denormalization**: Store `bookmark_count` in clusters table to avoid expensive COUNT queries

### Scaling Considerations:
- **Partitioning**: Partition `bookmarks` table by `user_id` if scaling beyond 100K users
- **Archiving**: Move old import_jobs to archive table after 90 days
- **Connection pooling**: SQLAlchemy async pool with max 20 connections

---

## Next: API Contracts

With data model defined, proceed to generate OpenAPI specifications in `contracts/` directory.
