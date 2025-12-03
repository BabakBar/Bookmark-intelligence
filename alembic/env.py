"""Alembic environment configuration for async SQLAlchemy 2.0.

This configuration supports:
- Async database engine (asyncpg)
- Auto-generation from SQLAlchemy models
- Environment variable configuration
- Both offline and online migration modes
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import Base and models for autogenerate support
from src.app.core.database import Base
from src.app.core.config import settings

# Import all models to ensure they're registered with Base.metadata
from src.app.models import Bookmark, ImportJob  # noqa: F401

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
# Fix: disable_existing_loggers=False prevents conflicts with app logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Set target metadata from Base for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url from settings if available
if settings.async_database_url:
    config.set_main_option("sqlalchemy.url", settings.async_database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    By skipping the Engine creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the provided connection.

    Called by run_migrations_online() after establishing connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode.

    Creates an async engine and runs migrations within an async context.
    This is the modern approach for async SQLAlchemy applications.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an async Engine
    and associate a connection with the context.
    """
    asyncio.run(run_async_migrations())


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
