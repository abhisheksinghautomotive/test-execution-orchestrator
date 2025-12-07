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
