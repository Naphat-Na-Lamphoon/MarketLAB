from functools import lru_cache
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str = "dev"
    database_url: str = "sqlite+aiosqlite:///./marketlab.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("ENV", "dev"),
        database_url=os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./marketlab.db",
        ),
    )
