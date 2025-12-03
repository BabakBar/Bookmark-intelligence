"""Pydantic schemas for API request/response models.

Following Pydantic v2 patterns with ConfigDict.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BookmarkResponse(BaseModel):
    """Response model for a single bookmark."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    title: str
    domain: str | None = None
    original_folder: str | None = None
    add_date: datetime | None = None
    tags: list[str] | None = None
    summary: str | None = None
    content_type: str | None = None
    processed: bool = False
    import_job_id: uuid.UUID | None = None
    created_at: datetime


class ImportJobResponse(BaseModel):
    """Response model for an import job."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str | None = None
    file_size_bytes: int | None = None
    total_bookmarks: int = 0
    status: str
    progress: int = 0
    imported_count: int = 0
    embeddings_generated: int = 0
    tags_generated: int = 0
    failed_count: int = 0
    total_cost_usd: Decimal = Decimal("0.00")
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class ImportJobWithBookmarks(ImportJobResponse):
    """Import job response with included bookmarks."""

    bookmarks: list[BookmarkResponse] = Field(default_factory=list)


class ImportSummaryResponse(BaseModel):
    """Summary response after importing bookmarks."""

    message: str
    import_job: ImportJobResponse
    bookmarks_count: int
    bookmarks_sample: list[BookmarkResponse] = Field(
        default_factory=list,
        description="First 10 bookmarks as preview",
    )
