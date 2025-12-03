"""FastAPI application with modern async patterns.

Uses lifespan context manager for startup/shutdown (FastAPI 0.115+).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.v1.endpoints import import_bookmarks
from src.app.core.config import settings
from src.app.core.database import dispose_db, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown.

    Startup:
        - Log application startup
        - Database is assumed to be migrated via Alembic CLI

    Shutdown:
        - Dispose of database connections

    Note: Database migrations should be run before starting the app:
        $ alembic upgrade head

    DO NOT run migrations here - use Alembic CLI for production deployments.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Database: {engine.url.database}")

    yield

    # Shutdown
    print("Shutting down application...")
    await dispose_db()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered bookmark manager with context-aware search",
    version=settings.app_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "message": "Welcome to BookmarkAI API",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# Include API routers
app.include_router(
    import_bookmarks.router,
    prefix=f"{settings.api_v1_prefix}/import",
    tags=["Import"],
)
