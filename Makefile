.PHONY: test lint typecheck web-typecheck

test:
	cd backend && uv run --with pytest --with pytest-asyncio --with SQLAlchemy --with greenlet --with aiosqlite --with alembic --with fastapi --with pydantic --with python-dotenv --with asyncpg python -m pytest -q

lint:
	cd backend && python -m compileall -q app tests

typecheck:
	cd backend && python -m compileall -q app

web-typecheck:
	cd web && npm run typecheck
