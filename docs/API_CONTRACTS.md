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

## Execution API Contracts

### POST /executions
Request: ExecutionCreate (reservation_id, optional commit_sha, test_suite, parameters)
Response: Execution (201)

### GET /executions
Query:
- limit (int) default 100
Response: list of Execution

### GET /executions/{id}
Response: Execution or 404

### POST /executions/{id}/start
Starts execution (synchronous simulation). Response: Execution

### POST /executions/{id}/stop
Stops running execution. Response: Execution

Models: see `src/orchestrator/models/execution.py`
- Execution: id, reservation_id, commit_sha, test_suite, status, artifacts_uri, timestamps
