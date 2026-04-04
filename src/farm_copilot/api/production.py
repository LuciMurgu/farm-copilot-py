"""Production entry point — runs migrations then starts uvicorn.

Usage: python -m farm_copilot.api.production
Docker CMD: ["python", "-m", "farm_copilot.api.production"]
"""

from __future__ import annotations

import logging
import subprocess
import sys

import uvicorn

from farm_copilot.api.logging_config import setup_logging


def run_migrations() -> None:
    """Run Alembic migrations before starting the server."""
    logger = logging.getLogger(__name__)
    logger.info("Running database migrations...")
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error("Migration failed: %s", result.stderr)
        sys.exit(1)
    logger.info("Migrations complete: %s", result.stdout.strip())


def main() -> None:
    """Start production server with auto-migrations."""
    setup_logging()
    run_migrations()

    uvicorn.run(
        "farm_copilot.api.app:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        workers=1,  # Single worker — scheduler runs in-process
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
