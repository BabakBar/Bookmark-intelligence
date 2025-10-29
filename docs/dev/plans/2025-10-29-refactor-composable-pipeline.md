# Refactoring Plan: Composable Bookmark Processing Pipeline

**Date:** 2025-10-29
**Status:** Draft
**Goal:** Transform monolithic script into composable, reusable pipeline for batch processing

## Recent Updates

**2025-10-29 Evening:**
- ✅ Added LAST_MODIFIED extraction for folders (clean_bookmarks.py:206-209)
- ✅ Folders now track: name, path, last_modified_date, last_modified_timestamp
- ✅ Updated polished report format with quality issues, duplicates, active folders
- ✅ Learned: BeautifulSoup html5lib normalizes HTML attributes to lowercase
- 📝 Next: Begin Phase 1 refactoring or build quick report generator

---

## Current Situation

### What Exists
- Single script `clean_bookmarks.py` (~340 lines)
- Successfully processes 772 bookmarks from HTML export
- **Bookmarks extract:** URL, domain, title, folder_path, added_date, added_timestamp
- **Folders extract:** name, path, last_modified_date, last_modified_timestamp (NEW)
- Generates 3 outputs: hierarchical JSON, flat JSON, markdown
- Domain extraction with normalization (www removal, case folding)
- BeautifulSoup with html5lib parser (normalizes attributes to lowercase)

### What Works Well
✅ Parsing logic handles nested folder structure
✅ Domain extraction is robust (handles edge cases)
✅ Folder LAST_MODIFIED extraction provides activity signals
✅ Output formats meet initial needs
✅ BeautifulSoup handles malformed HTML gracefully

### Current Problems

**1. Monolithic Structure**
- Parsing, extraction, analysis, output generation all mixed
- Business logic (domain normalization) buried in class methods
- Hard to test individual components
- Hard to extend with new extractors

**2. Hardcoded Configuration**
```python
# Lines 272-275: Hardcoded paths
input_file = Path("data/bookmarks_29_10_2025.html")
output_md = Path("bookmarks_clean.md")
output_json = Path("bookmarks_clean.json")
output_flat_json = Path("bookmarks_flat.json")
```

**3. Lost Analysis**
- Created domain analysis script for insights
- Deleted after one-time use (not persistent)
- No way to compare batches over time
- Insights don't feed back into processing

**4. No Incremental Processing**
- Must reprocess entire HTML file each time
- No deduplication across batches
- No change detection (moved folders, updated titles)
- No merging with existing data

**5. No Input Flexibility**
- Script expects specific filename
- Manual code edits for each new batch
- No support for processing multiple files
- No CLI interface

**6. Debug Output Pollution**
```python
# Lines 112-207: 30+ print statements for debugging
print(f"{indent}DEBUG: Processing child {i+1}...")
```
Mixed with actual output, hard to silence in production

---

## Target Architecture

### Design Principles
1. **Separation of Concerns** - each module has one job
2. **Pure Functions** - testable, predictable transformations
3. **Configuration-Driven** - business rules in YAML, not code
4. **Composable Pipeline** - stages can run independently
5. **Persistent Analysis** - insights saved for comparison

### Directory Structure

