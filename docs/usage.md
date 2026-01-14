# TUI Dashboard Usage

## Overview Tab

The Overview tab provides a high-level summary of your Factory.ai usage:

- **Summary Statistics**: Total sessions, projects, groups, active time, estimated cost
- **Token Distribution**: Visual breakdown of input, output, cache tokens
- **Activity Heatmap**: GitHub-style calendar showing session frequency
- **Top Projects**: Projects with highest token usage

## Groups Tab

View aggregate statistics by project group:

- **Statistics Table**: Projects, sessions, tokens, cost per group
- **Share Charts**: Visual distribution of tokens, cost, and active time across groups

## Projects Tab

Per-project statistics with interactive sorting:

- **Click column headers** to sort by that column
- **Click again** to reverse sort order
- Sorted column shows indicator (▼ descending, ▲ ascending)

Columns: Project, Group, Sessions, Tokens, Active Time, Est. Cost

## Sessions Tab

Browse and explore all sessions:

### Controls

- **Sort by**: Date, Tokens, or Duration (ascending/descending)
- **Group by**: None, Project, Group, or Model
- **Hide empty sessions**: Filter out sessions with no prompts

### Session List

- **★ column**: Favorite indicator
- **Title**: Session title (editable with `e` key)
- **Prompts Panel**: Shows user prompts for selected session

### Actions

| Key | Action |
|-----|--------|
| `e` | Edit session title |
| `f` | Toggle favorite |
| `c` | Connect to session |

## Favorites Tab

Quick access to marked favorite sessions:

- Same features as Sessions tab
- Toggle favorites with `f` key
- Favorites persist across sessions (stored in `.favorites` file)

## Settings Tab

Configure dashboard behavior:

### Display Defaults

- Default tab on startup
- Default sort order and grouping
- Hide empty sessions toggle
- Dark mode toggle
- Heatmap weeks to display

### Column Visibility

Show/hide columns in the sessions table.

### Pricing

Customize token pricing for cost estimation:

- Input tokens per million
- Output tokens per million
- Cache write/read tokens per million

### Paths

Configure the sessions directory location.

## Connect to Session

Press `c` on a selected session to:

1. Exit the dashboard
2. Change to the session's original project directory
3. Launch `droid -r <session_id>` to resume the session

!!! note
    Requires `droid` command to be available in PATH.

## Keyboard Shortcuts Reference

| Key | Action | Available On |
|-----|--------|--------------|
| `1` | Overview tab | All |
| `2` | Groups tab | All |
| `3` | Projects tab | All |
| `4` | Sessions tab | All |
| `5` | Favorites tab | All |
| `6` | Settings tab | All |
| `e` | Edit title | Sessions, Favorites |
| `f` | Toggle favorite | Sessions, Favorites |
| `c` | Connect to session | Sessions, Favorites |
| `d` | Toggle dark mode | All |
| `r` | Refresh data | All |
| `q` | Quit | All |
