# Farm Copilot (Python)

Procurement and margin intelligence assistant for Romanian crop farms.

Ported from the TypeScript version. See `CLAUDE.md` for the full project constitution.

## Quick Start

```bash
uv sync
cp .env.example .env
# Edit .env with your DATABASE_URL
uv run uvicorn farm_copilot.api:app --reload
```

## Stack

- Python 3.12+, FastAPI, SQLAlchemy 2.0 async, Pydantic v2
- PostgreSQL (asyncpg), Alembic, lxml, pytest
- uv (package manager), Ruff (linter), pyright (types)
