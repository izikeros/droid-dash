"""Nox configuration for multi-version testing."""

import nox

# Use uv as backend to automatically download Python versions
nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
DEFAULT_PYTHON = "3.11"


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite across Python versions."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", "tests/", "-v", "--tb=short")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Run ruff linter."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "check", "src/", "tests/")


@nox.session(python=DEFAULT_PYTHON)
def format_check(session: nox.Session) -> None:
    """Check code formatting with ruff."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "format", "--check", "src/", "tests/")


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run mypy type checker."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("mypy", "src/droid_dash", "--ignore-missing-imports")


@nox.session(python=DEFAULT_PYTHON)
def coverage(session: nox.Session) -> None:
    """Run tests with coverage report."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run(
        "pytest",
        "tests/",
        "-v",
        "--cov=droid_dash",
        "--cov-report=term-missing",
        "--cov-report=html",
    )


@nox.session(python=DEFAULT_PYTHON)
def build(session: nox.Session) -> None:
    """Build the package."""
    session.run("uv", "build", external=True)
