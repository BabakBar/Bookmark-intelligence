"""Bookmark and Folder data models"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class Bookmark:
    """Represents a single bookmark entry"""

    def __init__(
        self,
        url: str,
        title: str,
        add_date: Optional[int] = None,
        folder_path: Optional[List[str]] = None
    ):
        self.url = url
        self.title = title
        self.add_date = add_date
        self.folder_path = folder_path or []
        self.domain = self._extract_domain(url)

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract and normalize domain from URL

        Handles:
        - Standard URLs (http/https)
        - Malformed URLs
        - Missing schemes
        - Strips www. prefix for normalization
        """
        if not url:
            return ""

        try:
            # Handle URLs without scheme
            if not url.startswith(('http://', 'https://', 'ftp://')):
                url = 'https://' + url

            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Normalize: remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]

            return domain
        except Exception:
            # Fallback: return empty string for invalid URLs
            return ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert bookmark to dictionary format"""
        data: Dict[str, Any] = {
            "url": self.url,
            "domain": self.domain,
            "title": self.title,
            "folder_path": " > ".join(self.folder_path) if self.folder_path else "Root",
        }

        if self.add_date:
            # Convert Unix timestamp to readable date
            data["added_date"] = datetime.fromtimestamp(self.add_date).isoformat()
            data["added_timestamp"] = self.add_date

        return data

    def to_markdown(self, indent_level: int = 0) -> str:
        """Convert bookmark to Markdown format"""
        indent = "  " * indent_level

        date_str = ""
        if self.add_date:
            date_str = f" (Added: {datetime.fromtimestamp(self.add_date).strftime('%Y-%m-%d')})"

        return f"{indent}- [{self.title}]({self.url}){date_str}"


class Folder:
    """Represents a bookmark folder"""

    def __init__(
        self,
        name: str,
        parent_path: Optional[List[str]] = None,
        last_modified: Optional[int] = None
    ):
        self.name = name
        self.parent_path = parent_path or []
        self.last_modified = last_modified
        self.bookmarks: List[Bookmark] = []
        self.subfolders: List['Folder'] = []

    @property
    def full_path(self) -> List[str]:
        """Get the full path of this folder"""
        return self.parent_path + [self.name]

    def to_dict(self) -> Dict[str, Any]:
        """Convert folder to dictionary format"""
        data: Dict[str, Any] = {
            "name": self.name,
            "path": " > ".join(self.full_path),
            "bookmark_count": len(self.bookmarks),
            "subfolder_count": len(self.subfolders),
            "bookmarks": [b.to_dict() for b in self.bookmarks],
            "subfolders": [f.to_dict() for f in self.subfolders]
        }

        if self.last_modified:
            data["last_modified_date"] = datetime.fromtimestamp(self.last_modified).isoformat()
            data["last_modified_timestamp"] = self.last_modified

        return data

    def to_markdown(self, indent_level: int = 0) -> str:
        """Convert folder to Markdown format"""
        indent = "  " * indent_level
        lines = [f"{indent}## {self.name}"]

        if self.bookmarks:
            lines.append("")
            for bookmark in self.bookmarks:
                lines.append(bookmark.to_markdown(indent_level))

        if self.subfolders:
            for subfolder in self.subfolders:
                lines.append("")
                lines.append(subfolder.to_markdown(indent_level + 1))

        return "\n".join(lines)
