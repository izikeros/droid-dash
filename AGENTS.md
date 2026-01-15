# droid-dash

TUI dashboard for Factory.ai Droid session analytics - track tokens, costs, and explore sessions.

## Core Commands

- `make install` - Create venv and install all dependencies with uv
- `make test` - Run pytest test suite
- `make lint` - Check code style with ruff
- `make format` - Auto-format code with ruff
- `make type` - Run mypy type checker
- `make build` - Build package with uv
- `make run` - Launch TUI dashboard
- `make nox` - Run multi-version tests (Python 3.9-3.13)
- `make nox-list` - List available nox sessions

## Project Layout

```
├── src/droid_dash/
│   ├── core/           # Backend logic
│   │   ├── models.py   # Data models (Session, Project, TokenUsage)
│   │   ├── parser.py   # Session file parser
│   │   ├── aggregator.py # Statistics aggregation
│   │   ├── cost.py     # Token cost estimation
│   │   ├── config.py   # TOML configuration management
│   │   └── grouping.py # Project grouping logic
│   ├── tui/            # Textual TUI frontend
│   │   ├── app.py      # Main app, screens, modals
│   │   └── widgets/    # Custom widgets (heatmap, charts)
│   └── cli.py          # Click CLI entry point
├── tests/              # pytest tests
│   ├── test_*.py       # Unit tests
│   └── test_tui/       # TUI tests with snapshots
└── docs/               # MkDocs documentation
```

## Development Patterns & Constraints

**Python Compatibility (3.9-3.13):**
- Always use `from __future__ import annotations` for union type hints (`X | None`)
- Use `datetime.timezone.utc` instead of `datetime.UTC` (3.11+ only)
- Conditional import for tomllib: `tomllib` (3.11+) or `tomli` (3.9-3.10)

**Code Style:**
- Ruff for linting and formatting
- Type hints required for all public functions
- Tests use pytest with pytest-textual-snapshot for visual regression

**Dependencies:**
- Textual for TUI framework
- Rich for terminal rendering
- Click for CLI
- Pydantic for data validation

**Tools:**
- All tools run via `.venv/bin/` prefix or `uv run`
- Use `uv sync --group dev` for dependency installation
- Use `uv build` for package building

## Git Workflow

- Branch from `main` with descriptive names
- Run `make lint test` before committing
- Never force-push to `main`

**Commit Messages (STRICT):**
- Use conventional commits format: `type: description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`
- Keep subject line under 72 characters
- **DO NOT add "Co-authored-by" lines** - no co-author attribution in commits
- Example: `feat: add dark mode toggle to settings`

**Versioning (ACTIVE):**
- **Be proactive** - commit changes frequently and bump version after completing features
- For every major piece of completed work:
  1. Commit all changes
  2. Run `make bump-patch` (or `bump-minor`/`bump-major` as appropriate)
  3. Run `make changelog` to update CHANGELOG.md
  4. Commit the version bump and changelog update
- This creates a git tag automatically (e.g., `v0.1.1`)

## Gotchas

- Session files are in `~/.factory/sessions/` with `.jsonl` format
- The TUI uses reactive patterns - update reactive vars to trigger UI refresh
- DataTable requires `cursor_type="row"` for row selection to work
- Use `markup=False` when displaying user content to avoid Rich markup errors
