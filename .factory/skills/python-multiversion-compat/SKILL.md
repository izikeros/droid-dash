---
name: python-multiversion-compat
description: Ensure Python code works across versions 3.9-3.13. Handle tomllib/tomli imports, datetime.UTC, union type syntax, and other version-specific APIs. Use when maintaining cross-version compatibility.
---

# Python Multi-Version Compatibility (3.9-3.13)

## When to Use

Use this skill when:
- Writing code that must work on Python 3.9 through 3.13
- Encountering ImportError or TypeError on older Python versions
- Using modern type hints in code that needs backward compatibility

## Instructions

### 1. Union Type Syntax

The `X | None` syntax is only available at runtime in Python 3.10+.

Add future annotations import at the top of every file:

```python
from __future__ import annotations

def my_function(value: str | None = None) -> dict | list:
    ...
```

### 2. datetime.UTC

`datetime.UTC` was added in Python 3.11. Use `datetime.timezone.utc` instead:

```python
from datetime import datetime, timezone
dt = datetime.now(timezone.utc)
```

### 3. tomllib Module

`tomllib` was added in Python 3.11. Use conditional import:

```python
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

Add conditional dependency in pyproject.toml:

```toml
dependencies = [
    "tomli>=2.0.0; python_version < '3.11'",
]
```

### 4. Ruff Configuration

Set target version in ruff.toml:

```toml
target-version = "py39"
```

### 5. Testing Multiple Versions

Use nox for multi-version testing:

```python
import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]

@nox.session(python=PYTHON_VERSIONS)
def tests(session):
    session.install("-e", ".[dev]")
    session.run("pytest", "tests/", "-v")
```

## Common Version-Specific Issues

| Feature | Available From | Workaround |
|---------|---------------|------------|
| X or None syntax | 3.10 | future annotations import |
| datetime.UTC | 3.11 | datetime.timezone.utc |
| tomllib | 3.11 | tomli package |
| Self type | 3.11 | typing_extensions.Self |

## Verification

1. Run nox to test across all Python versions
2. Check CI matrix results for each Python version
3. Set ruff target-version to minimum supported version
