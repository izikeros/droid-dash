# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-14

### Added

- **Overview Tab**: Summary statistics, token usage breakdown, activity heatmap, top projects
- **Groups Tab**: Project group statistics with share bar charts (tokens, cost, active time)
- **Projects Tab**: Per-project statistics with clickable column sorting
- **Sessions Tab**: Session browser with sorting, grouping, filtering, and prompts side panel
- **Favorites Tab**: Quick access to favorite sessions with persistent storage
- **Settings Tab**: Configurable display defaults, column visibility, pricing, and paths
- Session title editing with modal dialog
- Connect to session feature - resume Droid sessions directly from dashboard
- Dark/light mode toggle
- CLI commands: `stats`, `tokens`, `groups`, `export`
- Configuration file support (TOML) at `~/.config/factory-dashboard/config.toml`
- Custom pricing per model for cost estimation
- GitHub-style activity heatmap widget
- Share bar chart widget for distribution visualization

### Technical

- Textual-based TUI with tabbed interface
- Separated backend (core) and frontend (tui) architecture
- Session parser for Factory.ai `.settings.json` and `.jsonl` files
- Cost estimation for Claude Opus, Sonnet, and Haiku models
- Python 3.9+ support

[Unreleased]: https://github.com/izikeros/factory-dashboard/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/izikeros/factory-dashboard/releases/tag/v0.1.0
