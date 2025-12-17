"""Bookmark processing pipeline orchestrator"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
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

    def run_ai_processing(
        self,
        input_file: Optional[Path] = None,
        stage: str = "all",
        batch_id: Optional[str] = None
    ) -> None:
        """Run AI processing pipeline

        Args:
            input_file: Path to bookmarks_flat.json (uses latest if None)
            stage: Stage to run (embed, tag, cluster, all)
            batch_id: Resume from existing OpenAI batch job
        """
        from bookmark_intelligence.ai import (
            BookmarkClusterer,
            FolderRecommender,
            GPTTaggingService,
            OpenAIEmbeddingService,
            ProjectSuggester,
        )

        # Initialize AI config
        ai_config_path = Path("config/ai_settings.yaml")

        # Create output directory
        ai_dir = Path("data/ai")
        ai_dir.mkdir(parents=True, exist_ok=True)

        # Load bookmarks
        if input_file is None:
            input_file = self.processed_dir / "bookmarks_flat.json"

        if not input_file.exists():
            logger.error(f"Bookmarks file not found: {input_file}")
            logger.info("Run bookmark processing first: uv run scripts/process_bookmarks.py")
            return

        logger.info(f"Loading bookmarks from {input_file}")
        with open(input_file) as f:
            bookmarks = json.load(f)
        logger.info(f"Loaded {len(bookmarks)} bookmarks")

        start_time = datetime.now()

        # Stage 1: Embeddings
        if stage in ["embed", "all"]:
            logger.info("=" * 60)
            logger.info("STAGE 1: GENERATING EMBEDDINGS")
            logger.info("=" * 60)

            embedding_service = OpenAIEmbeddingService(ai_config_path)
            embeddings_path = ai_dir / "embeddings.npy"

            if batch_id:
                # Resume from existing batch
                logger.info(f"Resuming from batch: {batch_id}")
                embeddings = embedding_service.retrieve_batch_results(batch_id, embeddings_path)
            else:
                # Create new batch job
                batch_id = embedding_service.create_batch_job(bookmarks, ai_dir)
                logger.info(f"Batch job submitted: {batch_id}")
                logger.info("Waiting for completion (up to 24 hours)...")

                # Wait for completion
                embedding_service.wait_for_completion(batch_id)

                # Retrieve results
                embeddings = embedding_service.retrieve_batch_results(batch_id, embeddings_path)

            logger.info(f"✓ Embeddings saved: {embeddings_path}")
            logger.info(f"  Shape: {embeddings.shape}")

            # Estimate cost
            cost = embedding_service.estimate_cost(len(bookmarks))
            logger.info(f"  Estimated cost: ${cost:.2f}")

            if stage == "embed":
                logger.info("Embedding stage complete. Run with --stage tag to continue.")
                return

        # Stage 2: Tagging
        if stage in ["tag", "all"]:
            logger.info("=" * 60)
            logger.info("STAGE 2: TAGGING & SUMMARIZATION")
            logger.info("=" * 60)

            tagging_service = GPTTaggingService(ai_config_path)

            # Progress callback
            def progress(completed, total):
                if completed % 50 == 0 or completed == total:
                    logger.info(f"  Progress: {completed}/{total} ({100*completed/total:.1f}%)")

            # Run async tagging
            enrichments = asyncio.run(
                tagging_service.tag_batch(bookmarks, batch_size=50, progress_callback=progress)
            )

            # Merge enrichments with bookmarks
            for i, enrichment in enumerate(enrichments):
                bookmarks[i].update(enrichment)

            logger.info(f"✓ Tagged {len(bookmarks)} bookmarks")

            # Estimate cost
            cost = tagging_service.estimate_cost(len(bookmarks))
            logger.info(f"  Estimated cost: ${cost:.2f}")

            if stage == "tag":
                logger.info("Tagging stage complete. Run with --stage cluster to continue.")
                # Save intermediate results
                ai_bookmarks_path = ai_dir / "bookmarks_tagged.json"
                with open(ai_bookmarks_path, "w") as f:
                    json.dump(bookmarks, f, indent=2)
                logger.info(f"  Saved: {ai_bookmarks_path}")
                return

        # Stage 3: Clustering
        if stage in ["cluster", "all"]:
            logger.info("=" * 60)
            logger.info("STAGE 3: CLUSTERING")
            logger.info("=" * 60)

            # Load embeddings
            embeddings_path = ai_dir / "embeddings.npy"
            if not embeddings_path.exists():
                logger.error("Embeddings not found. Run --stage embed first.")
                return

            embeddings = np.load(embeddings_path)
            logger.info(f"Loaded embeddings: {embeddings.shape}")

            # Run clustering
            clusterer = BookmarkClusterer(ai_config_path)
            cluster_results = clusterer.cluster_bookmarks(embeddings, bookmarks)

            # Add cluster_id to bookmarks
            labels = cluster_results["labels"]
            for i, label in enumerate(labels):
                bookmarks[i]["cluster_id"] = int(label)
                # Find cluster name
                cluster_info = next(c for c in cluster_results["clusters"] if c["id"] == label)
                bookmarks[i]["cluster_name"] = cluster_info["name"]

            logger.info(f"✓ Created {cluster_results['n_clusters']} clusters")

            # Save cluster results
            clusters_path = ai_dir / "clusters.json"
            with open(clusters_path, "w") as f:
                json.dump(cluster_results, f, indent=2)
            logger.info(f"  Saved: {clusters_path}")

        # Stage 4: Project Suggestions
        if stage in ["all"]:
            logger.info("=" * 60)
            logger.info("STAGE 4: PROJECT SUGGESTIONS")
            logger.info("=" * 60)

            suggester = ProjectSuggester(ai_config_path)
            projects = suggester.suggest_projects(cluster_results, bookmarks)

            logger.info(f"✓ Generated {len(projects)} project suggestions")

            # Save projects
            projects_path = ai_dir / "projects_suggested.json"
            with open(projects_path, "w") as f:
                json.dump({"projects": projects}, f, indent=2)
            logger.info(f"  Saved: {projects_path}")

            # Stage 4.5: Folder Reorganization Recommendations
            logger.info("=" * 60)
            logger.info("STAGE 4.5: FOLDER REORGANIZATION")
            logger.info("=" * 60)

            folder_recommender = FolderRecommender()
            folder_analysis = folder_recommender.analyze_and_recommend(
                bookmarks,
                cluster_results
            )

            logger.info(f"✓ Analyzed folder structure")
            logger.info(f"  Current folders: {folder_analysis['current_analysis']['total_folders']}")
            logger.info(f"  Recommendations: {len(folder_analysis['reorganization_plan'])}")
            logger.info(f"  Issues found: {len(folder_analysis['issues'])}")
            logger.info(f"  Action items: {len(folder_analysis['action_items'])}")

            # Save folder analysis
            folder_analysis_path = ai_dir / "folder_recommendations.json"
            with open(folder_analysis_path, "w") as f:
                json.dump(folder_analysis, f, indent=2)
            logger.info(f"  Saved: {folder_analysis_path}")

        # Stage 5: Export AI Results
        logger.info("=" * 60)
        logger.info("STAGE 5: EXPORTING AI RESULTS")
        logger.info("=" * 60)

        # Save enriched bookmarks
        ai_bookmarks_path = ai_dir / "bookmarks_ai.json"
        total_cost = (
            OpenAIEmbeddingService(ai_config_path).estimate_cost(len(bookmarks)) +
            GPTTaggingService(ai_config_path).estimate_cost(len(bookmarks))
        )

        ai_output = {
            "generated_at": datetime.now().isoformat(),
            "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
            "total_cost_usd": round(total_cost, 2),
            "n_bookmarks": len(bookmarks),
            "n_clusters": cluster_results["n_clusters"],
            "bookmarks": bookmarks
        }

        with open(ai_bookmarks_path, "w") as f:
            json.dump(ai_output, f, indent=2)

        logger.info(f"✓ Saved AI results: {ai_bookmarks_path}")

        # Stage 6: Generate AI Report
        logger.info("=" * 60)
        logger.info("STAGE 6: GENERATING AI REPORT")
        logger.info("=" * 60)

        report_path = self.reports_dir / f"{datetime.now().strftime('%Y-%m-%d')}-ai-processing.md"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            f.write(f"# AI Processing Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Source:** {input_file.name}\n")
            f.write(f"**Processing time:** {(datetime.now() - start_time).total_seconds():.0f} seconds\n\n")

            f.write(f"## Summary\n\n")
            f.write(f"- **Total bookmarks:** {len(bookmarks)}\n")
            f.write(f"- **Clusters created:** {cluster_results['n_clusters']}\n")
            f.write(f"- **Projects suggested:** {len(projects) if 'projects' in locals() else 0}\n")
            f.write(f"- **Folder recommendations:** {len(folder_analysis['reorganization_plan']) if 'folder_analysis' in locals() else 0}\n")
            f.write(f"- **Issues identified:** {len(folder_analysis['issues']) if 'folder_analysis' in locals() else 0}\n")
            f.write(f"- **Total cost:** ${total_cost:.2f}\n\n")

            # Add folder reorganization section
            if "folder_analysis" in locals():
                f.write(f"## 📁 Folder Reorganization Recommendations\n\n")
                f.write(f"### Current State\n\n")
                summary = folder_analysis["summary"]
                f.write(f"- Total folders: {summary['current_state']['total_folders']}\n")
                f.write(f"- Top-level folders: {summary['current_state']['top_level_folders']}\n\n")

                f.write(f"### Issues Found ({summary['issues_found']['total']})\n\n")
                for issue in folder_analysis["issues"][:5]:
                    f.write(f"**{issue['type'].replace('_', ' ').title()}** ({issue['severity']})\n")
                    f.write(f"- {issue['description']}\n")
                    f.write(f"- Recommendation: {issue['recommendation']}\n\n")

                f.write(f"### Action Items\n\n")
                for i, action in enumerate(folder_analysis["action_items"][:5], 1):
                    f.write(f"{i}. **{action['title']}** (Priority: {action['priority']})\n")
                    f.write(f"   - {action['description']}\n")
                    f.write(f"   - Time: {action['estimated_time']}\n\n")

                f.write(f"### Top Reorganization Recommendations\n\n")
                for rec in folder_analysis["reorganization_plan"][:8]:
                    if rec["action"] == "create_folder":
                        f.write(f"**Create: `{rec['folder']}`**\n")
                        f.write(f"- Reason: {rec['reason']}\n")
                        f.write(f"- Bookmarks: {rec['bookmark_count']}\n\n")

            f.write(f"## Clusters\n\n")
            for cluster in cluster_results["clusters"][:10]:
                f.write(f"### {cluster['name']}\n\n")
                f.write(f"- **Size:** {cluster['size']} bookmarks\n")
                f.write(f"- **Keywords:** {', '.join(cluster['keywords'])}\n")
                f.write(f"- **Top domains:** {', '.join(cluster['top_domains'][:3])}\n\n")

            if "projects" in locals() and projects:
                f.write(f"## Suggested Projects\n\n")
                for proj in projects:
                    f.write(f"### {proj['name']}\n\n")
                    f.write(f"- **Description:** {proj['description']}\n")
                    f.write(f"- **Bookmarks:** {proj['bookmark_count']}\n")
                    f.write(f"- **Confidence:** {proj['confidence']:.2f}\n")
                    f.write(f"- **Keywords:** {', '.join(proj['keywords'])}\n\n")

        logger.info(f"✓ Report saved: {report_path}")

        logger.info("=" * 60)
        logger.info("AI PROCESSING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Total time: {(datetime.now() - start_time).total_seconds():.0f} seconds")
        logger.info(f"Total cost: ${total_cost:.2f}")
        logger.info(f"\nResults saved to: {ai_dir}")
        logger.info(f"Report: {report_path}")
