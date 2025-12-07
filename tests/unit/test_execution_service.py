"""Additional execution service tests."""

from orchestrator.services.execution_service import ExecutionService
from orchestrator.repository.in_memory_execution import InMemoryExecutionRepo
from orchestrator.models.execution import ExecutionCreate, ExecutionStatus


def test_execution_service_start_nonexistent():
    """Test starting non-existent execution returns None."""
    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    result = svc.start("nonexistent-id")
    assert result is None


def test_execution_service_stop_nonexistent():
    """Test stopping non-existent execution returns None."""
    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    result = svc.stop("nonexistent-id")
    assert result is None


def test_execution_service_stop_not_running():
    """Test stopping execution that's not running returns as-is."""
    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    # Create pending execution
    payload = ExecutionCreate(
        reservation_id="res123", commit_sha="abc123", test_suite="smoke"
    )
    exe = svc.create(payload)

    # Try to stop it (should return as-is since not running)
    result = svc.stop(exe.id)
    assert result is not None
    assert result.status == ExecutionStatus.PENDING


def test_execution_repo_delete():
    """Test deleting execution from repository."""
    repo = InMemoryExecutionRepo()

    # Create execution
    payload = ExecutionCreate(
        reservation_id="res123", commit_sha="abc123", test_suite="smoke"
    )
    exe = repo.create(payload)

    # Delete it
    deleted = repo.delete(exe.id)
    assert deleted is True

    # Verify it's gone
    assert repo.get(exe.id) is None

    # Delete non-existent
    assert repo.delete("nonexistent") is False


def test_execution_update_nonexistent():
    """Test updating non-existent execution returns None."""
    repo = InMemoryExecutionRepo()

    result = repo.update("nonexistent-id", status=ExecutionStatus.RUNNING)
    assert result is None


def test_execution_service_start_completed():
    """Test starting already completed execution returns as-is."""
    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    # Create and start execution (which auto-completes in service)
    payload = ExecutionCreate(
        reservation_id="res123", commit_sha="abc123", test_suite="smoke"
    )
    exe = svc.create(payload)
    svc.start(exe.id)  # Complete the execution

    # Try to start again - should return as-is (line 22)
    result = svc.start(exe.id)
    assert result is not None
    assert result.status == ExecutionStatus.COMPLETED


def test_execution_stop_completed():
    """Test stopping completed execution returns as-is."""
    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    # Create and complete execution
    payload = ExecutionCreate(
        reservation_id="res123", commit_sha="abc123", test_suite="smoke"
    )
    exe = svc.create(payload)
    completed = svc.start(exe.id)
    assert completed is not None

    # Stop completed execution - should return as-is (line 45)
    result = svc.stop(completed.id)
    assert result is not None
    assert result.status == ExecutionStatus.COMPLETED


def test_execution_stop_running():
    """Test stopping running execution cancels it."""
    from datetime import datetime

    repo = InMemoryExecutionRepo()
    svc = ExecutionService(repo=repo)

    # Create execution and mark it as RUNNING manually (bypass start logic)
    payload = ExecutionCreate(
        reservation_id="res123", commit_sha="abc123", test_suite="smoke"
    )
    exe = svc.create(payload)

    # Manually set to RUNNING
    running_exe = repo.update(
        exe.id, status=ExecutionStatus.RUNNING, started_at=datetime.utcnow()
    )
    assert running_exe is not None
    assert running_exe.status == ExecutionStatus.RUNNING

    # Stop it - should cancel (lines 44-45)
    result = svc.stop(exe.id)
    assert result is not None
    assert result.status == ExecutionStatus.CANCELLED
    assert result.finished_at is not None
