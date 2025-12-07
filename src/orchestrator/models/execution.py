from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExecutionBase(BaseModel):
    reservation_id: str = Field(..., min_length=1)
    commit_sha: Optional[str] = None
    test_suite: Optional[str] = None
    parameters: Optional[dict] = None


class ExecutionCreate(ExecutionBase):
    pass


class Execution(ExecutionBase):
    id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    artifacts_uri: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
