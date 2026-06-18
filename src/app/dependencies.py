"""FastAPI dependency injection providers."""

from db.engine import get_db

__all__ = ["get_db"]
