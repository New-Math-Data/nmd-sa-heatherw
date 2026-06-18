"""Document service — async CRUD operations for the Document model."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Document
from models.schemas import DocumentCreate


async def list_documents(session: AsyncSession) -> list[Document]:
    """Retrieve all documents ordered by creation date (newest first)."""
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def create_document(session: AsyncSession, payload: DocumentCreate) -> Document:
    """Create a new document and persist it to the database."""
    document = Document(
        id=uuid.uuid4(),
        title=payload.title,
        content=payload.content,
        metadata_=payload.metadata_ if payload.metadata_ else {},
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def get_document_by_id(session: AsyncSession, document_id: uuid.UUID) -> Document | None:
    """Retrieve a single document by its primary key. Returns None if not found."""
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()
