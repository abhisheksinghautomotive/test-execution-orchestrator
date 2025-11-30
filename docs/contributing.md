# **Contributing Guidelines**

This document provides a minimal reference for contributing to **python-validation-lib**.
For full details, see the root-level `CONTRIBUTING.md`.

---

## **Development Setup**

```bash
git clone https://github.com/<owner>/python-validation-lib.git
cd python-validation-lib
poetry install
poetry shell
```

Run tests:

```bash
poetry run pytest
```

Run linting and formatting:

```bash
poetry run ruff check .
poetry run black .
```

---

## **Branching Rules**

* Use feature branches:
  `feature/<short-description>`
* Use fix branches:
  `fix/<issue>`
* Never commit directly to `main`.

---

## **Commit Messages**

Use **Conventional Commits**:

```
feat: description
fix: description
docs: description
test: description
refactor: description
chore: description
```

---

## **Pull Requests**

Before opening a PR:

```bash
poetry run pre-commit run --all-files
```

A PR must pass:

* Black (format)
* Ruff (lint)
* mypy (types)
* pytest (unit tests)
* coverage >= 80%
* Bandit (SAST)
* pip-audit (dependency scan)
* Gitleaks (secrets)

---

## **Documentation**

All new modules must include:

* module-level docstring
* minimal usage example (if applicable)

Update `docs/` when adding new features.

---

## **Architecture Decisions (ADRs)**

If your change introduces a new architectural choice:

1. Add a new `ADRs/ADR-xxx.md`
2. Use the template from ADR-000
3. Submit ADR in its own PR

---

## **Releases**

Release flow is automated using semantic-release.

Dry-run locally:

```bash
./scripts/release_dryrun.sh --create-dry-tag
```

Refer CONTRIBUTING.md for more Info
