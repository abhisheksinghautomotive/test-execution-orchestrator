from __future__ import annotations
from typing import Optional, Iterable
from datetime import datetime
import uuid
import os

try:
    import boto3
    from botocore.exceptions import ClientError
except Exception:
    boto3 = None  # will raise if used without dependency


from orchestrator.repository.base import ReservationRepository
from orchestrator.repository.execution_base import ExecutionRepository
from orchestrator.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
)
from orchestrator.models.execution import Execution, ExecutionCreate, ExecutionStatus


def _iso(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()


class DynamoReservationRepo(ReservationRepository):
    def __init__(self, table_name: Optional[str] = None):
        if boto3 is None:
            raise RuntimeError("boto3 is required for DynamoDB repo")
        self._table_name = table_name or os.environ.get(
            "DYNAMO_RESERVATION_TABLE", "orchestrator-reservations"
        )
        self._d = boto3.resource("dynamodb")
        self._table = self._d.Table(self._table_name)

    def create(self, payload: ReservationCreate) -> Reservation:
        rid = uuid.uuid4().hex
        now = datetime.utcnow()
        item = {
            "id": rid,
            "user_id": payload.user_id,
            "bench_type": payload.bench_type,
            "start": _iso(payload.start),
            "end": _iso(payload.end),
            "tags": payload.tags or [],
            "status": ReservationStatus.PENDING,
            "created_at": _iso(now),
            "updated_at": _iso(now),
        }
        self._table.put_item(Item=item)
        # convert strings back to datetimes where expected by models
        item["start"] = item["start"]
        item["end"] = item["end"]
        return Reservation(**item)

    def get(self, reservation_id: str) -> Optional[Reservation]:
        try:
            r = self._table.get_item(Key={"id": reservation_id})
        except ClientError:
            return None
        item = r.get("Item")
        if not item:
            return None
        return Reservation(**item)

    def list(self, limit: int = 100) -> Iterable[Reservation]:
        resp = self._table.scan(Limit=limit)
        items = resp.get("Items", [])
        return [Reservation(**it) for it in items]

    def delete(self, reservation_id: str) -> bool:
        try:
            self._table.delete_item(Key={"id": reservation_id})
            return True
        except ClientError:
            return False


class DynamoExecutionRepo(ExecutionRepository):
    def __init__(self, table_name: Optional[str] = None):
        if boto3 is None:
            raise RuntimeError("boto3 is required for DynamoDB repo")
        self._table_name = table_name or os.environ.get(
            "DYNAMO_EXEC_TABLE", "orchestrator-executions"
        )
        self._d = boto3.resource("dynamodb")
        self._table = self._d.Table(self._table_name)

    def create(self, payload: ExecutionCreate) -> Execution:
        eid = uuid.uuid4().hex
        now = datetime.utcnow()
        item = {
            "id": eid,
            "reservation_id": payload.reservation_id,
            "commit_sha": payload.commit_sha,
            "test_suite": payload.test_suite,
            "parameters": payload.parameters or {},
            "status": ExecutionStatus.PENDING,
            "artifacts_uri": None,
            "started_at": None,
            "finished_at": None,
            "created_at": _iso(now),
            "updated_at": _iso(now),
        }
        self._table.put_item(Item=item)
        return Execution(**item)

    def get(self, execution_id: str) -> Optional[Execution]:
        try:
            r = self._table.get_item(Key={"id": execution_id})
        except ClientError:
            return None
        item = r.get("Item")
        if not item:
            return None
        return Execution(**item)

    def list(self, limit: int = 100) -> Iterable[Execution]:
        resp = self._table.scan(Limit=limit)
        items = resp.get("Items", [])
        return [Execution(**it) for it in items]

    def update(self, execution_id: str, **fields) -> Optional[Execution]:
        # DynamoDB update is simplified: read-modify-write (not ideal for concurrency)
        item = self.get(execution_id)
        if not item:
            return None
        data = item.dict()
        data.update(fields)
        data["updated_at"] = _iso(datetime.utcnow())
        self._table.put_item(Item=data)
        return Execution(**data)

    def delete(self, execution_id: str) -> bool:
        try:
            self._table.delete_item(Key={"id": execution_id})
            return True
        except ClientError:
            return False
