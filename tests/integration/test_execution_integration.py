import os
import time
import signal
import subprocess
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8002")
UVICORN_HOST = "127.0.0.1"
UVICORN_PORT = "8002"


def _wait_for_health(url: str, timeout: int = 15) -> bool:
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
    # ensure app is importable from src/
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


def test_execution_end_to_end():
    proc = _start_uvicorn()
    try:
        assert _wait_for_health(
            BASE_URL, timeout=20
        ), "uvicorn did not start or /health not reachable"
        start = iso_now()
        end = (
            (datetime.now(timezone.utc) + timedelta(hours=1))
            .replace(microsecond=0)
            .isoformat()
        )

        # create reservation
        res = requests.post(
            f"{BASE_URL}/reservations",
            json={
                "user_id": "integration",
                "bench_type": "SIL",
                "start": start,
                "end": end,
            },
            timeout=5,
        )
        assert res.status_code == 201, res.text
        rid = res.json()["id"]

        # create execution
        r = requests.post(
            f"{BASE_URL}/executions",
            json={
                "reservation_id": rid,
                "commit_sha": "deadbeef",
                "test_suite": "integration",
            },
            timeout=5,
        )
        assert r.status_code == 201, r.text
        eid = r.json()["id"]

        # start execution
        r = requests.post(f"{BASE_URL}/executions/{eid}/start", timeout=10)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "status" in body
        assert body.get("artifacts_uri") is not None

        # get execution
        r = requests.get(f"{BASE_URL}/executions/{eid}", timeout=5)
        assert r.status_code == 200
        assert r.json()["id"] == eid

        # list executions
        r = requests.get(f"{BASE_URL}/executions", timeout=5)
        assert r.status_code == 200
        assert any(it["id"] == eid for it in r.json())

        # stop execution (best-effort)
        r = requests.post(f"{BASE_URL}/executions/{eid}/stop", timeout=5)
        assert r.status_code in (200, 204, 404)

    finally:
        _stop_process(proc)
