#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

generate_timestamps() {
  START=$(python -c "from datetime import datetime,timezone; print(datetime.now(timezone.utc).replace(microsecond=0).isoformat())")
  END=$(python -c "from datetime import datetime,timezone,timedelta; print((datetime.now(timezone.utc)+timedelta(hours=1)).replace(microsecond=0).isoformat())")
  echo "START=$START"
  echo "END=$END"
}

create_reservation() {
  local start="$1" end="$2" user="${3:-ci}" bench="${4:-SIL}" tags="${5:-[]}"
  resp=$(curl -sS -X POST "$BASE_URL/reservations" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\":\"$user\",\"bench_type\":\"$bench\",\"start\":\"$start\",\"end\":\"$end\",\"tags\":$tags}")
  echo "$resp"
}

get_reservation() {
  local id="$1"
  curl -sS "$BASE_URL/reservations/$id"
}

list_reservations() {
  curl -sS "$BASE_URL/reservations"
}

delete_reservation() {
  local id="$1"
  curl -sS -X DELETE "$BASE_URL/reservations/$id" -w "%{http_code}" -o /dev/null
}

main() {
  generate_timestamps

  echo "Creating reservation..."
  created=$(create_reservation "$START" "$END" "ci" "SIL" '["smoke"]')
  echo "Created: $created"
  id=$(echo "$created" | jq -r .id)
  if [ -z "$id" ] || [ "$id" = "null" ]; then
    echo "Failed to create reservation"
    echo "$created"
    exit 2
  fi

  echo "Getting reservation $id..."
  get_reservation "$id" | jq

  echo "Listing reservations..."
  list_reservations | jq

  echo "Deleting reservation $id..."
  status_code=$(delete_reservation "$id")
  if [ "$status_code" != "204" ]; then
    echo "Delete failed, http status: $status_code"
    exit 3
  fi

  echo "Confirm deleted (should return 404)..."
  http_status=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL/reservations/$id" || true)
  if [ "$http_status" = "404" ]; then
    echo "Confirmed deletion; smoke test passed."
    exit 0
  else
    echo "Expected 404 after deletion but got: $http_status"
    exit 4
  fi
}

main
