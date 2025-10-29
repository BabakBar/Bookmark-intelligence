"""Pydantic validation schemas for bookmarks and folders"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BookmarkSchema(BaseModel):
    """Pydantic schema for bookmark validation"""

    url: str = Field(..., min_length=1, description="Bookmark URL")
    title: str = Field(..., description="Bookmark title")
    domain: str = Field(..., description="Extracted domain")
    add_date: Optional[int] = Field(None, description="Unix timestamp when bookmark was added")
    folder_path: List[str] = Field(default_factory=list, description="Folder hierarchy path")
    added_date: Optional[datetime] = Field(None, description="ISO format added date")
    added_timestamp: Optional[int] = Field(None, description="Unix timestamp (duplicate of add_date)")

    @field_validator('url')
    @classmethod
    def validate_url_not_file(cls, v: str) -> str:
        """Ensure URL is not a file:// URL"""
        if v.startswith('file://'):
            raise ValueError('file:// URLs are not allowed')
        return v

    @field_validator('add_date')
    @classmethod
    def validate_timestamp(cls, v: Optional[int]) -> Optional[int]:
        """Ensure timestamp is reasonable (after 2000-01-01)"""
        if v is not None and v < 946684800:  # 2000-01-01 00:00:00 UTC
            raise ValueError('Timestamp must be after 2000-01-01')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://github.com/anthropics/claude-code",
                "title": "Claude Code Repository",
                "domain": "github.com",
                "add_date": 1698768000,
                "folder_path": ["Bookmarks bar", "Dev", "AI Tools"],
            }
        }
    }


class FolderSchema(BaseModel):
    """Pydantic schema for folder validation"""

    name: str = Field(..., min_length=1, description="Folder name")
    path: str = Field(..., description="Full folder path (formatted)")
    bookmark_count: int = Field(..., ge=0, description="Number of bookmarks in folder")
    subfolder_count: int = Field(..., ge=0, description="Number of subfolders")
    last_modified: Optional[int] = Field(None, description="Unix timestamp when folder was last modified")
    last_modified_date: Optional[datetime] = Field(None, description="ISO format last modified date")
    last_modified_timestamp: Optional[int] = Field(None, description="Unix timestamp (duplicate)")

    @field_validator('last_modified')
    @classmethod
    def validate_timestamp(cls, v: Optional[int]) -> Optional[int]:
        """Ensure timestamp is reasonable (after 2000-01-01)"""
        if v is not None and v < 946684800:  # 2000-01-01 00:00:00 UTC
            raise ValueError('Timestamp must be after 2000-01-01')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Dev",
                "path": "Bookmarks bar > Dev",
                "bookmark_count": 42,
                "subfolder_count": 3,
                "last_modified": 1698768000,
            }
        }
    }
