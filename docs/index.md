# Factory Dashboard

A terminal-based dashboard for analyzing [Factory.ai](https://factory.ai) Droid sessions. Track token usage, estimate costs, explore session history, and connect to previous sessions directly from the TUI.

![Demo](https://raw.githubusercontent.com/izikeros/factory-dashboard/main/demo.gif)

## Features

- **Overview Dashboard** - Summary statistics, token breakdown, activity heatmap
- **Groups & Projects** - Aggregate statistics by project group with share charts
- **Sessions Explorer** - Browse, filter, sort sessions with prompts preview
- **Favorites** - Quick access to marked favorite sessions
- **Settings** - Configure display defaults, pricing, and paths
- **Connect to Session** - Resume Droid sessions directly from the dashboard

## Quick Install

```bash
pip install factory-dashboard
```

## Quick Start

```bash
# Launch the TUI dashboard
factory-dashboard

# Or use CLI commands
factory-dashboard stats
factory-dashboard tokens --limit 10
```

## Screenshots

### Overview Tab
![Overview](https://raw.githubusercontent.com/izikeros/factory-dashboard/main/screenshots/overview.svg)

### Sessions Tab
![Sessions](https://raw.githubusercontent.com/izikeros/factory-dashboard/main/screenshots/sessions.svg)

## Requirements

- Python 3.9+
- Factory.ai Droid sessions (stored in `~/.factory/sessions`)

## License

MIT License - see [LICENSE](https://github.com/izikeros/factory-dashboard/blob/main/LICENSE) for details.
