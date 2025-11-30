#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

print_header() {
  echo
  echo "================================================================"
  echo "STEP: $1"
  echo "----------------------------------------------------------------"
}

run_step() {
  local name="$1"; shift
  print_header "$name"
  if "$@"; then
    echo "RESULT: $name  [OK]"
    return 0
  else
    echo "RESULT: $name  [FAILED]"
    return 1
  fi
}

echo "Local CI helper (src/ layout)"
run_step "Poetry check" poetry check || true
run_step "Install dependencies" poetry install --no-interaction --no-ansi || true

run_step "Black (format check)" poetry run black --check src tests || true
run_step "Ruff (lint check)" poetry run ruff check src tests || true
run_step "Mypy (type checking)" poetry run mypy src || true
run_step "Pytest (unit tests)" poetry run pytest -q --maxfail=1 tests/unit || true

# Security checks (non-blocking locally by default)
run_step "Bandit (SAST)" poetry run bandit -r src -f json -o bandit-output.json || true
if command -v pip-audit >/dev/null 2>&1; then
  poetry export -f requirements.txt --without-hashes --with dev | python -m pip_audit --format json -o pip-audit.json || true
else
  echo "pip-audit not installed; skipping SCA"
fi

echo
echo "==================== SUMMARY ===================="
echo "Review outputs (bandit-output.json, pip-audit.json, coverage.xml) for details."
