from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    FAILED = "FAILED"


class ReservationBase(BaseModel):
    user_id: str = Field(..., min_length=1)
    bench_type: str = Field(..., min_length=1)
    start: datetime
    end: datetime
    tags: Optional[list[str]] = None

    @validator("end")
    def end_after_start(cls, v, values):
        if "start" in values and v <= values["start"]:
            raise ValueError("end must be after start")
        return v


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: str
    status: ReservationStatus = ReservationStatus.PENDING
    created_at: datetime
    updated_at: datetime
