"""Pydantic v2 schemas for API request/response models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Schema for creating a new document."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    metadata_: dict | None = Field(default=None, alias="metadata")

    model_config = {"populate_by_name": True}


class DocumentResponse(BaseModel):
    """Schema for document API responses."""

    id: UUID
    title: str
    content: str
    metadata_: dict | None = Field(default=None, alias="metadata")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

    @classmethod
    def from_orm_document(cls, doc) -> "DocumentResponse":
        """Create from a SQLAlchemy Document, avoiding the metadata name collision.

        DeclarativeBase exposes a class-level .metadata attribute (MetaData registry).
        Pydantic's from_attributes mode with alias="metadata" would resolve to that
        instead of the instance column value (metadata_). This method reads the
        correct attribute explicitly.
        """
        return cls(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            metadata_=doc.metadata_,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )


class SearchRequest(BaseModel):
    """Schema for semantic search requests."""

    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    """Schema for a single search result."""

    id: UUID
    title: str
    content: str
    score: float
    metadata_: dict | None = Field(default=None, alias="metadata")

    model_config = {"from_attributes": True, "populate_by_name": True}


class FieldExtractionRequest(BaseModel):
    """Schema for field extraction requests."""

    document_id: UUID
    fields: list[str] = Field(..., min_length=1)


class FieldExtractionResponse(BaseModel):
    """Schema for field extraction responses."""

    document_id: UUID
    extracted_fields: dict[str, str | None]
