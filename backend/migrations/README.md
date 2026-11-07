# Database Migrations

This project uses **Alembic** for schema migrations.

## Setup

```bash
cd backend
pip install alembic
alembic init migrations
```

Edit `alembic.ini` and set:
```
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/mediteach
```

Edit `migrations/env.py` to import your models:
```python
from app.database.base import Base
from app.models import *   # noqa – ensures all models are registered
target_metadata = Base.metadata
```

## Common Commands

```bash
# Auto-generate a migration from model changes
alembic revision --autogenerate -m "describe change"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# View current revision
alembic current
```

## Notes
- For SQLite (dev), tables are auto-created on startup via `Base.metadata.create_all`.
- Use Alembic only when switching to PostgreSQL for production.
