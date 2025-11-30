"""Version endpoint tests."""

from fastapi.testclient import TestClient
from orchestrator.main import app
from orchestrator import __version__

client = TestClient(app)


def test_version_endpoint():
    """Test version endpoint returns current version."""
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_version_matches_package():
    """Test API version matches package version."""
    response = client.get("/version")
    assert response.json()["version"] == __version__
