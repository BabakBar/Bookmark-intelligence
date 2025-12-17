"""Project suggestion engine from cluster analysis"""

import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ProjectSuggester:
    """Suggest projects from bookmark clusters"""

    @staticmethod
    def _expand_keyword(keyword: str) -> Set[str]:
        kw = keyword.lower().strip()
        if not kw:
            return set()
        parts = [p for p in kw.split("-") if p]
        expanded = {kw, kw.replace("-", "")}
        expanded.update(parts)
        return expanded

    @classmethod
    def _expand_keyword_set(cls, keywords: Set[str]) -> Set[str]:
        expanded: Set[str] = set()
        for kw in keywords:
            expanded |= cls._expand_keyword(kw)
        return expanded

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize project suggester

        Args:
            config_path: Path to ai_settings.yaml
        """
        # Load config
        if config_path and config_path.exists():
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
                self.min_confidence = config["project_suggestion"]["min_confidence"]
                self.max_projects = config["project_suggestion"]["max_projects"]
        else:
            # Defaults
            self.min_confidence = 0.7
            self.max_projects = 5

        # Project detection patterns
        self.work_keywords = {
            "docker", "kubernetes", "k8s", "deployment", "infrastructure",
            "backend", "api", "database", "postgresql", "redis", "fastapi",
            "production", "monitoring", "logging", "ci-cd", "devops"
        }

        self.learning_keywords = {
            "tutorial", "course", "learning", "guide", "documentation",
            "getting-started", "introduction", "beginner", "example", "demo"
        }

        self.frontend_keywords = {
            "react", "vue", "angular", "frontend", "ui", "ux", "design",
            "css", "html", "javascript", "typescript", "component"
        }

        self.cloud_keywords = {
            "aws", "azure", "gcp", "cloud", "lambda", "ec2", "s3",
            "cloudformation", "terraform", "ansible"
        }

        # Normalized versions that handle hyphenated keywords consistently
        self.work_keywords_norm = self._expand_keyword_set(self.work_keywords)
        self.learning_keywords_norm = self._expand_keyword_set(self.learning_keywords)
        self.frontend_keywords_norm = self._expand_keyword_set(self.frontend_keywords)
        self.cloud_keywords_norm = self._expand_keyword_set(self.cloud_keywords)

    def suggest_projects(
        self,
        clusters: Dict,
        bookmarks: List[Dict]
    ) -> List[Dict]:
        """Generate 3-5 project suggestions from clusters

        Args:
            clusters: Cluster results from BookmarkClusterer
            bookmarks: Original bookmarks with folder_path

        Returns:
            List of project suggestions
        """
        logger.info("Generating project suggestions from clusters")

        projects = []

        # Strategy 1: Folder-based projects
        folder_projects = self._suggest_from_folders(bookmarks)
        projects.extend(folder_projects)

        # Strategy 2: Work-related clusters
        work_projects = self._suggest_work_projects(clusters, bookmarks)
        projects.extend(work_projects)

        # Strategy 3: Learning-focused clusters
        learning_projects = self._suggest_learning_projects(clusters, bookmarks)
        projects.extend(learning_projects)

        # Strategy 4: Technology-specific clusters
        tech_projects = self._suggest_tech_projects(clusters, bookmarks)
        projects.extend(tech_projects)

        # Deduplicate and rank by confidence
        projects = self._deduplicate_projects(projects)
        projects.sort(key=lambda x: x["confidence"], reverse=True)

        # Filter by min confidence and limit
        projects = [p for p in projects if p["confidence"] >= self.min_confidence]
        projects = projects[:self.max_projects]

        logger.info(f"Suggested {len(projects)} projects")
        for proj in projects:
            logger.info(f"  {proj['name']}: {proj['bookmark_count']} bookmarks (confidence={proj['confidence']:.2f})")

        return projects

    def _suggest_from_folders(self, bookmarks: List[Dict]) -> List[Dict]:
        """Extract projects from folder structure

        Args:
            bookmarks: List of bookmarks with folder_path

        Returns:
            List of folder-based project suggestions
        """
        # Count bookmarks per top-level folder
        folder_counts = Counter()
        folder_bookmarks = {}

        for i, bookmark in enumerate(bookmarks):
            if "folder_path" not in bookmark:
                continue

            folder_path = bookmark["folder_path"]
            if isinstance(folder_path, list):
                folder_path = " > ".join(folder_path)

            # Get top-level folder after "Bookmarks bar"
            parts = folder_path.split(" > ")
            if len(parts) >= 2 and parts[0] == "Bookmarks bar":
                top_folder = parts[1]
            elif len(parts) >= 1:
                top_folder = parts[0]
            else:
                continue

            folder_counts[top_folder] += 1
            if top_folder not in folder_bookmarks:
                folder_bookmarks[top_folder] = []
            folder_bookmarks[top_folder].append(i)

        # Create projects from folders with 20+ bookmarks
        projects = []
        for folder_name, count in folder_counts.most_common(10):
            if count < 20:  # Threshold for project
                continue

            # Extract keywords from bookmarks in folder
            indices = folder_bookmarks[folder_name]
            folder_tags = []
            for idx in indices:
                if "tags" in bookmarks[idx]:
                    folder_tags.extend(bookmarks[idx]["tags"])

            top_keywords = [tag for tag, _ in Counter(folder_tags).most_common(5)]

            # Confidence based on folder size
            confidence = min(0.9, 0.6 + (count / 100))

            projects.append({
                "name": folder_name,
                "description": f"Bookmarks from {folder_name} folder",
                "source": "folder_structure",
                "cluster_ids": [],
                "bookmark_count": count,
                "bookmark_indices": indices,
                "confidence": confidence,
                "keywords": top_keywords
            })

        return projects

    def _suggest_work_projects(self, clusters: Dict, bookmarks: List[Dict]) -> List[Dict]:
        """Identify work-related project clusters

        Args:
            clusters: Cluster results
            bookmarks: Original bookmarks

        Returns:
            Work project suggestions
        """
        projects = []

        for cluster in clusters["clusters"]:
            # Check if cluster has work keywords
            cluster_keywords: Set[str] = set()
            for kw in cluster["keywords"]:
                cluster_keywords |= self._expand_keyword(kw)

            work_overlap = len(cluster_keywords & self.work_keywords_norm)

            if work_overlap >= 2 and cluster["size"] >= 30:
                # Strong work signal
                confidence = min(0.85, 0.7 + (work_overlap / 10))

                projects.append({
                    "name": f"{cluster['name']} Project",
                    "description": f"Work-related bookmarks in {cluster['name']} cluster",
                    "source": "work_cluster",
                    "cluster_ids": [cluster["id"]],
                    "bookmark_count": cluster["size"],
                    "bookmark_indices": cluster["bookmark_indices"],
                    "confidence": confidence,
                    "keywords": cluster["keywords"]
                })

        return projects

    def _suggest_learning_projects(self, clusters: Dict, bookmarks: List[Dict]) -> List[Dict]:
        """Identify learning-focused clusters

        Args:
            clusters: Cluster results
            bookmarks: Original bookmarks

        Returns:
            Learning project suggestions
        """
        projects = []
        learning_clusters = []

        for cluster in clusters["clusters"]:
            cluster_keywords: Set[str] = set()
            for kw in cluster["keywords"]:
                cluster_keywords |= self._expand_keyword(kw)

            learning_overlap = len(cluster_keywords & self.learning_keywords_norm)

            if learning_overlap >= 1:
                learning_clusters.append(cluster)

        # Merge learning clusters into single project
        if learning_clusters:
            total_bookmarks = sum(c["size"] for c in learning_clusters)
            all_keywords = []
            all_indices = []
            for c in learning_clusters:
                all_keywords.extend(c["keywords"])
                all_indices.extend(c["bookmark_indices"])

            top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(5)]

            projects.append({
                "name": "Personal Learning",
                "description": "Tutorials, courses, and learning resources",
                "source": "learning_cluster",
                "cluster_ids": [c["id"] for c in learning_clusters],
                "bookmark_count": total_bookmarks,
                "bookmark_indices": all_indices,
                "confidence": 0.75,
                "keywords": top_keywords
            })

        return projects

    def _suggest_tech_projects(self, clusters: Dict, bookmarks: List[Dict]) -> List[Dict]:
        """Identify technology-specific projects

        Args:
            clusters: Cluster results
            bookmarks: Original bookmarks

        Returns:
            Technology project suggestions
        """
        projects = []

        # Frontend project
        frontend_clusters = []
        for cluster in clusters["clusters"]:
            cluster_keywords: Set[str] = set()
            for kw in cluster["keywords"]:
                cluster_keywords |= self._expand_keyword(kw)

            frontend_overlap = len(cluster_keywords & self.frontend_keywords_norm)

            if frontend_overlap >= 2:
                frontend_clusters.append(cluster)

        if frontend_clusters:
            total_bookmarks = sum(c["size"] for c in frontend_clusters)
            all_keywords = []
            all_indices = []
            for c in frontend_clusters:
                all_keywords.extend(c["keywords"])
                all_indices.extend(c["bookmark_indices"])

            top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(5)]

            projects.append({
                "name": "Frontend Development",
                "description": "UI/UX and frontend technology bookmarks",
                "source": "tech_cluster",
                "cluster_ids": [c["id"] for c in frontend_clusters],
                "bookmark_count": total_bookmarks,
                "bookmark_indices": all_indices,
                "confidence": 0.8,
                "keywords": top_keywords
            })

        # Cloud infrastructure project
        cloud_clusters = []
        for cluster in clusters["clusters"]:
            cluster_keywords: Set[str] = set()
            for kw in cluster["keywords"]:
                cluster_keywords |= self._expand_keyword(kw)

            cloud_overlap = len(cluster_keywords & self.cloud_keywords_norm)

            if cloud_overlap >= 2:
                cloud_clusters.append(cluster)

        if cloud_clusters:
            total_bookmarks = sum(c["size"] for c in cloud_clusters)
            all_keywords = []
            all_indices = []
            for c in cloud_clusters:
                all_keywords.extend(c["keywords"])
                all_indices.extend(c["bookmark_indices"])

            top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(5)]

            projects.append({
                "name": "Cloud Infrastructure",
                "description": "AWS, Azure, and cloud infrastructure resources",
                "source": "tech_cluster",
                "cluster_ids": [c["id"] for c in cloud_clusters],
                "bookmark_count": total_bookmarks,
                "bookmark_indices": all_indices,
                "confidence": 0.78,
                "keywords": top_keywords
            })

        return projects

    def _deduplicate_projects(self, projects: List[Dict]) -> List[Dict]:
        """Remove duplicate or overlapping projects

        Args:
            projects: List of project suggestions

        Returns:
            Deduplicated projects
        """
        if not projects:
            return []

        # Group by similar names
        unique_projects = []
        seen_names = set()

        for project in projects:
            name_lower = project["name"].lower()

            # Check for duplicates
            is_duplicate = False
            for seen_name in seen_names:
                if self._names_similar(name_lower, seen_name):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_projects.append(project)
                seen_names.add(name_lower)

        return unique_projects

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if project names are similar

        Args:
            name1, name2: Project names (lowercase)

        Returns:
            True if similar
        """
        # Exact match
        if name1 == name2:
            return True

        # One contains the other
        if name1 in name2 or name2 in name1:
            return True

        # Common words overlap >= 50%
        words1 = set(name1.split())
        words2 = set(name2.split())
        overlap = len(words1 & words2)
        min_words = min(len(words1), len(words2))

        if min_words > 0 and overlap / min_words >= 0.5:
            return True

        return False
