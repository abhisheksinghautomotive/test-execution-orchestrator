from fastapi.testclient import TestClient
from orchestrator.main import app
from datetime import datetime, timezone, timedelta

client = TestClient(app)


def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def test_create_start_complete_execution():
    # create a reservation first (reuse existing reservation flow)
    start = iso_now()
    end = (
        (datetime.now(timezone.utc) + timedelta(hours=1))
        .replace(microsecond=0)
        .isoformat()
    )
    res = client.post(
        "/reservations",
        json={"user_id": "tester", "bench_type": "SIL", "start": start, "end": end},
    )
    assert res.status_code == 201
    reservation = res.json()
    rid = reservation["id"]

    # create execution
    payload = {"reservation_id": rid, "commit_sha": "deadbeef", "test_suite": "smoke"}
    r = client.post("/executions", json=payload)
    assert r.status_code == 201
    exe = r.json()
    eid = exe["id"]
    assert exe["status"] == "PENDING"

    # start execution
    r = client.post(f"/executions/{eid}/start")
    assert r.status_code == 200
    exe2 = r.json()
    assert exe2["status"] in (
        "RUNNING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "COMPLETED",
    )
    # completed artifacts present for simulated run
    assert "artifacts_uri" in exe2 and exe2["artifacts_uri"] is not None

    # get execution
    r = client.get(f"/executions/{eid}")
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == eid

    # list executions
    r = client.get("/executions")
    assert r.status_code == 200
    items = r.json()
    assert any(it["id"] == eid for it in items)


def test_get_nonexistent_execution():
    """Test getting an execution that doesn't exist returns 404."""
    r = client.get("/executions/nonexistent-id")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_start_nonexistent_execution():
    """Test starting an execution that doesn't exist returns 404."""
    r = client.post("/executions/nonexistent-id/start")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_stop_nonexistent_execution():
    """Test stopping an execution that doesn't exist returns 404."""
    r = client.post("/executions/nonexistent-id/stop")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_stop_running_execution():
    """Test stopping a running execution."""
    # Create reservation
    start = iso_now()
    end = (
        (datetime.now(timezone.utc) + timedelta(hours=1))
        .replace(microsecond=0)
        .isoformat()
    )
    res = client.post(
        "/reservations",
        json={"user_id": "tester", "bench_type": "SIL", "start": start, "end": end},
    )
    assert res.status_code == 201
    rid = res.json()["id"]

    # Create execution
    r = client.post(
        "/executions",
        json={
            "reservation_id": rid,
            "commit_sha": "abc123",
            "test_suite": "integration",
        },
    )
    assert r.status_code == 201
    eid = r.json()["id"]

    # Start execution
    r = client.post(f"/executions/{eid}/start")
    assert r.status_code == 200

    # Stop execution (service simulates instant completion, but we can still call stop)
    r = client.post(f"/executions/{eid}/stop")
    assert r.status_code == 200
    # Should return the execution (even if already completed)
    assert r.json()["id"] == eid


def test_list_executions_with_limit():
    """Test listing executions with limit parameter."""
    r = client.get("/executions?limit=5")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) <= 5
