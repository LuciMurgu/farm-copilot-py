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

### DEC-0005 — Shared async engine via module-level singleton — no pool-per-request

- **Date:** 2026-04-03
- **Decision:** A single `AsyncEngine` (pool_size=5, max_overflow=10) and `async_sessionmaker` are created once at module level in `database/session.py`. FastAPI route handlers obtain sessions via a `get_db` async generator dependency. No engine or pool is created per request.
- **Reason:** The TypeScript version suffered from a pool-per-request anti-pattern that caused connection exhaustion under load. A module-level singleton ensures one pool shared across all requests for the server lifetime.
- **Alternatives rejected:** Per-request pool creation (proven anti-pattern), middleware-based session management (less explicit than DI).

### DEC-0006 — Domain enums defined independently from database enums

- **Date:** 2026-04-03
- **Decision:** Domain enums (`domain/enums.py`) are defined as separate `StrEnum` classes with identical values to the database enums (`database/models.py`). The domain layer does not import from the database layer.
- **Reason:** Preserves domain layer purity — `domain/` must have zero imports from `database/`, `contracts/`, `worker/`, or `api/`. Identical values are intentional and verified by convention.
- **Alternatives rejected:** Shared enum module (creates coupling), importing database enums in domain (violates layer boundary).

### DEC-0007 — Alert evidence uses typed dataclasses per alert kind

- **Date:** 2026-04-03
- **Decision:** Alert evidence uses typed dataclasses per alert kind (`ConfirmedDuplicateEvidence`, `PossibleDuplicateEvidence`, `InvoiceTotalMismatchEvidence`, `SuspiciousOverpaymentEvidence`) instead of untyped `dict[str, unknown]`. Resolves OQ-0009 from the TypeScript version.
- **Reason:** The TypeScript version used `evidence: Record<string, unknown>` which caused silent breakage when evidence field names were renamed. Typed dataclasses catch field mismatches at definition time and provide IDE autocompletion. This is the key architectural improvement of the Python port.
- **Alternatives rejected:** Keeping `dict[str, object]` (repeats TypeScript mistake), single generic evidence class (less type safety).

### DEC-0008 — lxml for XML parsing (replaces fast-xml-parser)

- **Date:** 2026-04-04
- **Decision:** lxml is the XML parsing library for e-Factura UBL 2.1 invoices. The parser uses namespace-aware XPath with a UBL 2.1 namespace map instead of stripping namespace prefixes.
- **Reason:** Native XPath support, proper namespace handling, future schematron validation capability for CIUS-RO compliance. lxml is the de facto standard for XML processing in Python.
- **Alternatives rejected:** fast-xml-parser (JS only), xml.etree.ElementTree (no XPath namespace support, limited API), defusedxml (wrapper, not full parser).

### DEC-0009 — Integration tests use transaction rollback for isolation

- **Date:** 2026-04-04
- **Decision:** Integration tests use transaction rollback for isolation. Each test runs inside a transaction that rolls back after the test, preventing cross-test interference. Tests are skipped when `DATABASE_URL` is not set.
- **Reason:** No cleanup needed, tests don't interfere, DB is unchanged after tests run. Simpler than commit + cleanup approach.
- **Alternatives rejected:** Committed transactions + explicit cleanup (more complex, risk of leftover data), separate test databases per test (resource-heavy).

### DEC-0010 — ANAF tokens encrypted at rest using Fernet symmetric encryption

- **Date:** 2026-04-04
- **Decision:** ANAF OAuth2 tokens (access_token, refresh_token, client_secret) are encrypted at rest using Fernet symmetric encryption. Key loaded from `ANAF_ENCRYPTION_KEY` env var. One token per farm (unique constraint on farm_id). Proactive refresh at 70% of access token lifetime.
- **Reason:** ANAF tokens are fiscal credentials — a leaked token pair exposes all invoice data for the farm. Fernet provides authenticated encryption (AES-128-CBC + HMAC-SHA256). 70% threshold prevents token expiry during active API calls.
- **Alternatives rejected:** Asymmetric encryption (unnecessary complexity for at-rest encryption), vault-based storage (overkill for pilot), no encryption (unacceptable security risk).

### DEC-0011 — ANAF API client uses exponential backoff + circuit breaker

- **Date:** 2026-04-04
- **Decision:** ANAF API client uses exponential backoff (2s→16s, ±20% jitter, max 5 attempts) + circuit breaker (5 failures → 5min cooldown). 4xx errors are non-retryable. Response bodies hashed (SHA-256) for audit trail integrity. Circuit breaker uses `time.monotonic()` for clock-change immunity.
- **Reason:** ANAF APIs are notoriously unstable. Retry with jitter prevents thundering herd. Circuit breaker prevents cascading failures when ANAF is down. SHA-256 hashing enables tamper-evident audit logs without storing full response bodies.
- **Alternatives rejected:** Fixed retry delays (thundering herd risk), no circuit breaker (cascading failures), third-party resilience library (unnecessary dependency for 3-state machine).

### DEC-0012 — ANAF sync uses id_descarcare as deduplication key

- **Date:** 2026-04-04
- **Decision:** ANAF sync uses `id_descarcare` as deduplication key with unique constraint on `(farm_id, anaf_id_descarcare)`. Polling window starts from last successful sync minus 1 day (overlap for safety), capped at 60 days (ANAF retention limit). End time uses 10-minute buffer to avoid clock sync issues.
- **Reason:** `id_descarcare` is ANAF's unique identifier for downloadable documents. The 1-day overlap ensures no messages are missed during edge cases (clock drift, partial failures). 60-day cap matches ANAF's retention policy. 10-minute buffer prevents race conditions between our clock and ANAF's server clock.
- **Alternatives rejected:** Message ID as dedup key (not always unique across document types), hash-based dedup (requires downloading first), no overlap (risk of missing messages at window boundaries).

### DEC-0013 — ANAF OAuth callback uses module-level state dict for CSRF protection

- **Date:** 2026-04-04
- **Decision:** ANAF OAuth callback uses module-level state dict for CSRF protection. Acceptable for single-server MVP. Must move to encrypted cookie or server-side session store before horizontal scaling.
- **Reason:** Simple, stateless (from caller's perspective), and sufficient for pilot deployment on a single server. The state parameter is a 32-byte cryptographically random token that prevents cross-site request forgery on the OAuth callback endpoint.
- **Alternatives rejected:** Database-backed session store (too heavy for MVP), signed cookies (adds complexity without benefit for single-server), no CSRF protection (security risk).