```
bookmark-intelligence/
├── src/
│   └── bookmark_intelligence/
│       ├── __init__.py
│       ├── models/              # Data structures
│       │   ├── __init__.py
│       │   ├── bookmark.py      # Bookmark, Folder classes
│       │   └── schemas.py       # Pydantic validation schemas
│       ├── parsers/             # Input handlers
│       │   ├── __init__.py
│       │   └── html_parser.py   # BeautifulSoup parsing logic
│       ├── extractors/          # Feature extraction
│       │   ├── __init__.py
│       │   ├── base.py          # BaseExtractor interface
│       │   └── domain.py        # DomainExtractor
│       ├── analyzers/           # Insights generation
│       │   ├── __init__.py
│       │   ├── domain_stats.py  # Domain distribution
│       │   └── quality.py       # Validation, health checks
│       ├── storage/             # Data persistence
│       │   ├── __init__.py
│       │   └── json_store.py    # JSON read/write operations
│       └── pipeline/            # Orchestration
│           ├── __init__.py
│           └── processor.py     # Pipeline coordinator
├── config/
│   ├── settings.yaml            # Paths, batch naming
│   └── extractors.yaml          # Domain categories, rules
├── scripts/
│   └── process_bookmarks.py     # CLI entry point
├── data/
│   ├── raw/                     # bookmarks_DD_MM_YYYY.html
│   ├── processed/               # bookmarks_clean.json (latest)
│   └── reports/                 # YYYY-MM-DD-analysis.md
├── tests/
│   ├── test_parsers.py
│   ├── test_extractors.py
│   └── fixtures/                # Sample HTML for testing
└── clean_bookmarks.py           # [DEPRECATED - keep for reference]
```

### Pipeline Stages (Composable)

```
┌─────────────────────────────────────────────────────────┐
│                    BOOKMARK PIPELINE                     │
└─────────────────────────────────────────────────────────┘

1. [DISCOVER]  Scan data/raw/ → find latest HTML file
               ├─ Pattern: bookmarks_DD_MM_YYYY.html
               └─ Sort by date in filename

2. [PARSE]     HTML file → List[Bookmark] + List[Folder]
               ├─ BeautifulSoup extraction
               ├─ Folder hierarchy traversal
               └─ Skip invalid URLs (file://, empty)

3. [EXTRACT]   Apply extractors to each bookmark
               ├─ DomainExtractor (implemented)
               ├─ Future: MetadataExtractor
               └─ Future: CategoryInferenceExtractor

4. [VALIDATE]  Check data quality
               ├─ Required fields present
               ├─ URL format valid
               └─ Timestamp reasonable

5. [ANALYZE]   Generate insights
               ├─ Domain distribution
               ├─ Folder statistics
               ├─ Top domains by category
               └─ Quality metrics

6. [EXPORT]    Write multiple formats
               ├─ processed/bookmarks_clean.json (hierarchical)
               ├─ processed/bookmarks_flat.json (for AI)
               └─ processed/bookmarks_clean.md (human-readable)

7. [REPORT]    Persist analysis (NEW)
               └─ reports/YYYY-MM-DD-import.md
```

### Configuration Files

**config/settings.yaml**
```yaml
# File paths
paths:
  raw: data/raw
  processed: data/processed
  reports: data/reports

# Input file pattern
input:
  pattern: "bookmarks_*.html"
  date_format: "%d_%m_%Y"

# Output files
output:
  hierarchical: bookmarks_clean.json
  flat: bookmarks_flat.json
  markdown: bookmarks_clean.md

# Logging
logging:
  level: INFO
  debug_parsing: false  # Disable DEBUG print statements
```

**config/extractors.yaml**
```yaml
# Domain extraction rules
domain:
  normalize_www: true
  lowercase: true

  # Domain → Category mapping (for analysis hints)
  categories:
    code_repos:
      - github.com
      - gitlab.com
      - bitbucket.org

    documentation:
      - docs.python.org
      - developer.mozilla.org
      - learn.microsoft.com

    video:
      - youtube.com
      - vimeo.com
      - loom.com

    social:
      - x.com
      - twitter.com
      - linkedin.com
      - reddit.com

    google_services:
      - mail.google.com
      - docs.google.com
      - drive.google.com
      - console.cloud.google.com
      - analytics.google.com
```

---

## Refactoring Steps

### Phase 1: Extract Core Models (1-2 hours) ✅

**Goal:** Separate data structures from logic

**Tasks:**

- [x] Create `src/bookmark_intelligence/models/bookmark.py`
  - [x] Move `Bookmark` class
  - [x] Move `Folder` class
  - [x] Keep domain extraction logic for now

