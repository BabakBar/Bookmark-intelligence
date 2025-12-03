"""Database models for BookmarkAI.

Modern SQLAlchemy 2.0 models using Mapped type annotations.
"""

from src.app.models.bookmark import Bookmark
from src.app.models.import_job import ImportJob

__all__ = [
    "Bookmark",
    "ImportJob",
]
