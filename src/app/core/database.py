"""Database engine and session management with SQLAlchemy 2.0 async patterns."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Using SQLAlchemy 2.0 declarative style with Mapped types.
    """

    pass


# Global engine instance
# Using module-level to ensure single engine across application
engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    echo=settings.database_echo,
    pool_pre_ping=settings.database_pool_pre_ping,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    # For testing with Testcontainers, use NullPool in test environment
    poolclass=NullPool if settings.environment == "test" else None,
)

# Session factory
# expire_on_commit=False maintains object connection after commit
# Critical for async to avoid "object is not bound" errors
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Yields an async session and ensures proper cleanup.
    Use with FastAPI's Depends():

    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in Base metadata.
    Used for development and testing.

    For production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    """Dispose of database engine and close all connections.

    Should be called on application shutdown.
    """
    await engine.dispose()


def get_test_engine(database_url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create engine and session factory for testing.

    Args:
        database_url: Test database connection URL (from Testcontainers)

    Returns:
        Tuple of (engine, session_factory)

    Example:
        engine, session_factory = get_test_engine(
            "postgresql+asyncpg://test:test@localhost:5555/test"
        )
    """
    test_engine = create_async_engine(
        database_url,
        echo=False,
        poolclass=NullPool,  # No pooling for tests
    )

    test_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return test_engine, test_session_factory
