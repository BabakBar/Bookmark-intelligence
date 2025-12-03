"""Bookmark model for storing imported bookmarks with AI metadata.

Follows SQLAlchemy 2.0 modern patterns with Mapped type annotations.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.app.core.database import Base

if TYPE_CHECKING:
    from src.app.models.import_job import ImportJob


class Bookmark(Base):
    """Stores imported bookmarks with AI-generated metadata.

    Each bookmark has:
    - Original browser data (URL, title, folder, add_date)
    - AI-generated metadata (tags, summary, content_type) - Week 2
    - Import tracking (which import job created it)
    - Processing status

    Attributes:
        id: Unique bookmark identifier
        url: Bookmark URL
        title: Bookmark title
        original_folder: Browser folder path (e.g., "Work/DevOps")
        add_date: Original browser bookmark date
        domain: Extracted domain (computed from URL)
        tags: AI-generated semantic tags (Week 2)
        summary: AI-generated 2-3 sentence summary (Week 2)
        content_type: Classification (tutorial/documentation/article/video/tool)
        processed: Whether AI processing completed (Week 2)
        processed_at: When AI processing completed (Week 2)
        import_job_id: Which import job created this bookmark
        created_at: When bookmark was imported
        updated_at: Last modification timestamp
    """

    __tablename__ = "bookmarks"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # For future multi-user support (commented out for Task 4)
    # user_id: Mapped[uuid.UUID] = mapped_column(
    #     UUID(as_uuid=True),
    #     ForeignKey("users.id", ondelete="CASCADE"),
    #     nullable=False,
    #     index=True,
    # )

    # For future project assignment (Week 2 feature)
    # project_id: Mapped[uuid.UUID | None] = mapped_column(
    #     UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL")
    # )

    # Original bookmark data
    url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    original_folder: Mapped[str | None] = mapped_column(Text)
    add_date: Mapped[datetime | None] = mapped_column()

    # Computed field (extracted from URL)
    domain: Mapped[str | None] = mapped_column(String(255), index=True)

    # AI-generated metadata (Week 2 features, but schema ready now)
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), default=list
    )  # GIN index added in migration
    summary: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str | None] = mapped_column(String(50))
    processed: Mapped[bool] = mapped_column(default=False, index=True)
    processed_at: Mapped[datetime | None] = mapped_column()

    # Import tracking
    import_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("import_jobs.id", ondelete="SET NULL"),
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    import_job: Mapped["ImportJob"] = relationship(
        back_populates="bookmarks",
        lazy="selectin",  # Prevent N+1 queries in async
    )

    # Future relationships (commented out for Task 4)
    # user: Mapped["User"] = relationship(back_populates="bookmarks")
    # project: Mapped["Project"] = relationship(back_populates="bookmarks")
    # clusters: Mapped[list["Cluster"]] = relationship(
    #     secondary="bookmark_clusters", back_populates="bookmarks"
    # )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "content_type IS NULL OR content_type IN ('tutorial', 'documentation', 'article', 'video', 'tool')",
            name="valid_content_type",
        ),
        # Unique URL per user (commented out until multi-user support)
        # UniqueConstraint("user_id", "url", name="unique_user_url"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Bookmark(id={self.id}, title='{self.title[:30]}...', url='{self.url[:50]}...')>"
