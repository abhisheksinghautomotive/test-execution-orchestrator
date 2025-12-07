from __future__ import annotations
import os
from typing import Optional


class Settings:
    """
    Minimal configuration holder for persistence selection.
    Use environment variable ORCHESTRATOR_PERSISTENCE to pick:
      - "postgres"  -> Postgres implementation
      - "dynamodb"  -> DynamoDB implementation
      - "memory"    -> In-memory default
    Postgres connection via DATABASE_URL (SQLAlchemy format).
    DynamoDB uses AWS credentials environment vars.
    """

    PERSISTENCE: str
    DATABASE_URL: Optional[str]

    def __init__(self) -> None:
        self.PERSISTENCE = os.environ.get("ORCHESTRATOR_PERSISTENCE", "memory").lower()
        self.DATABASE_URL = os.environ.get(
            "DATABASE_URL"
        )  # e.g. postgresql://user:pass@host:5432/dbname


settings = Settings()
