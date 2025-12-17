"""AI processing module for bookmark intelligence

This module provides:
- Embedding generation via OpenAI Batch API
- Tagging and summarization via GPT-5.2
- Clustering using MiniBatchKMeans
- Project suggestions from cluster analysis
- Folder reorganization recommendations
"""

from .embedding_service import OpenAIEmbeddingService
from .tagging_service import GPTTaggingService
from .clustering import BookmarkClusterer
from .project_suggester import ProjectSuggester
from .folder_recommender import FolderRecommender

__all__ = [
    "OpenAIEmbeddingService",
    "GPTTaggingService",
    "BookmarkClusterer",
    "ProjectSuggester",
    "FolderRecommender",
]
