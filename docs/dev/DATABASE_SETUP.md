# Database Setup Guide

Modern async database stack with SQLAlchemy 2.0, asyncpg, and Alembic.

## Tech Stack (2024-2025)

- **ORM**: SQLAlchemy 2.0+ with async support
- **Driver**: asyncpg 0.31.0 (5x faster than alternatives)
- **Migrations**: Alembic 1.13.0+
- **Testing**: anyio + Testcontainers

### Why This Stack?

Based on comprehensive 2024-2025 research:
- **SQLAlchemy 2.0**: Industry standard, battle-tested, best for complex queries
- **asyncpg**: Maximum performance for AI workloads (embeddings, vector operations)
- **Alembic**: Reliable migrations with async support

See research report in project commit history for detailed analysis.

---

## Local Development Setup

### 1. Start PostgreSQL

Using Docker Compose:

```bash
# Start all services (PostgreSQL, Qdrant, Valkey)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f postgres
```

Database will be available at:
- **Host**: localhost
- **Port**: 5432
- **Database**: bookmarkai
- **User**: user
- **Password**: password

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and update if needed:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bookmarkai
```

### 3. Run Migrations

Create the database schema:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run migrations
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial schema
```

### 4. Verify Setup

```bash
# Start the FastAPI server
uvicorn src.app.main:app --reload

# In another terminal, check health
curl http://localhost:8000/health
```

---

## Database Migrations

### Creating New Migrations

When you modify database models:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add user authentication"

# Review the generated file in alembic/versions/
# Edit if needed, then apply:
alembic upgrade head
```

### Migration Commands

```bash
# Show current version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123
```

### Best Practices

1. **Review auto-generated migrations** - Alembic isn't perfect
2. **Test migrations on staging first** - Never run untested migrations in production
3. **Small, incremental changes** - One logical change per migration
4. **Meaningful names** - Use descriptive names, not generic "update_schema"
5. **Run before app startup** - Migrations via CLI, not in application code

---

## Database Models

### Current Schema (Task 4 - Week 1)

#### ImportJob
Tracks HTML import progress and costs.

```python
from src.app.models import ImportJob

job = ImportJob(
    filename="bookmarks.html",
    file_size_bytes=52341,
    status="importing",
)
```

#### Bookmark
Stores imported bookmarks with metadata.

```python
from src.app.models import Bookmark

bookmark = Bookmark(
    url="https://github.com/anthropics/claude-code",
    title="Claude Code - GitHub",
    domain="github.com",
    original_folder="Dev Tools/AI",
    import_job_id=job.id,
)
```

### Future Models (Week 2+)
- `User` - Authentication and multi-user support
- `Project` - Bookmark organization workspaces
- `Cluster` - AI-generated semantic clusters
- `bookmark_clusters` - Many-to-many junction table

---

## Connection Management

### Async Session Pattern

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db

@app.get("/bookmarks")
async def get_bookmarks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bookmark).limit(10))
    return result.scalars().all()
```

### Key Settings

From `src/app/core/config.py`:

- `pool_size=5` - Normal connection pool size
- `max_overflow=10` - Extra connections under load
- `pool_pre_ping=True` - Verify connections before use
- `expire_on_commit=False` - Critical for async (prevents "object not bound" errors)

### Relationship Loading

**Always use eager loading** to prevent N+1 queries in async:

```python
from sqlalchemy.orm import selectinload

# Good: Explicit eager loading
result = await db.execute(
    select(ImportJob).options(selectinload(ImportJob.bookmarks))
)

# Or set in model definition
class ImportJob(Base):
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        lazy="selectin"  # Auto-loads in async
    )
```

---

## Testing

### With Testcontainers (Recommended)

Tests automatically spin up PostgreSQL 17:

```python
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
async def db_container():
    with PostgresContainer("postgres:17") as postgres:
        engine = create_async_engine(
            postgres.get_connection_url(driver="asyncpg")
        )
        # ... create tables and yield
```

Run tests:

```bash
pytest tests/ -v
```

### Manual Test Database

```bash
# Create test database
docker compose exec postgres createdb -U user bookmarkai_test

# Run tests with test database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bookmarkai_test pytest
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Run migrations on staging first
- [ ] Back up production database
- [ ] Review migration SQL (`alembic upgrade --sql`)
- [ ] Monitor for slow queries after migration
- [ ] Set up connection pooling (PgBouncer recommended)

### Coolify Deployment

Migrations run automatically via Dockerfile entry point:

```dockerfile
CMD alembic upgrade head && uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

Set in Coolify:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/bookmarkai
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false
ENVIRONMENT=production
```

---

## Troubleshooting

### "Cannot operate on a closed database"

**Cause**: Accessing object after session closed

**Solution**: Use `expire_on_commit=False` (already configured)

```python
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Critical!
)
```

### "Object is not bound to a Session"

**Cause**: Lazy loading in async context

**Solution**: Use eager loading (selectinload, joined load)

```python
# Bad
bookmark = await db.get(Bookmark, bookmark_id)
job = await bookmark.import_job  # ❌ Won't work in async

# Good
result = await db.execute(
    select(Bookmark)
    .options(selectinload(Bookmark.import_job))
    .where(Bookmark.id == bookmark_id)
)
bookmark = result.scalar_one()
job = bookmark.import_job  # ✅ Works!
```

### "Connection pool limit exceeded"

**Cause**: Too many concurrent requests

**Solutions**:
1. Increase pool size in config
2. Add PgBouncer for connection pooling
3. Implement request queuing
4. Scale horizontally (add more app instances)

### Migration Conflicts

**Cause**: Multiple developers creating migrations simultaneously

**Solution**:
```bash
# Merge migrations
alembic merge heads -m "Merge migrations"

# Then upgrade
alembic upgrade head
```

---

## Monitoring

### Useful Queries

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'bookmarkai';

-- Slow queries (if pg_stat_statements enabled)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public';
```

### Logging

Enable SQL logging for debugging (development only):

```.env
DATABASE_ECHO=true
```

---

## Next Steps

- **Week 2**: Add AI processing (OpenAI embeddings, Claude tagging)
- **Week 3+**: Add User authentication (JWT) and multi-user support
- **Week 4+**: Add Projects and Clusters tables

---

**Tech Stack Research**: See commit `feat: implement database persistence with modern async stack` for full 2024-2025 research report on ORM choices, migration tools, and testing strategies.
