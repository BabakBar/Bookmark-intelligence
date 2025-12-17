# Quick Start Guide

## 1. Start Infrastructure
```bash
docker compose up -d
```

## 2. Setup Backend
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies and run migrations
uv pip install -e ".[dev]"
alembic upgrade head

# Start server
uvicorn src.app.main:app --reload
```

## 3. Setup Frontend
```bash
cd frontend
npm install  # or bun install
npm run dev  # or bun run dev
```

## 4. Test It
1. Open `http://localhost:5173`
2. Upload `tests/fixtures/sample_bookmarks.html`
3. See imported bookmarks appear

**Done!** Your full-stack app is now running.

---

## Quick Commands Reference

### Start Everything
```bash
docker compose up -d && \
source .venv/bin/activate && \
uvicorn src.app.main:app --reload & \
cd frontend && bun run dev
```

### Stop Everything
```bash
docker compose down
pkill -f uvicorn
pkill -f vite
```

### Reset Database
```bash
alembic downgrade base && alembic upgrade head
```

### Run Tests
```bash
pytest tests/ -v
```

---

## URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Next Steps
- Import your browser bookmarks
- Check database: `docker compose exec postgres psql -U user bookmarkai -c "SELECT COUNT(*) FROM bookmarks;"`
- Explore API documentation at `/docs`

For detailed setup or troubleshooting, see the original documentation.
