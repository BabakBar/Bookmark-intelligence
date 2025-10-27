import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag


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
        
    def to_dict(self) -> Dict:
        """Convert bookmark to dictionary format"""
        data = {
            "url": self.url,
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
    
    def __init__(self, name: str, parent_path: Optional[List[str]] = None):
        self.name = name
        self.parent_path = parent_path or []
        self.bookmarks: List[Bookmark] = []
        self.subfolders: List['Folder'] = []
        
    @property
    def full_path(self) -> List[str]:
        """Get the full path of this folder"""
        return self.parent_path + [self.name]
    
    def to_dict(self) -> Dict:
        """Convert folder to dictionary format"""
        return {
            "name": self.name,
            "path": " > ".join(self.full_path),
            "bookmark_count": len(self.bookmarks),
            "subfolder_count": len(self.subfolders),
            "bookmarks": [b.to_dict() for b in self.bookmarks],
            "subfolders": [f.to_dict() for f in self.subfolders]
        }
    
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


class BookmarkParser:
    """Parse HTML bookmark files"""
    
    def __init__(self, html_file: Path):
        self.html_file = html_file
        with open(html_file, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html5lib')
        
        self.root_folders: List[Folder] = []
        self.root_bookmarks: List[Bookmark] = []
        self.total_bookmarks = 0
        self.total_folders = 0
        
    def parse(self):
        """Parse the bookmark HTML file"""
        # Find the main DL (definition list) tag
        main_dl = self.soup.find('dl')
        if not main_dl:
            raise ValueError("No bookmark structure found in HTML file")
        
        print("DEBUG: Starting parse of main DL")
        self._parse_dl(main_dl, parent_path=[], level=0)
        
        print(f"✓ Parsed {self.total_bookmarks} bookmarks in {self.total_folders} folders")
    
    def _parse_dl(self, dl_tag: Tag, parent_path: List[str], current_folder: Optional[Folder] = None, level: int = 0):
        """Recursively parse DL tags (bookmark lists)"""
        indent = "  " * level
        
        # Get only direct DT and DD children (not recursive)
        # NOTE: Because of HTML structure like <DL><p> where <p> is not self-closing,
        # BeautifulSoup nests subsequent content inside the P tag. So we need to check both:
        # 1. Direct DT/DD children of the DL
        # 2. DT/DD children nested inside P tags (could be nested deeper)
        all_children = list(dl_tag.children)
        print(f"{indent}DEBUG: Level {level}, dl_tag has {len(all_children)} total children")
        
        dt_children = []
        for child in all_children:
            if hasattr(child, 'name'):
                if child.name in ['dt', 'dd']:
                    dt_children.append(child)
                elif child.name == 'p':
                    # Check for DT/DD elements inside the P tag (try recursive first)
                    nested_dts = child.find_all(['dt', 'dd'], recursive=True)
                    if nested_dts and level == 1:
                        print(f"{indent}DEBUG: Found {len(nested_dts)} DT/DD elements inside P tag (recursive)")
                        # Check first few to see their structure
                        for i, dt in enumerate(nested_dts[:3]):
                            parent_chain = [dt.name]
                            p = dt.parent
                            while p and p != child:
                                parent_chain.insert(0, p.name)
                                p = p.parent
                            print(f"{indent}DEBUG:   DT #{i} parent chain: {' > '.join(parent_chain)}")
                    dt_children.extend(nested_dts)
        
        print(f"{indent}DEBUG: Level {level}, found {len(dt_children)} total DT/DD children")
        
        for i, child in enumerate(dt_children):
            print(f"{indent}DEBUG: Processing child {i+1}/{len(dt_children)}: {child.name}")
            if child.name == 'dt':
                # Check if it's a folder (H3) or bookmark (A)
                h3 = child.find('h3', recursive=False)
                a_tag = child.find('a', recursive=False)
                
                if h3:
                    # It's a folder
                    folder_name = h3.get_text().strip()
                    print(f"{indent}DEBUG: Found folder: {folder_name}")
                    folder = Folder(folder_name, parent_path)
                    
                    # Look for the nested DL - check CHILD first, then sibling
                    nested_dl = child.find('dl', recursive=False)  # Check if DL is a direct child of this DT
                    if not nested_dl:
                        nested_dl = child.find_next_sibling('dl')  # Fall back to sibling
                    
                    if nested_dl:
                        print(f"{indent}DEBUG: Found nested DL for folder {folder_name}, recursing...")
                        self._parse_dl(nested_dl, folder.full_path, folder, level + 1)
                        print(f"{indent}DEBUG: Returned from nested DL for folder {folder_name}")
                    else:
                        print(f"{indent}DEBUG: NO nested DL found for folder {folder_name}")
                    
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
                        print(f"{indent}DEBUG: SKIPPED bookmark (empty or file://): {title[:50]}...")
                        continue
                    
                    print(f"{indent}DEBUG: Found bookmark: {title[:80]}...")
                    bookmark = Bookmark(url, title, add_date, parent_path)
                    
                    if current_folder:
                        current_folder.bookmarks.append(bookmark)
                    else:
                        self.root_bookmarks.append(bookmark)
                    
                    self.total_bookmarks += 1
                else:
                    print(f"{indent}DEBUG: DT with no H3 or A tag found!")
        
        print(f"{indent}DEBUG: EXITING _parse_dl at level {level}")
    
    def to_json(self) -> Dict:
        """Convert all bookmarks to JSON structure"""
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
        """Convert all bookmarks to Markdown format"""
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
    
    def get_flat_bookmarks(self) -> List[Dict]:
        """Get a flat list of all bookmarks for AI/database use"""
        bookmarks = []
        
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


def main():
    """Main function to clean bookmarks"""
    
    # Input and output paths
    input_file = Path("bookmarks_10_27_25.html")
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