- [x] Create `src/bookmark_intelligence/models/schemas.py`
  - [x] Add Pydantic models for validation
  - [x] `BookmarkSchema`, `FolderSchema`

- [x] Update imports in `clean_bookmarks.py`
  - [x] Verify script still works

**Success Criteria:**

- ✅ `clean_bookmarks.py` runs unchanged (verified: 772 bookmarks, 60 folders parsed)
- ✅ Models importable: `from bookmark_intelligence.models import Bookmark`

---

### Phase 2: Extract Parsing Logic (2-3 hours) ✅

**Goal:** Isolate BeautifulSoup operations

**Tasks:**

- [x] Create `src/bookmark_intelligence/parsers/html_parser.py`
  - [x] Move `BookmarkParser` class
  - [x] Remove print statements, use Python logging
  - [x] Add docstrings for public methods

- [x] Create parser configuration
  - [x] `config/settings.yaml` with logging level
  - [x] Replace hardcoded paths with config

- [x] Add tests
  - [x] `tests/test_parsers.py` with sample HTML
  - [x] Test nested folders
  - [x] Test malformed HTML handling

**Success Criteria:**

- ✅ Parser extracted to module: `bookmark_intelligence.parsers`
- ✅ Logging configurable (INFO by default, DEBUG optional)
- ✅ Tests pass: 11/11 tests passing
- ✅ Type checking passes (mypy)
- ✅ Linting passes (ruff)

---

### Phase 3: Extract Feature Extractors (1-2 hours) ✅

**Goal:** Make domain extraction pluggable (simplified to single file)

**Tasks:**

- [x] Create `src/bookmark_intelligence/extractors/extractors.py` (simplified: single file instead of base.py + domain.py)
   ```python
  - [x] BaseExtractor abstract class
  - [x] DomainExtractor implementation
  - [x] Category inference from config

- [x] Create `config/extractors.yaml`
  - [x] Domain categories (code_repos, social, video, etc.)

**Success Criteria:**

- ✅ Extractors pluggable: BaseExtractor interface ready for future extractors
- ✅ Domain categories loaded from YAML: 6 categories configured
- ✅ Tests pass: 7/7 extractor tests passing

---

### Phase 4: Create Analysis Module (2-3 hours) ✅

**Goal:** Persistent, reusable analysis (simplified to single file)

**Tasks:**

- [x] Create `src/bookmark_intelligence/analyzers/analyzers.py` (single file with all functions)
  - [x] `analyze_domains()` - domain stats and categorization
  - [x] `analyze_quality()` - duplicates, empty titles, missing dates
  - [x] `analyze_folder_activity()` - recently active, stale folders
  - [x] `generate_report()` - markdown and JSON reports

**Example Report:**

```markdown
# Bookmark Analysis Report

**Generated:** 2025-10-29 23:15:43
**Source:** bookmarks_29_10_2025.html

## Overview

- **Total bookmarks:** 772
- **Unique domains:** 351
- **Folders:** 60 (12 modified in last 30 days)
- **Date range:** 2022-12-07 to 2025-10-29

## Top 10 Domains

| Domain | Count | % | Category |
|--------|-------|---|----------|
| github.com | 157 | 20.3% | code_repos |
| docs.google.com | 62 | 8.0% | google_services |
| reddit.com | 37 | 4.8% | social |
| youtube.com | 35 | 4.5% | video |
| miro.com | 16 | 2.1% | productivity |
| x.com | 12 | 1.6% | social |
| learn.microsoft.com | 8 | 1.0% | documentation |
| drive.google.com | 6 | 0.8% | google_services |
| console.cloud.google.com | 6 | 0.8% | google_services |
| linkedin.com | 6 | 0.8% | social |

## Category Distribution

- **Code repos:** 173 (22.4%) - github, gitlab
- **Google services:** 100 (13.0%) - docs, drive, analytics, console
- **Documentation:** 64 (8.3%) - learn.microsoft, docs.python
- **Video:** 35 (4.5%) - youtube, vimeo
- **Social:** 55 (7.1%) - reddit, x, linkedin

