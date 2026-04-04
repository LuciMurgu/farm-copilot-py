"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from farm_copilot.api.logging_config import setup_logging
from farm_copilot.api.routes.anaf import router as anaf_router
from farm_copilot.api.routes.invoice import router as invoice_router
from farm_copilot.api.routes.upload import router as upload_router
from farm_copilot.api.templates import STATIC_DIR
from farm_copilot.worker.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """FastAPI lifespan — start/stop background scheduler."""
    setup_logging()
    start_scheduler()
    yield
    await stop_scheduler()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    application = FastAPI(
        title="Farm Copilot",
        description="Invoice processing pipeline for Romanian farms",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Static files
    application.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Routes
    application.include_router(upload_router)
    application.include_router(invoice_router)
    application.include_router(anaf_router)

    return application


app = create_app()
