from fastapi import FastAPI
from orchestrator.api.reservations import router as reservations_router
from orchestrator.api.routes import router as routes_router

app = FastAPI(title="Test Execution Orchestrator - API (dev)")

app.include_router(reservations_router)
app.include_router(routes_router)


@app.get("/health")
def health():
    return {"status": "ok"}
