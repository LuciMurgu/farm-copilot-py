"""Invoice routes — detail view, reprocess, correct line."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from farm_copilot.api import result_cache
from farm_copilot.api.deps import get_db
from farm_copilot.api.templates import templates
from farm_copilot.database.invoice_intake import get_invoice_shell_by_id
from farm_copilot.database.invoice_line_items import (
    get_invoice_line_items_by_invoice_id,
)
from farm_copilot.worker.line_correction import apply_unresolved_line_correction
from farm_copilot.worker.xml_invoice_processing import (
    resolve_xml_invoice_processing,
)

router = APIRouter()

_PILOT_FARM_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("/invoice/{invoice_id}")
async def invoice_detail(
    request: Request,
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> object:
    """Render the invoice detail page with lines, alerts, explanations."""
    invoice = await get_invoice_shell_by_id(
        session, invoice_id=invoice_id, farm_id=_PILOT_FARM_ID
    )
    if invoice is None:
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "error": "Invoice not found."},
            status_code=404,
        )

    line_items = await get_invoice_line_items_by_invoice_id(
        session, invoice_id=invoice_id, farm_id=_PILOT_FARM_ID
    )

    # Retrieve cached processing result
    cached = result_cache.get_result(str(invoice_id))

    alerts = []
    explanations = []
    steps = None

    if cached is not None:
        alerts = getattr(
            getattr(cached, "alerts_payload", None), "alerts", []
        ) or []
        explanations = getattr(
            getattr(cached, "explanations_payload", None), "explanations", []
        ) or []
        steps = getattr(cached, "steps", None)

    return templates.TemplateResponse(
        "invoice_detail.html",
        {
            "request": request,
            "invoice": invoice,
            "line_items": line_items,
            "alerts": alerts,
            "explanations": explanations,
            "steps": steps,
        },
    )


@router.post("/invoice/{invoice_id}/reprocess")
async def reprocess_invoice(
    invoice_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> object:
    """Re-run the full pipeline for an invoice."""
    async with session.begin():
        result = await resolve_xml_invoice_processing(
            session,
            invoice_id=invoice_id,
            farm_id=_PILOT_FARM_ID,
        )

    result_cache.set_result(str(invoice_id), result)

    return RedirectResponse(
        url=f"/invoice/{invoice_id}",
        status_code=303,
    )


@router.post("/invoice/{invoice_id}/correct-line")
async def correct_line(
    invoice_id: uuid.UUID,
    line_item_id: str = Form(...),
    canonical_product_id: str = Form(...),
    reason: str = Form(""),
    session: AsyncSession = Depends(get_db),
) -> object:
    """Apply a line correction (manual product assignment)."""
    async with session.begin():
        correction_result = await apply_unresolved_line_correction(
            session,
            invoice_id=invoice_id,
            farm_id=_PILOT_FARM_ID,
            line_item_id=uuid.UUID(line_item_id),
            new_canonical_product_id=uuid.UUID(canonical_product_id),
            actor="web_ui",
            reason=reason or None,
        )

    # Update cached alerts/explanations if correction was applied
    if correction_result.kind == "applied":
        existing = result_cache.get_result(str(invoice_id))
        if existing is not None and hasattr(correction_result, "alerts_rerun"):
            result_cache.set_result(str(invoice_id), correction_result)

    return RedirectResponse(
        url=f"/invoice/{invoice_id}",
        status_code=303,
    )
