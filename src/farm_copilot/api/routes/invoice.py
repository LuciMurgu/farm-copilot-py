"""Invoice routes — detail view, reprocess, correct line."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from farm_copilot.api.deps import get_current_farm_id, get_db
from farm_copilot.api.templates import templates
from farm_copilot.database.invoice_alerts import get_alerts_by_invoice_id
from farm_copilot.database.invoice_explanations import (
    get_explanations_by_invoice_id,
)
from farm_copilot.database.invoice_intake import get_invoice_shell_by_id
from farm_copilot.database.invoice_line_items import (
    get_invoice_line_items_by_invoice_id,
)
from farm_copilot.worker.line_correction import apply_unresolved_line_correction
from farm_copilot.worker.xml_invoice_processing import (
    resolve_xml_invoice_processing,
)

router = APIRouter()


@router.get("/invoice/{invoice_id}")
async def invoice_detail(
    request: Request,
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> object:
    """Render the invoice detail page with lines, alerts, explanations."""
    farm_id = get_current_farm_id(request)
    if farm_id is None:
        return RedirectResponse(url="/login", status_code=302)

    invoice = await get_invoice_shell_by_id(
        session, invoice_id=invoice_id, farm_id=farm_id
    )
    if invoice is None:
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={"error": "Invoice not found."},
            status_code=404,
        )

    line_items = await get_invoice_line_items_by_invoice_id(
        session, invoice_id=invoice_id, farm_id=farm_id
    )

    alert_records = await get_alerts_by_invoice_id(
        session, invoice_id=invoice_id, farm_id=farm_id
    )
    explanation_records = await get_explanations_by_invoice_id(
        session, invoice_id=invoice_id, farm_id=farm_id
    )

    return templates.TemplateResponse(
        request=request,
        name="invoice_detail.html",
        context={
            "invoice": invoice,
            "line_items": line_items,
            "alerts": alert_records,
            "explanations": explanation_records,
            "steps": None,
        },
    )


@router.post("/invoice/{invoice_id}/reprocess")
async def reprocess_invoice(
    request: Request,
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> object:
    """Re-run the full pipeline for an invoice."""
    farm_id = get_current_farm_id(request)
    if farm_id is None:
        return RedirectResponse(url="/login", status_code=302)

    async with session.begin():
        await resolve_xml_invoice_processing(
            session,
            invoice_id=invoice_id,
            farm_id=farm_id,
        )

    return RedirectResponse(
        url=f"/invoice/{invoice_id}",
        status_code=303,
    )


@router.post("/invoice/{invoice_id}/correct-line")
async def correct_line(
    request: Request,
    invoice_id: uuid.UUID,
    line_item_id: str = Form(...),
    canonical_product_id: str = Form(...),
    reason: str = Form(""),
    session: AsyncSession = Depends(get_db),
) -> object:
    """Apply a line correction (manual product assignment)."""
    farm_id = get_current_farm_id(request)
    if farm_id is None:
        return RedirectResponse(url="/login", status_code=302)

    async with session.begin():
        await apply_unresolved_line_correction(
            session,
            invoice_id=invoice_id,
            farm_id=farm_id,
            line_item_id=uuid.UUID(line_item_id),
            new_canonical_product_id=uuid.UUID(canonical_product_id),
            actor="web_ui",
            reason=reason or None,
        )

    return RedirectResponse(
        url=f"/invoice/{invoice_id}",
        status_code=303,
    )
