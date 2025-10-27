# Quickstart: Phase 0 Bootstrap Import

**Feature**: Phase 0 Bootstrap - Import & Organize Existing Bookmarks
**Target**: Local development environment
**Time**: ~30 minutes setup

## Prerequisites

### Required Tools

```bash
# Python 3.13+
python --version  # Should be >= 3.13

# Docker & Docker Compose (for databases)
docker --version
docker-compose --version

# Node.js 20+ & npm (for frontend)
node --version  # Should be >= 20
npm --version

# Git
git --version
```

### API Keys

You'll need API keys for:
- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Anthropic**: Get from https://console.anthropic.com/settings/keys

---

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
cd /Users/Sia/Code/GitHub/Bookmark-intelligence
git checkout 002-bootstrap-import
```

### 2. Start Databases (Docker)

```bash
# Create docker-compose.yml if not exists
cat > docker-compose.dev.yml <<EOF
version: '3.8'

services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: bookmarkai
      POSTGRES_USER: bookmarkuser
      POSTGRES_PASSWORD: devpass123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:v1.12
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

  valkey:
    image: valkey/valkey:7.4-alpine
    ports:
      - "6379:6379"
    command: valkey-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  postgres_data:
  qdrant_storage:
EOF

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Verify services are running
docker-compose -f docker-compose.dev.yml ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment (using uv for speed)
uv venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows

# Install dependencies
cat > requirements.txt <<EOF
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
alembic==1.14.0
psycopg[binary]==3.2.3
asyncpg==0.30.0
qdrant-client==1.12.0
openai==1.54.0
anthropic==0.39.0
bookmarks-parser==1.1.0
scikit-learn==1.6.0
celery[redis]==5.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.18
pydantic-settings==2.6.1
EOF

uv pip install -r requirements.txt

# Create .env file
cat > .env <<EOF
# Database
DATABASE_URL=postgresql+asyncpg://bookmarkuser:devpass123@localhost:5432/bookmarkai

# Vector Database
QDRANT_URL=http://localhost:6333

# Task Queue
REDIS_URL=redis://localhost:6379/0

# AI APIs
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# JWT
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Environment
ENVIRONMENT=development
EOF

echo "⚠️  Edit backend/.env and add your API keys!"
```

### 4. Database Migrations

```bash
# Still in backend/ directory

# Initialize Alembic
alembic init migrations

# Edit alembic.ini (set sqlalchemy.url)
sed -i '' 's|sqlalchemy.url = .*|sqlalchemy.url = postgresql+asyncpg://bookmarkuser:devpass123@localhost:5432/bookmarkai|' alembic.ini

# Create initial migration
alembic revision --autogenerate -m "Initial schema: users, bookmarks, projects, clusters, import_jobs"

# Apply migrations
alembic upgrade head

# Verify tables created
psql postgresql://bookmarkuser:devpass123@localhost:5432/bookmarkai -c "\dt"
```

### 5. Frontend Setup

```bash
cd ../frontend

# Initialize React + Vite project (if not exists)
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
npm install @tanstack/react-query axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react

# Initialize Tailwind
npx tailwindcss init -p

# Create .env
cat > .env <<EOF
VITE_API_URL=http://localhost:8000/api/v1
EOF
```

---

## Running the Application

### Terminal 1: Backend API

```bash
cd backend
source .venv/bin/activate

# Run FastAPI with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs (Swagger UI)

### Terminal 2: Celery Worker

```bash
cd backend
source .venv/bin/activate

# Run Celery worker for background tasks
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
```

### Terminal 3: Frontend Dev Server

```bash
cd frontend

# Run Vite dev server
npm run dev
```

**Verify**: Open http://localhost:3000 (React app)

---

## Testing the Import Flow

### 1. Create Test User

```bash
# Using httpie (install with: brew install httpie)
http POST http://localhost:8000/api/v1/auth/register \
  email=sia@test.com \
  password=testpass123 \
  full_name="Sia Test"

# Login to get token
http POST http://localhost:8000/api/v1/auth/login \
  username=sia@test.com \
  password=testpass123

# Save the access_token for next requests
export TOKEN="<access_token_from_response>"
```

### 2. Import Bookmarks

