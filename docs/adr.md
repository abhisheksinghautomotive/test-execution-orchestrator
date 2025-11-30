# **Architecture Decision Records (ADRs)**

Architecture Decision Records (ADRs) document the key engineering decisions that define the long-term architecture, design, CI/CD, and security posture of the **python-validation-lib** project.
All ADRs live under the `ADRs/` directory in the repository.

ADRs are **immutable once accepted**.
Changes require a **new ADR** describing the modification, rationale, and consequences.

---

## **Purpose of ADRs**

ADRs serve to:

* Capture critical architectural and process decisions
* Provide traceability for future maintainers
* Standardize behavior across all six repositories in the validation ecosystem
* Support audits, security compliance, and reproducible builds
* Ensure decisions survive personnel or context changes

Every new feature or major change **must reference or propose an ADR**.

---

# **ADR Index**

Below is the list of ADRs currently accepted and used by this project.

Each ADR is fully documented under the `ADRs/` directory.

---

## **Core Build & Packaging ADRs**

### **ADR-001 — Packaging Tool Choice (Poetry vs setuptools)**

Defines Poetry as the build system, dependency manager, and environment manager.
Ensures reproducible builds via `pyproject.toml` + `poetry.lock`.

### **ADR-002 — Versioning Policy (Conventional Commits + Tag-Based Releases)**

Specifies that semantic versioning is driven by Git tags and conventional commits.
Used by python-semantic-release.

### **ADR-003 — Artifact Repository Choice (Artifactory vs GitHub Packages)**

Defines the dual-repository strategy:

* GitHub Packages for internal CI integration
* Artifactory as the production source of truth (future sprint)

---

## **Security ADRs**

### **ADR-005 — Security Scanning Policy & Tools**

Defines SAST (Bandit) and SCA (pip-audit / Snyk) rules.
Critical issues block PRs.
Applies to every repo in the ecosystem.

### **ADR-006 — CI/CD Runtime & Hermetic Build Environment**

Specifies use of containerized, pinned, deterministic runners for builds and tests.

### **ADR-008 — Secret Management & Credential Strategy**

Defines authentication policy for:

* GitHub Actions
* Publishing to Artifactory
* Signing keys
  Requires short-lived tokens, no secrets in repo.

### **ADR-016 — Updated Unified Security Policy (SAST + SCA + Secrets + Policy Enforcement)**

Introduces enforcement step that merges Bandit, pip-audit, and Gitleaks results against `.github/security/policy.yml` + allowlist.

---

## **Testing & Quality ADRs**

### **ADR-009 — Test Strategy & Python Version Matrix**

Defines test pyramid:

* unit tests on all PRs
* integration tests reserved for release workflows
* required coverage ≥ 80%
  Also defines Python versions 3.9/3.10/3.11 across the matrix.

### **ADR-010 — Dependency Update & Lockfile Maintenance**

Defines upgrade policy, Dependabot rules, manual update flow, and lockfile checks.

### **ADR-011 — Semantic Release & Changelog Generation**

Describes automation of:

* version bump
* changelog generation
* GitHub Release metadata
* build artifact preparation

---

## **Release & Traceability ADRs**

### **ADR-004 — Release Signing Policy**

Defines signing strategy for wheels/sdists and checksum signing (future sprint).

### **ADR-012 — Artifact Immutability & Deprecation Policy**

Artifacts **must never be deleted** from production repositories.
Only deprecation markers are allowed.

### **ADR-013 — Traceability & Audit Data Model**

Defines the metadata JSON embedded in every release:
commit SHA, build ID, CI URL, changelog, artifact checksums, Python versions, etc.

---

## **Process ADRs**

### **ADR-007 — Branching, Merge Strategy & Protection Rules**

Defines:

* Conventional Commit rules
* Required PR checks
* main-branch protections
* feature branch model
* squash-merge strategy

### **ADR-014 — Observability & CI Metrics**

Defines CI metrics emitted in `ci-metrics.json` for all repos.
Future integration with testbench-observability (Sprint 4).

### **ADR-015 — Licensing & Contribution Policy**

Defines MIT license usage, contributor rules, pre-commit, and documentation requirements.

---

# **How to Create a New ADR**

1. Copy `ADRs/ADR-000.md` (template).
2. Rename to `ADR-XYZ-title.md` where `XYZ` is the next number.
3. Fill in:

   * Context
   * Decision
   * Rationale
   * Consequences
   * Implementation Notes
4. Submit as part of a PR with label:

   ```
   type:adr
   ```

If the ADR changes existing behavior, reference affected ADRs under “Consequences”.

---

# **Referencing ADRs in Code and PRs**

When making a change affecting architecture:

* Reference ADR in commit:

  ```
  ref: ADR-009
  ```
* Reference in PR description:

  ```
  This PR implements ADR-011 section “Release automation”.
  ```
* Add comments in code only when clarifying architectural constraints:

  ```python
  # Follows DIP per ADR-009
  ```

---

# **Summary**

ADRs are a critical part of this project's governance.
They enforce clarity, traceability, confidence, and long-term maintainability across the entire validation ecosystem.

Whenever in doubt:

* **Check the ADRs first.**
* **Create a new ADR if the architecture changes.**
