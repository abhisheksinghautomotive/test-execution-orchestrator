# **Usage Guide**

This page explains how to install, import, and use the `python-validation-lib` package.
The examples below are designed for developers integrating the library into test-orchestration systems, validation runners, and supporting tools.

---

# **1. Installation**

### **From source (local development)**

```bash
poetry install
```

### **From a built artifact (wheel / sdist)**

Once published (future sprint):

```bash
pip install python-validation-lib
```

### **From Artifactory (future)**

As per ADR-003 (Artifact Repository):

```bash
pip install --index-url <artifactory-url> python-validation-lib
```

---

# **2. Package Overview**

The package follows a SOLID-aligned internal structure:

```
python_validation_lib/
├── core/        # Validation rules, interfaces, base validators
├── models/      # Domain-level objects (ValidationResult, etc.)
├── services/    # Runners/loaders orchestrating full validation flows
└── adapters/    # Logging, file-system abstraction, registries, plugins
```

The **public API** is exposed through:

```python
from python_validation_lib import (
    __version__,
    BaseValidator,
    ValidationRunner,
    ValidationResult,
    Registry,
    REGISTRY,
    get_logger,
)
```

---

# **3. Basic Concepts**

### **Validation Rule**

A validation rule checks a single aspect of input data.

### **Validator**

A validator applies multiple rules and returns structured results.

### **Runner**

A high-level orchestrator that:

* loads validators
* executes them
* aggregates results

### **Registry**

A thread-safe plugin registry for validators, adapters, and dynamic extensions.

---

# **4. Examples**

## **4.1. Creating a Custom Rule**

```python
# rules/example_rule.py
from python_validation_lib.core.rules import BaseRule

class IsPositive(BaseRule):
    def check(self, value: int) -> bool:
        return value > 0

    @property
    def name(self) -> str:
        return "is_positive"
```

---

## **4.2. Creating a Custom Validator**

```python
from python_validation_lib.core.validator import BaseValidator
from python_validation_lib.models.validation_result import ValidationResult
from rules.example_rule import IsPositive

class NumberValidator(BaseValidator):
    def __init__(self) -> None:
        self.rules = [IsPositive()]

    def validate(self, value: int) -> ValidationResult:
        results = {rule.name: rule.check(value) for rule in self.rules}
        passed = all(results.values())
        return ValidationResult(passed=passed, details=results)
```

---

## **4.3. Using the Validation Runner**

```python
from python_validation_lib.services.runner import ValidationRunner
from number_validator import NumberValidator

runner = ValidationRunner()
result = runner.run(NumberValidator(), value=5)

print(result)
```

Output:

```
ValidationResult(passed=True, details={'is_positive': True})
```

---

## **4.4. Using the Plugin Registry**

```python
from python_validation_lib.adapters.registry import REGISTRY

# Register validator under a named key
REGISTRY.register("number_validator", NumberValidator)

# Retrieve dynamically
ValidatorClass = REGISTRY.get("number_validator")
validator = ValidatorClass()
```

---

## **4.5. Logging**

```python
from python_validation_lib.adapters.logging import get_logger

logger = get_logger(__name__)
logger.info("Validation started")
```

---

# **5. Working With Validation Results**

```python
from python_validation_lib.models.validation_result import ValidationResult

result = ValidationResult(
    passed=False,
    details={"is_positive": False}
)

if not result.passed:
    print("Failed:", result.details)
```

---

# **6. Using This Library in Test-Orchestration Systems**

Future integration (Sprint 2+):

* The orchestrator imports validators and runners
* Uses the registry for dependency injection
* Consumes the package version for traceability (ADR-013)
* Executes the library inside isolated CI agents or bench nodes

Example usage:

```python
import python_validation_lib

print("Using version:", python_validation_lib.__version__)
```

---

# **7. Error Handling**

All validators must:

* raise deterministic exceptions
* avoid catching errors silently
* use clear return types (`ValidationResult`)
* avoid side effects inside rules or validators

The library itself raises:

* `KeyError` for missing registry entries
* `ValueError` for misconfigured validators
* `RuntimeError` for invalid runner states

---

# **8. Recommended Project Structure for Users**

If you integrate this library in another repo:

```
my_project/
├── validators/
│   ├── custom_rule.py
│   └── custom_validator.py
├── orchestrator/
└── main.py
```

Import everything through the public API:

```python
from python_validation_lib import BaseValidator, ValidationRunner
```

---

# **9. Versioning & Compatibility**

This library uses:

* **Semantic Versioning (ADR-002)**
* Release automation via **python-semantic-release (ADR-011)**

Breaking changes bump **major** version.
New features bump **minor** version.
Fixes bump **patch** version.

---

# **10. Troubleshooting**

### Import errors

Ensure Poetry environment active:

```bash
poetry shell
```

### Registry errors

`KeyError`: the plugin name is not registered.

### Validation failed unexpectedly

Print details:

```python
print(result.details)
```

### Logging not appearing

Use correct logger:

```python
logger = get_logger("python_validation_lib")
```

---

# **Summary**

This library provides a clean, extensible foundation for Python-based validation workflows.
Use runners, validators, rules, models, and adapters as building blocks to assemble your own validation pipelines and integrate them into larger testbench platforms.
