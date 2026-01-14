# CLI Reference

Factory Dashboard provides CLI commands for quick access to statistics without launching the TUI.

## Global Options

```bash
factory-dashboard [OPTIONS] COMMAND
```

| Option | Description |
|--------|-------------|
| `-d, --sessions-dir PATH` | Path to Factory sessions directory |
| `-c, --config PATH` | Path to config file (TOML) |
| `--help` | Show help message |

## Commands

### `stats`

Display overall statistics.

```bash
factory-dashboard stats [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-g, --group TEXT` | Filter by project group |
| `-p, --project TEXT` | Filter by project name |

**Examples:**

```bash
# All statistics
factory-dashboard stats

# Filter by group
factory-dashboard stats --group work

# Filter by project
factory-dashboard stats --project my-api
```

### `tokens`

Display token usage breakdown by project.

```bash
factory-dashboard tokens [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit INTEGER` | Number of projects to show (default: 10) |

**Examples:**

```bash
# Top 10 projects by tokens
factory-dashboard tokens

# Top 20 projects
factory-dashboard tokens --limit 20
```

### `groups`

List all project groups with statistics.

```bash
factory-dashboard groups
```

### `export`

Export session data to JSON or CSV.

```bash
factory-dashboard export [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--format [json\|csv]` | Output format (default: json) |
| `--output PATH` | Output file path |

**Examples:**

```bash
# Export to JSON
factory-dashboard export --format json --output sessions.json

# Export to CSV
factory-dashboard export --format csv --output sessions.csv
```

## Usage Examples

### Quick Statistics Check

```bash
$ factory-dashboard stats
      Session Statistics      
┌─────────────────┬──────────┐
│ Total Sessions  │ 110      │
│ Total Projects  │ 20       │
│ Project Groups  │ 4        │
│ Total Tokens    │ 548.6M   │
│ Cache Hit Ratio │ 93.9%    │
│ Estimated Cost  │ $1549.14 │
└─────────────────┴──────────┘
```

### Compare Groups

```bash
$ factory-dashboard groups
        Project Groups         
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ Group  ┃ Projects ┃ Cost     ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ work   │ 5        │ $386.77  │
│ priv   │ 11       │ $1045.56 │
└────────┴──────────┴──────────┘
```

### Export for Analysis

```bash
# Export to JSON for further processing
factory-dashboard export --format json --output ~/sessions.json

# Use with jq
cat ~/sessions.json | jq '.sessions | length'
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid arguments, missing files, etc.) |
