"""OpenAI Embedding Service using Batch API for cost optimization"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from openai import OpenAI
from openai.types.batch import Batch

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """Generate embeddings using OpenAI Batch API (50% cost savings)"""

    def __init__(self, config_path: Optional[Path] = None, api_key: Optional[str] = None):
        """Initialize embedding service

        Args:
            config_path: Path to ai_settings.yaml
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        """
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()

        # Load config
        if config_path and config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.embedding_model = config["openai"]["embedding_model"]
                self.dimensions = config["openai"]["dimensions"]
                self.batch_api_enabled = config["openai"]["batch_api_enabled"]
        else:
            # Defaults
            self.embedding_model = "text-embedding-3-small"
            self.dimensions = 1536
            self.batch_api_enabled = True

    def create_batch_job(self, bookmarks: List[Dict], output_dir: Path) -> str:
        """Submit batch embedding job to OpenAI

        Args:
            bookmarks: List of bookmark dicts with 'url', 'title', 'domain'
            output_dir: Directory to save batch input file

        Returns:
            batch_id: Job ID for polling
        """
        logger.info(f"Creating batch job for {len(bookmarks)} bookmarks")

        # Create JSONL batch file
        batch_input_path = output_dir / "batch_embeddings_input.jsonl"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(batch_input_path, "w") as f:
            for i, bookmark in enumerate(bookmarks):
                # Combine URL and title for embedding
                text = f"{bookmark['title']}\n{bookmark['url']}"

                request = {
                    "custom_id": f"bookmark-{i}",
                    "method": "POST",
                    "url": "/v1/embeddings",
                    "body": {
                        "model": self.embedding_model,
                        "input": text,
                        "dimensions": self.dimensions
                    }
                }
                f.write(json.dumps(request) + "\n")

        logger.info(f"Batch input file: {batch_input_path}")

        # Upload batch file
        with open(batch_input_path, "rb") as f:
            batch_file = self.client.files.create(
                file=f,
                purpose="batch"
            )

        # Create batch job
        batch = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/embeddings",
            completion_window="24h"
        )

        logger.info(f"Batch job created: {batch.id}")
        logger.info(f"Status: {batch.status}")
        logger.info(f"Completion window: 24 hours")

        # Save batch ID for resuming
        batch_id_path = output_dir / "batch_id.txt"
        with open(batch_id_path, "w") as f:
            f.write(batch.id)

        return batch.id

    def poll_batch_status(self, batch_id: str) -> Dict:
        """Check batch job status

        Returns:
            Dict with status info: {status, completed_at, failed_at, request_counts}
        """
        batch = self.client.batches.retrieve(batch_id)

        return {
            "status": batch.status,
            "completed_at": batch.completed_at,
            "failed_at": batch.failed_at,
            "request_counts": {
                "total": batch.request_counts.total,
                "completed": batch.request_counts.completed,
                "failed": batch.request_counts.failed
            }
        }

    def wait_for_completion(
        self,
        batch_id: str,
        poll_interval_seconds: int = 600,  # 10 minutes
        timeout_hours: int = 26
    ) -> Batch:
        """Poll batch job until complete or failed

        Args:
            batch_id: Batch job ID
            poll_interval_seconds: Seconds between status checks
            timeout_hours: Max hours to wait

        Returns:
            Completed Batch object
        """
        logger.info(f"Waiting for batch {batch_id} to complete...")
        logger.info(f"Polling every {poll_interval_seconds/60:.0f} minutes")

        start_time = time.time()
        timeout_seconds = timeout_hours * 3600

        while True:
            batch = self.client.batches.retrieve(batch_id)

            if batch.status == "completed":
                logger.info(f"Batch completed!")
                return batch
            elif batch.status == "failed":
                raise RuntimeError(f"Batch failed: {batch}")
            elif batch.status in ["expired", "cancelled"]:
                raise RuntimeError(f"Batch {batch.status}: {batch}")

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Batch timeout after {timeout_hours}h")

            # Log progress
            counts = batch.request_counts
            logger.info(
                f"Status: {batch.status} | "
                f"Progress: {counts.completed}/{counts.total} | "
                f"Elapsed: {elapsed/3600:.1f}h"
            )

            # Wait before next poll
            time.sleep(poll_interval_seconds)

    def retrieve_batch_results(self, batch_id: str, output_path: Path) -> np.ndarray:
        """Download and parse batch results

        Args:
            batch_id: Completed batch job ID
            output_path: Path to save embeddings.npy

        Returns:
            Numpy array of shape (n_bookmarks, dimensions)
        """
        logger.info(f"Retrieving batch results: {batch_id}")

        # Get batch info
        batch = self.client.batches.retrieve(batch_id)

        if batch.status != "completed":
            raise ValueError(f"Batch not completed: {batch.status}")

        if not batch.output_file_id:
            raise ValueError("No output file available")

        # Download results
        result_content = self.client.files.content(batch.output_file_id)
        result_lines = result_content.text.strip().split("\n")

        logger.info(f"Downloaded {len(result_lines)} results")

        # Parse embeddings
        embeddings = []
        for line in result_lines:
            result = json.loads(line)

            if result["response"]["status_code"] != 200:
                logger.error(f"Failed request: {result}")
                continue

            embedding = result["response"]["body"]["data"][0]["embedding"]
            custom_id = result["custom_id"]
            bookmark_idx = int(custom_id.split("-")[1])

            embeddings.append((bookmark_idx, embedding))

        # Sort by bookmark index
        embeddings.sort(key=lambda x: x[0])
        embedding_vectors = np.array([emb for _, emb in embeddings])

        # Save to numpy file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(output_path, embedding_vectors)

        logger.info(f"Saved {len(embeddings)} embeddings to {output_path}")
        logger.info(f"Shape: {embedding_vectors.shape}")

        return embedding_vectors

    def estimate_cost(self, num_bookmarks: int, avg_tokens: int = 500) -> float:
        """Estimate embedding cost

        Args:
            num_bookmarks: Number of bookmarks
            avg_tokens: Average tokens per bookmark (title + URL)

        Returns:
            Estimated cost in USD
        """
        total_tokens = num_bookmarks * avg_tokens

        # text-embedding-3-small: $0.020 per 1M tokens
        # Batch API: 50% discount
        base_cost_per_1m = 0.020
        batch_discount = 0.5 if self.batch_api_enabled else 1.0

        cost = (total_tokens / 1_000_000) * base_cost_per_1m * batch_discount

        return cost
