"""
DEPRECATED: This script is deprecated and kept for reference only.

Use the new pipeline instead:
    uv run scripts/process_bookmarks.py

The new pipeline provides:
- Automatic file discovery
- Domain categorization
- Quality analysis
- Folder activity tracking
- Comprehensive reports

See: docs/dev/plans/2025-10-29-refactor-composable-pipeline.md
"""

import json
import logging
from pathlib import Path

from bookmark_intelligence.parsers import BookmarkParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("⚠️  WARNING: This script is deprecated!")
print("   Use: uv run scripts/process_bookmarks.py")
print("")


def main():
    """Main function to clean bookmarks"""
    
    # Input and output paths
    input_file = Path("data/bookmarks_29_10_2025.html")
    output_md = Path("bookmarks_clean.md")
    output_json = Path("bookmarks_clean.json")
    output_flat_json = Path("bookmarks_flat.json")
    
    if not input_file.exists():
        print(f"❌ Error: {input_file} not found!")
        return
    
    print(f"📖 Reading bookmarks from: {input_file}")
    print()
    
    # Parse bookmarks
    parser = BookmarkParser(input_file)
    parser.parse()
    
    print()
    print("=" * 60)
    print()
    
    # Generate outputs
    print("💾 Generating outputs...")
    
    # 1. Markdown for humans
    markdown_content = parser.to_markdown()
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"  ✓ Human-readable format: {output_md}")
    
    # 2. JSON structure (hierarchical)
    json_content = parser.to_json()
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Structured JSON: {output_json}")
    
    # 3. Flat JSON for database/AI
    flat_bookmarks = parser.get_flat_bookmarks()
    with open(output_flat_json, 'w', encoding='utf-8') as f:
        json.dump(flat_bookmarks, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Flat JSON (for DB/AI): {output_flat_json}")
    
    print()
    print("=" * 60)
    print()
    print("✅ Done! Your bookmarks have been cleaned and formatted.")
    print()
    print("📊 Summary:")
    print(f"   • Total bookmarks: {parser.total_bookmarks}")
    print(f"   • Total folders: {parser.total_folders}")
    print()
    print("📁 Output files:")
    print(f"   • {output_md} - Easy to read")
    print(f"   • {output_json} - Full structure with folders")
    print(f"   • {output_flat_json} - Flat list for database/AI")


if __name__ == "__main__":
    main()
