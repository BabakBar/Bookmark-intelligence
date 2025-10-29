"""Bookmark feature extractors

All extractors follow the BaseExtractor interface and can be chained
to enrich bookmark data with additional features.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

import yaml

from bookmark_intelligence.models import Bookmark


class BaseExtractor(ABC):
    """Base class for bookmark feature extractors"""

    @abstractmethod
    def extract(self, bookmark: Bookmark) -> Bookmark:
        """Extract features from a bookmark

        Args:
            bookmark: Bookmark to process

        Returns:
            Bookmark with enriched data
        """
        pass


class DomainExtractor(BaseExtractor):
    """Extract and categorize domains from bookmark URLs

    Handles:
    - Domain extraction (already done in Bookmark.__init__)
    - Domain categorization based on config rules
    - www. normalization
    """

    def __init__(self, config_path: Path = Path("config/extractors.yaml")):
        """Initialize domain extractor

        Args:
            config_path: Path to extractors configuration file
        """
        self.config_path = config_path
        self.categories: Dict[str, List[str]] = {}
        self.domain_to_category: Dict[str, str] = {}

        if config_path.exists():
            self._load_config()

    def _load_config(self) -> None:
        """Load domain categories from YAML config"""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)

        domain_config = config.get("domain", {})
        self.categories = domain_config.get("categories", {})

        # Build reverse mapping: domain -> category
        for category, domains in self.categories.items():
            for domain in domains:
                self.domain_to_category[domain.lower()] = category

    def extract(self, bookmark: Bookmark) -> Bookmark:
        """Extract domain features (already extracted in Bookmark.__init__)

        Args:
            bookmark: Bookmark to process

        Returns:
            Same bookmark (domain already extracted)
        """
        # Domain extraction happens in Bookmark.__init__ via _extract_domain()
        # This method is a no-op but maintains interface consistency
        return bookmark

    def infer_category(self, domain: str) -> str:
        """Infer category for a domain based on config

        Args:
            domain: Domain to categorize

        Returns:
            Category name or "uncategorized"
        """
        return self.domain_to_category.get(domain.lower(), "uncategorized")

    def get_category_domains(self, category: str) -> List[str]:
        """Get all domains in a category

        Args:
            category: Category name

        Returns:
            List of domains in category
        """
        return self.categories.get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get list of all configured categories

        Returns:
            List of category names
        """
        return list(self.categories.keys())
