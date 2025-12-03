# Reservation API Contracts

## Endpoints
### POST /reservations
Request: ReservationCreate
Response: Reservation (201)

### GET /reservations
Query:
- limit (int) default 100
Response: list of Reservation

### GET /reservations/{id}
Response: Reservation or 404

### DELETE /reservations/{id}
Response: 204 or 404

## Models
See `src/orchestrator/models/reservation.py`

- ReservationCreate: user_id, bench_type, start (RFC3339), end (RFC3339), tags
- Reservation: ReservationCreate + id, status, created_at, updated_at

## Notes
- Datetimes are UTC in ISO-8601 format.
- Validation enforces `end > start`.
- Repository injected via dependency `get_repo_dep` — replace with persistent implementation in Sprint 3.
