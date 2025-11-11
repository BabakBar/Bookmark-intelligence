from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import tempfile

from bookmark_intelligence.parsers import BookmarkParser

router = APIRouter()

@router.post("/")
async def import_bookmarks(file: UploadFile = File(...)):
    """
    Uploads a bookmarks HTML file, parses it, and returns the parsed data.
    """
    if not file.filename.endswith(".html"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an HTML file.")

    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        # Parse the bookmarks file
        parser = BookmarkParser(tmp_path)
        parser.parse()
        bookmarks = parser.get_flat_bookmarks()

        # Clean up the temporary file
        tmp_path.unlink()

        return {
            "message": f"Successfully parsed {len(bookmarks)} bookmarks from {file.filename}",
            "bookmarks": bookmarks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while parsing the file: {e}")
    finally:
        await file.close()
