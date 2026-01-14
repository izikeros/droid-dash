# Contributing to Factory Dashboard

Thank you for your interest in contributing to Factory Dashboard! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/izikeros/factory-dashboard.git
   cd factory-dashboard
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Run the tests to make sure everything is working:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### Running the Dashboard

```bash
# With test data
factory-dashboard -d test_sessions

# With your own Factory.ai sessions
factory-dashboard
```

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Run linter
ruff check src/

# Run type checker
mypy src/factory_dashboard --ignore-missing-imports

# Run tests with coverage
pytest tests/ -v --cov=factory_dashboard

# Format code (if needed)
ruff format src/ tests/
```

### Running Tests

Run the full suite (unit + TUI tests):
```bash
PYTHONPATH=src pytest tests/ -v
```

#### TUI & BDD-style Tests
These tests use Textual's Pilot framework to simulate user interaction:

```bash
# Run only TUI functionality tests
PYTHONPATH=src pytest tests/test_tui/test_pilot_navigation.py -v

# Run all TUI related tests (including snapshots)
PYTHONPATH=src pytest tests/test_tui/ -v
```

#### Visual Snapshot Testing
We use visual snapshots to prevent UI regressions:

```bash
# Verify UI matches existing snapshots
PYTHONPATH=src pytest tests/test_tui/test_snapshots.py -v

# Update snapshots after intentional UI changes
PYTHONPATH=src pytest tests/test_tui/test_snapshots.py --snapshot-update
```

#### Coverage
```bash
PYTHONPATH=src pytest tests/ --cov=factory_dashboard --cov-report=html
```

## Making Changes

### Branch Naming

- `feature/` - New features (e.g., `feature/add-export-csv`)
- `fix/` - Bug fixes (e.g., `fix/parser-encoding-error`)
- `docs/` - Documentation changes (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-aggregator`)

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add CSV export for session data
fix: handle missing cwd field in session files
docs: update installation instructions
```

### Pull Request Process

1. Fork the repository and create your branch from `main`
2. Make your changes with appropriate tests
3. Ensure all tests pass and linting is clean
4. Update documentation if needed
5. Submit a pull request with a clear description of changes

## Project Structure

```
factory-dashboard/
├── src/factory_dashboard/
│   ├── core/           # Backend logic (parser, aggregator, cost)
│   │   ├── models.py   # Data models
│   │   ├── parser.py   # Session file parser
│   │   ├── config.py   # Configuration management
│   │   ├── cost.py     # Cost estimation
│   │   └── ...
│   ├── tui/            # TUI frontend (Textual)
│   │   ├── app.py      # Main application
│   │   └── widgets/    # Custom widgets
│   └── cli.py          # CLI entry point
├── tests/              # Test suite
├── docs/               # MkDocs documentation
└── scripts/            # Utility scripts
```

## Adding New Features

### Adding a New Widget

1. Create the widget in `src/factory_dashboard/tui/widgets/`
2. Export it from `widgets/__init__.py`
3. Add tests if the widget has complex logic
4. Update the app to use the widget

### Adding a New CLI Command

1. Add the command in `src/factory_dashboard/cli.py`
2. Follow the existing Click command patterns
3. Add help text and examples

### Adding Configuration Options

1. Add the option to appropriate config class in `core/config.py`
2. Update the TOML parsing in `_parse_config()`
3. Update the TOML writing in `save_config()`
4. Add to Settings tab UI if user-configurable
5. Add tests for the new option

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages or screenshots

## Questions?

Feel free to open an issue for any questions about contributing.
