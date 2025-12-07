from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from orchestrator.repository.execution_base import ExecutionRepository
from orchestrator.repository.in_memory_execution import InMemoryExecutionRepo
from orchestrator.models.execution import ExecutionCreate, ExecutionStatus


# simple service with injected repo (default to in-memory)
class ExecutionService:
    def __init__(self, repo: Optional[ExecutionRepository] = None):
        self.repo = repo or InMemoryExecutionRepo()

    def create(self, payload: ExecutionCreate):
        return self.repo.create(payload)

    def start(self, execution_id: str):
        ex = self.repo.get(execution_id)
        if not ex:
            return None
        if ex.status not in (ExecutionStatus.PENDING, ExecutionStatus.FAILED):
            return ex
        started = datetime.utcnow()
        # simulate quick run for now: set RUNNING then COMPLETED
        self.repo.update(
            execution_id, status=ExecutionStatus.RUNNING, started_at=started
        )
        # for demo: mark completed with artifacts_uri after small simulated duration
        finished = started + timedelta(seconds=1)
        artifacts = f"s3://fake-bucket/executions/{execution_id}/artifacts.tar.gz"
        self.repo.update(
            execution_id,
            status=ExecutionStatus.COMPLETED,
            finished_at=finished,
            artifacts_uri=artifacts,
        )
        return self.repo.get(execution_id)

    def stop(self, execution_id: str):
        ex = self.repo.get(execution_id)
        if not ex:
            return None
        if ex.status == ExecutionStatus.RUNNING:
            now = datetime.utcnow()
            return self.repo.update(
                execution_id, status=ExecutionStatus.CANCELLED, finished_at=now
            )
        return ex

    def list(self, limit: int = 100):
        return list(self.repo.list(limit=limit))

    def get(self, execution_id: str):
        return self.repo.get(execution_id)
