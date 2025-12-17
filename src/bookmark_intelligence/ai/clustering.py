"""Bookmark clustering using MiniBatchKMeans"""

import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)


class BookmarkClusterer:
    """Cluster bookmarks using embeddings"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize clusterer

        Args:
            config_path: Path to ai_settings.yaml
        """
        # Load config
        if config_path and config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.min_clusters = config["clustering"]["min_clusters"]
                self.max_clusters = config["clustering"]["max_clusters"]
                self.batch_size = config["clustering"]["batch_size"]
                self.random_state = config["clustering"]["random_state"]
        else:
            # Defaults
            self.min_clusters = 8
            self.max_clusters = 15
            self.batch_size = 100
            self.random_state = 42

    def determine_optimal_k(self, embeddings: np.ndarray) -> int:
        """Find optimal number of clusters using elbow method

        Args:
            embeddings: Numpy array of shape (n_samples, n_features)

        Returns:
            Optimal k in range [min_clusters, max_clusters]
        """
        logger.info(f"Determining optimal k in range [{self.min_clusters}, {self.max_clusters}]")

        # Normalize for cosine similarity
        embeddings_norm = normalize(embeddings, norm='l2')

        k_range = range(self.min_clusters, self.max_clusters + 1)
        silhouette_scores = []

        for k in k_range:
            kmeans = MiniBatchKMeans(
                n_clusters=k,
                batch_size=self.batch_size,
                random_state=self.random_state,
                n_init=3
            )
            labels = kmeans.fit_predict(embeddings_norm)

            # Calculate silhouette score
            score = silhouette_score(embeddings_norm, labels, sample_size=min(1000, len(embeddings)))
            silhouette_scores.append(score)

            logger.info(f"k={k}: silhouette_score={score:.3f}")

        # Find k with highest silhouette score
        optimal_idx = np.argmax(silhouette_scores)
        optimal_k = list(k_range)[optimal_idx]

        logger.info(f"Optimal k={optimal_k} (silhouette_score={silhouette_scores[optimal_idx]:.3f})")

        return optimal_k

    def cluster_bookmarks(
        self,
        embeddings: np.ndarray,
        bookmarks: List[Dict],
        n_clusters: Optional[int] = None
    ) -> Dict:
        """Cluster bookmarks using MiniBatchKMeans

        Args:
            embeddings: Numpy array of shape (n_bookmarks, dimensions)
            bookmarks: List of bookmark dicts with tags
            n_clusters: Number of clusters (auto-detect if None)

        Returns:
            Dict with cluster results
        """
        if len(embeddings) != len(bookmarks):
            raise ValueError(f"Embedding count ({len(embeddings)}) != bookmark count ({len(bookmarks)})")

        # Normalize embeddings for cosine similarity
        embeddings_norm = normalize(embeddings, norm='l2')

        # Determine optimal k
        if n_clusters is None:
            n_clusters = self.determine_optimal_k(embeddings)

        logger.info(f"Clustering {len(bookmarks)} bookmarks into {n_clusters} clusters")

        # Fit KMeans
        kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=self.batch_size,
            random_state=self.random_state,
            n_init=10,
            max_iter=300
        )
        labels = kmeans.fit_predict(embeddings_norm)

        # Build cluster metadata
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(labels == cluster_id)[0].tolist()
            cluster_bookmarks = [bookmarks[i] for i in cluster_indices]

            # Generate cluster name and keywords
            cluster_name, keywords = self._generate_cluster_name(cluster_bookmarks)

            # Extract top domains
            domains = [b["domain"] for b in cluster_bookmarks]
            top_domains = [domain for domain, _ in Counter(domains).most_common(5)]

            clusters.append({
                "id": int(cluster_id),
                "name": cluster_name,
                "size": len(cluster_indices),
                "keywords": keywords,
                "top_domains": top_domains,
                "bookmark_indices": cluster_indices
            })

        # Sort clusters by size (largest first)
        clusters.sort(key=lambda x: x["size"], reverse=True)

        result = {
            "n_clusters": n_clusters,
            "method": "minibatch_kmeans",
            "clusters": clusters,
            "labels": labels.tolist()
        }

        logger.info(f"Clustering complete: {n_clusters} clusters")
        for cluster in clusters[:5]:  # Log top 5
            logger.info(f"  Cluster {cluster['id']}: {cluster['name']} ({cluster['size']} bookmarks)")

        return result

    def _generate_cluster_name(self, cluster_bookmarks: List[Dict]) -> Tuple[str, List[str]]:
        """Generate human-readable cluster name from bookmarks

        Args:
            cluster_bookmarks: List of bookmarks in cluster

        Returns:
            Tuple of (cluster_name, keywords)
        """
        # Extract all tags
        all_tags = []
        for bookmark in cluster_bookmarks:
            if "tags" in bookmark:
                all_tags.extend(bookmark["tags"])

        # Get top 10 most common tags
        tag_counts = Counter(all_tags)
        top_tags = [tag for tag, _ in tag_counts.most_common(10)]

        if not top_tags:
            return "Uncategorized", []

        # Extract domains for context
        domains = [b["domain"] for b in cluster_bookmarks]
        top_domain = Counter(domains).most_common(1)[0][0] if domains else ""

        # Generate name from top tags
        keywords = top_tags[:5]  # Keep top 5 as keywords

        # Name generation logic
        name = self._create_cluster_name_from_tags(top_tags, top_domain)

        return name, keywords

    def _create_cluster_name_from_tags(self, tags: List[str], top_domain: str) -> str:
        """Create readable cluster name from tags

        Args:
            tags: List of top tags
            top_domain: Most common domain

        Returns:
            Cluster name
        """
        if not tags:
            return "Uncategorized"

        # Common patterns
        patterns = {
            ("docker", "kubernetes", "container"): "Docker & Kubernetes",
            ("python", "programming", "tutorial"): "Python Development",
            ("javascript", "react", "frontend"): "Frontend Development",
            ("aws", "cloud", "infrastructure"): "AWS Cloud Infrastructure",
            ("azure", "cloud", "devops"): "Azure DevOps",
            ("documentation", "api", "reference"): "API Documentation",
            ("tutorial", "learning", "guide"): "Learning Resources",
            ("video", "youtube", "tutorial"): "Video Tutorials",
            ("article", "blog", "post"): "Articles & Blogs",
        }

        # Check for pattern matches
        # Normalize tags: "docker-compose" → both "dockercompose" and "docker"
        tags_normalized = set()
        for t in tags:
            t_lower = t.lower()
            tags_normalized.add(t_lower.replace("-", ""))  # "dockercompose"
            tags_normalized.add(t_lower.split("-")[0])      # "docker"

        for pattern_keywords, pattern_name in patterns.items():
            if any(keyword in tags_normalized for keyword in pattern_keywords):
                return pattern_name

        # Domain-based naming
        domain_names = {
            "github.com": "GitHub Repositories",
            "stackoverflow.com": "Stack Overflow Q&A",
            "youtube.com": "YouTube Videos",
            "medium.com": "Medium Articles",
            "docs.google.com": "Google Docs",
        }

        if top_domain in domain_names:
            return domain_names[top_domain]

        # Fallback: Use top 2 tags
        if len(tags) >= 2:
            tag1 = tags[0].replace("-", " ").title()
            tag2 = tags[1].replace("-", " ").title()
            return f"{tag1} & {tag2}"
        elif len(tags) == 1:
            return tags[0].replace("-", " ").title()
        else:
            return "Miscellaneous"
