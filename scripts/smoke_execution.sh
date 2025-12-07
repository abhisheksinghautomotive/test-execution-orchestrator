#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
TIMEOUT=10

info() { printf "\n=> %s\n" "$*" ; }

# generate RFC3339-like timestamps (UTC)
generate_timestamps() {
  START=$(python -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).replace(microsecond=0).isoformat())')
  END=$(python -c 'from datetime import datetime,timezone,timedelta; print((datetime.now(timezone.utc)+timedelta(hours=1)).replace(microsecond=0).isoformat())')
}

post_json() {
  curl -sS -X POST "$1" -H "Content-Type: application/json" -d "$2"
}

wait_for_health() {
  local url="$1"
  local deadline=$((SECONDS + TIMEOUT))
  while [ $SECONDS -lt $deadline ]; do
    if curl -sS --fail "$url/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

main() {
  info "Checking server health at $BASE_URL"
  if ! wait_for_health "$BASE_URL"; then
    echo "Server not healthy at $BASE_URL; aborting"
    exit 2
  fi

  generate_timestamps
  info "Timestamps: START=$START END=$END"

  info "Creating reservation..."
  reservation_payload=$(jq -n --arg u "smoke-ci" --arg b "SIL" --arg s "$START" --arg e "$END" '{user_id:$u, bench_type:$b, start:$s, end:$e}')
  created_res=$(post_json "$BASE_URL/reservations" "$reservation_payload")
  echo "$created_res" | jq
  RID=$(echo "$created_res" | jq -r .id)
  if [ -z "$RID" ] || [ "$RID" = "null" ]; then
    echo "Failed to create reservation"
    exit 3
  fi

  info "Creating execution for reservation $RID"
  exec_payload=$(jq -n --arg r "$RID" --arg c "deadbeef" --arg t "smoke" '{reservation_id:$r, commit_sha:$c, test_suite:$t}')
  created_exec=$(post_json "$BASE_URL/executions" "$exec_payload")
  echo "$created_exec" | jq
  EID=$(echo "$created_exec" | jq -r .id)
  if [ -z "$EID" ] || [ "$EID" = "null" ]; then
    echo "Failed to create execution"
    exit 4
  fi

  info "Starting execution $EID"
  start_resp=$(curl -sS -X POST "$BASE_URL/executions/$EID/start")
  echo "$start_resp" | jq
  status=$(echo "$start_resp" | jq -r .status)
  if [ -z "$status" ] || [ "$status" = "null" ]; then
    echo "Start did not return valid status"
    exit 5
  fi

  info "Fetching execution $EID"
  curl -sS "$BASE_URL/executions/$EID" | jq

  info "Listing executions"
  curl -sS "$BASE_URL/executions" | jq

  info "Attempting to stop execution (best-effort)"
  stop_resp=$(curl -sS -X POST "$BASE_URL/executions/$EID/stop" || true)
  echo "$stop_resp" | jq || true

  info "Smoke test completed successfully."
  exit 0
}

main
