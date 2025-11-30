"""Health endpoint tests."""

from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)


def test_health():
    """Test health endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
