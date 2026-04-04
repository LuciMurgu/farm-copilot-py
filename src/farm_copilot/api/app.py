"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from farm_copilot.api.routes.invoice import router as invoice_router
from farm_copilot.api.routes.upload import router as upload_router
from farm_copilot.api.templates import STATIC_DIR


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    application = FastAPI(
        title="Farm Copilot",
        description="Invoice processing pipeline for Romanian farms",
        version="0.1.0",
    )

    # Static files
    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Routes
    application.include_router(upload_router)
    application.include_router(invoice_router)

    return application


app = create_app()
