# src/orchestrator/api/routes.py
from fastapi import APIRouter
import orchestrator

router = APIRouter()


@router.get("/ping")
def ping():
    return {"pong": True}


@router.get("/version")
def version():
    # return package version; keep response shape simple for tests
    return {"version": getattr(orchestrator, "__version__", "0.0.0")}
