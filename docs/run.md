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

## AI + Bookmark Processing Pipelines (CLI)

These pipelines write files under `data/processed/`, `data/ai/`, and `data/reports/`.

### 1) Offline Bookmark Processing (Dry Run)
Runs entirely locally (no OpenAI required) using the sample fixture:

```bash
uv run scripts/process_bookmarks.py --input tests/fixtures/sample_bookmarks.html
```

Expected outputs:
- `data/processed/bookmarks_flat.json`
- `data/processed/bookmarks_clean.json`
- `data/processed/bookmarks_clean.md`

### 2) AI Tagging Only (Cheap Dry Run)
Useful to validate prompts + 12-field outputs without waiting for embeddings/clustering.

1) Ensure you have `OPENAI_API_KEY` set (copy `.env.example` → `.env` if you use dotenv tooling).
2) Create a small input file (first 20 bookmarks):

```bash
python - <<'PY'
import json
from pathlib import Path

src = Path("data/processed/bookmarks_flat.json")
dst = Path("data/processed/bookmarks_flat_small.json")

bookmarks = json.loads(src.read_text())
dst.write_text(json.dumps(bookmarks[:20], indent=2))
print(f"Wrote {dst} ({min(20, len(bookmarks))} bookmarks)")
PY
```

3) Run tagging stage only:

```bash
uv run scripts/process_ai.py --input data/processed/bookmarks_flat_small.json --stage tag
```

Expected output:
- `data/ai/bookmarks_tagged.json` (intermediate list of enriched bookmarks)

Optional: verify all 12 AI fields exist (and are non-empty where required):

```bash
python - <<'PY'
import json
from pathlib import Path

required = {
  "tags", "summary", "content_type", "primary_technology", "skill_level",
  "use_cases", "key_topics", "value_proposition", "folder_recommendation",
  "priority", "related_keywords", "actionability",
}

bookmarks = json.loads(Path("data/ai/bookmarks_tagged.json").read_text())
bad = []
for i, b in enumerate(bookmarks):
    missing = sorted(required - set(b.keys()))
    if missing:
        bad.append((i, missing))

print(f"bookmarks: {len(bookmarks)}")
print(f"missing-required: {len(bad)}")
if bad:
    print("first-bad:", bad[0])
PY
```

### 3) Full AI Pipeline (Embeddings + Tagging + Clustering)
This uses the OpenAI Batch API for embeddings and can take time (batch completion window is up to 24 hours).

```bash
uv run scripts/process_ai.py --stage all
```

If you need to resume a finished/ongoing embedding batch:

```bash
uv run scripts/process_ai.py --stage embed --batch-id "$(cat data/ai/batch_id.txt)"
```

Expected outputs:
- `data/ai/embeddings.npy`
- `data/ai/clusters.json`
- `data/ai/projects_suggested.json`
- `data/ai/folder_recommendations.json`
- `data/ai/bookmarks_ai.json`
- `data/reports/YYYY-MM-DD-ai-processing.md`

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
