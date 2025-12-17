# Week 2: AI Processing Implementation Plan

> **Note:** This plan will be moved to `docs/dev/plans/2025-12-17-week2-ai-processing.md` during implementation

**Date:** 2025-12-17
**Status:** Planning
**Goal:** Prove AI can organize 871 messy bookmarks into meaningful clusters and projects

**Technical Decisions:**
- ✓ OpenAI Batch API for embeddings (24hr, 50% cost savings)
- ✓ GPT-5.2 (Standard) for tagging/summarization
- ✓ Auto-detect optimal clusters (8-15 range using elbow method)

**Estimated Cost:** ~$8 for 871 bookmarks (one-time processing)

---

## Implementation: 4 Phases

### Phase 1: Setup & Dependencies (2h)

**Add AI libraries to pyproject.toml:**
```toml
dependencies = [
    "openai>=1.58.0",
    "scikit-learn>=1.6.1",
    "numpy>=2.2.0",
]
```

**Create config/ai_settings.yaml:**
```yaml
openai:
  embedding_model: text-embedding-3-small
  dimensions: 1536
  batch_api_enabled: true

  tagging_model: gpt-5.2
  max_tokens: 200
  temperature: 0.3

clustering:
  min_clusters: 8
  max_clusters: 15
  method: minibatch_kmeans
```

**Create .env.example:**
```
OPENAI_API_KEY=sk-...
```

**Create module structure:**
```
src/bookmark_intelligence/ai/
├── __init__.py
├── embedding_service.py
├── tagging_service.py
└── clustering.py
```

**Verification:**
```bash
uv sync
pytest tests/  # Existing tests still pass
```

---

### Phase 2: AI Services (6h)

#### 2.1 OpenAI Embedding Service

**File:** `src/bookmark_intelligence/ai/embedding_service.py`

**Key methods:**
- `create_batch_job(bookmarks)` → batch_id
- `poll_batch_status(batch_id)` → status dict
- `retrieve_batch_results(batch_id)` → List[List[float]]

**Process:**
1. Format bookmarks as JSONL (URL + title for embedding)
2. Submit to OpenAI Batch API
3. Poll every 10min until complete
4. Download results, save to `data/ai/embeddings.npy`

#### 2.2 GPT Tagging Service

**File:** `src/bookmark_intelligence/ai/tagging_service.py`

**Key methods:**
- `async tag_bookmark(bookmark)` → {tags, summary, content_type}
- `async tag_batch(bookmarks, batch_size=50)` → List[Dict]

**Prompt:**
```
Given bookmark:
URL: {url}
Title: {title}
Domain: {domain}

Generate JSON:
{
  "tags": ["tag1", "tag2", ...],  // 3-7 tags
  "summary": "2-3 sentence summary",
  "content_type": "tutorial|documentation|tool|article"
}
```

**Process:**
1. Async batch processing with asyncio.gather()
2. Rate limit: 50 concurrent requests (semaphore)
3. Exponential backoff on errors
4. Progress tracking every 50 bookmarks

**Cost:** GPT-5.2 pricing TBD (estimated similar to gpt-4o: ~$2-3 for 871 bookmarks)

---

### Phase 3: Clustering & Projects (4h)

#### 3.1 Clustering Engine

**File:** `src/bookmark_intelligence/ai/clustering.py`

**Class:** `BookmarkClusterer`

**Key methods:**
- `determine_optimal_k(embeddings, k_range=(8,15))` → optimal k
  - Uses silhouette score
  - Elbow method
- `cluster_bookmarks(embeddings, bookmarks, n_clusters=None)` → cluster results
  - MiniBatchKMeans with cosine similarity
  - Generate cluster names from top tags/domains
  - Return cluster_id per bookmark

**Cluster naming strategy:**
1. Extract top 10 tags in cluster
2. Extract top 5 domains
3. Generate names like "Docker & DevOps" or "Python Learning"

#### 3.2 Project Suggester

**File:** `src/bookmark_intelligence/ai/project_suggester.py`

**Class:** `ProjectSuggester`

**Method:** `suggest_projects(clusters, bookmarks)` → List[Dict]

**Strategy:**
1. Identify work clusters (keywords: docker, kubernetes, fastapi)
2. Identify learning clusters (keywords: tutorial, course, guide)
3. Use folder_path hints (e.g., "FabrikTakt" folder → project name)
4. Suggest 3-5 projects with confidence scores

**Output:**
```json
{
  "name": "FabrikTakt",
  "description": "Work-related infrastructure bookmarks",
  "cluster_ids": [0, 3, 7],
  "bookmark_count": 143,
  "confidence": 0.87,
  "keywords": ["docker", "kubernetes", "fastapi"]
}
```

---

### Phase 4: Pipeline Integration (6h)

#### 4.1 Extend Pipeline

**File:** `src/bookmark_intelligence/pipeline/processor.py`

**Add method:** `run_ai_processing()`

