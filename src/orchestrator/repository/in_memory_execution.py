from __future__ import annotations
from threading import Lock
from typing import Dict, Iterable, Optional
from datetime import datetime
import uuid

from orchestrator.models.execution import Execution, ExecutionCreate, ExecutionStatus
from orchestrator.repository.execution_base import ExecutionRepository


class InMemoryExecutionRepo(ExecutionRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Execution] = {}
        self._lock = Lock()

    def create(self, payload: ExecutionCreate) -> Execution:
        with self._lock:
            eid = uuid.uuid4().hex
            now = datetime.utcnow()
            exe = Execution(
                id=eid,
                reservation_id=payload.reservation_id,
                commit_sha=payload.commit_sha,
                test_suite=payload.test_suite,
                parameters=payload.parameters or {},
                status=ExecutionStatus.PENDING,
                artifacts_uri=None,
                started_at=None,
                finished_at=None,
                created_at=now,
                updated_at=now,
            )
            self._store[eid] = exe
            return exe

    def get(self, execution_id: str) -> Optional[Execution]:
        return self._store.get(execution_id)

    def list(self, limit: int = 100) -> Iterable[Execution]:
        vals = list(self._store.values())
        return vals[:limit]

    def update(self, execution_id: str, **fields) -> Optional[Execution]:
        with self._lock:
            ex = self._store.get(execution_id)
            if not ex:
                return None
            data = ex.dict()
            data.update(fields)
            data["updated_at"] = datetime.utcnow()
            # pydantic model reconstruct
            new_ex = Execution(**data)
            self._store[execution_id] = new_ex
            return new_ex

    def delete(self, execution_id: str) -> bool:
        with self._lock:
            if execution_id in self._store:
                del self._store[execution_id]
                return True
            return False
