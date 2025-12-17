"""GPT Tagging Service for bookmark analysis and summarization"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class GPTTaggingService:
    """Generate tags and summaries using GPT-5.2"""

    def __init__(self, config_path: Optional[Path] = None, api_key: Optional[str] = None):
        """Initialize tagging service

        Args:
            config_path: Path to ai_settings.yaml
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        """
        self.client = AsyncOpenAI(api_key=api_key) if api_key else AsyncOpenAI()

        # Load config
        if config_path and config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.model = config["openai"]["tagging_model"]
                self.max_tokens = config["openai"]["max_tokens"]
                self.temperature = config["openai"]["temperature"]
        else:
            # Defaults
            self.model = "gpt-5.2"
            self.max_tokens = 200
            self.temperature = 0.3

    def build_prompt(self, bookmark: Dict) -> str:
        """Construct comprehensive tagging prompt

        Args:
            bookmark: Dict with 'url', 'title', 'domain', 'folder_path'

        Returns:
            Prompt string
        """
        folder_path = bookmark.get('folder_path', 'Unknown')
        if isinstance(folder_path, list):
            folder_path = ' > '.join(folder_path)

        return f"""Analyze this bookmark comprehensively and extract maximum insights.

Bookmark:
- URL: {bookmark['url']}
- Title: {bookmark['title']}
- Domain: {bookmark['domain']}
- Current folder: {folder_path}

Generate detailed JSON analysis with these fields:

1. "tags": Array of 5-10 specific, actionable tags (lowercase, hyphenated)
   - Include: technology stack, use case, topic area, skill level
   - Examples: "docker-compose", "python-testing", "aws-lambda", "beginner-friendly", "production-ready"

2. "summary": 3-4 sentence detailed summary
   - What is this resource?
   - What problem does it solve?
   - Who is it for?
   - Why is it valuable?

3. "content_type": One of: tutorial, documentation, tool, article, reference, video, course, blog-post, repository, cheatsheet, example-code, other

4. "primary_technology": Main technology/platform (e.g., "Docker", "Python", "AWS", "React", "PostgreSQL")

5. "skill_level": One of: beginner, intermediate, advanced, expert, mixed

6. "use_cases": Array of 2-4 specific use cases (e.g., ["container orchestration", "ci-cd pipeline", "development environment"])

7. "key_topics": Array of 3-5 main topics covered (e.g., ["networking", "volume management", "multi-stage builds"])

8. "value_proposition": One sentence explaining why this bookmark is worth keeping

9. "folder_recommendation": Suggest best folder structure for this bookmark
   - Use format: "Category > Subcategory" or "Category > Tech > Specific"
   - Examples: "Development > Docker", "Learning > Python > Testing", "Work > Infrastructure"

10. "priority": How important/useful is this? (high, medium, low)
    - high: Essential reference, frequently needed
    - medium: Useful occasionally
    - low: Nice to have, rarely accessed

11. "related_keywords": Array of 3-5 keywords for semantic search (beyond tags)

12. "actionability": What can you DO with this resource? (e.g., "implement in production", "follow tutorial", "reference when debugging", "learn fundamentals")

Guidelines:
- Be specific and technical
- Focus on practical value
- Consider the user's context (they saved this for a reason)
- Folder recommendations should create a logical, searchable hierarchy

