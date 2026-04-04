"""Stock movement query helpers — idempotent insert + list."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import StockMovement


async def insert_stock_movement_idempotent(
    session: AsyncSession,
    *,
    farm_id: UUID,
    canonical_product_id: UUID,
    direction: str,
    quantity: Decimal,
    unit: str,
    idempotency_key: str,
    effective_at: datetime,
    invoice_id: UUID | None = None,
    invoice_line_item_id: UUID | None = None,
    notes: str | None = None,
) -> tuple[StockMovement, bool]:
    """Insert a stock movement with ON CONFLICT DO NOTHING on
    ``(farm_id, idempotency_key)``.

    Returns ``(row, created)`` where ``created=True`` if inserted,
    ``False`` if already existed.
    """
    stmt = (
        pg_insert(StockMovement)
        .values(
            farm_id=farm_id,
            canonical_product_id=canonical_product_id,
            direction=direction,
            quantity=quantity,
            unit=unit,
            idempotency_key=idempotency_key,
            effective_at=effective_at,
            invoice_id=invoice_id,
            invoice_line_item_id=invoice_line_item_id,
            notes=notes,
        )
        .on_conflict_do_nothing(
            index_elements=["farm_id", "idempotency_key"],
        )
        .returning(StockMovement)
    )

    result = await session.execute(stmt)
    row = result.scalar_one_or_none()

    if row is not None:
        return (row, True)

    # Conflict — fetch existing row
    existing = await session.execute(
        select(StockMovement).where(
            StockMovement.farm_id == farm_id,
            StockMovement.idempotency_key == idempotency_key,
        )
    )
    return (existing.scalar_one(), False)


async def list_stock_movements_by_invoice_id(
    session: AsyncSession,
    *,
    farm_id: UUID,
    invoice_id: UUID,
) -> list[StockMovement]:
    """List all stock movements linked to a specific invoice."""
    result = await session.execute(
        select(StockMovement).where(
            StockMovement.farm_id == farm_id,
            StockMovement.invoice_id == invoice_id,
        ).order_by(StockMovement.effective_at)
    )
    return list(result.scalars().all())
