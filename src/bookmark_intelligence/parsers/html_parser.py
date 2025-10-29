"""HTML bookmark file parser"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from bs4 import BeautifulSoup, PageElement, Tag

from bookmark_intelligence.models import Bookmark, Folder

logger = logging.getLogger(__name__)


class BookmarkParser:
    """Parse HTML bookmark files exported from browsers

    Handles:
    - Nested folder structures
    - Bookmark metadata (URL, title, add_date, last_modified)
    - Malformed HTML (via html5lib parser)
    - Invalid URLs (file://, empty)
    """

    def __init__(self, html_file: Path):
        """Initialize parser with HTML file

        Args:
            html_file: Path to HTML bookmark export file
        """
        self.html_file = html_file
        logger.info(f"Loading bookmark file: {html_file}")

        with open(html_file, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html5lib')

        self.root_folders: List[Folder] = []
        self.root_bookmarks: List[Bookmark] = []
        self.total_bookmarks = 0
        self.total_folders = 0

    def parse(self) -> None:
        """Parse the bookmark HTML file

        Raises:
            ValueError: If no bookmark structure found in HTML
        """
        # Find the main DL (definition list) tag
        main_dl = self.soup.find('dl')
        if not main_dl:
            raise ValueError("No bookmark structure found in HTML file")

        logger.debug("Starting parse of main DL")
        self._parse_dl(main_dl, parent_path=[], level=0)

        logger.info(f"Parsed {self.total_bookmarks} bookmarks in {self.total_folders} folders")

    def _parse_dl(
        self,
        dl_tag: Tag,
        parent_path: List[str],
        current_folder: Optional[Folder] = None,
        level: int = 0
    ) -> None:
        """Recursively parse DL tags (bookmark lists)

        Args:
            dl_tag: BeautifulSoup DL tag to parse
            parent_path: List of parent folder names
            current_folder: Current folder being populated (if any)
            level: Recursion depth for logging
        """
        # Get only direct DT and DD children (not recursive)
        # NOTE: Because of HTML structure like <DL><p> where <p> is not self-closing,
        # BeautifulSoup nests subsequent content inside the P tag. So we need to check both:
        # 1. Direct DT/DD children of the DL
        # 2. DT/DD children nested inside P tags (could be nested deeper)
        all_children = list(dl_tag.children)
        logger.debug(f"Level {level}, dl_tag has {len(all_children)} total children")

        dt_children: List[Union[Tag, PageElement]] = []
        for child in all_children:
            if hasattr(child, 'name'):
                if child.name in ['dt', 'dd']:
                    dt_children.append(child)
                elif child.name == 'p':
                    # Check for DT/DD elements inside the P tag (try recursive first)
                    nested_dts = child.find_all(['dt', 'dd'], recursive=True)  # type: ignore[attr-defined]
                    if nested_dts and level == 1:
                        logger.debug(f"Found {len(nested_dts)} DT/DD elements inside P tag (recursive)")
                        # Check first few to see their structure
                        for i, dt in enumerate(nested_dts[:3]):
                            parent_chain = [dt.name]
                            p = dt.parent
                            while p and p != child:
                                parent_chain.insert(0, p.name)
                                p = p.parent
                            logger.debug(f"DT #{i} parent chain: {' > '.join(parent_chain)}")
                    dt_children.extend(nested_dts)

        logger.debug(f"Level {level}, found {len(dt_children)} total DT/DD children")

        for i, child in enumerate(dt_children):
            logger.debug(f"Processing child {i+1}/{len(dt_children)}: {child.name}")  # type: ignore[attr-defined]

            if child.name == 'dt':  # type: ignore[attr-defined]
                # Check if it's a folder (H3) or bookmark (A)
                h3 = child.find('h3', recursive=False)  # type: ignore[attr-defined]
                a_tag = child.find('a', recursive=False)  # type: ignore[attr-defined]

                if h3:
                    # It's a folder
                    folder_name = h3.get_text().strip()
                    last_modified_str = h3.get('last_modified')  # BeautifulSoup normalizes to lowercase
                    last_modified = int(last_modified_str) if last_modified_str else None
                    logger.debug(f"Found folder: {folder_name}")
                    folder = Folder(folder_name, parent_path, last_modified)

                    # Look for the nested DL - check CHILD first, then sibling
                    nested_dl = child.find('dl', recursive=False)  # type: ignore[attr-defined]  # Check if DL is a direct child of this DT
                    if not nested_dl:
                        nested_dl = child.find_next_sibling('dl')  # Fall back to sibling

                    if nested_dl:
                        logger.debug(f"Found nested DL for folder {folder_name}, recursing...")
                        self._parse_dl(nested_dl, folder.full_path, folder, level + 1)
                        logger.debug(f"Returned from nested DL for folder {folder_name}")
                    else:
                        logger.debug(f"NO nested DL found for folder {folder_name}")

                    if current_folder:
                        current_folder.subfolders.append(folder)
                    else:
                        self.root_folders.append(folder)

                    self.total_folders += 1

                elif a_tag:
                    # It's a bookmark
                    url = a_tag.get('href', '')
                    title = a_tag.get_text().strip()
                    add_date_str = a_tag.get('add_date')
                    add_date = int(add_date_str) if add_date_str else None

                    # Skip empty URLs or file:// URLs
                    if not url or url.startswith('file://'):
                        logger.debug(f"SKIPPED bookmark (empty or file://): {title[:50]}...")
                        continue

                    logger.debug(f"Found bookmark: {title[:80]}...")
                    bookmark = Bookmark(url, title, add_date, parent_path)

                    if current_folder:
                        current_folder.bookmarks.append(bookmark)
                    else:
                        self.root_bookmarks.append(bookmark)

                    self.total_bookmarks += 1
                else:
                    logger.debug("DT with no H3 or A tag found!")

        logger.debug(f"EXITING _parse_dl at level {level}")

    def to_json(self) -> Dict[str, Any]:
        """Convert all bookmarks to JSON structure

        Returns:
            Dict with metadata, folders, and root bookmarks
        """
        return {
            "metadata": {
                "source_file": str(self.html_file.name),
                "parsed_at": datetime.now().isoformat(),
                "total_bookmarks": self.total_bookmarks,
                "total_folders": self.total_folders
            },
            "folders": [f.to_dict() for f in self.root_folders],
            "root_bookmarks": [b.to_dict() for b in self.root_bookmarks]
        }

    def to_markdown(self) -> str:
        """Convert all bookmarks to Markdown format

        Returns:
            Markdown string with folder hierarchy
        """
        lines = [
            "# Bookmarks",
            "",
            f"*Parsed from: {self.html_file.name}*",
            f"*Total Bookmarks: {self.total_bookmarks} | Folders: {self.total_folders}*",
            "",
            "---",
            ""
        ]

        if self.root_bookmarks:
            lines.append("## Root Bookmarks")
            lines.append("")
            for bookmark in self.root_bookmarks:
                lines.append(bookmark.to_markdown())
            lines.append("")

        for folder in self.root_folders:
            lines.append(folder.to_markdown())
            lines.append("")

        return "\n".join(lines)

    def get_flat_bookmarks(self) -> List[Dict[str, Any]]:
        """Get a flat list of all bookmarks for AI/database use

        Returns:
            List of bookmark dictionaries (no folder hierarchy)
        """
        bookmarks: List[Dict[str, Any]] = []

        # Add root bookmarks
        for bookmark in self.root_bookmarks:
            bookmarks.append(bookmark.to_dict())

        # Recursively add bookmarks from folders
        def collect_bookmarks(folder: Folder):
            for bookmark in folder.bookmarks:
                bookmarks.append(bookmark.to_dict())
            for subfolder in folder.subfolders:
                collect_bookmarks(subfolder)

        for folder in self.root_folders:
            collect_bookmarks(folder)

        return bookmarks
