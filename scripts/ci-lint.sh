#!/usr/bin/env bash
# Local CI helper — macOS-safe, auto-fix Black & Ruff when run locally
set -e
set -o pipefail

export PATH="$HOME/.local/bin:$PATH"

FAILED_STEPS=""

print_header() {
  echo
  echo "================================================================"
  echo "STEP: $1"
  echo "----------------------------------------------------------------"
}

run_step() {
  local name="$1"; shift
  print_header "$name"
  echo "COMMAND: $*"
  echo "START: $(date '+%Y-%m-%d %H:%M:%S')"

  if "$@"; then
    echo "RESULT: $name  [OK]"
    return 0
  else
    echo "RESULT: $name  [FAILED]"
    FAILED_STEPS+="\n- $name"
    return 1
  fi
}

# Run a check, auto-fix if it fails, then re-run the check to report status
run_check_with_auto_fix() {
  local name="$1"; shift
  local check_cmd=("$@")
  local fix_cmd=()

  # Determine fix command based on the check command
  # If check is Black check -> fix with `black .`
  if [[ "${check_cmd[*]}" == *"black --check"* ]]; then
    fix_cmd=(poetry run black .)
  # If check is ruff check -> fix with `ruff check --fix`
  elif [[ "${check_cmd[*]}" == *"ruff check"* ]]; then
    # append --fix to the ruff check command but run it as a separate invocation
    fix_cmd=(poetry run ruff check src tests scripts --fix)
  else
    # no auto-fix known
    fix_cmd=()
  fi

  # Run initial check
  if run_step "$name" "${check_cmd[@]}"; then
    return 0
  fi

  # If we reach here, the check failed. Try auto-fix if available.
  if [ "${#fix_cmd[@]}" -ne 0 ]; then
    echo
    echo "Auto-fix available for $name — attempting fix:"
    echo "FIX COMMAND: ${fix_cmd[*]}"
    if "${fix_cmd[@]}"; then
      echo "Auto-fix succeeded. Re-running check..."
      if run_step "${name} (re-check after fix)" "${check_cmd[@]}"; then
        echo "$name fixed and now OK."
        return 0
      else
        echo "Re-check still failing after auto-fix."
        return 1
      fi
    else
      echo "Auto-fix failed for $name."
      return 1
    fi
  else
    # No auto-fix available; leave failure recorded
    return 1
  fi
}

echo "Local CI helper (macOS-safe, auto-fix where allowed)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo

# 1. Poetry check (non-fatal)
run_step "Poetry check" poetry check || true

# 2. Install dependencies (non-fatal)
run_step "Install dependencies" poetry install --no-interaction --no-ansi || true

# 3. Black (format check) — auto-fix if issues
run_check_with_auto_fix "Black (format check)" poetry run black --check src tests scripts || true

# 4. Ruff (lint check) — auto-fix if issues
run_check_with_auto_fix "Ruff (lint check)" poetry run ruff check src tests scripts || true

# 5. Mypy (type checking)
run_step "Mypy (type checking)" poetry run mypy src scripts || true

# 6. Pytest (unit tests, verbose)
run_step "Pytest (unit tests)" poetry run pytest -vv --maxfail=1 tests/unit || true

# 7. Coverage run (xml + term-missing)
run_step "Pytest (coverage)" \
  poetry run pytest tests/unit --maxfail=1 --cov=src --cov-report=term-missing --cov-report=xml || true

# 8. Coverage threshold check (local)
# script path reference: scripts/check_coverage.py
run_step "Coverage threshold (>=80%)" poetry run python scripts/check_coverage.py 80 || true

# 9. Bandit (SAST)
run_step "Bandit (SAST)" poetry run bandit -r src scripts || true

# 10. pip-audit (SCA) - informative only, allowlisted vulnerabilities are acceptable
run_step "pip-audit (SCA)" poetry run pip-audit --progress-spinner off || echo "Note: pip-audit found vulnerabilities (see allowlist)"

# 11. pre-commit: install hooks and run (informative)
run_step "pre-commit install" poetry run pre-commit install || true
run_step "pre-commit run --all-files" poetry run pre-commit run --all-files || true

echo
echo "==================== SUMMARY ===================="
if [ -z "$FAILED_STEPS" ]; then
  echo "All steps passed (or were auto-fixed where allowed)."
  exit 0
else
  echo "Some steps failed or remain failing:"
  # Use printf to interpret newline escapes
  printf "%b\n" "$FAILED_STEPS"
  exit 1
fi
