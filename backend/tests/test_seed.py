import pytest_asyncio
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import create_engine
from app.models import Hypothesis, User, Variant
from app.models.base import Base
from app.seed import SEED_USERS, seed_demo_data


@pytest_asyncio.fixture
async def session():
    engine = create_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        yield db
    await engine.dispose()


@pytest.mark.asyncio
async def test_seed_creates_one_workspace_per_role(session):
    await seed_demo_data(session)
    await seed_demo_data(session)

    users = (await session.execute(select(User))).scalars().all()
    hypotheses = (await session.execute(select(Hypothesis))).scalars().all()
    variants = (await session.execute(select(Variant))).scalars().all()

    assert {user.role for user in users} == {"admin", "operator", "viewer"}
    assert len(users) == len(SEED_USERS)
    assert len(hypotheses) == len(SEED_USERS)
    assert len(variants) == len(SEED_USERS) * 2
    assert all(user.password_hash.startswith("pbkdf2_sha256$") for user in users)