## Quality Issues

### Duplicates (0 found)

✓ No exact URL duplicates detected

### Empty Titles (13 found)

- https://mail.google.com/... (Bookmarks bar)
- https://chat.openai.com/... (Bookmarks bar)
- https://claude.ai/new (Bookmarks bar)
- _[10 more...]_

### Recently Active Folders

| Folder | Last Modified | Bookmarks | Path |
|--------|---------------|-----------|------|
| Sia | 2025-10-29 | 44 | Bookmarks bar > Sia |
| Cld | 2025-10-26 | 8 | Bookmarks bar > Cld |
| Dev | 2025-10-14 | 12 | Bookmarks bar > Dev |
| DE | 2025-10-10 | 16 | Bookmarks bar > DE |

## Recommendations

- ⚠ 13 bookmarks missing titles - consider adding descriptions
- ✓ No duplicates found - good bookmark hygiene
- ℹ 20% of bookmarks are GitHub repos - consider tagging for project tracking
- 📊 Sia folder actively maintained (modified today)
```

**Success Criteria:**

- ✅ Reports persist in `data/reports/` (verified with real data)
- ✅ Can compare reports across batches (JSON + markdown generated)
- ✅ JSON data available for programmatic analysis
- ✅ Tested with 772 bookmarks: 351 domains, 60 folders, 61 quality issues found

---

### Phase 5: Build Pipeline Orchestrator (2-3 hours) ✅

**Goal:** Coordinate all stages

**Tasks:**

- [x] Create `src/bookmark_intelligence/pipeline/processor.py`
   ```python
  - [x] BookmarkProcessor class with all pipeline stages
  - [x] Config loading from YAML
  - [x] Auto-discovery of latest HTML file

- [x] Create `scripts/process_bookmarks.py` (CLI with click)
  - [x] --input flag for manual file selection
  - [x] --config flag for custom config
  - [x] --debug flag for verbose logging

**Success Criteria:**

- ✅ `uv run scripts/process_bookmarks.py` works end-to-end
- ✅ Auto-discovers latest file in `data/raw/`
- ✅ Generates all outputs + report (tested with 772 bookmarks)
- ✅ Configurable via YAML and CLI args

---

### Phase 6: Storage Layer (1 hour) ✅

**Goal:** Abstract file I/O

**Tasks:**

- [x] Create `src/bookmark_intelligence/storage/json_store.py`
  - [x] `save_hierarchical()`, `save_flat()`, `save_markdown()`

- [x] Update pipeline to use storage layer

**Success Criteria:**

- ✅ File operations abstracted in storage module
- ✅ Easy to swap JSON → SQLite later (interface-based design)

---

### Phase 7: Testing & Documentation (2 hours) ✅

**Goal:** Ensure reliability

**Tasks:**

- [x] Add test fixtures
  - [x] `tests/fixtures/sample_bookmarks.html`

  - [x] `tests/test_parsers.py` - 11 tests for parsing edge cases
  - [x] `tests/test_extractors.py` - 7 tests for domain normalization
  - [ ] `tests/test_analyzers.py` - (tested manually with real data)
  - [ ] `tests/test_pipeline.py` - (tested end-to-end with real data)

**Success Criteria:**

- ✅ 18/18 tests passing (parsers + extractors)
- ✅ Type checking passes (mypy)
- ✅ Linting passes (ruff)
- ✅ End-to-end tested with real 772 bookmark dataset

---

### Phase 8: Migration & Deprecation (30 min) ✅

**Goal:** Clean transition

**Tasks:**

- [x] Keep `clean_bookmarks.py` for reference
  - [x] Add deprecation notice at top
  - [x] Document: "See scripts/process_bookmarks.py"

- [x] Update `.gitignore`
  - [x] Add `data/reports/*.json`

- [x] Run new pipeline, verify output matches old

**Success Criteria:**

