"""Bookmark processing pipeline orchestrator"""

import logging
from pathlib import Path
from typing import Optional

import yaml

from bookmark_intelligence.analyzers import (
    analyze_domains,
    analyze_folder_activity,
    analyze_quality,
    generate_report,
)
from bookmark_intelligence.extractors import DomainExtractor
from bookmark_intelligence.parsers import BookmarkParser
from bookmark_intelligence.storage import save_flat, save_hierarchical, save_markdown

logger = logging.getLogger(__name__)


class BookmarkProcessor:
    """Orchestrates the full bookmark processing pipeline

    Stages:
    1. Discover - find latest HTML file in raw directory
    2. Parse - extract bookmarks and folders from HTML
    3. Extract - enrich with domain categories
    4. Analyze - generate insights
    5. Export - save in multiple formats
    6. Report - generate analysis report
    """

    def __init__(self, config_path: Path = Path("config/settings.yaml")):
        """Initialize processor with configuration

        Args:
            config_path: Path to settings YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()

        # Initialize paths
        self.raw_dir = Path(self.config["paths"]["raw"])
        self.processed_dir = Path(self.config["paths"]["processed"])
        self.reports_dir = Path(self.config["paths"]["reports"])

        # Initialize extractor
        extractor_config = Path("config/extractors.yaml")
        self.extractor = DomainExtractor(extractor_config)

    def _load_config(self) -> dict:
        """Load configuration from YAML"""
        if not self.config_path.exists():
            # Return defaults if config doesn't exist
            return {
                "paths": {
                    "raw": "data/raw",
                    "processed": "data/processed",
                    "reports": "data/reports"
                },
                "input": {
                    "pattern": "bookmarks_*.html",
                    "date_format": "%d_%m_%Y"
                },
                "output": {
                    "hierarchical": "bookmarks_clean.json",
                    "flat": "bookmarks_flat.json",
                    "markdown": "bookmarks_clean.md"
                }
            }

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def discover_input(self) -> Optional[Path]:
        """Find latest HTML file in raw directory

        Returns:
            Path to latest file, or None if no files found
        """
        if not self.raw_dir.exists():
            logger.warning(f"Raw directory does not exist: {self.raw_dir}")
            return None

        pattern = self.config["input"]["pattern"]
        files = sorted(self.raw_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No files matching {pattern} found in {self.raw_dir}")
            return None

        latest = files[0]
        logger.info(f"Discovered: {latest}")
        return latest

    def run(self, input_file: Optional[Path] = None) -> None:
        """Run the full processing pipeline

        Args:
            input_file: Optional path to HTML file. If None, auto-discovers latest.
        """
        # Stage 1: Discover
        if input_file is None:
            input_file = self.discover_input()
            if input_file is None:
                logger.error("No input file found. Aborting.")
                return
        else:
            logger.info(f"Using specified file: {input_file}")

        # Stage 2: Parse
        logger.info("Parsing HTML...")
        parser = BookmarkParser(input_file)
        parser.parse()
        logger.info(f"Parsed {parser.total_bookmarks} bookmarks in {parser.total_folders} folders")

        # Stage 3: Extract (domain already extracted in Bookmark.__init__)
        logger.info("Extracting features...")
        flat_bookmarks = parser.get_flat_bookmarks()
        logger.info(f"Domains extracted: {len(set(b['domain'] for b in flat_bookmarks if b.get('domain')))} unique domains")

        # Stage 4: Analyze
        logger.info("Analyzing...")
        domain_analysis = analyze_domains(flat_bookmarks, self.extractor)
        quality_analysis = analyze_quality(flat_bookmarks)
        folder_activity = analyze_folder_activity(parser.root_folders)
        logger.info("Analysis complete")

        # Stage 5: Export
        logger.info("Exporting...")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        hierarchical_path = self.processed_dir / self.config["output"]["hierarchical"]
        flat_path = self.processed_dir / self.config["output"]["flat"]
        markdown_path = self.processed_dir / self.config["output"]["markdown"]

        save_hierarchical(parser.to_json(), hierarchical_path)
        logger.info(f"Saved: {hierarchical_path}")

        save_flat(flat_bookmarks, flat_path)
        logger.info(f"Saved: {flat_path}")

        save_markdown(parser.to_markdown(), markdown_path)
        logger.info(f"Saved: {markdown_path}")

        # Stage 6: Report
        logger.info("Generating report...")
        report_path = generate_report(
            source_file=input_file.name,
            bookmarks=flat_bookmarks,
            folders=parser.root_folders,
            domain_analysis=domain_analysis,
            quality_analysis=quality_analysis,
            folder_activity=folder_activity,
            output_dir=self.reports_dir
        )
        logger.info(f"Report: {report_path}")

        logger.info("Done!")
