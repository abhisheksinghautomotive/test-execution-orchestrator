"""FastAPI application entrypoint."""
from fastapi import FastAPI

app = FastAPI(
    title="Test Execution Orchestrator",
    description="Distributed Test Execution Orchestrator for HIL/SIL bench scheduling and execution",
    version="0.1.3"
)

@app.get("/health", tags=["health"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}
