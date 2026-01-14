---
name: uv-package-management
description: Manage Python projects with uv for fast dependency resolution, virtual environments, package building, and CI integration. Use when setting up or managing Python project dependencies.
---

# UV Package Management

## When to Use

Use this skill when:
- Setting up a new Python project
- Managing dependencies and virtual environments
- Building and publishing Python packages
- Configuring CI/CD with fast dependency installation

## Instructions

### 1. Project Setup

```bash
uv venv --python 3.11
uv python pin 3.11
uv sync
```

### 2. Dependency Management

pyproject.toml with dependency groups:

```toml
[project]
dependencies = [
    "textual>=0.47.0",
    "rich>=13.0.0",
]

[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "nox>=2024.0.0",
]
```

Install commands:

```bash
uv sync                    # Main dependencies only
uv sync --group dev        # With dev dependencies
uv add requests            # Add new dependency
uv add --group dev mypy    # Add to dev group
```

### 3. Running Tools

```bash
uv run pytest tests/ -v
uv run ruff check src/
.venv/bin/pytest tests/    # Direct venv usage
```

### 4. Building Packages

```bash
uv build
```

### 5. GitHub Actions CI

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
  - uses: astral-sh/setup-uv@v4
  - run: uv sync --group dev
  - run: uv run pytest tests/ -v
```

### 6. Makefile Integration

```makefile
VENV = .venv/bin

install:
	uv venv --python 3.11
	uv sync --group dev

test:
	$(VENV)/pytest tests/ -v

build:
	uv build
```

## Common Commands

| Task | Command |
|------|---------|
| Create venv | uv venv --python 3.11 |
| Install deps | uv sync --group dev |
| Add dependency | uv add package |
| Run tool | uv run pytest |
| Build package | uv build |
| Lock deps | uv lock |

## Verification

1. Check uv.lock is committed to git
2. Verify uv sync installs all required packages
3. Test CI workflow installs dependencies correctly
