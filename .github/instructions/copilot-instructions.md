---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

# Purpose: instruct Copilot (and any AI-assisted editing) how to propose fixes and code suggestions
# for the test-execution-orchestrator repository. Follow rules strictly.

## Role
- Act as a focused coding assistant that proposes minimal, test-covered fixes for issues.
- Prioritize correctness, safety, and maintainability over verbosity.
- Produce code changes that are ready to apply as small patches/PRs.

## Hard Constraints (must follow)
- Use Python 3.11+ idioms and existing project conventions (FastAPI, Typer, pydantic, Poetry).
- Respect ADRs (docs/ADRs/) and project architecture decisions (ULID for execution IDs, DynamoDB primary, etc.).
- Do NOT add secrets, credentials, or plaintext tokens to code or tests.
- All changes must include or update unit tests when behavioral code changes.
- New code must pass linting (ruff/black) and type checks (mypy) by default.
- Prefer existing utilities, repositories, and patterns — avoid introducing new frameworks.
- Keep diffs minimal: smallest change that fixes the issue and has tests.
- Avoid long generated boilerplate; prefer concise, idiomatic implementations.

## Suggested Fix Workflow (follow these steps)
1. **Reproduce**: Identify minimal failing test or create one that demonstrates the bug.
2. **Propose Fix**: Create the smallest patch that fixes the test while preserving existing APIs.
3. **Add Test(s)**: Add unit test(s) validating the fix and edge cases.
4. **Run Static Checks**: Ensure code likely passes ruff/mypy/pytest.
5. **Write Commit Message**: Use Conventional Commit style (see docs/CONVENTIONAL_COMMITS.md).
6. **Provide Short PR Body**: Explain the change in 2–3 lines and reference issue number.

## Guidance for Generated Code
- Keep functions short and single-responsibility.
- Use dependency injection patterns (interfaces/repos) already present.
- Use repository abstractions for persistence calls — do not bypass repo layer.
- Use `async` only where the existing module uses async. Match function signatures.
- Use ULID generator utilities when creating execution/reservation IDs.
- When adding logs, use structured log format keys: `correlation_id`, `execution_id`, `task_id`, `trace_id`.
- When editing CI, prefer to add steps that are idempotent and cache dependencies.

## Token-efficiency Rules (produce minimal tokens)
- Prefer succinct diffs and small code snippets.
- Avoid long commentary in code — use short, necessary comments only.
- When generating tests, create focused unit tests only (no heavy integration unless required).
- When providing explanations, keep to 2–4 short bullet points.

## When to escalate to human reviewer
- Changes that modify architecture, persistence choices, or ADRs.
- Security-sensitive changes (auth, secrets, IAM roles).
- Any change that affects cost model (warm pools, autoscaling).
- Ambiguous behavior without deterministic test reproduction.

## Example prompts for Copilot (internal)
- "Produce a minimal unit-test demonstrating the bug in `workers/executor.py` and a 5-line fix that uses `TaskRepository.update_status`."
- "Refactor `api/reservations.py` to validate `end` > `start`, add pydantic validator, and add two unit tests: valid and invalid."

## Files to consult first
- `docs/ADRs/*`
- `docs/CONVENTIONAL_COMMITS.md`
- `pyproject.toml`
- `api/`, `workers/`, `adapters/`, `cli/`

## Acceptance for a proposed change
- Patch includes code + tests
- Tests are deterministic and small in scope
- Commit adheres to Conventional Commits
- Changes do not add secrets or external credentials
