"""Import bookmarks endpoint with database persistence.

Handles HTML file upload, parses bookmarks, and saves to PostgreSQL.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bookmark_intelligence.parsers import BookmarkParser
from src.app.api.v1.schemas import (
    BookmarkResponse,
    ImportJobResponse,
    ImportSummaryResponse,
)
from src.app.core.database import get_db
from src.app.models import Bookmark, ImportJob

router = APIRouter()


@router.post("/", response_model=ImportSummaryResponse)
async def import_bookmarks(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Import bookmarks from HTML file and save to database.

    This endpoint:
    1. Validates the uploaded file is HTML
    2. Creates an ImportJob record to track progress
    3. Parses bookmarks using BookmarkParser
    4. Saves all bookmarks to PostgreSQL
    5. Updates ImportJob status and counts
    6. Returns import summary with job info

    Args:
        file: Uploaded HTML bookmark file (Chrome/Firefox/Safari format)
        db: Database session (injected)

    Returns:
        ImportSummaryResponse with job info and bookmark preview

    Raises:
        HTTPException 400: Invalid file type (not HTML)
        HTTPException 500: Parsing or database error
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(".html"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an HTML file.",
        )

    # Get file size
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)  # Reset for reading again

    # Create ImportJob record
    import_job = ImportJob(
        filename=file.filename,
        file_size_bytes=file_size,
        status="importing",
        started_at=datetime.utcnow(),
    )

    db.add(import_job)
    await db.commit()
    await db.refresh(import_job)

    tmp_path = None

    try:
        # Create temporary file for parsing
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".html", mode="wb"
        ) as tmp:
            tmp.write(file_content)
            tmp_path = Path(tmp.name)

        # Parse bookmarks using existing parser
        parser = BookmarkParser(tmp_path)
        parser.parse()
        parsed_bookmarks = parser.get_flat_bookmarks()

        # Update total count
        import_job.total_bookmarks = len(parsed_bookmarks)

        # Convert parsed bookmarks to ORM models and save
        bookmark_models = []
        for parsed_bm in parsed_bookmarks:
            bookmark = Bookmark(
                url=parsed_bm["url"],
                title=parsed_bm["title"],
                domain=parsed_bm.get("domain"),
                original_folder="/".join(parsed_bm.get("folder_path", [])) or None,
                add_date=datetime.fromtimestamp(parsed_bm["add_date"])
                if parsed_bm.get("add_date")
                else None,
                import_job_id=import_job.id,
                processed=False,  # AI processing happens in Week 2
            )
            bookmark_models.append(bookmark)

        # Bulk insert bookmarks (more efficient than one-by-one)
        db.add_all(bookmark_models)

        # Update import job status
        import_job.status = "completed"
        import_job.imported_count = len(bookmark_models)
        import_job.progress = 100
        import_job.completed_at = datetime.utcnow()

        await db.commit()

        # Clean up temporary file
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()

        # Fetch saved bookmarks for response (first 10 as preview)
        result = await db.execute(
            select(Bookmark)
            .where(Bookmark.import_job_id == import_job.id)
            .limit(10)
        )
        bookmark_sample = list(result.scalars().all())

        return ImportSummaryResponse(
            message=f"Successfully imported {len(bookmark_models)} bookmarks from {file.filename}",
            import_job=ImportJobResponse.model_validate(import_job),
            bookmarks_count=len(bookmark_models),
            bookmarks_sample=[
                BookmarkResponse.model_validate(bm) for bm in bookmark_sample
            ],
        )

    except Exception as e:
        # Update import job with error
        import_job.status = "failed"
        import_job.error_message = str(e)
        import_job.completed_at = datetime.utcnow()
        await db.commit()

        # Clean up temp file if it exists
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while importing bookmarks: {e}",
        )

    finally:
        await file.close()


@router.get("/{import_job_id}", response_model=ImportJobResponse)
async def get_import_job(
    import_job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get import job status by ID.

    Useful for polling job progress during long imports (Week 2 AI processing).

    Args:
        import_job_id: UUID of the import job
        db: Database session (injected)

    Returns:
        ImportJobResponse with current job status

    Raises:
        HTTPException 404: Import job not found
    """
    result = await db.execute(
        select(ImportJob).where(ImportJob.id == import_job_id)
    )
    import_job = result.scalar_one_or_none()

    if not import_job:
        raise HTTPException(
            status_code=404,
            detail=f"Import job {import_job_id} not found",
        )

    return ImportJobResponse.model_validate(import_job)
