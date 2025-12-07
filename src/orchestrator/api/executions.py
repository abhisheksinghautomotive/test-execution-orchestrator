from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from orchestrator.models.execution import Execution, ExecutionCreate
from orchestrator.services.execution_service import (
    ExecutionService,
)
from orchestrator.repository.in_memory_execution import InMemoryExecutionRepo

router = APIRouter(prefix="/executions", tags=["executions"])

# Singleton in-memory repo to persist data across requests
_execution_repo = InMemoryExecutionRepo()


# simple dependency factory (replaceable later)
def get_service():
    return ExecutionService(repo=_execution_repo)


@router.post("", response_model=Execution, status_code=status.HTTP_201_CREATED)
def create_execution(
    payload: ExecutionCreate, svc: ExecutionService = Depends(get_service)
):
    exe = svc.create(payload)
    return exe


@router.get("", response_model=List[Execution])
def list_executions(
    limit: int = Query(100, ge=1, le=1000), svc: ExecutionService = Depends(get_service)
):
    return svc.list(limit=limit)


@router.get("/{execution_id}", response_model=Execution)
def get_execution(execution_id: str, svc: ExecutionService = Depends(get_service)):
    ex = svc.get(execution_id)
    if not ex:
        raise HTTPException(status_code=404, detail="execution not found")
    return ex


@router.post("/{execution_id}/start", response_model=Execution)
def start_execution(execution_id: str, svc: ExecutionService = Depends(get_service)):
    ex = svc.start(execution_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="execution not found")
    return ex


@router.post("/{execution_id}/stop", response_model=Execution)
def stop_execution(execution_id: str, svc: ExecutionService = Depends(get_service)):
    ex = svc.stop(execution_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="execution not found")
    return ex
