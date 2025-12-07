"""Test reservation API edge cases."""

from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)


def test_delete_nonexistent_reservation():
    """Test deleting non-existent reservation returns 404."""
    response = client.delete("/reservations/nonexistent-id")
    assert response.status_code == 404
