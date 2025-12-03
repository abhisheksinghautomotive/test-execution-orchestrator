from __future__ import annotations
from threading import Lock
from typing import Dict, Iterable, Optional
from datetime import datetime
import uuid

from orchestrator.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationStatus,
)
from orchestrator.repository.base import ReservationRepository


class InMemoryReservationRepo(ReservationRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Reservation] = {}
        self._lock = Lock()

    def create(self, payload: ReservationCreate) -> Reservation:
        with self._lock:
            rid = uuid.uuid4().hex
            now = datetime.utcnow()
            res = Reservation(
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
            self._store[rid] = res
            return res

    def get(self, reservation_id: str) -> Optional[Reservation]:
        return self._store.get(reservation_id)

    def list(self, limit: int = 100) -> Iterable[Reservation]:
        vals = list(self._store.values())
        return vals[:limit]

    def delete(self, reservation_id: str) -> bool:
        with self._lock:
            if reservation_id in self._store:
                del self._store[reservation_id]
                return True
            return False