Output ONLY valid JSON, no markdown:
{{
  "tags": ["tag1", "tag2", ...],
  "summary": "...",
  "content_type": "...",
  "primary_technology": "...",
  "skill_level": "...",
  "use_cases": ["...", "..."],
  "key_topics": ["...", "..."],
  "value_proposition": "...",
  "folder_recommendation": "...",
  "priority": "...",
  "related_keywords": ["...", "..."],
  "actionability": "..."
}}"""

    async def tag_bookmark(self, bookmark: Dict) -> Dict:
        """Generate tags and summary for single bookmark

        Args:
            bookmark: Dict with 'url', 'title', 'domain'

        Returns:
            Dict with 'tags', 'summary', 'content_type'
        """
        prompt = self.build_prompt(bookmark)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing and summarizing web resources. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Ensure ALL 12 fields are present with valid values
            defaults = {
                "tags": [],
                "summary": "",
                "content_type": "other",
                "primary_technology": "Unknown",
                "skill_level": "mixed",
                "use_cases": [],
                "key_topics": [],
                "value_proposition": "Bookmark saved for future reference",
                "folder_recommendation": "Uncategorized",
                "priority": "medium",
                "related_keywords": [],
                "actionability": "Review and categorize"
            }

            # Fill missing fields
            missing_fields = []
            for field, default in defaults.items():
                if field not in result or not result[field]:
                    result[field] = default
                    missing_fields.append(field)

            if missing_fields:
                logger.warning(f"Filled {len(missing_fields)} missing fields for {bookmark.get('url', 'unknown')}: {missing_fields}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {bookmark['url']}: {e}")
            # Fallback to basic tags
            return self._fallback_tags(bookmark)

        except Exception as e:
            logger.error(f"Tagging error for {bookmark['url']}: {e}")
            return self._fallback_tags(bookmark)

    def _fallback_tags(self, bookmark: Dict) -> Dict:
        """Generate basic tags when API fails

        Uses domain and title keywords
        """
        domain = bookmark.get("domain", "unknown")
        title_lower = bookmark.get("title", "").lower()

        # Basic domain-based tags
        domain_parts = domain.split(".")
        tags = [domain_parts[0]] if len(domain_parts) > 1 else [domain]

        # Add common keywords
        keywords = ["docker", "kubernetes", "python", "javascript", "aws", "azure", "api", "tutorial", "guide"]
        for keyword in keywords:
            if keyword in title_lower or keyword in domain.lower():
                tags.append(keyword)

        return {
            "tags": tags[:5],
            "summary": f"Resource from {domain}: {bookmark.get('title', 'Untitled')}",
            "content_type": "other",
            "primary_technology": "Unknown",
            "skill_level": "mixed",
            "use_cases": [],
            "key_topics": [],
            "value_proposition": "Bookmark saved for future reference",
            "folder_recommendation": "Uncategorized > Misc",
            "priority": "medium",
            "related_keywords": tags[:3],
            "actionability": "Review and categorize"
        }

    async def tag_batch(
        self,
        bookmarks: List[Dict],
        batch_size: int = 50,
        progress_callback: Optional[callable] = None
    ) -> List[Dict]:
        """Process bookmarks in parallel batches

        Args:
            bookmarks: List of bookmark dicts
            batch_size: Max concurrent requests
            progress_callback: Optional function(completed, total)

        Returns:
            List of enrichment results (same order as input)
        """
        logger.info(f"Tagging {len(bookmarks)} bookmarks with batch_size={batch_size}")

        semaphore = asyncio.Semaphore(batch_size)
        results = []

        async def tag_with_semaphore(idx: int, bookmark: Dict) -> tuple:
            async with semaphore:
                result = await self.tag_bookmark(bookmark)
                if progress_callback:
                    progress_callback(idx + 1, len(bookmarks))
                return (idx, result)

        # Create tasks
        tasks = [
            tag_with_semaphore(i, bookmark)
            for i, bookmark in enumerate(bookmarks)
        ]

        # Execute with progress tracking
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        for item in completed_tasks:
            if isinstance(item, Exception):
                logger.error(f"Task failed: {item}")
                results.append((None, self._fallback_tags({})))
            else:
                results.append(item)

        # Sort by original index
        results.sort(key=lambda x: x[0] if x[0] is not None else 999999)

        logger.info(f"Completed tagging {len(results)} bookmarks")

        return [result for _, result in results]

    def estimate_cost(self, num_bookmarks: int, avg_input_tokens: int = 800, avg_output_tokens: int = 400) -> float:
        """Estimate tagging cost

        Args:
            num_bookmarks: Number of bookmarks
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per response

        Returns:
            Estimated cost in USD
        """
        # GPT-5.2 pricing (assuming similar to gpt-4o for now)
        # Input: $2.50 per 1M tokens
        # Output: $10.00 per 1M tokens
        input_cost_per_1m = 2.50
        output_cost_per_1m = 10.00

        input_cost = (num_bookmarks * avg_input_tokens / 1_000_000) * input_cost_per_1m
        output_cost = (num_bookmarks * avg_output_tokens / 1_000_000) * output_cost_per_1m

        total_cost = input_cost + output_cost

        return total_cost
