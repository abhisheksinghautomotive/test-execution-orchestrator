"""API routes."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    """Ping endpoint."""
    return {"pong": True}
