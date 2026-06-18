"""Search and extraction API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from common.settings import get_settings
from models.schemas import (
    FieldExtractionRequest,
    FieldExtractionResponse,
    SearchRequest,
    SearchResult,
)
from services.bedrock import BedrockService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


def _get_bedrock_service() -> BedrockService:
    """Create a BedrockService instance from app settings."""
    settings = get_settings()
    return BedrockService(
        region=settings.aws_region or "us-west-2",
        profile=settings.aws_profile,
    )


@router.post("/search", response_model=list[SearchResult])
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> list[SearchResult]:
    """Search documents using vector similarity."""
    logger.info("Search requested: %s", request.query)

    bedrock = _get_bedrock_service()
    embedding = await bedrock.generate_embedding(request.query)

    # pgvector cosine distance query
    # Use CAST() instead of :: to avoid conflict with SQLAlchemy's :param syntax
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    query = text("""
        SELECT id, title, content, metadata,
               1 - (embedding <=> CAST(:embedding AS vector)) AS score
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """)

    result = await db.execute(query, {"embedding": embedding_str, "top_k": request.top_k})
    rows = result.fetchall()

    return [
        SearchResult(
            id=row.id,
            title=row.title,
            content=row.content,
            score=row.score,
            metadata_=row.metadata,
        )
        for row in rows
    ]


@router.post("/extract", response_model=FieldExtractionResponse)
async def extract_fields(
    request: FieldExtractionRequest,
    db: AsyncSession = Depends(get_db),
) -> FieldExtractionResponse:
    """Extract structured fields from a document using an LLM."""
    logger.info("Field extraction requested for document: %s", request.document_id)

    # Load document from DB
    query = text("SELECT id, content FROM documents WHERE id = :doc_id")
    result = await db.execute(query, {"doc_id": str(request.document_id)})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    bedrock = _get_bedrock_service()
    extracted = await bedrock.extract_fields(row.content, request.fields)

    return FieldExtractionResponse(
        document_id=request.document_id,
        extracted_fields=extracted,
    )
