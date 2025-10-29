"""Bookmark analysis functions

Provides insights about bookmark collections:
- Domain distribution and statistics
- Quality issues (duplicates, missing titles)
- Folder activity patterns
- Report generation
"""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

from bookmark_intelligence.extractors import DomainExtractor
from bookmark_intelligence.models import Folder


def analyze_domains(
    bookmarks: List[Dict[str, Any]],
    extractor: DomainExtractor
) -> Dict[str, Any]:
    """Analyze domain distribution and categorization

    Args:
        bookmarks: Flat list of bookmark dictionaries
        extractor: DomainExtractor for categorization

    Returns:
        Dict with domain stats, top domains, category distribution
    """
    # Count domains
    domain_counts = Counter(b["domain"] for b in bookmarks if b.get("domain"))

    # Categorize domains
    category_counts: Dict[str, int] = {}
    for bookmark in bookmarks:
        domain = bookmark.get("domain")
        if domain:
            category = extractor.infer_category(domain)
            category_counts[category] = category_counts.get(category, 0) + 1

    # Top domains
    top_domains = [
        {
            "domain": domain,
            "count": count,
            "percentage": round(count / len(bookmarks) * 100, 1),
            "category": extractor.infer_category(domain)
        }
        for domain, count in domain_counts.most_common(10)
    ]

    return {
        "total_bookmarks": len(bookmarks),
        "unique_domains": len(domain_counts),
        "top_domains": top_domains,
        "categories": [
            {
                "name": cat,
                "count": count,
                "percentage": round(count / len(bookmarks) * 100, 1)
            }
            for cat, count in sorted(
                category_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]
    }


def analyze_quality(bookmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze bookmark quality issues

    Args:
        bookmarks: Flat list of bookmark dictionaries

    Returns:
        Dict with quality metrics and issues
    """
    # Find duplicates (exact URL match)
    url_counts = Counter(b["url"] for b in bookmarks)
    duplicates = [
        {"url": url, "count": count}
        for url, count in url_counts.items()
        if count > 1
    ]

    # Find empty/missing titles
    empty_titles = [
        {
            "url": b["url"],
            "folder": b.get("folder_path", "Root")
        }
        for b in bookmarks
        if not b.get("title") or b["title"].strip() == ""
    ]

    # Find bookmarks without dates
    missing_dates = [
        {
            "url": b["url"],
            "title": b.get("title", ""),
            "folder": b.get("folder_path", "Root")
        }
        for b in bookmarks
        if not b.get("added_date")
    ]

    return {
        "total_issues": len(duplicates) + len(empty_titles) + len(missing_dates),
        "duplicates": {
            "count": len(duplicates),
            "items": duplicates[:10]  # Limit to first 10
        },
        "empty_titles": {
            "count": len(empty_titles),
            "items": empty_titles[:10]
        },
        "missing_dates": {
            "count": len(missing_dates),
            "items": missing_dates[:10]
        }
    }


def analyze_folder_activity(
    folders: List[Folder],
    days_recent: int = 30,
    days_stale: int = 365
) -> Dict[str, Any]:
    """Analyze folder activity based on last_modified timestamps

    Args:
        folders: List of Folder objects
        days_recent: Threshold for "recently active" folders (default: 30 days)
        days_stale: Threshold for "stale" folders (default: 365 days)

    Returns:
        Dict with folder activity metrics
    """
    now = datetime.now()
    recent_threshold = now - timedelta(days=days_recent)
    stale_threshold = now - timedelta(days=days_stale)

    all_folders_flat: List[Tuple[str, Folder]] = []

    def collect_folders(folder: Folder, path_prefix: str = "") -> None:
        """Recursively collect all folders with paths"""
        folder_path = f"{path_prefix} > {folder.name}" if path_prefix else folder.name
        all_folders_flat.append((folder_path, folder))
        for subfolder in folder.subfolders:
            collect_folders(subfolder, folder_path)

    for folder in folders:
        collect_folders(folder)

    # Categorize by activity
    recently_active = []
    stale = []
    no_timestamp = []

    for path, folder in all_folders_flat:
        if folder.last_modified:
            modified_date = datetime.fromtimestamp(folder.last_modified)
            if modified_date >= recent_threshold:
                recently_active.append({
                    "name": folder.name,
                    "path": path,
                    "last_modified": modified_date.strftime("%Y-%m-%d"),
                    "bookmark_count": len(folder.bookmarks)
                })
            elif modified_date <= stale_threshold:
                stale.append({
                    "name": folder.name,
                    "path": path,
                    "last_modified": modified_date.strftime("%Y-%m-%d"),
                    "bookmark_count": len(folder.bookmarks)
                })
        else:
            no_timestamp.append({
                "name": folder.name,
                "path": path,
                "bookmark_count": len(folder.bookmarks)
            })

    # Sort by last modified (most recent first)
    recently_active.sort(key=lambda x: str(x["last_modified"]), reverse=True)
    stale.sort(key=lambda x: str(x["last_modified"]))

    return {
        "total_folders": len(all_folders_flat),
        "recently_active": {
            "count": len(recently_active),
            "items": recently_active[:10]  # Top 10 most recent
        },
        "stale": {
            "count": len(stale),
            "items": stale[:10]  # Oldest 10
        },
        "no_timestamp": {
            "count": len(no_timestamp),
            "items": no_timestamp[:10]
        }
    }


def generate_report(
    source_file: str,
    bookmarks: List[Dict[str, Any]],
    folders: List[Folder],
    domain_analysis: Dict[str, Any],
    quality_analysis: Dict[str, Any],
    folder_activity: Dict[str, Any],
    output_dir: Path = Path("data/reports")
) -> Path:
    """Generate markdown report with analysis results

    Args:
        source_file: Source HTML filename
        bookmarks: Flat list of bookmarks
        folders: List of root folders
        domain_analysis: Results from analyze_domains()
        quality_analysis: Results from analyze_quality()
        folder_activity: Results from analyze_folder_activity()
        output_dir: Directory to save report

    Returns:
        Path to generated report file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames
    timestamp = datetime.now()
    report_md = output_dir / f"{timestamp.strftime('%Y-%m-%d')}-import.md"
    report_json = output_dir / f"{timestamp.strftime('%Y-%m-%d')}-data.json"

    # Calculate date range
    dates = [
        datetime.fromisoformat(b["added_date"])
        for b in bookmarks
        if b.get("added_date")
    ]
    date_range = ""
    if dates:
        min_date = min(dates).strftime("%Y-%m-%d")
        max_date = max(dates).strftime("%Y-%m-%d")
        date_range = f"{min_date} to {max_date}"

    # Generate markdown report
    lines = [
        "# Bookmark Analysis Report",
        "",
        f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source:** {source_file}",
        "",
        "## Overview",
        "",
        f"- **Total bookmarks:** {domain_analysis['total_bookmarks']}",
        f"- **Unique domains:** {domain_analysis['unique_domains']}",
        f"- **Total folders:** {folder_activity['total_folders']}",
        f"- **Date range:** {date_range}" if date_range else "",
        "",
        "## Top 10 Domains",
        "",
        "| Domain | Count | % | Category |",
        "|--------|-------|---|----------|",
    ]

    for item in domain_analysis["top_domains"]:
        lines.append(
            f"| {item['domain']} | {item['count']} | {item['percentage']}% | {item['category']} |"
        )

    lines.extend([
        "",
        "## Category Distribution",
        "",
    ])

    for cat in domain_analysis["categories"][:10]:  # Top 10 categories
        lines.append(f"- **{cat['name']}:** {cat['count']} ({cat['percentage']}%)")

    lines.extend([
        "",
        "## Quality Issues",
        "",
        f"**Total issues found:** {quality_analysis['total_issues']}",
        "",
    ])

    # Duplicates
    dup_count = quality_analysis["duplicates"]["count"]
    if dup_count > 0:
        lines.extend([
            f"### Duplicates ({dup_count} found)",
            "",
        ])
        for item in quality_analysis["duplicates"]["items"][:5]:
            lines.append(f"- {item['url']} (appears {item['count']} times)")
    else:
        lines.append("### Duplicates (0 found)")
        lines.append("")
        lines.append("✓ No exact URL duplicates detected")

    lines.append("")

    # Empty titles
    empty_count = quality_analysis["empty_titles"]["count"]
    if empty_count > 0:
        lines.extend([
            f"### Empty Titles ({empty_count} found)",
            "",
        ])
        for item in quality_analysis["empty_titles"]["items"][:5]:
            url_short = item['url'][:60] + "..." if len(item['url']) > 60 else item['url']
            lines.append(f"- {url_short} ({item['folder']})")
        if empty_count > 5:
            lines.append(f"- _[{empty_count - 5} more...]_")
    else:
        lines.append("### Empty Titles (0 found)")
        lines.append("")
        lines.append("✓ All bookmarks have titles")

    lines.extend([
        "",
        "## Folder Activity",
        "",
    ])

    # Recently active folders
    recent_count = folder_activity["recently_active"]["count"]
    if recent_count > 0:
        lines.extend([
            f"### Recently Active Folders (last 30 days) - {recent_count} folders",
            "",
            "| Folder | Last Modified | Bookmarks | Path |",
            "|--------|---------------|-----------|------|",
        ])
        for item in folder_activity["recently_active"]["items"][:5]:
            lines.append(
                f"| {item['name']} | {item['last_modified']} | {item['bookmark_count']} | {item['path']} |"
            )

    lines.extend([
        "",
        "## Recommendations",
        "",
    ])

    # Generate recommendations
    if quality_analysis["empty_titles"]["count"] > 0:
        lines.append(
            f"- ⚠ {quality_analysis['empty_titles']['count']} bookmarks missing titles - consider adding descriptions"
        )
    else:
        lines.append("- ✓ All bookmarks have titles")

    if quality_analysis["duplicates"]["count"] > 0:
        lines.append(
            f"- ⚠ {quality_analysis['duplicates']['count']} duplicate URLs found - consider deduplication"
        )
    else:
        lines.append("- ✓ No duplicates found - good bookmark hygiene")

    # Category insights
    if domain_analysis["categories"]:
        top_cat = domain_analysis["categories"][0]
        pct = top_cat["percentage"]
        if pct > 20:
            lines.append(
                f"- ℹ {pct}% of bookmarks are {top_cat['name']} - consider organizing with tags"
            )

    # Folder insights
    if recent_count > 0:
        most_recent = folder_activity["recently_active"]["items"][0]
        lines.append(f"- 📊 '{most_recent['name']}' folder actively maintained (modified {most_recent['last_modified']})")

    # Write markdown report
    with open(report_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Write JSON data
    report_data = {
        "generated_at": timestamp.isoformat(),
        "source_file": source_file,
        "domain_analysis": domain_analysis,
        "quality_analysis": quality_analysis,
        "folder_activity": folder_activity
    }

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    return report_md
