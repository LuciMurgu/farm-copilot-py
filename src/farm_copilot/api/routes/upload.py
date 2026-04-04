"""Upload routes — GET / (upload form) + POST /upload."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from farm_copilot.api import result_cache
from farm_copilot.api.deps import get_db
from farm_copilot.api.templates import templates
from farm_copilot.database.invoice_intake import (
    insert_invoice_shell,
    insert_uploaded_document,
)
from farm_copilot.worker.xml_invoice_processing import (
    resolve_xml_invoice_processing,
)

router = APIRouter()

# Hardcoded farm_id for pilot (single-farm mode)
_PILOT_FARM_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

# Upload storage directory
_UPLOAD_DIR = Path("uploads")


@router.get("/")
async def upload_page(request: Request) -> object:
    """Render the upload form."""
    return templates.TemplateResponse(
        request=request,
        name="upload.html",
    )


@router.post("/upload")
async def upload_invoice(
    request: Request,
    file: UploadFile,
    session: AsyncSession = Depends(get_db),
) -> object:
    """Handle XML file upload → intake → pipeline → redirect to detail."""
    # 1. Validate file
    if not file.filename or not file.filename.lower().endswith(".xml"):
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={"error": "Only XML files are supported."},
            status_code=400,
        )

    # 2. Save file to disk
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_id = uuid.uuid4()
    storage_path = _UPLOAD_DIR / f"{file_id}.xml"

    with storage_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = storage_path.stat().st_size

    # 3. Insert uploaded document
    doc = await insert_uploaded_document(
        session,
        farm_id=_PILOT_FARM_ID,
        source_type="xml",
        original_filename=file.filename,
        storage_path=str(storage_path),
        file_size_bytes=file_size,
        mime_type=file.content_type,
    )

    # 4. Insert invoice shell
    invoice = await insert_invoice_shell(
        session,
        farm_id=_PILOT_FARM_ID,
        uploaded_document_id=doc.id,
    )

    await session.commit()

    # 5. Run pipeline
    async with session.begin():
        result = await resolve_xml_invoice_processing(
            session,
            invoice_id=invoice.id,
            farm_id=_PILOT_FARM_ID,
        )

    # 6. Cache result (alerts/explanations)
    result_cache.set_result(str(invoice.id), result)

    # 7. Redirect to invoice detail
    return RedirectResponse(
        url=f"/invoice/{invoice.id}",
        status_code=303,
    )
