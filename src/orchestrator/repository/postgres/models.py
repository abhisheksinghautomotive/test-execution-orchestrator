from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Table,
    Column,
    String,
    DateTime,
    JSON,
    MetaData,
    Text,
)
from sqlalchemy.orm import registry

mapper_registry = registry()
metadata = MetaData()

reservation_table = Table(
    "reservations",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(128), nullable=False),
    Column("bench_type", String(64), nullable=False),
    Column("start", DateTime, nullable=False),
    Column("end", DateTime, nullable=False),
    Column("tags", JSON, nullable=True),
    Column("status", String(32), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)

execution_table = Table(
    "executions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("reservation_id", String(64), nullable=False),
    Column("commit_sha", String(128), nullable=True),
    Column("test_suite", String(128), nullable=True),
    Column("parameters", JSON, nullable=True),
    Column("status", String(32), nullable=False),
    Column("artifacts_uri", Text, nullable=True),
    Column("started_at", DateTime, nullable=True),
    Column("finished_at", DateTime, nullable=True),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime, nullable=False),
)


class ReservationORM:
    def __init__(
        self,
        id: str,
        user_id: str,
        bench_type: str,
        start: datetime,
        end: datetime,
        tags,
        status: str,
        created_at: datetime,
        updated_at: datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.bench_type = bench_type
        self.start = start
        self.end = end
        self.tags = tags
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at


class ExecutionORM:
    def __init__(
        self,
        id: str,
        reservation_id: str,
        commit_sha: str | None,
        test_suite: str | None,
        parameters,
        status: str,
        artifacts_uri: str | None,
        started_at,
        finished_at,
        created_at,
        updated_at,
    ):
        self.id = id
        self.reservation_id = reservation_id
        self.commit_sha = commit_sha
        self.test_suite = test_suite
        self.parameters = parameters
        self.status = status
        self.artifacts_uri = artifacts_uri
        self.started_at = started_at
        self.finished_at = finished_at
        self.created_at = created_at
        self.updated_at = updated_at


mapper_registry.map_imperatively(ReservationORM, reservation_table)
mapper_registry.map_imperatively(ExecutionORM, execution_table)
