"""Invoice intake query helpers — document upload + invoice shell creation."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Invoice, UploadedDocument


async def insert_uploaded_document(
    session: AsyncSession,
    *,
    farm_id: UUID,
    source_type: str,
    original_filename: str | None,
    storage_path: str,
    file_size_bytes: int | None,
    mime_type: str | None,
) -> UploadedDocument:
    """Insert a new uploaded document. Returns the created row."""
    doc = UploadedDocument(
        farm_id=farm_id,
        source_type=source_type,
        original_filename=original_filename,
        storage_path=storage_path,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
    )
    session.add(doc)
    await session.flush()
    await session.refresh(doc)
    return doc


async def insert_invoice_shell(
    session: AsyncSession,
    *,
    farm_id: UUID,
    uploaded_document_id: UUID,
    supplier_id: UUID | None = None,
    status: str = "uploaded",
) -> Invoice:
    """Insert an invoice shell (header only, no lines). Returns the created row."""
    invoice = Invoice(
        farm_id=farm_id,
        uploaded_document_id=uploaded_document_id,
        supplier_id=supplier_id,
        status=status,
    )
    session.add(invoice)
    await session.flush()
    await session.refresh(invoice)
    return invoice


async def get_invoice_shell_by_id(
    session: AsyncSession,
    *,
    invoice_id: UUID,
    farm_id: UUID,
) -> Invoice | None:
    """Fetch an invoice by ID, scoped to farm. Returns None if not found."""
    result = await session.execute(
        select(Invoice).where(
            Invoice.id == invoice_id,
            Invoice.farm_id == farm_id,
        )
    )
    return result.scalar_one_or_none()


async def get_uploaded_document_by_id(
    session: AsyncSession,
    *,
    document_id: UUID,
    farm_id: UUID,
) -> UploadedDocument | None:
    """Fetch an uploaded document by ID, scoped to farm."""
    result = await session.execute(
        select(UploadedDocument).where(
            UploadedDocument.id == document_id,
            UploadedDocument.farm_id == farm_id,
        )
    )
    return result.scalar_one_or_none()
