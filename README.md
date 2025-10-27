# Bookmark Intelligence - Cleaner

This tool cleans HTML bookmark exports and creates structured formats suitable for:
- **Human reading** (Markdown)
- **AI/LLM processing** (JSON)
- **Database storage** (Flat JSON)

## What it does

The script removes noise from bookmark files including:
- ✅ Base64 ICON data (those long `data:image/png;base64,...` strings)
- ✅ Excessive HTML markup
- ✅ Duplicates and invalid URLs (like `file://` links)
- ✅ Creates clean, structured outputs

## Quick Start

### Using uv (Recommended)

```bash
# Run directly with uv (no installation needed!)
uv run clean_bookmarks.py
```

### Traditional Python

```bash
# Install dependencies
pip install beautifulsoup4 lxml

# Run the script
python clean_bookmarks.py
```

## Output Files

The script generates three files:

1. **`bookmarks_clean.md`** - Human-readable Markdown
   - Easy to browse and search
   - Organized by folders
   - Includes dates

2. **`bookmarks_clean.json`** - Hierarchical structure
   - Preserves folder organization
   - Includes metadata
   - Good for backup/migration

3. **`bookmarks_flat.json`** - Flat list for AI/Database
   - One array of all bookmarks
   - Perfect for vector embeddings
   - Easy to import into databases
   - Optimized for LLM context

## Example Output

### Markdown Format
```markdown
## FabrikTakt
  - [MinIO](https://github.com/minio/minio) (Added: 2025-01-15)
  - [Signoz](https://github.com/SigNoz/signoz) (Added: 2025-01-16)
```

### JSON Format
```json
{
  "url": "https://github.com/minio/minio",
  "title": "minio/minio: MinIO is a high-performance object store",
  "folder_path": "Sia > FabrikTakt > stack",
  "added_date": "2025-01-15T10:30:00",
  "added_timestamp": 1736935800
}
```

## Integration with BookmarkAI System

This cleaner is designed to prepare bookmarks for **BookmarkAI** - an AI-powered browser extension that transforms static bookmarks into an intelligent, context-aware knowledge management system.

**How it integrates:**
- **Flat JSON** → Ready for vector embeddings (OpenAI text-embedding-3-small)
- **Structured data** → Easy to import into PostgreSQL
- **Clean titles/URLs** → Better AI analysis with chatgpt

### Learn More About BookmarkAI

- **📚 [Full Documentation](./docs/)** - Complete system specifications
- **🚀 [Quick Overview](./docs/overview.md)** - 5-minute introduction
- **🏗️ [System Architecture](./docs/architecture.md)** - Technical design
- **✨ [Features](./docs/features.md)** - Detailed feature specs
- **🗓️ [Roadmap](./docs/roadmap.md)** - 12-week development plan

## File Structure

```
.
├── bookmarks_10_27_25.html      # Your original bookmark export
├── clean_bookmarks.py           # The cleaner script
├── pyproject.toml               # Python project config
├── README.md                    # This file
├── docs/                        # BookmarkAI system documentation
│   ├── README.md                # Documentation index
│   ├── overview.md              # Product overview
│   ├── architecture.md          # System architecture
│   ├── features.md              # Feature specifications
│   ├── roadmap.md               # Development roadmap
│   └── reference.md             # Costs, security, metrics
├── spec-v1.md                   # Legacy spec (superseded by docs/)
└── [outputs]
    ├── bookmarks_clean.md       # Human-readable
    ├── bookmarks_clean.json     # Hierarchical
    └── bookmarks_flat.json      # Flat for DB/AI
```

## Statistics

After running, you'll see:
```
✓ Parsed 150 bookmarks in 12 folders
✅ Done! Your bookmarks have been cleaned and formatted.

📊 Summary:
   • Total bookmarks: 150
   • Total folders: 12
```

## Next Steps

Once you have clean bookmarks:

1. **Import to database**: Use `bookmarks_flat.json` with PostgreSQL
2. **Generate embeddings**: Send to OpenAI API for vector representations
3. **Build the full system**: Follow [docs/](./docs/) for the complete BookmarkAI platform

### Building BookmarkAI

Ready to build the full system? Start here:

1. **[Read the Overview](./docs/overview.md)** - Understand the product vision
2. **[Review Architecture](./docs/architecture.md)** - Learn the technical design
3. **[Follow the Roadmap](./docs/roadmap.md)** - 12-week development plan

## License

MIT
