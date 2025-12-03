from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from orchestrator.models.reservation import Reservation, ReservationCreate
from orchestrator.repository.base import ReservationRepository
from orchestrator.deps import get_repo_dep

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=Reservation, status_code=status.HTTP_201_CREATED)
def create_reservation(
    payload: ReservationCreate, repo: ReservationRepository = Depends(get_repo_dep)
):
    res = repo.create(payload)
    return res


@router.get("", response_model=List[Reservation])
def list_reservations(
    limit: int = Query(100, ge=1, le=1000),
    repo: ReservationRepository = Depends(get_repo_dep),
):
    return list(repo.list(limit=limit))


@router.get("/{reservation_id}", response_model=Reservation)
def get_reservation(
    reservation_id: str, repo: ReservationRepository = Depends(get_repo_dep)
):
    res = repo.get(reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="reservation not found")
    return res


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: str, repo: ReservationRepository = Depends(get_repo_dep)
):
    ok = repo.delete(reservation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="reservation not found")
    return None
