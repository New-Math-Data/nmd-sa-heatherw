"""Document API routes."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from models.database import Document
from models.schemas import DocumentCreate, DocumentResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)) -> list[DocumentResponse]:
    """List all documents."""
    logger.info("Listing documents")
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    return [DocumentResponse.from_orm_document(doc) for doc in documents]


# BUG: Should return 201 with Location header — returns 200 instead
@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate, db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Create a new document."""
    logger.info("Creating document: %s", document.title)
    db_document = Document(
        title=document.title,
        content=document.content,
        metadata_=document.metadata_ if document.metadata_ else {},
    )
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return DocumentResponse.from_orm_document(db_document)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID, db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """Get a document by ID."""
    logger.info("Getting document: %s", document_id)
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.from_orm_document(document)
