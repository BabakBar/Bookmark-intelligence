# Quick Start

1. **Start Infrastructure**  
Run PostgreSQL, Qdrant, and Valkey:

```bash
docker compose up -d
```

2. **Run Backend**  
Set up and start the FastAPI server:

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn src.app.main:app --reload --port 8000
```

3. **Run Frontend**  
Set up and start the React app:

```bash
cd frontend
npm install  # or bun install
npm run dev  # or bun run dev
```

## Test It

- Open `http://localhost:5173` in your browser.
- Upload a bookmarks HTML file (e.g., `tests/fixtures/sample_bookmarks.html`).
- Verify parsed bookmarks appear on the page.

The app is now running with full-stack functionality.
