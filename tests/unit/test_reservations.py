from fastapi.testclient import TestClient
from orchestrator.main import app
from datetime import datetime, timedelta

client = TestClient(app)


def iso(dt):
    return dt.isoformat()


def test_create_get_list_delete_reservation():
    start = datetime.utcnow()
    end = start + timedelta(hours=1)
    payload = {
        "user_id": "alice",
        "bench_type": "SIL",
        "start": iso(start),
        "end": iso(end),
        "tags": ["smoke"],
    }
    # create
    r = client.post("/reservations", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    rid = body["id"]

    # get
    r = client.get(f"/reservations/{rid}")
    assert r.status_code == 200
    got = r.json()
    assert got["user_id"] == "alice"
    assert got["bench_type"] == "SIL"

    # list
    r = client.get("/reservations")
    assert r.status_code == 200
    items = r.json()
    assert any(item["id"] == rid for item in items)

    # delete
    r = client.delete(f"/reservations/{rid}")
    assert r.status_code == 204

    # confirm 404 after delete
    r = client.get(f"/reservations/{rid}")
    assert r.status_code == 404
