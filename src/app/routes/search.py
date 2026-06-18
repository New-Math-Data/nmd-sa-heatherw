"""Search and extraction API routes.

TODO: Wire up the BedrockService to implement these endpoints.
The service class (src/services/bedrock.py) is fully implemented — you just need to:
1. Import and instantiate BedrockService
2. Use generate_embedding() for search
3. Use extract_fields() for extraction
4. Query pgvector using cosine distance (<=> operator)
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from models.schemas import (
    FieldExtractionRequest,
    FieldExtractionResponse,
    SearchRequest,
    SearchResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.post("/search", response_model=list[SearchResult])
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Search documents using vector similarity.

    TODO: Implement this endpoint by:
    1. Instantiating BedrockService (from services.bedrock)
    2. Calling generate_embedding(request.query) to get the query vector
    3. Using pgvector's cosine distance operator (<=>) to find similar documents
    4. Returning results as a list of SearchResult

    Hint — pgvector cosine distance query:
        SELECT *, embedding <=> '<vector>'::vector AS distance
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY distance
        LIMIT :top_k
    """
    logger.info("Search requested: %s", request.query)
    return JSONResponse(
        status_code=501,
        content={
            "detail": "Search endpoint not wired up. "
            "BedrockService is implemented — connect it to this route. "
            "See the TODO in this file and src/services/bedrock.py."
        },
    )


@router.post("/extract", response_model=FieldExtractionResponse)
async def extract_fields(
    request: FieldExtractionRequest,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Extract structured fields from a document using an LLM.

    TODO: Implement this endpoint by:
    1. Loading the document from the database by request.document_id
    2. Instantiating BedrockService (from services.bedrock)
    3. Calling extract_fields(document.content, request.fields)
    4. Returning a FieldExtractionResponse
    """
    logger.info("Field extraction requested for document: %s", request.document_id)
    return JSONResponse(
        status_code=501,
        content={
            "detail": "Extract endpoint not wired up. "
            "BedrockService is implemented — connect it to this route. "
            "See the TODO in this file and src/services/bedrock.py."
        },
    )
