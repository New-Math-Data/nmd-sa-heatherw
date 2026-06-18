"""Database engine and session management."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from common.settings import get_settings
from models.database import Base

logger = logging.getLogger(__name__)

settings = get_settings()

# Note: No SSL configuration here — works for both local docker-compose and RDS
# (RDS in the assessment account does not enforce SSL).
engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Yield a database session for FastAPI dependency injection."""
    async with async_session() as session:
        yield session


async def create_tables() -> None:
    """Create pgvector extension and all database tables.

    This is called once on application startup via the FastAPI lifespan event.
    """
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")
