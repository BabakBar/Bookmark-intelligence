"""ImportJob model for tracking bookmark import progress and costs.

Follows SQLAlchemy 2.0 modern patterns with Mapped type annotations.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.app.core.database import Base

if TYPE_CHECKING:
    from src.app.models.bookmark import Bookmark


class ImportJob(Base):
    """Tracks HTML import and AI processing jobs.

    State transitions:
        pending → importing → processing → clustering → completed
                                                    ↓
                                                 failed

    Attributes:
        id: Unique job identifier
        user_id: Owner of the import (currently unused, for future multi-user)
        filename: Original uploaded HTML filename
        file_size_bytes: File size in bytes
        total_bookmarks: Total bookmarks found in HTML
        status: Current job status
        progress: Overall progress percentage (0-100)
        imported_count: Bookmarks successfully imported
        embeddings_generated: Embeddings generated (Week 2 feature)
        tags_generated: Tags/summaries generated (Week 2 feature)
        failed_count: Bookmarks that failed processing
        total_cost_usd: Total AI processing cost
        openai_cost_usd: OpenAI embedding cost
        claude_cost_usd: Claude tagging cost
        error_message: Human-readable error if failed
        error_details: Structured error data (JSONB)
        started_at: Job start timestamp
        completed_at: Job completion timestamp
        created_at: Job creation timestamp
    """

    __tablename__ = "import_jobs"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # For future multi-user support (currently unused in Task 4)
    # user_id: Mapped[uuid.UUID] = mapped_column(
    #     UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    # )

    # Job metadata
    filename: Mapped[str | None] = mapped_column(String(255))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    total_bookmarks: Mapped[int] = mapped_column(Integer, default=0)

    # Progress tracking
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)

    # Processing stages (Week 2 features, but tracked now)
    imported_count: Mapped[int] = mapped_column(Integer, default=0)
    embeddings_generated: Mapped[int] = mapped_column(Integer, default=0)
    tags_generated: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    # Cost tracking (for Week 2 AI processing)
    total_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("0.00")
    )
    openai_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("0.00")
    )
    claude_cost_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=Decimal("0.00")
    )

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text)
    error_details: Mapped[dict | None] = mapped_column(JSONB)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column()
    completed_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), index=True
    )

    # Relationships
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="import_job",
        lazy="selectin",  # Prevent N+1 queries in async
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'importing', 'processing', 'clustering', 'completed', 'failed')",
            name="valid_status",
        ),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<ImportJob(id={self.id}, status={self.status}, "
            f"imported={self.imported_count}/{self.total_bookmarks})>"
        )
