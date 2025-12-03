from orchestrator.repository.in_memory import InMemoryReservationRepo
from orchestrator.repository.base import ReservationRepository

# Simple global repo instance for local/dev use.
_repo: ReservationRepository | None = None


def get_repo() -> ReservationRepository:
    global _repo
    if _repo is None:
        _repo = InMemoryReservationRepo()
    return _repo


def get_repo_dep() -> ReservationRepository:
    return get_repo()
