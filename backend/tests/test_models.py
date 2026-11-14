from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.db import create_engine
from app.models import Experiment, Hypothesis, User, Variant
from app.models.base import Base


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
async def test_hypothesis_variant_experiment_relationships(session):
    user = User(email="operator@example.com", password_hash="test", role="operator")
    hypothesis = Hypothesis(
        title="Reporting guide",
        concept_id="concept-1",
        problem_statement="Reports take too long",
        target_segment="Office workers",
        offer_description="Free guide",
        pricing_tier="free",
        budget_cap_thb=Decimal("1000.00"),
        owner_id=None,
    )
    variant = Variant(name="Control", hypothesis=hypothesis, is_control=True)
    experiment = Experiment(
        hypothesis=hypothesis,
        variant=variant,
        channel_type="simulated",
    )
    session.add_all([user, hypothesis, variant, experiment])
    await session.commit()

    result = await session.execute(select(Hypothesis))
    saved = result.scalar_one()
    assert saved.variants[0].is_control is True
    assert saved.experiments[0].variant.name == "Control"


@pytest.mark.asyncio
async def test_foreign_key_relationship_can_be_loaded(session):
    hypothesis = Hypothesis(
        title="Telemetry test",
        concept_id="concept-2",
        problem_statement="Problem",
        target_segment="Segment",
        offer_description="Offer",
        pricing_tier="free",
        budget_cap_thb=Decimal("20.00"),
    )
    variant = Variant(name="Treatment", hypothesis=hypothesis)
    session.add(hypothesis)
    hypothesis.variants.append(variant)
    await session.commit()

    result = await session.execute(select(Variant))
    assert result.scalar_one().hypothesis.hypothesis_id == hypothesis.hypothesis_id
