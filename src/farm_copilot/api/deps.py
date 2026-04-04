"""Database session dependency — re-export from database.session."""

from __future__ import annotations

from farm_copilot.database.session import get_db

__all__ = ["get_db"]
