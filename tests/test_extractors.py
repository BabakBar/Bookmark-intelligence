"""Tests for feature extractors"""

from pathlib import Path

import pytest

from bookmark_intelligence.extractors import DomainExtractor
from bookmark_intelligence.models import Bookmark


@pytest.fixture
def extractor():
    """Create DomainExtractor with config"""
    config_path = Path(__file__).parent.parent / "config" / "extractors.yaml"
    return DomainExtractor(config_path)


def test_extractor_loads_config(extractor):
    """Test extractor loads categories from config"""
    assert len(extractor.categories) > 0
    assert "code_repos" in extractor.categories
    assert "google_services" in extractor.categories


def test_infer_category_github(extractor):
    """Test category inference for GitHub"""
    assert extractor.infer_category("github.com") == "code_repos"


def test_infer_category_youtube(extractor):
    """Test category inference for YouTube"""
    assert extractor.infer_category("youtube.com") == "video"


def test_infer_category_uncategorized(extractor):
    """Test uncategorized domain"""
    assert extractor.infer_category("unknown-site.com") == "uncategorized"


def test_get_category_domains(extractor):
    """Test retrieving domains in a category"""
    code_repos = extractor.get_category_domains("code_repos")
    assert "github.com" in code_repos
    assert "gitlab.com" in code_repos


def test_get_all_categories(extractor):
    """Test retrieving all categories"""
    categories = extractor.get_all_categories()
    assert "code_repos" in categories
    assert "social" in categories
    assert "video" in categories


def test_extract_preserves_bookmark(extractor):
    """Test extract method preserves bookmark"""
    bookmark = Bookmark(
        url="https://github.com/test/repo",
        title="Test Repo",
        add_date=1698768000
    )

    result = extractor.extract(bookmark)
    assert result.url == bookmark.url
    assert result.title == bookmark.title
    assert result.domain == "github.com"
