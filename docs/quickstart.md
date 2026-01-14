# Quick Start

## Launch the Dashboard

After installation, simply run:

```bash
factory-dashboard
```

This opens the TUI dashboard showing your Factory.ai Droid session analytics.

## Navigation

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1-6` | Switch tabs (Overview, Groups, Projects, Sessions, Favorites, Settings) |
| `e` | Edit session title (Sessions/Favorites tab) |
| `f` | Toggle favorite status |
| `c` | Connect to session (resume in Droid) |
| `d` | Toggle dark/light mode |
| `r` | Refresh data |
| `q` | Quit |

### Tabs

1. **Overview** - Summary statistics and activity heatmap
2. **Groups** - Project groups with share distribution charts
3. **Projects** - Per-project statistics (click headers to sort)
4. **Sessions** - Browse all sessions with filters and prompts panel
5. **Favorites** - Quick access to marked sessions
6. **Settings** - Configure defaults and preferences

## CLI Commands

Quick access without launching the full TUI:

```bash
# Show statistics
factory-dashboard stats

# Token usage by project
factory-dashboard tokens

# List groups
factory-dashboard groups

# Export data
factory-dashboard export --format json --output sessions.json
```

## Custom Sessions Directory

If your sessions are in a different location:

```bash
factory-dashboard --sessions-dir /path/to/sessions
```

## Next Steps

- [Usage Guide](usage.md) - Detailed feature documentation
- [Configuration](configuration.md) - Customize the dashboard
- [CLI Reference](cli.md) - All CLI commands
