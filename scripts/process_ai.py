#!/usr/bin/env python3
"""CLI for AI bookmark processing

Usage:
    uv run scripts/process_ai.py                    # Run all stages
    uv run scripts/process_ai.py --stage embed      # Submit embedding batch job
    uv run scripts/process_ai.py --stage tag        # Run tagging (after embeddings)
    uv run scripts/process_ai.py --stage cluster    # Run clustering
    uv run scripts/process_ai.py --batch-id batch_xxx  # Resume from batch job
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
    help="Path to bookmarks_flat.json (uses data/processed/bookmarks_flat.json if not specified)"
)
@click.option(
    "--stage",
    "-s",
    type=click.Choice(["embed", "tag", "cluster", "all"]),
    default="all",
    help="Processing stage to run"
)
@click.option(
    "--batch-id",
    "-b",
    type=str,
    help="Resume from existing OpenAI batch job ID"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable DEBUG logging"
)
def main(input: Path | None, stage: str, batch_id: str | None, debug: bool) -> None:
    """Run AI processing on bookmarks

    This command processes bookmarks through:
    1. Embedding generation (OpenAI Batch API)
    2. Tagging & summarization (GPT-5.2)
    3. Clustering (MiniBatchKMeans)
    4. Project suggestions

    The pipeline can be run in stages or all at once.
    """

    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s - %(message)s"
    )

    try:
        # Initialize processor
        processor = BookmarkProcessor()

        # Run AI processing
        processor.run_ai_processing(
            input_file=input,
            stage=stage,
            batch_id=batch_id
        )

    except Exception as e:
        logging.error(f"AI processing failed: {e}")
        if debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
