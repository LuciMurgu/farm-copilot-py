"""Product alias query helpers — including 4-tier precedence ordering.

Precedence tiers (when supplier_id is provided):
  Tier 0: farm_id match + supplier_id match (most specific)
  Tier 1: farm_id match + supplier_id NULL
  Tier 2: farm_id NULL + supplier_id match
  Tier 3: farm_id NULL + supplier_id NULL (global)

When supplier_id is None, 2-tier precedence:
  Tier 0: farm_id match + supplier_id NULL
  Tier 1: farm_id NULL + supplier_id NULL
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, case, null, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ProductAlias


async def list_product_aliases_by_canonical_product_id(
    session: AsyncSession,
    *,
    canonical_product_id: UUID,
    farm_id: UUID | None = None,
    supplier_id: UUID | None = None,
    limit: int | None = None,
) -> list[ProductAlias]:
    """List aliases for a canonical product, optionally filtered by
    farm/supplier scope. Ordered by alias_text, then created_at.
    """
    stmt = select(ProductAlias).where(
        ProductAlias.canonical_product_id == canonical_product_id,
    )
    if farm_id is not None:
        stmt = stmt.where(ProductAlias.farm_id == farm_id)
    if supplier_id is not None:
        stmt = stmt.where(ProductAlias.supplier_id == supplier_id)
    stmt = stmt.order_by(ProductAlias.alias_text, ProductAlias.created_at)
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_product_aliases_by_alias_text(
    session: AsyncSession,
    *,
    alias_text: str,
    farm_id: UUID | None = None,
    supplier_id: UUID | None = None,
    limit: int | None = None,
) -> list[ProductAlias]:
    """List aliases matching exact alias_text, optionally filtered
    by scope. Ordered by canonical_product_id, then created_at.
    """
    stmt = select(ProductAlias).where(
        ProductAlias.alias_text == alias_text,
    )
    if farm_id is not None:
        stmt = stmt.where(ProductAlias.farm_id == farm_id)
    if supplier_id is not None:
        stmt = stmt.where(ProductAlias.supplier_id == supplier_id)
    stmt = stmt.order_by(ProductAlias.canonical_product_id, ProductAlias.created_at)
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_visible_product_aliases_by_alias_text(
    session: AsyncSession,
    *,
    alias_text: str,
    farm_id: UUID,
    supplier_id: UUID | None = None,
    limit: int | None = None,
) -> list[ProductAlias]:
    """List aliases visible to a farm context.

    Visibility rules:
    - Farm: global (NULL) OR matching farm_id
    - Supplier: if provided, global (NULL) OR matching supplier_id.
      If not provided, only global (NULL supplier) aliases.
    """
    stmt = select(ProductAlias).where(
        ProductAlias.alias_text == alias_text,
        ProductAlias.farm_id.in_([farm_id]) | ProductAlias.farm_id.is_(None),
    )
    if supplier_id is not None:
        stmt = stmt.where(
            ProductAlias.supplier_id.in_([supplier_id])
            | ProductAlias.supplier_id.is_(None),
        )
    else:
        stmt = stmt.where(ProductAlias.supplier_id.is_(None))

    stmt = stmt.order_by(ProductAlias.canonical_product_id, ProductAlias.created_at)
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _precedence_case(farm_id: UUID, supplier_id: UUID | None):  # noqa: ANN202
    """Build a CASE expression for 4-tier (or 2-tier) precedence ordering."""
    if supplier_id is not None:
        return case(
            (
                and_(
                    ProductAlias.farm_id == farm_id,
                    ProductAlias.supplier_id == supplier_id,
                ),
                0,
            ),
            (
                and_(
                    ProductAlias.farm_id == farm_id,
                    ProductAlias.supplier_id == null(),
                ),
                1,
            ),
            (
                and_(
                    ProductAlias.farm_id == null(),
                    ProductAlias.supplier_id == supplier_id,
                ),
                2,
            ),
            else_=3,
        )
    return case(
        (
            and_(
                ProductAlias.farm_id == farm_id,
                ProductAlias.supplier_id == null(),
            ),
            0,
        ),
        else_=1,
    )


async def list_precedence_ordered_visible_aliases(
    session: AsyncSession,
    *,
    alias_text: str,
    farm_id: UUID,
    supplier_id: UUID | None = None,
    limit: int | None = None,
) -> list[ProductAlias]:
    """Like list_visible but ordered by 4-tier precedence.

    When supplier_id is None, uses 2-tier: farm-specific (0), global (1).
    """
    precedence = _precedence_case(farm_id, supplier_id)

    stmt = select(ProductAlias).where(
        ProductAlias.alias_text == alias_text,
        ProductAlias.farm_id.in_([farm_id]) | ProductAlias.farm_id.is_(None),
    )
    if supplier_id is not None:
        stmt = stmt.where(
            ProductAlias.supplier_id.in_([supplier_id])
            | ProductAlias.supplier_id.is_(None),
        )
    else:
        stmt = stmt.where(ProductAlias.supplier_id.is_(None))

    stmt = stmt.order_by(precedence, ProductAlias.created_at)
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
