from fastapi.testclient import TestClient
from orchestrator.main import app
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError
from orchestrator.models.reservation import ReservationCreate

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


def test_reservation_validation_end_before_start():
    """Test reservation validation: end must be after start."""
    start = datetime.utcnow()
    end = start - timedelta(hours=1)  # end before start

    with pytest.raises(ValidationError) as exc_info:
        ReservationCreate(user_id="alice", bench_type="SIL", start=start, end=end)

    errors = exc_info.value.errors()
    assert any("end must be after start" in str(e) for e in errors)
