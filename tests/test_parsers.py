"""Tests for HTML bookmark parser"""

import logging
from pathlib import Path

import pytest

from bookmark_intelligence.parsers import BookmarkParser

# Disable logging during tests
logging.disable(logging.CRITICAL)


@pytest.fixture
def sample_html_path():
    """Path to sample bookmarks HTML fixture"""
    return Path(__file__).parent / "fixtures" / "sample_bookmarks.html"


@pytest.fixture
def parser(sample_html_path):
    """Create parser instance with sample HTML"""
    return BookmarkParser(sample_html_path)


def test_parser_initialization(sample_html_path):
    """Test parser initializes correctly"""
    parser = BookmarkParser(sample_html_path)
    assert parser.html_file == sample_html_path
    assert parser.soup is not None
    assert parser.total_bookmarks == 0
    assert parser.total_folders == 0


def test_parser_basic_parsing(parser):
    """Test basic parsing of bookmarks and folders"""
    parser.parse()

    # Should have parsed 7 valid bookmarks (2 skipped: file:// and empty)
    # 2 in Dev Tools, 2 in Dev Tools>Python, 2 in Social, 1 at root
    assert parser.total_bookmarks == 7

    # Should have 3 folders: Dev Tools, Python (nested), Social
    assert parser.total_folders == 3


def test_parser_nested_folders(parser):
    """Test nested folder structure is preserved"""
    parser.parse()

    # Find Dev Tools folder
    dev_folder = None
    for folder in parser.root_folders:
        if folder.name == "Dev Tools":
            dev_folder = folder
            break

    assert dev_folder is not None
    assert len(dev_folder.bookmarks) == 2  # GitHub repos
    assert len(dev_folder.subfolders) == 1  # Python subfolder

    # Check nested Python folder
    python_folder = dev_folder.subfolders[0]
    assert python_folder.name == "Python"
    assert len(python_folder.bookmarks) == 2  # Python docs and PyPI


def test_parser_bookmark_metadata(parser):
    """Test bookmark metadata is extracted correctly"""
    parser.parse()

    # Find the Claude Code bookmark
    dev_folder = next(f for f in parser.root_folders if f.name == "Dev Tools")
    claude_bookmark = dev_folder.bookmarks[0]

    assert claude_bookmark.url == "https://github.com/anthropics/claude-code"
    assert claude_bookmark.title == "Claude Code Repository"
    assert claude_bookmark.add_date == 1698768000
    assert claude_bookmark.domain == "github.com"
    assert claude_bookmark.folder_path == ["Dev Tools"]


def test_parser_domain_normalization(parser):
    """Test domain extraction normalizes www prefix"""
    parser.parse()

    # Find Linux kernel bookmark (has www.)
    dev_folder = next(f for f in parser.root_folders if f.name == "Dev Tools")
    linux_bookmark = dev_folder.bookmarks[1]

    # www. should be stripped
    assert linux_bookmark.domain == "github.com"
    assert not linux_bookmark.domain.startswith("www.")


def test_parser_skips_invalid_urls(parser):
    """Test parser skips file:// and empty URLs"""
    parser.parse()

    # Collect all bookmark URLs
    all_bookmarks = parser.get_flat_bookmarks()
    urls = [b["url"] for b in all_bookmarks]

    # Should not contain file:// or empty URLs
    assert not any(url.startswith("file://") for url in urls)
    assert not any(url == "" for url in urls)


def test_parser_folder_metadata(parser):
    """Test folder metadata (last_modified) is extracted"""
    parser.parse()

    dev_folder = next(f for f in parser.root_folders if f.name == "Dev Tools")

    assert dev_folder.last_modified == 1698854400
    assert dev_folder.full_path == ["Dev Tools"]


def test_parser_to_json(parser):
    """Test JSON export structure"""
    parser.parse()
    json_data = parser.to_json()

    assert "metadata" in json_data
    assert "folders" in json_data
    assert "root_bookmarks" in json_data

    assert json_data["metadata"]["total_bookmarks"] == 7
    assert json_data["metadata"]["total_folders"] == 3
    assert json_data["metadata"]["source_file"] == "sample_bookmarks.html"


def test_parser_to_markdown(parser):
    """Test Markdown export generates valid output"""
    parser.parse()
    markdown = parser.to_markdown()

    assert "# Bookmarks" in markdown
    assert "Dev Tools" in markdown
    assert "Claude Code Repository" in markdown
    assert "Python" in markdown


def test_parser_get_flat_bookmarks(parser):
    """Test flat bookmark list generation"""
    parser.parse()
    flat_bookmarks = parser.get_flat_bookmarks()

    assert len(flat_bookmarks) == 7

    # Check structure of first bookmark
    assert "url" in flat_bookmarks[0]
    assert "domain" in flat_bookmarks[0]
    assert "title" in flat_bookmarks[0]
    assert "folder_path" in flat_bookmarks[0]


def test_parser_empty_file():
    """Test parser raises error on invalid HTML"""
    empty_file = Path(__file__).parent / "fixtures" / "empty.html"
    empty_file.parent.mkdir(exist_ok=True)
    empty_file.write_text("<html><body></body></html>")

    parser = BookmarkParser(empty_file)

    with pytest.raises(ValueError, match="No bookmark structure found"):
        parser.parse()

    # Cleanup
    empty_file.unlink()
