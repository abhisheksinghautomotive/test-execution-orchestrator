# **Testing Guide**

This document describes how testing works in **python-validation-lib**, including test structure, conventions, coverage requirements, CI expectations, and how to write new tests.

This library establishes the **test baseline** for all future repositories in the validation ecosystem.
Tests must be **fast, deterministic, isolated, and reproducible**.

---

# **1. Test Structure**

```
tests/
├── unit/
│   ├── test_smoke.py
│   ├── test_imports.py
│   ├── test_models_and_api.py
│   ├── test_validator_and_rules.py
│   ├── test_adapters_filesystem_logging.py
│   ├── test_adapters_registry.py
│   └── test_runner_loader.py
└── conftest.py
```

### **Unit Tests**

* Cover individual components in isolation
* No external dependencies
* No filesystem/network unless mocked
* Fast (<100ms per test)

### **Integration Tests (Future: Sprint 2+)**

Executed only in release workflows:

* Runner + validator chains
* Staging artifact tests
* Behavior against orchestrator API (mocked + real staging)

### **Contract/API Tests**

* Validate public API surface does not break
* Validate import paths
* Validate dataclass structures

---

# **2. Running Tests**

### **Run all unit tests**

```bash
poetry run pytest
```

### **Run with verbose output**

```bash
poetry run pytest -vv
```

### **Run specific file**

```bash
poetry run pytest tests/unit/test_validator_and_rules.py
```

### **Run a single test**

```bash
poetry run pytest -k test_specific_case
```

---

# **3. Coverage Requirements (≥ 80%)**

Coverage is enforced via:

* **Local script**: `scripts/ci-lint.sh`
* **CI coverage gate**: 80% threshold
* **coverage.xml** parsed in GitHub Actions

Run with coverage:

```bash
poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml
```

View detailed report:

```bash
poetry run coverage html
open htmlcov/index.html
```

---

# **4. Writing New Tests**

### **Test naming convention**

```
test_<module>_<behavior>()
```

### **Example: Testing a rule**

```python
from python_validation_lib.core.rules import BaseRule

class AlwaysTrue(BaseRule):
    def check(self, value):
        return True

    @property
    def name(self):
        return "always_true"

def test_rule_always_true():
    rule = AlwaysTrue()
    assert rule.check(10)
    assert rule.name == "always_true"
```

### **Example: Testing a validator**

```python
from python_validation_lib.core.validator import BaseValidator
from python_validation_lib.models.validation_result import ValidationResult

class DummyValidator(BaseValidator):
    def validate(self, value):
        return ValidationResult(passed=True, details={"ok": True})

def test_dummy_validator():
    v = DummyValidator()
    result = v.validate("input")
    assert result.passed
    assert result.details["ok"] is True
```

### **Example: Using pytest fixtures (`conftest.py`)**

```python
import pytest

@pytest.fixture
def sample_value():
    return 42

def test_with_fixture(sample_value):
    assert sample_value == 42
```

---

# **5. Testing Guidelines**

### **1. No external systems**

* No live API calls
* No writing outside test temp directory
* No network dependency

### **2. Deterministic**

* Use fixed inputs
* No randomness unless seeded
* No flaky behavior

### **3. Small, targeted tests**

* One assertion per behavior when possible
* Avoid “god tests” that test multiple unrelated behaviors

### **4. Avoid touching the filesystem**

If necessary:

```python
from pathlib import Path

tmp = Path(tmp_path)  # pytest provides tmp_path
```

### **5. Test against public API**

Import from:

```python
import python_validation_lib
```

Not from deep internal paths unless the test explicitly requires it.

---

# **6. CI Testing Workflow**

Every pull request triggers:

### **1. Unit tests across matrix**

```
Python 3.9
Python 3.10
Python 3.11
```

### **2. Coverage gate**

Must be ≥ 80%.

### **3. Mypy type checking**

Ensures typed public surface.

### **4. SAST (Bandit)**

Must not contain high/critical issues.

### **5. SCA (pip-audit)**

Fail only on blocking vulnerabilities (per ADR-016).

### **6. Secrets scan (Gitleaks)**

### **7. Policy enforcement**

`enforce_security_policy.py` merges all scans and applies rules from:

```
.github/security/policy.yml
.github/security/allowlist.yml
```

---

# **7. Testing the Release Workflow (dry-run)**

You may test the release process without publishing:

```bash
./scripts/release_dryrun.sh --create-dry-tag
```

This validates:

* semantic-release version bump
* changelog rendering
* dist build
* traceability metadata (ADR-013)
* optional dry-run tag + draft GitHub Release

---

# **8. Testing Plugin Registry**

Example test:

```python
from python_validation_lib.adapters.registry import REGISTRY

def test_registry_register_and_get():
    class X: pass

    REGISTRY.unregister("x")
    REGISTRY.register("x", X)
    assert REGISTRY.get("x") is X
```

---

# **9. When Tests Must Be Updated**

Update tests when:

* public API changes (ADR-002 / ADR-011)
* new validation rules introduced
* `.services.runner` logic changes
* registry behavior changes
* new adapters added
* new models added or updated

Never remove tests without **replacing them with equivalent coverage**.

---

# **10. Troubleshooting**

### **Import errors**

Activate Poetry environment:

```bash
poetry shell
```

### **Missing coverage.xml in CI**

Ensure you ran:

```bash
pytest --cov=src --cov-report=xml
```

### **Test flakiness**

Run with repeat:

```bash
pytest --count=10
```

### **Bandit false positives**

Use allowlist file:

```
.github/security/allowlist.yml
```

---

# **Summary**

Testing is an essential quality gate in this project.
All changes must preserve:

* determinism
* reproducibility
* ≥ 80% coverage
* SOLID architecture boundaries
* CI consistency
* security posture

Following this guide ensures your contributions remain robust and aligned with the project’s engineering standards.