- ✅ New pipeline produces identical output (minor enhancement: domain field now included)
- ✅ Old script marked deprecated but functional
- ✅ Documentation updated with new workflow

---

## Future Batch Workflow (After Refactoring)

```bash
# 1. Export bookmarks from browser
# Save as: bookmarks_15_11_2025.html

# 2. Copy to raw directory
cp ~/Downloads/bookmarks_15_11_2025.html data/raw/

# 3. Run pipeline (auto-discovers latest file)
uv run scripts/process_bookmarks.py

# Output:
# 📖 Discovered: data/raw/bookmarks_15_11_2025.html
# 🔍 Parsing HTML...
# ✓ Parsed 850 bookmarks in 60 folders
# 🔧 Extracting features...
# ✓ Domains extracted: 365 unique domains
# 📊 Analyzing...
# ✓ Analysis complete
# 💾 Exporting...
# ✓ Saved: data/processed/bookmarks_clean.json
# ✓ Saved: data/processed/bookmarks_flat.json
# ✓ Saved: data/processed/bookmarks_clean.md
# 📄 Report: data/reports/2025-11-15-import.md
# ✅ Done!

# 4. Review report
cat data/reports/2025-11-15-import.md

# 5. Compare with previous batch
diff reports/2025-10-29-data.json reports/2025-11-15-data.json
# Shows: 78 new bookmarks, 15 new domains
```

---

## Estimated Timeline

| Phase | Description | Time | Dependencies |
|-------|-------------|------|--------------|
| 1 | Extract Models | 1-2h | - |
| 2 | Extract Parsers | 2-3h | Phase 1 |
| 3 | Extract Extractors | 1-2h | Phase 1 |
| 4 | Analysis Module | 2-3h | Phase 1, 2 |
| 5 | Pipeline Orchestrator | 2-3h | Phase 1-4 |
| 6 | Storage Layer | 1h | Phase 1 |
| 7 | Testing & Docs | 2h | Phase 1-6 |
| 8 | Migration | 30m | Phase 1-7 |
| **Total** | | **12-16h** | |

Can work in phases - each phase leaves system in working state.

---

## Dependencies to Add

**pyproject.toml:**
```toml
[project]
dependencies = [
    "beautifulsoup4>=4.12.0",
    "html5lib>=1.1",
    "pyyaml>=6.0",          # NEW - config files
    "pydantic>=2.0",        # NEW - validation
    "click>=8.0",           # NEW - CLI
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

---

## Open Questions

1. **Incremental Processing:** Do we merge new batches with existing data, or keep each batch separate?
   - Option A: Merge → single source of truth, deduplication
   - Option B: Separate → easier comparison, track changes over time

2. **Deduplication Strategy:** How to detect duplicate bookmarks?
   - **Phase 0:** Exact URL match (simplest, already works for current batch)
   - **Future:** URL normalization (strip query params, trailing slashes)
   - **Advanced:** Title similarity for near-duplicates
   - Keep all versions with timestamps for audit trail?

3. **AI Processing Trigger:** When does Phase 0 (AI embeddings) start?
   - After each batch automatically?
   - Manual trigger after validation?

---

## Success Metrics

**Before Refactoring:**
- ❌ Must edit code for new batch
- ❌ Analysis insights lost after one run
- ❌ No test coverage
- ❌ Hard to extend with new features

**After Refactoring:**
- ✅ Drop file in `data/raw/`, run one command
- ✅ Analysis persists in `reports/`
- ✅ >80% test coverage
- ✅ New extractors added in <1 hour
- ✅ Configuration-driven (no code changes for rules)
- ✅ Clear separation of concerns
- ✅ Ready for Phase 0 (AI batch processing)

---

## Next Steps

1. **Get alignment** - review this plan with Sia
2. **Resolve open questions** - decide incremental vs separate batches
3. **Start Phase 1** - extract models (low risk, high value)
4. **Iterate** - each phase adds value, can pause anytime
