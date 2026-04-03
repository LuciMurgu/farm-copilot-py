# Project Memory — Farm Copilot (Python)

## Purpose

This file records what is built, audited, deferred, and likely next.
It is an operational snapshot — not a narrative essay.

Update this file at the end of every meaningful session.

---

## Last updated

2026-04-03 (project scaffold created — uv, FastAPI, SQLAlchemy, Pydantic, directory structure, foundational docs)

---

## Implemented now

### Project scaffold

| Item | Status |
|------|--------|
| `pyproject.toml` | Configured with all deps, dev deps, ruff, pytest, pyright |
| Directory structure | `src/farm_copilot/` with domain, contracts, database, worker, api packages |
| Tests structure | `tests/` with domain, worker, api packages + empty `conftest.py` |
| Docs structure | `docs/` with adr, sessions, api, domain, product, runbooks |
| Evals structure | `evals/` with fixtures, reports, runner, seed_cases |
| `.env.example` | DATABASE_URL, PORT, ENV |
| `.gitignore` | Standard Python ignores |
| `CLAUDE.md` | Full project constitution |
| `AGENTS.md` | Full agent operating instructions |
| `docs/ARCHITECTURE.md` | Layer boundaries, pipeline, invariants |

---

## Not built (to be ported from TypeScript version)

| Item | TS source | Priority |
|------|-----------|----------|
| Database models (10 tables, 6 enums) | `packages/database/src/schema.ts` | **Next (Prompt 2)** |
| Alembic migrations | from Drizzle migrations 0000–0003 | **Next (Prompt 2)** |
| Database query helpers (14 modules) | `packages/database/src/*.ts` | After schema |
| Domain layer (10 pure modules) | `packages/domain/src/*.ts` | After DB |
| Worker pipeline (9 steps) | `apps/worker/src/*.ts` | After domain |
| API routes + views | `apps/web/app/*.ts` | After worker |
| Contracts (Pydantic models) | `packages/contracts/src/*.ts` | With domain |
| Tests (294 total in TS) | `packages/domain/tests/`, `apps/worker/tests/` | With each layer |

---

## Deferred (same as TypeScript version)

| Item | Reason |
|------|--------|
| Alert persistence (DB table) | Alerts currently in-memory only |
| Explanation persistence (DB table) | Explanations currently in-memory only |
| OCR extraction adapter | ADR 0002 decided provider; not implemented |
| Already-mapped line reassignment | Needs stock reversal logic |
| Alias creation from corrections | Designed but deferred |
| Auth + user model | ADR 0003 designed; not implemented |
| Queue/workflow engine | Direct invocation only |
| Eval cases | Framework spec only |

---

## Next likely work

1. **Prompt 2** — Database models (SQLAlchemy) + Alembic migrations
2. **Prompt 3** — Database query helpers
3. **Prompt 4** — Domain layer (pure business logic)
