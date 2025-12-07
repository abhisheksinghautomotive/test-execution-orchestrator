from __future__ import annotations
from typing import Tuple

from orchestrator.config import settings

# import protocols
from orchestrator.repository.base import (
    ReservationRepository as ReservationRepoProtocol,
)
from orchestrator.repository.execution_base import (
    ExecutionRepository as ExecutionRepoProtocol,
)


def get_repositories() -> Tuple[ReservationRepoProtocol, ExecutionRepoProtocol]:
    mode = settings.PERSISTENCE
    if mode == "postgres":
        # explicit validation so tests (and callers) get a clear error fast
        if not settings.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is required when ORCHESTRATOR_PERSISTENCE=postgres"
            )
        # import after validation to avoid heavy deps at module import time
        from orchestrator.repository.postgres.repo import (
            PostgresReservationRepo,
            PostgresExecutionRepo,
        )

        r = PostgresReservationRepo(settings.DATABASE_URL)
        e = PostgresExecutionRepo(settings.DATABASE_URL)
        return r, e

    if mode == "dynamodb":
        # no DB URL required for dynamodb, but boto3 must be available at runtime
        from orchestrator.repository.dynamodb.repo import (
            DynamoReservationRepo,
            DynamoExecutionRepo,
        )

        res_repo: ReservationRepoProtocol = DynamoReservationRepo()
        exec_repo: ExecutionRepoProtocol = DynamoExecutionRepo()
        return res_repo, exec_repo

    # fallback to in-memory (existing modules)
    from orchestrator.repository.in_memory import InMemoryReservationRepo
    from orchestrator.repository.in_memory_execution import InMemoryExecutionRepo

    return InMemoryReservationRepo(), InMemoryExecutionRepo()
