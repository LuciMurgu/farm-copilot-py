# Decisions — Farm Copilot (Python)

## Purpose

This file records binding decisions that are smaller than a full ADR.
For decisions that require extensive context, alternatives analysis, or affect architecture boundaries, use `docs/adr/` instead.

Update this file when a decision is made during a session.

---

## Entry template

Copy and fill in when adding a new decision:

```markdown
### DEC-NNNN — [short title]

- **Date:** YYYY-MM-DD
- **Decision:** [what was decided]
- **Reason:** [why this was chosen]
- **Alternatives rejected:** [what was considered and why not]
```

---

## Decisions

### DEC-0001 — Python 3.12+ with FastAPI/SQLAlchemy/Pydantic as the stack

- **Date:** 2026-04-03
- **Decision:** The Python port uses Python 3.12+, FastAPI (web), SQLAlchemy 2.0 async (ORM), Pydantic v2 (validation), Alembic (migrations), asyncpg (driver), lxml (XML parsing), uvicorn (ASGI server).
- **Reason:** Port from TypeScript codebase. Python ecosystem provides mature async DB support, strong typing with Pydantic, and FastAPI's built-in OpenAPI generation. The architect selected this stack for the port.
- **Alternatives rejected:** Keeping TypeScript (architect decision to port), Django (heavier ORM, less async-native), Flask (less built-in validation).

### DEC-0002 — uv as package manager

- **Date:** 2026-04-03
- **Decision:** uv is the package manager and virtual environment tool.
- **Reason:** Fastest Python package manager. Single tool for venv creation, dependency resolution, and script running. Deterministic lock files.
- **Alternatives rejected:** pip + venv (slower, no lock file), poetry (slower resolution, heavier), pdm (less adoption).

### DEC-0003 — SQLAlchemy 2.0 async with asyncpg for PostgreSQL

- **Date:** 2026-04-03
- **Decision:** SQLAlchemy 2.0 with async session and asyncpg driver. Models use the declarative mapping pattern.
- **Reason:** Async-native ORM that matches FastAPI's async request handling. asyncpg is the fastest PostgreSQL driver for Python. SQLAlchemy 2.0's new query API is type-safe and composable.
- **Alternatives rejected:** SQLAlchemy sync (blocks event loop), raw asyncpg (no ORM, manual SQL), Tortoise ORM (less mature, smaller ecosystem).

### DEC-0004 — Ruff for linting/formatting, pyright strict for type checking

- **Date:** 2026-04-03
- **Decision:** Ruff handles both linting and formatting. Pyright in strict mode handles type checking. Line length = 100, target Python 3.12.
- **Reason:** Ruff is the fastest Python linter (Rust-based), replaces flake8 + isort + black. Pyright strict mode catches type errors that mypy would miss in default mode.
- **Alternatives rejected:** flake8 + black + isort (three tools instead of one), mypy (slower, less strict by default).
