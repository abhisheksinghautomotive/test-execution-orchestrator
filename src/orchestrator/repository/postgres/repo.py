from __future__ import annotations
from typing import Optional, Iterable
from datetime import datetime
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from orchestrator.repository.base import ReservationRepository
from orchestrator.repository.execution_base import ExecutionRepository
from orchestrator.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
)
from orchestrator.models.execution import Execution, ExecutionCreate, ExecutionStatus

from orchestrator.repository.postgres import models as pgm


class PostgresReservationRepo(ReservationRepository):
    def __init__(self, database_url: Optional[str]):
        if not database_url:
            raise ValueError("DATABASE_URL is required for Postgres repo")
        self._engine = create_engine(database_url, future=True)
        pgm.metadata.create_all(self._engine)

    def create(self, payload: ReservationCreate) -> Reservation:
        with Session(self._engine) as s:
            rid = uuid.uuid4().hex
            now = datetime.utcnow()
            row = pgm.ReservationORM(
                id=rid,
                user_id=payload.user_id,
                bench_type=payload.bench_type,
                start=payload.start,
                end=payload.end,
                tags=payload.tags or [],
                status=ReservationStatus.PENDING,
                created_at=now,
                updated_at=now,
            )
            s.add(row)
            s.commit()
            return Reservation(**row.__dict__)

    def get(self, reservation_id: str) -> Optional[Reservation]:
        with Session(self._engine) as s:
            row = s.get(pgm.ReservationORM, reservation_id)
            if not row:
                return None
            return Reservation(**row.__dict__)

    def list(self, limit: int = 100) -> Iterable[Reservation]:
        with Session(self._engine) as s:
            q = s.query(pgm.ReservationORM).limit(limit).all()
            return [Reservation(**r.__dict__) for r in q]

    def delete(self, reservation_id: str) -> bool:
        with Session(self._engine) as s:
            row = s.get(pgm.ReservationORM, reservation_id)
            if not row:
                return False
            s.delete(row)
            s.commit()
            return True


class PostgresExecutionRepo(ExecutionRepository):
    def __init__(self, database_url: Optional[str]):
        if not database_url:
            raise ValueError("DATABASE_URL is required for Postgres repo")
        self._engine = create_engine(database_url, future=True)
        pgm.metadata.create_all(self._engine)

    def create(self, payload: ExecutionCreate) -> Execution:
        with Session(self._engine) as s:
            eid = uuid.uuid4().hex
            now = datetime.utcnow()
            row = pgm.ExecutionORM(
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
            s.add(row)
            s.commit()
            return Execution(**row.__dict__)

    def get(self, execution_id: str) -> Optional[Execution]:
        with Session(self._engine) as s:
            row = s.get(pgm.ExecutionORM, execution_id)
            if not row:
                return None
            return Execution(**row.__dict__)

    def list(self, limit: int = 100) -> Iterable[Execution]:
        with Session(self._engine) as s:
            q = s.query(pgm.ExecutionORM).limit(limit).all()
            return [Execution(**r.__dict__) for r in q]

    def update(self, execution_id: str, **fields) -> Optional[Execution]:
        with Session(self._engine) as s:
            row = s.get(pgm.ExecutionORM, execution_id)
            if not row:
                return None
            for k, v in fields.items():
                setattr(row, k, v)
            row.updated_at = datetime.utcnow()
            s.commit()
            return Execution(**row.__dict__)

    def delete(self, execution_id: str) -> bool:
        with Session(self._engine) as s:
            row = s.get(pgm.ExecutionORM, execution_id)
            if not row:
                return False
            s.delete(row)
            s.commit()
            return True
