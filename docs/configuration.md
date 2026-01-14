# Configuration

Factory Dashboard supports persistent configuration via TOML files.

## Config File Locations

Configuration is loaded from (in priority order):

1. Path specified via `--config` CLI option
2. `~/.config/factory-dashboard/config.toml`
3. `~/.factory-dashboard.toml`
4. Built-in defaults

## Creating a Config File

You can create a config file manually or use the Settings tab in the TUI to save your preferences.

## Configuration Options

### Full Example

```toml
[display]
default_tab = "sessions"
default_sort = "tokens_desc"
default_group = "project"
hide_empty_sessions = true
dark_mode = true
heatmap_weeks = 20

[columns.sessions]
show_title = true
show_date = true
show_project = true
show_model = true
show_tokens = true
show_favorites = true
show_prompts = true
show_duration = true

[pricing.default]
input_per_million = 3.0
output_per_million = 15.0
cache_write_per_million = 3.75
cache_read_per_million = 0.30

[pricing.models."claude-opus-4-5-20251101"]
input_per_million = 15.0
output_per_million = 75.0
cache_write_per_million = 18.75
cache_read_per_million = 1.50

[paths]
sessions_dir = "~/.factory/sessions"
```

### Display Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_tab` | string | `"sessions"` | Tab to show on startup: `overview`, `groups`, `projects`, `sessions`, `favorites` |
| `default_sort` | string | `"tokens_desc"` | Default sort order: `date_desc`, `date_asc`, `tokens_desc`, `tokens_asc`, `duration_desc`, `duration_asc` |
| `default_group` | string | `"project"` | Default grouping: `none`, `project`, `group`, `model` |
| `hide_empty_sessions` | bool | `true` | Hide sessions with no prompts |
| `dark_mode` | bool | `true` | Use dark theme |
| `heatmap_weeks` | int | `20` | Weeks to show in activity heatmap |

### Column Visibility

Control which columns appear in the sessions table:

| Option | Default | Description |
|--------|---------|-------------|
| `show_title` | `true` | Session title |
| `show_date` | `true` | Session date |
| `show_project` | `true` | Project name |
| `show_model` | `true` | Model used |
| `show_tokens` | `true` | Token count |
| `show_favorites` | `true` | Favorite indicator |
| `show_prompts` | `true` | Prompt count |
| `show_duration` | `true` | Active time |

### Pricing

Customize token pricing for cost estimation.

#### Default Pricing

Applied to unknown models:

```toml
[pricing.default]
input_per_million = 3.0
output_per_million = 15.0
cache_write_per_million = 3.75
cache_read_per_million = 0.30
```

#### Per-Model Pricing

Override pricing for specific models:

```toml
[pricing.models."claude-opus-4-5-20251101"]
input_per_million = 15.0
output_per_million = 75.0
cache_write_per_million = 18.75
cache_read_per_million = 1.50

[pricing.models."claude-3-haiku-20240307"]
input_per_million = 0.25
output_per_million = 1.25
cache_write_per_million = 0.30
cache_read_per_million = 0.03
```

### Paths

| Option | Default | Description |
|--------|---------|-------------|
| `sessions_dir` | `"~/.factory/sessions"` | Factory sessions directory |

## Using Custom Config

```bash
# Use specific config file
factory-dashboard --config /path/to/config.toml

# Use custom sessions directory (overrides config)
factory-dashboard --sessions-dir /path/to/sessions
```

## Editing via TUI

The Settings tab (key `6`) provides a UI for editing configuration:

1. Navigate to Settings tab
2. Modify values using form controls
3. Click "Save Configuration" to persist changes

Changes are saved to `~/.config/factory-dashboard/config.toml`.
