import os
import subprocess
import time
import signal
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8001")
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = "8001"


def _wait_for_health(url: str, timeout: int = 10) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/health", timeout=1.0)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.25)
    return False


def _start_uvicorn():
    env = os.environ.copy()
    # Ensure app import finds package under src/
    env["PYTHONPATH"] = env.get("PYTHONPATH", "")
    if "src" not in env["PYTHONPATH"].split(os.pathsep):
        env["PYTHONPATH"] = os.pathsep.join(filter(None, ["src", env["PYTHONPATH"]]))
    cmd = [
        "python",
        "-m",
        "uvicorn",
        "orchestrator.main:app",
        "--host",
        UVICORN_HOST,
        "--port",
        UVICORN_PORT,
        "--log-level",
        "warning",
    ]
    proc = subprocess.Popen(
        cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return proc


def _stop_process(proc: subprocess.Popen):
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
        proc.wait(timeout=2)


def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def test_reservation_end_to_end():
    proc = _start_uvicorn()
    try:
        assert _wait_for_health(
            BASE_URL, timeout=15
        ), "uvicorn did not start or /health not reachable"
        start = iso_now()
        end = (
            (datetime.now(timezone.utc) + timedelta(hours=1))
            .replace(microsecond=0)
            .isoformat()
        )

        # create
        payload = {
            "user_id": "integration",
            "bench_type": "SIL",
            "start": start,
            "end": end,
            "tags": ["integration"],
        }
        r = requests.post(f"{BASE_URL}/reservations", json=payload, timeout=5)
        assert r.status_code == 201, r.text
        body = r.json()
        rid = body["id"]

        # get
        r = requests.get(f"{BASE_URL}/reservations/{rid}", timeout=5)
        assert r.status_code == 200
        assert r.json()["user_id"] == "integration"

        # list
        r = requests.get(f"{BASE_URL}/reservations", timeout=5)
        assert r.status_code == 200
        items = r.json()
        assert any(it["id"] == rid for it in items)

        # delete
        r = requests.delete(f"{BASE_URL}/reservations/{rid}", timeout=5)
        assert r.status_code == 204

        # confirm deletion
        r = requests.get(f"{BASE_URL}/reservations/{rid}", timeout=5)
        assert r.status_code == 404

    finally:
        _stop_process(proc)
