"""Application configuration using Pydantic Settings v2."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support.

    Follows modern Pydantic v2 patterns with model_config.
    Environment variables are loaded from .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "BookmarkAI"
    app_version: str = "0.1.0"
    environment: Literal["development", "production", "test"] = "development"
    debug: bool = Field(default=False, description="Enable debug mode")

    # Database (PostgreSQL 17)
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/bookmarkai",
        description="Async PostgreSQL connection URL",
    )
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    database_pool_pre_ping: bool = Field(default=True, description="Verify connections before use")
    database_echo: bool = Field(default=False, description="Echo SQL queries (debug)")

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # API
    api_v1_prefix: str = "/api/v1"

    @property
    def async_database_url(self) -> str:
        """Get async database URL as string."""
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Using lru_cache ensures we only create one Settings instance
    during the application lifecycle, improving performance.
    """
    return Settings()


# Convenience export
settings = get_settings()
