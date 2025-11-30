# **Python Validation Library**

Welcome to the official documentation of **python-validation-lib** — the foundational Python library powering validation workflows across the ECU testing and automation ecosystem.

This project sets the engineering standards, CI/CD quality gates, and architectural patterns that future repositories will inherit:

* **test-execution-orchestrator** (Sprint 2)
* **infra-bench-platform** (Sprint 3)
* **testbench-observability** (Sprint 4)
* **cloud-cost-optimizer** (Sprint 5)
* **hybrid-networking-simulation** (Sprint 6)

---

# **What This Library Provides**

* A clean, **SOLID-aligned Python architecture**
* A reproducible build system using **Poetry**
* Strict **quality gates**: formatting, linting, typing, coverage, SAST, SCA, secrets
* A unified **plugin/registry system**
* Standard **validation primitives** (rules, validators, runners)
* A secure, deterministic CI pipeline with matrix testing
* Semantic versioning + automated release metadata
* A documentation and ADR baseline for the entire portfolio

---

# **Why This Project Exists**

This library establishes the **common validation logic** shared across systems responsible for:

* ECU firmware validation
* automated bench execution
* workflow orchestration
* test analytics
* cloud-scale simulation
* cost & resource tracking

Every repository that depends on validation logic must rely on a consistent, well-tested, and traceable foundation.
This library provides that foundation.

---

# **Project Structure**

```
python_validation_lib/
├── core/        # Core validation logic, rules, base validators
├── models/      # Domain models (ValidationResult, etc.)
├── services/    # High-level runners/orchestration logic
└── adapters/    # File system, logging, registries, extension adapters
```

Design follows SOLID + clean architecture principles:

* Core modules never depend on adapters
* Public API defined in `__init__.py`
* Rules and validators remain composable and testable

---

# **Getting Started**

### Install dependencies

```bash
poetry install
```

### Basic usage

```python
from python_validation_lib import ValidationRunner, BaseValidator
```

Detailed usage examples are in:

➡️ **[Usage Guide](usage.md)**

---

# **Testing**

This project enforces:

* **≥80% coverage**
* deterministic unit tests
* Bandit SAST
* pip-audit vulnerability checks
* Gitleaks secret scanning
* Policy-enforced security gates

Learn more:

➡️ **[Testing Guide](testing.md)**

---

# **Contributing**

All contributions must follow:

* Conventional Commits
* Branch naming rules
* PR quality checks through GitHub Actions
* ADR-driven architecture decisions

Start here:

➡️ **[Contributor Guide](contributing.md)**

---

# **Architecture Decisions (ADRs)**

Every major decision is recorded in the `ADRs/` directory.
These documents define long-term architecture, CI/CD behavior, and security posture.

Read the summary:

➡️ **[ADR Index](adr.md)**

---

# **Releases**

This library uses **semantic-release** to automate:

* version determination
* changelog generation
* draft releases
* release metadata generation (ADR-013)

Run a local dry-run:

```bash
./scripts/release_dryrun.sh --create-dry-tag
```

Full release automation arrives in Sprint 2.

---

# **Documentation Structure**

| Page                | Description                               |
| ------------------- | ----------------------------------------- |
| **index.md**        | Landing page (this page)                  |
| **usage.md**        | How to install & use the library          |
| **testing.md**      | Testing strategy, running tests, coverage |
| **contributing.md** | Guidelines for contributions              |
| **adr.md**          | Summary of all ADRs                       |

---

# **Future Roadmap**

| Sprint       | Milestone                                                     |
| ------------ | ------------------------------------------------------------- |
| **Sprint 1** | Architecture, ADRs, CI Quality Gates, Docs                    |
| **Sprint 2** | Release pipeline (staging → prod), orchestrator integration   |
| **Sprint 3** | Bench-platform integration, distribution & artifact hardening |
| **Sprint 4** | Observability & CI analytics (ADR-014)                        |
| **Sprint 5** | Cost optimization tooling integration                         |
| **Sprint 6** | Hybrid networking & simulation extensions                     |

---

# **Summary**

This repository defines the **engineering baseline** for the entire validation ecosystem.

It provides:

* predictable, high-quality validation primitives
* secure, deterministic CI pipelines
* reproducible builds
* strong documentation
* architectural clarity

Explore the sections on the left to dive deeper.
