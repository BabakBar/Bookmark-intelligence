"""Folder reorganization recommendation engine"""

import logging
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class FolderRecommender:
    """Generate folder reorganization recommendations"""

    def __init__(self):
        """Initialize folder recommender"""
        pass

    def analyze_and_recommend(
        self,
        bookmarks: List[Dict],
        clusters: Dict
    ) -> Dict:
        """Analyze bookmark organization and generate recommendations

        Args:
            bookmarks: List of AI-enriched bookmarks
            clusters: Cluster results

        Returns:
            Dict with folder recommendations
        """
        logger.info("Analyzing folder structure and generating recommendations")

        # Analyze current folder structure
        current_analysis = self._analyze_current_folders(bookmarks)

        # Generate AI-based folder suggestions
        ai_folder_suggestions = self._aggregate_ai_recommendations(bookmarks)

        # Generate cluster-based folders
        cluster_folders = self._generate_cluster_folders(clusters, bookmarks)

        # Create comprehensive reorganization plan
        reorganization_plan = self._create_reorganization_plan(
            bookmarks,
            current_analysis,
            ai_folder_suggestions,
            cluster_folders
        )

        # Identify problematic areas
        issues = self._identify_issues(bookmarks, current_analysis)

        # Generate action items
        action_items = self._generate_action_items(
            bookmarks,
            reorganization_plan,
            issues
        )

        logger.info(f"Generated {len(reorganization_plan)} folder recommendations")
        logger.info(f"Identified {len(issues)} organizational issues")
        logger.info(f"Created {len(action_items)} action items")

        return {
            "current_analysis": current_analysis,
            "ai_folder_suggestions": ai_folder_suggestions,
            "cluster_folders": cluster_folders,
            "reorganization_plan": reorganization_plan,
            "issues": issues,
            "action_items": action_items,
            "summary": self._generate_summary(
                current_analysis,
                reorganization_plan,
                issues
            )
        }

    def _analyze_current_folders(self, bookmarks: List[Dict]) -> Dict:
        """Analyze current folder structure

        Args:
            bookmarks: List of bookmarks

        Returns:
            Analysis of current folders
        """
        folder_counts = Counter()
        folder_contents = defaultdict(list)

        for idx, bookmark in enumerate(bookmarks):
            folder = bookmark.get("folder_path", "Uncategorized")
            if isinstance(folder, list):
                folder = " > ".join(folder)

            folder_counts[folder] += 1
            folder_contents[folder].append(idx)

        # Identify top-level folders and bookmark counts
        top_level_folders = defaultdict(int)
        for folder, count in folder_counts.items():
            parts = folder.split(" > ")
            if len(parts) >= 2 and parts[0] == "Bookmarks bar":
                top_level = parts[1]
            elif len(parts) >= 1:
                top_level = parts[0]
            else:
                top_level = "Uncategorized"

            top_level_folders[top_level] += count  # Count bookmarks, not folders

        return {
            "total_folders": len(folder_counts),
            "folder_distribution": dict(folder_counts.most_common(20)),
            "top_level_folders": dict(sorted(
                top_level_folders.items(),
                key=lambda x: x[1],
                reverse=True
            )),
            "largest_folders": [
                {"folder": f, "count": c}
                for f, c in folder_counts.most_common(10)
            ],
            "folder_contents": dict(folder_contents)
        }

    def _aggregate_ai_recommendations(self, bookmarks: List[Dict]) -> Dict:
        """Aggregate AI folder recommendations

        Args:
            bookmarks: List of AI-enriched bookmarks

        Returns:
            Aggregated folder suggestions
        """
        folder_recommendations = Counter()
        category_mapping = defaultdict(list)

        for idx, bookmark in enumerate(bookmarks):
            rec = bookmark.get("folder_recommendation", "Uncategorized")
            folder_recommendations[rec] += 1

            # Extract category (first part before >)
            category = rec.split(" > ")[0] if " > " in rec else rec
            category_mapping[category].append(idx)

        return {
            "suggested_folders": dict(folder_recommendations.most_common(30)),
            "category_distribution": {
                cat: len(indices)
                for cat, indices in category_mapping.items()
            },
            "top_categories": sorted(
                category_mapping.keys(),
                key=lambda x: len(category_mapping[x]),
                reverse=True
            )[:10]
        }

    def _generate_cluster_folders(
        self,
        clusters: Dict,
        bookmarks: List[Dict]
    ) -> List[Dict]:
        """Generate folder structure from clusters

        Args:
            clusters: Cluster results
            bookmarks: Bookmarks

        Returns:
            Cluster-based folder suggestions
        """
        cluster_folders = []

        for cluster in clusters["clusters"]:
            # Analyze bookmarks in cluster
            cluster_bookmarks = [
                bookmarks[i] for i in cluster["bookmark_indices"]
                if i < len(bookmarks)
            ]

            # Find most common AI folder recommendations in cluster
            folder_recs = [
                b.get("folder_recommendation", "").split(" > ")[0]
                for b in cluster_bookmarks
                if b.get("folder_recommendation")
            ]
            most_common_category = Counter(folder_recs).most_common(1)[0][0] if folder_recs else "Uncategorized"

            # Find primary technologies
            techs = [
                b.get("primary_technology", "")
                for b in cluster_bookmarks
                if b.get("primary_technology")
            ]
            primary_tech = Counter(techs).most_common(1)[0][0] if techs else None

            # Suggest folder structure
            if primary_tech and primary_tech != "Unknown":
                suggested_folder = f"{most_common_category} > {primary_tech}"
            else:
                suggested_folder = f"{most_common_category} > {cluster['name']}"

            cluster_folders.append({
                "cluster_id": cluster["id"],
                "cluster_name": cluster["name"],
                "suggested_folder": suggested_folder,
                "bookmark_count": cluster["size"],
                "confidence": "high" if cluster["size"] > 50 else "medium"
            })

        return cluster_folders

    def _create_reorganization_plan(
        self,
        bookmarks: List[Dict],
        current_analysis: Dict,
        ai_suggestions: Dict,
        cluster_folders: List[Dict]
    ) -> List[Dict]:
        """Create comprehensive reorganization plan

        Args:
            bookmarks: Bookmarks
            current_analysis: Current folder analysis
            ai_suggestions: AI folder suggestions
            cluster_folders: Cluster-based folders

        Returns:
            List of reorganization actions
        """
        plan = []

        # Strategy 1: High-priority bookmarks
        high_priority = [
            (i, b) for i, b in enumerate(bookmarks)
            if b.get("priority") == "high"
        ]

        if high_priority:
            plan.append({
                "action": "create_folder",
                "folder": "⭐ High Priority",
                "reason": "Quick access to essential bookmarks",
                "bookmark_count": len(high_priority),
                "bookmark_indices": [i for i, _ in high_priority],
                "priority": 1
            })

        # Strategy 2: Technology-specific folders
        tech_groups = defaultdict(list)
        for idx, bookmark in enumerate(bookmarks):
            tech = bookmark.get("primary_technology")
            if tech and tech != "Unknown":
                tech_groups[tech].append(idx)

        for tech, indices in tech_groups.items():
            if len(indices) >= 15:  # Threshold for dedicated folder
                plan.append({
                    "action": "create_folder",
                    "folder": f"Development > {tech}",
                    "reason": f"{len(indices)} {tech}-related bookmarks",
                    "bookmark_count": len(indices),
                    "bookmark_indices": indices,
                    "priority": 2
                })

        # Strategy 3: Learning resources
        learning = [
            (i, b) for i, b in enumerate(bookmarks)
            if b.get("content_type") in ["tutorial", "course"] or
               b.get("skill_level") == "beginner"
        ]

        if len(learning) >= 20:
            plan.append({
                "action": "create_folder",
                "folder": "Learning",
                "reason": "Consolidate tutorials and courses",
                "bookmark_count": len(learning),
                "bookmark_indices": [i for i, _ in learning],
                "priority": 2
            })

        # Strategy 4: Project-based folders from AI recommendations
        ai_categories = ai_suggestions["category_distribution"]
        for category, count in ai_categories.items():
            if count >= 30 and category != "Uncategorized":
                related_bookmarks = [
                    i for i, b in enumerate(bookmarks)
                    if b.get("folder_recommendation", "").startswith(category)
                ]

                plan.append({
                    "action": "create_folder",
                    "folder": category,
                    "reason": f"AI suggests {count} bookmarks fit this category",
                    "bookmark_count": len(related_bookmarks),
                    "bookmark_indices": related_bookmarks,
                    "priority": 2
                })

        # Strategy 5: Consolidate duplicate folders
        current_folders = current_analysis["folder_distribution"]
        similar_folders = self._find_similar_folders(list(current_folders.keys()))

        for group in similar_folders:
            if len(group) >= 2:
                total_bookmarks = sum(current_folders[f] for f in group)
                plan.append({
                    "action": "consolidate_folders",
                    "folders": group,
                    "target_folder": group[0],  # Use first as target
                    "reason": "Similar folder names should be consolidated",
                    "bookmark_count": total_bookmarks,
                    "priority": 3
                })

        # Sort by priority
        plan.sort(key=lambda x: x["priority"])

        return plan

    def _identify_issues(
        self,
        bookmarks: List[Dict],
        current_analysis: Dict
    ) -> List[Dict]:
        """Identify organizational issues

        Args:
            bookmarks: Bookmarks
            current_analysis: Current folder analysis

        Returns:
            List of issues
        """
        issues = []

        # Issue 1: Bookmarks bar overload (bookmarks directly in Bookmarks bar)
        bookmarks_bar_count = 0
        for b in bookmarks:
            folder = b.get("folder_path", "")
            if isinstance(folder, list):
                folder = " > ".join(folder)
            if folder == "Bookmarks bar":
                bookmarks_bar_count += 1

        if bookmarks_bar_count > 20:
            issues.append({
                "type": "overloaded_folder",
                "severity": "high",
                "folder": "Bookmarks bar",
                "count": bookmarks_bar_count,
                "description": f"{bookmarks_bar_count} bookmarks in root Bookmarks bar - should move to subfolders",
                "recommendation": "Move to appropriate subfolders based on AI suggestions"
            })

        # Issue 2: Uncategorized bookmarks
        uncategorized = [
            b for b in bookmarks
            if "folder_path" not in b or not b["folder_path"]
        ]

        if len(uncategorized) > 10:
            issues.append({
                "type": "uncategorized",
                "severity": "medium",
                "count": len(uncategorized),
                "description": f"{len(uncategorized)} bookmarks without folders",
                "recommendation": "Use AI folder recommendations to categorize"
            })

        # Issue 3: Deep nesting (>4 levels)
        deep_nested = []
        for b in bookmarks:
            folder = b.get("folder_path", "")
            if isinstance(folder, list):
                folder = " > ".join(folder)
            # Count separators (4+ means 5+ levels)
            if folder.count(" > ") >= 4:
                deep_nested.append(b)

        if len(deep_nested) > 20:
            issues.append({
                "type": "deep_nesting",
                "severity": "low",
                "count": len(deep_nested),
                "description": f"{len(deep_nested)} bookmarks nested >4 levels deep",
                "recommendation": "Flatten folder structure for better accessibility"
            })

        # Issue 4: Fragmented categories
        tech_distribution = Counter()
        for b in bookmarks:
            tech = b.get("primary_technology")
            if tech and tech != "Unknown":
                tech_distribution[tech] += 1

        fragmented = [
            (tech, count) for tech, count in tech_distribution.items()
            if count >= 10
        ]

        for tech, count in fragmented:
            tech_bookmarks = [
                b for b in bookmarks
                if b.get("primary_technology") == tech
            ]

            # Check if spread across many folders
            folders = set(
                str(b.get("folder_path", ""))
                for b in tech_bookmarks
            )

            if len(folders) > 5:
                issues.append({
                    "type": "fragmented_category",
                    "severity": "medium",
                    "technology": tech,
                    "count": count,
                    "spread_across": len(folders),
                    "description": f"{count} {tech} bookmarks spread across {len(folders)} folders",
                    "recommendation": f"Consolidate into 'Development > {tech}' folder"
                })

        return issues

    def _generate_action_items(
        self,
        bookmarks: List[Dict],
        reorganization_plan: List[Dict],
        issues: List[Dict]
    ) -> List[Dict]:
        """Generate prioritized action items

        Args:
            bookmarks: Bookmarks
            reorganization_plan: Reorganization plan
            issues: Identified issues

        Returns:
            List of action items
        """
        actions = []

        # Action 1: Create essential folder structure
        actions.append({
            "priority": 1,
            "title": "Create base folder structure",
            "description": "Set up main organizational categories",
            "steps": [
                "Create 'Development' folder for technical resources",
                "Create 'Learning' folder for tutorials/courses",
                "Create 'Work' folder for professional bookmarks",
                "Create '⭐ High Priority' for essential references"
            ],
            "estimated_time": "5 minutes"
        })

        # Action 2: Move high-priority bookmarks
        high_priority_count = sum(
            1 for b in bookmarks if b.get("priority") == "high"
        )

        if high_priority_count > 0:
            actions.append({
                "priority": 1,
                "title": f"Organize {high_priority_count} high-priority bookmarks",
                "description": "Move essential bookmarks to quick-access folder",
                "steps": [
                    f"Review {high_priority_count} high-priority bookmarks",
                    "Move to '⭐ High Priority' folder",
                    "Verify frequently-accessed bookmarks are included"
                ],
                "estimated_time": f"{high_priority_count // 10} minutes"
            })

        # Action 3: Address critical issues
        critical_issues = [i for i in issues if i["severity"] == "high"]
        for issue in critical_issues:
            actions.append({
                "priority": 1,
                "title": f"Fix: {issue['description']}",
                "description": issue["recommendation"],
                "steps": [issue["recommendation"]],
                "estimated_time": "10 minutes"
            })

        # Action 4: Execute reorganization plan
        for i, plan_item in enumerate(reorganization_plan[:5]):  # Top 5 plans
            if plan_item["action"] == "create_folder":
                actions.append({
                    "priority": 2,
                    "title": f"Create '{plan_item['folder']}' folder",
                    "description": plan_item["reason"],
                    "steps": [
                        f"Create folder: {plan_item['folder']}",
                        f"Move {plan_item['bookmark_count']} bookmarks",
                        "Verify folder structure makes sense"
                    ],
                    "estimated_time": f"{plan_item['bookmark_count'] // 20} minutes"
                })

        # Action 5: Review and refine
        actions.append({
            "priority": 3,
            "title": "Review AI recommendations",
            "description": "Validate AI-suggested folder structure",
            "steps": [
                "Review folder_recommendation for each bookmark",
                "Identify any misclassifications",
                "Adjust folder structure as needed",
                "Create bookmark management routine"
            ],
            "estimated_time": "30 minutes"
        })

        return actions

    def _generate_summary(
        self,
        current_analysis: Dict,
        reorganization_plan: List[Dict],
        issues: List[Dict]
    ) -> Dict:
        """Generate executive summary

        Args:
            current_analysis: Current folder analysis
            reorganization_plan: Reorganization plan
            issues: Issues

        Returns:
            Summary dict
        """
        total_reorganization_bookmarks = sum(
            p.get("bookmark_count", 0) for p in reorganization_plan
        )

        return {
            "current_state": {
                "total_folders": current_analysis["total_folders"],
                "top_level_folders": len(current_analysis["top_level_folders"]),
                "largest_folder": current_analysis["largest_folders"][0] if current_analysis["largest_folders"] else None
            },
            "recommendations": {
                "new_folders": len([p for p in reorganization_plan if p["action"] == "create_folder"]),
                "consolidations": len([p for p in reorganization_plan if p["action"] == "consolidate_folders"]),
                "bookmarks_affected": total_reorganization_bookmarks
            },
            "issues_found": {
                "total": len(issues),
                "high_severity": len([i for i in issues if i["severity"] == "high"]),
                "medium_severity": len([i for i in issues if i["severity"] == "medium"])
            }
        }

    def _find_similar_folders(self, folders: List[str]) -> List[List[str]]:
        """Find similar folder names that should be consolidated

        Args:
            folders: List of folder paths

        Returns:
            Groups of similar folders
        """
        groups = []
        used = set()

        for i, folder1 in enumerate(folders):
            if folder1 in used:
                continue

            group = [folder1]

            for folder2 in folders[i+1:]:
                if folder2 in used:
                    continue
                if self._folders_similar(folder1, folder2):
                    group.append(folder2)
                    used.add(folder2)

            if len(group) > 1:
                groups.append(group)
                used.add(folder1)

        return groups

    @staticmethod
    def _normalize_folder_path(folder: str) -> List[str]:
        folder_norm = folder.strip().lower()
        for prefix in ["bookmarks bar > ", "bookmarks bar>"]:
            folder_norm = folder_norm.replace(prefix, "")
        return [p.strip() for p in folder_norm.split(" > ") if p.strip()]

    @staticmethod
    def _tokenize_folder_name(name: str) -> set[str]:
        tokens = set(re.findall(r"[a-z0-9]+", name.lower()))
        # Also add digit-stripped variants (e.g., "python3" -> "python")
        tokens |= {re.sub(r"\d+", "", t) for t in tokens if re.sub(r"\d+", "", t)}
        return {t for t in tokens if t}

    def _folders_similar(self, f1: str, f2: str) -> bool:
        """Check if two folder names are similar

        Args:
            f1, f2: Folder paths

        Returns:
            True if similar
        """
        parts1 = self._normalize_folder_path(f1)
        parts2 = self._normalize_folder_path(f2)

        if not parts1 or not parts2:
            return False

        # Avoid parent/child and cross-level consolidations
        if len(parts1) != len(parts2):
            return False

        leaf1 = parts1[-1]
        leaf2 = parts2[-1]

        if leaf1 == leaf2:
            return True

        tokens1 = self._tokenize_folder_name(leaf1)
        tokens2 = self._tokenize_folder_name(leaf2)

        if not tokens1 or not tokens2:
            return False

        overlap = len(tokens1 & tokens2)
        min_tokens = min(len(tokens1), len(tokens2))

        # Higher threshold to reduce false positives
        return overlap / min_tokens >= 0.7
