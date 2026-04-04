"""Dependencies — database session, auth helpers, app settings."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from fastapi.responses import RedirectResponse
from pydantic_settings import BaseSettings

from farm_copilot.database.session import get_db


class AppSettings(BaseSettings):
    """Application settings from environment."""

    session_secret_key: str = "CHANGE-ME-IN-PRODUCTION"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


app_settings = AppSettings()


def get_current_user_id(request: Request) -> UUID | None:
    """Extract user_id from session. Returns None if not logged in."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return UUID(user_id)


def get_current_farm_id(request: Request) -> UUID | None:
    """Extract active farm_id from session. Returns None if not set."""
    farm_id = request.session.get("farm_id")
    if not farm_id:
        return None
    return UUID(farm_id)


def require_auth(request: Request) -> UUID:
    """Get farm_id from session or raise redirect to login.

    Use in route handlers: farm_id = require_auth(request)
    """
    farm_id = get_current_farm_id(request)
    if farm_id is None:
        raise RedirectResponse(url="/login", status_code=302)  # type: ignore[misc]
    return farm_id


__all__ = [
    "AppSettings",
    "app_settings",
    "get_current_farm_id",
    "get_current_user_id",
    "get_db",
    "require_auth",
]
