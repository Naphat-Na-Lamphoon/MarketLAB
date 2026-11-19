from __future__ import annotations

import asyncio
import hashlib
import secrets
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionFactory, create_tables
from app.models import Hypothesis, User, Variant


@dataclass(frozen=True)
class SeedUser:
    email: str
    password: str
    role: str
    hypothesis_title: str
    concept_id: str


SEED_USERS = (
    SeedUser(
        email="admin@marketlab.local",
        password="Admin123!",
        role="admin",
        hypothesis_title="Admin workspace governance",
        concept_id="seed-admin",
    ),
    SeedUser(
        email="operator@marketlab.local",
        password="Operator123!",
        role="operator",
        hypothesis_title="Operator onboarding offer",
        concept_id="seed-operator",
    ),
    SeedUser(
        email="viewer@marketlab.local",
        password="Viewer123!",
        role="viewer",
        hypothesis_title="Viewer evidence review",
        concept_id="seed-viewer",
    ),
)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        120_000,
    )
    return f"pbkdf2_sha256$120000${salt.hex()}${derived_key.hex()}"


async def seed_demo_data(session: AsyncSession) -> None:
    for seed_user in SEED_USERS:
        result = await session.execute(
            select(User).where(User.email == seed_user.email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                email=seed_user.email,
                password_hash=hash_password(seed_user.password),
                role=seed_user.role,
            )
            session.add(user)
            await session.flush()

        hypothesis_result = await session.execute(
            select(Hypothesis).where(
                Hypothesis.concept_id == seed_user.concept_id,
                Hypothesis.owner_id == user.user_id,
            )
        )
        hypothesis = hypothesis_result.scalar_one_or_none()
        if hypothesis is None:
            hypothesis = Hypothesis(
                title=seed_user.hypothesis_title,
                concept_id=seed_user.concept_id,
                concept_text="Seed data for local role demonstrations.",
                problem_statement="Teams need a simple way to validate an offer.",
                target_segment="MarketLab demo users",
                offer_description="A simulated experiment workflow",
                pricing_tier="ฟรีสำหรับเดโม",
                budget_cap_thb=Decimal("1000.00"),
                owner_id=user.user_id,
            )
            session.add(hypothesis)
            await session.flush()
            session.add_all(
                [
                    Variant(
                        hypothesis_id=hypothesis.hypothesis_id,
                        name="Control",
                        is_control=True,
                        status="APPROVED",
                    ),
                    Variant(
                        hypothesis_id=hypothesis.hypothesis_id,
                        name="Treatment",
                        is_control=False,
                        status="DRAFT",
                    ),
                ]
            )

    await session.commit()


async def main() -> None:
    await create_tables()
    async with SessionFactory() as session:
        await seed_demo_data(session)
    print("Seeded demo users and role-specific hypotheses.")
    for seed_user in SEED_USERS:
        print(f"{seed_user.role}: {seed_user.email} / {seed_user.password}")


if __name__ == "__main__":
    asyncio.run(main())
