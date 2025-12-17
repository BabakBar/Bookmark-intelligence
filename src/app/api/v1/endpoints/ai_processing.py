"""AI Processing API endpoints"""

import json
from pathlib import Path
from typing import List, Dict

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Data directory
AI_DIR = Path("data/ai")
REPORTS_DIR = Path("data/reports")


@router.get("/status")
async def get_status():
    """Get AI processing status

    Returns whether AI processing has been completed and files exist
    """
    embeddings_exist = (AI_DIR / "embeddings.npy").exists()
    bookmarks_ai_exist = (AI_DIR / "bookmarks_ai.json").exists()
    clusters_exist = (AI_DIR / "clusters.json").exists()
    projects_exist = (AI_DIR / "projects_suggested.json").exists()

    status = "not_started"
    if embeddings_exist and bookmarks_ai_exist and clusters_exist:
        status = "completed"
    elif embeddings_exist:
        status = "in_progress"

    return {
        "status": status,
        "files": {
            "embeddings": embeddings_exist,
            "bookmarks_ai": bookmarks_ai_exist,
            "clusters": clusters_exist,
            "projects": projects_exist
        }
    }


@router.get("/clusters")
async def list_clusters():
    """List all clusters with metadata

    Returns:
        List of clusters with names, sizes, keywords, domains
    """
    clusters_path = AI_DIR / "clusters.json"

    if not clusters_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Clusters not found. Run AI processing first: uv run scripts/process_ai.py"
        )

    with open(clusters_path) as f:
        data = json.load(f)

    return {
        "n_clusters": data["n_clusters"],
        "method": data["method"],
        "clusters": data["clusters"]
    }


@router.get("/clusters/{cluster_id}/bookmarks")
async def get_cluster_bookmarks(cluster_id: int):
    """Get all bookmarks in a specific cluster

    Args:
        cluster_id: Cluster ID (0-indexed)

    Returns:
        List of bookmarks with tags, summaries, cluster info
    """
    bookmarks_path = AI_DIR / "bookmarks_ai.json"
    clusters_path = AI_DIR / "clusters.json"

    if not bookmarks_path.exists() or not clusters_path.exists():
        raise HTTPException(
            status_code=404,
            detail="AI data not found. Run AI processing first."
        )

    # Load cluster info
    with open(clusters_path) as f:
        clusters_data = json.load(f)

    # Find cluster
    cluster = next(
        (c for c in clusters_data["clusters"] if c["id"] == cluster_id),
        None
    )

    if not cluster:
        raise HTTPException(
            status_code=404,
            detail=f"Cluster {cluster_id} not found"
        )

    # Load bookmarks
    with open(bookmarks_path) as f:
        ai_data = json.load(f)
        all_bookmarks = ai_data["bookmarks"]

    # Filter bookmarks in this cluster
    cluster_bookmarks = [
        b for b in all_bookmarks if b.get("cluster_id") == cluster_id
    ]

    return {
        "cluster": cluster,
        "bookmarks": cluster_bookmarks
    }


@router.get("/projects/suggested")
async def get_suggested_projects():
    """Get AI-suggested projects

    Returns:
        List of project suggestions with bookmarks
    """
    projects_path = AI_DIR / "projects_suggested.json"

    if not projects_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Projects not found. Run AI processing first."
        )

    with open(projects_path) as f:
        data = json.load(f)

    return data


@router.get("/projects/{project_name}/bookmarks")
async def get_project_bookmarks(project_name: str):
    """Get all bookmarks for a suggested project

    Args:
        project_name: Project name (URL-encoded)

    Returns:
        Project info and bookmarks
    """
    projects_path = AI_DIR / "projects_suggested.json"
    bookmarks_path = AI_DIR / "bookmarks_ai.json"

    if not projects_path.exists() or not bookmarks_path.exists():
        raise HTTPException(
            status_code=404,
            detail="AI data not found. Run AI processing first."
        )

    # Load projects
    with open(projects_path) as f:
        projects_data = json.load(f)

    # Find project
    project = next(
        (p for p in projects_data["projects"] if p["name"] == project_name),
        None
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project '{project_name}' not found"
        )

    # Load bookmarks
    with open(bookmarks_path) as f:
        ai_data = json.load(f)
        all_bookmarks = ai_data["bookmarks"]

    # Get bookmarks by indices
    project_bookmarks = [
        all_bookmarks[idx] for idx in project["bookmark_indices"]
        if idx < len(all_bookmarks)
    ]

    return {
        "project": project,
        "bookmarks": project_bookmarks
    }


@router.get("/search")
async def search_bookmarks(q: str, limit: int = 50):
    """Search bookmarks by title, tags, or URL

    Args:
        q: Search query
        limit: Max results

    Returns:
        Matching bookmarks
    """
    bookmarks_path = AI_DIR / "bookmarks_ai.json"

    if not bookmarks_path.exists():
        raise HTTPException(
            status_code=404,
            detail="AI data not found. Run AI processing first."
        )

    with open(bookmarks_path) as f:
        ai_data = json.load(f)
        all_bookmarks = ai_data["bookmarks"]

    # Simple text search
    q_lower = q.lower()
    results = []

    for bookmark in all_bookmarks:
        # Search in title, URL, tags, summary
        searchable = [
            bookmark.get("title", "").lower(),
            bookmark.get("url", "").lower(),
            bookmark.get("summary", "").lower(),
        ]

        # Add tags
        tags = bookmark.get("tags", [])
        searchable.extend([tag.lower() for tag in tags])

        # Check if query matches
        if any(q_lower in text for text in searchable):
            results.append(bookmark)

        if len(results) >= limit:
            break

    return {
        "query": q,
        "count": len(results),
        "results": results
    }