```bash
# Upload your HTML bookmark export
http -f POST http://localhost:8000/api/v1/import \
  "Authorization: Bearer $TOKEN" \
  file@/path/to/bookmarks.html

# Example response:
# {
#   "job_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "pending",
#   "total_bookmarks": 800
# }

# Save job_id
export JOB_ID="<job_id_from_response>"
```

### 3. Check Import Status

```bash
# Poll import status
http GET http://localhost:8000/api/v1/import/$JOB_ID/status \
  "Authorization: Bearer $TOKEN"

# Should show:
# - status: "importing" → "pending"
# - imported_count: 800
```

### 4. Trigger AI Processing

```bash
# Start AI processing
http POST http://localhost:8000/api/v1/import/$JOB_ID/process \
  "Authorization: Bearer $TOKEN"

# Response:
# {
#   "job_id": "...",
#   "status": "processing",
#   "estimated_cost_usd": "42.00",
#   "estimated_duration_hours": 18
# }
```

### 5. Monitor Processing (Celery Logs)

```bash
# In Terminal 2 (Celery worker), you should see:
# [INFO] Task app.tasks.ai_tasks.generate_embeddings[...] received
# [INFO] Processing bookmark 1/800: https://example.com/...
# [INFO] Embedding generated (500ms)
# ...
```

### 6. Check Final Report

```bash
# After ~18-24 hours, get report
http GET http://localhost:8000/api/v1/import/$JOB_ID/report \
  "Authorization: Bearer $TOKEN"

# Should show:
# - status: "completed"
# - imported_count: 800
# - embeddings_generated: 795
# - tags_generated: 790
# - total_cost_usd: "42.30"
```

### 7. Browse Organized Bookmarks (Web UI)

Open http://localhost:3000 and:
1. Login with sia@test.com / testpass123
2. View Dashboard (800 bookmarks, 12 clusters, 5 projects)
3. Browse Bookmarks page
4. Filter by cluster: "Docker & Containers"
5. Filter by project: "FabrikTakt"
6. Search: "kubernetes tutorial"

---

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Database Management

```bash
# Create new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Reset database (DANGER: deletes all data)
alembic downgrade base
alembic upgrade head
```

### Debugging

**Backend (FastAPI)**:
- Logs: stdout (Terminal 1)
- API Docs: http://localhost:8000/docs
- Database: `psql postgresql://bookmarkuser:devpass123@localhost:5432/bookmarkai`

**Celery Tasks**:
- Logs: stdout (Terminal 2)
- Monitor: Install flower: `pip install flower && celery -A app.tasks.celery_app flower`
- Access: http://localhost:5555

**Qdrant**:
- Dashboard: http://localhost:6333/dashboard
- Check collection: `curl http://localhost:6333/collections/bookmarks`

---

## Common Issues

### Issue: Database connection refused
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Restart if needed
docker-compose -f docker-compose.dev.yml restart postgres
```

### Issue: OpenAI API rate limit
```bash
# Reduce batch size in backend/app/services/embedding_service.py
# Change: batch_size = 100 → batch_size = 50
```

### Issue: Celery worker not picking up tasks
```bash
# Check Valkey is running
docker-compose -f docker-compose.dev.yml ps valkey

# Restart Celery worker (Terminal 2)
# Ctrl+C, then: celery -A app.tasks.celery_app worker --loglevel=info
```

### Issue: Frontend can't connect to backend
```bash
# Check CORS settings in backend/app/main.py
# Should include: origins=["http://localhost:3000"]

# Check .env in frontend/ has correct VITE_API_URL
```

---

## Next Steps

After successful local testing:

1. **Deploy to Hetzner VPS** using Coolify (see deployment docs)
2. **Run with production data** (your actual 800 bookmarks)
3. **Validate clustering quality** (review suggested clusters)
4. **Accept project suggestions** (FabrikTakt, Learning, etc.)
5. **Proceed to Phase 1** (browser extension development)

---

## Support

**Documentation**: See `specs/002-bootstrap-import/`
- [spec.md](spec.md) - Feature specification
- [plan.md](plan.md) - Implementation plan
- [research.md](research.md) - Technical research
- [data-model.md](data-model.md) - Database schemas
- [contracts/](contracts/) - API specifications

**Issues**: Create GitHub issue in `Bookmark-intelligence` repo
