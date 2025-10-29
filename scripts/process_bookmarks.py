#!/usr/bin/env python3
"""CLI for bookmark processing pipeline

Usage:
    uv run scripts/process_bookmarks.py                     # Auto-discover latest file
    uv run scripts/process_bookmarks.py --input data/raw/bookmarks_29_10_2025.html
    uv run scripts/process_bookmarks.py --debug             # Enable DEBUG logging
"""

import logging
import sys
from pathlib import Path

import click

from bookmark_intelligence.pipeline import BookmarkProcessor


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    help="Path to HTML bookmark file (auto-discovers if not specified)"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default=Path("config/settings.yaml"),
    help="Path to settings YAML file"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable DEBUG logging"
)
def main(input: Path | None, config: Path, debug: bool) -> None:
    """Process bookmarks: parse, analyze, and generate reports"""

    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s - %(message)s"
    )

    try:
        # Initialize processor
        processor = BookmarkProcessor(config)

        # Run pipeline
        processor.run(input_file=input)

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        if debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
