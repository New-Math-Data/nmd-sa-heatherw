"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.search import router as search_router
from db.engine import create_tables

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — run startup/shutdown tasks."""
    logger.info("Starting up: creating database tables")
    await create_tables()
    yield


app = FastAPI(
    title="SA Assessment API",
    description="Document management and semantic search API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(documents_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
