"""JSON storage operations for bookmarks"""

import json
from pathlib import Path
from typing import Any, Dict, List


def save_hierarchical(data: Dict[str, Any], output_path: Path) -> None:
    """Save hierarchical bookmark structure to JSON

    Args:
        data: Hierarchical bookmark data (from parser.to_json())
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_flat(bookmarks: List[Dict[str, Any]], output_path: Path) -> None:
    """Save flat bookmark list to JSON

    Args:
        bookmarks: Flat list of bookmark dictionaries
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)


def save_markdown(content: str, output_path: Path) -> None:
    """Save markdown content to file

    Args:
        content: Markdown content string
        output_path: Path to output markdown file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
