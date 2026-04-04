# Farm Copilot

Procurement and margin intelligence for Romanian crop farms.
Automatic invoice ingestion from ANAF SPV with price alerts,
duplicate detection, and stock tracking.

## Quick Start (Development)

```bash
uv sync
cp .env.example .env
# edit .env with your DATABASE_URL
uv run alembic upgrade head
uv run python -m farm_copilot.api
```

## Production Deployment

```bash
# 1. Configure environment
cp .env.production.example .env.production

# 2. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste into .env.production as ANAF_ENCRYPTION_KEY

# 3. Set a strong DB password in .env.production

# 4. Configure ANAF OAuth credentials in .env.production

# 5. Deploy
docker compose --env-file .env.production up -d

# 6. Verify
curl http://localhost:8000/health
```

## Architecture

Five-layer Python application:
- **domain/** — Pure business logic (11 modules, zero side effects)
- **contracts/** — Pydantic DTOs for API boundaries
- **database/** — SQLAlchemy 2.0 async (14 tables, 17 query modules)
- **worker/** — Pipeline orchestration + ANAF sync
- **api/** — FastAPI routes + Jinja2 templates

## Testing

```bash
uv run pytest                           # unit tests (no DB needed)
DATABASE_URL=... uv run pytest tests/   # all tests including integration
```