**Pipeline stages:**
1. Load `data/processed/bookmarks_flat.json` (871 bookmarks)
2. Submit OpenAI batch embedding job → wait 24hr
3. Run GPT tagging (async batches of 50)
4. Cluster bookmarks (auto-detect k)
5. Generate project suggestions
6. Export AI results
7. Generate AI report

**Outputs:**
```
data/ai/
├── embeddings.npy             # 871 × 1536 numpy array
├── bookmarks_ai.json          # Bookmarks with tags/summaries/cluster_id
├── clusters.json              # Cluster definitions
└── projects_suggested.json    # 3-5 project suggestions

data/reports/
└── 2025-12-17-ai-processing.md  # AI analysis report
```

#### 4.2 Create CLI

**File:** `scripts/process_ai.py`

```python
@click.command()
@click.option('--stage', type=click.Choice(['embed', 'tag', 'cluster', 'all']))
@click.option('--batch-id', help='Resume from existing batch job')
def process_ai(stage, batch_id):
    processor = BookmarkProcessor()
    processor.run_ai_processing(stage=stage, batch_id=batch_id)
```

**Usage:**
```bash
# Start batch embedding job
uv run scripts/process_ai.py --stage embed

# After 24hr, continue with tagging
uv run scripts/process_ai.py --stage tag

# Or run all stages
uv run scripts/process_ai.py --stage all
```

#### 4.3 Add FastAPI Endpoints

**File:** `src/app/api/v1/endpoints/ai_processing.py`

**Endpoints:**
- `GET /api/v1/ai/clusters` → List clusters
- `GET /api/v1/ai/clusters/{id}/bookmarks` → Bookmarks in cluster
- `GET /api/v1/ai/projects/suggested` → Project suggestions
- `GET /api/v1/ai/status` → AI processing status

#### 4.4 Simple Web Dashboard

**File:** `frontend/src/pages/ClustersPage.jsx`

**Features:**
- Grid view of clusters with names and sizes
- Click cluster → see bookmarks
- Bookmark cards show: title, URL, tags (chips), summary
- Filter/search within clusters

---

## Data Schema

### bookmarks_ai.json

```json
{
  "generated_at": "2025-12-17T20:00:00Z",
  "total_cost_usd": 8.20,
  "bookmarks": [
    {
      "url": "https://github.com/anthropics/claude-code",
      "title": "Claude Code CLI",
      "domain": "github.com",
      "embedding_index": 0,
      "tags": ["ai", "coding-assistant", "cli"],
      "summary": "Claude Code is a CLI for AI-powered development...",
      "content_type": "tool",
      "cluster_id": 3,
      "cluster_name": "AI Development Tools"
    }
  ]
}
```

### clusters.json

```json
{
  "n_clusters": 12,
  "generated_at": "2025-12-17T20:30:00Z",
  "clusters": [
    {
      "id": 0,
      "name": "Docker & DevOps",
      "size": 87,
      "keywords": ["docker", "kubernetes", "deployment"],
      "top_domains": ["docker.com", "kubernetes.io"]
    }
  ]
}
```

---

## Testing Strategy

**Unit tests:** `tests/test_ai_services.py`
- Test embedding batch creation
- Test tagging prompt building
- Test clustering optimal k detection

**Integration test:** `tests/test_ai_pipeline.py`
- Run full pipeline on 10 sample bookmarks

**Manual validation:**
- [ ] 871 embeddings generated (1536-dim each)
- [ ] 85%+ tags are relevant (spot check 50)
- [ ] Summaries are accurate (spot check 50)
- [ ] 8-15 clusters with meaningful names
- [ ] 3-5 sensible project suggestions
- [ ] Total cost < $10
- [ ] Dashboard shows all bookmarks by cluster

---

## Critical Files to Modify/Create

**New files:**
- `src/bookmark_intelligence/ai/__init__.py`
- `src/bookmark_intelligence/ai/embedding_service.py`
- `src/bookmark_intelligence/ai/tagging_service.py`
- `src/bookmark_intelligence/ai/clustering.py`
- `src/bookmark_intelligence/ai/project_suggester.py`
- `scripts/process_ai.py`
- `src/app/api/v1/endpoints/ai_processing.py`
- `frontend/src/pages/ClustersPage.jsx`
- `config/ai_settings.yaml`
- `tests/test_ai_services.py`

**Modified files:**
- `pyproject.toml` (add dependencies)
- `src/bookmark_intelligence/pipeline/processor.py` (add run_ai_processing method)
- `src/app/main.py` (include AI router)

---

## Timeline

**Day 1 (2h):** Phase 1 - Setup, submit batch job
**Day 2 (6h):** Phase 2 - Develop tagging/clustering (while waiting for embeddings)
**Day 3 (4h):** Retrieve embeddings, run full pipeline
**Day 4 (6h):** Phase 4 - Dashboard, testing

**Total: 18h over 4 days**

---

## Success Criteria

✓ All 871 bookmarks have embeddings, tags, summaries
✓ Clustered into 8-15 semantic groups
✓ 3-5 sensible project suggestions
✓ Total cost < $10
✓ Web dashboard for browsing clusters
✓ Proof that AI organization works locally
