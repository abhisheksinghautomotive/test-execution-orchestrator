"""FastAPI application entrypoint."""
from fastapi import FastAPI

from orchestrator import __version__

app = FastAPI(
    title="Test Execution Orchestrator",
    description="Distributed Test Execution Orchestrator for HIL/SIL bench scheduling and execution",
    version=__version__
)

@app.get("/health", tags=["health"])
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/version", tags=["info"])
def version():
    """Get API version."""
    return {"version": __version__}
