"""Temporary in-memory cache for processing results.

Alerts and explanations are not persisted to DB yet.
This will be replaced by persistence tables.
"""

from __future__ import annotations

_cache: dict[str, object] = {}


def get_result(invoice_id: str) -> object | None:
    """Retrieve cached result for an invoice."""
    return _cache.get(invoice_id)


def set_result(invoice_id: str, result: object) -> None:
    """Cache a processing result for an invoice."""
    _cache[invoice_id] = result


def delete_result(invoice_id: str) -> None:
    """Remove a cached result."""
    _cache.pop(invoice_id, None)
