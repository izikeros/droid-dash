# Installation

## From PyPI (Recommended)

```bash
pip install factory-dashboard
```

## From Source

```bash
git clone https://github.com/izikeros/factory-dashboard.git
cd factory-dashboard
pip install -e .
```

## Development Installation

For development with all tools:

```bash
pip install -e ".[dev]"
```

## Requirements

- **Python**: 3.9 or higher
- **Dependencies**: Automatically installed
    - `textual` - TUI framework
    - `rich` - Terminal formatting
    - `click` - CLI framework
    - `pydantic` - Data validation
    - `tomli` - TOML parsing (Python < 3.11)

## Verify Installation

```bash
# Check version
factory-dashboard --help

# Run the dashboard
factory-dashboard
```

## Troubleshooting

### Command not found

If `factory-dashboard` is not found after installation, ensure your Python scripts directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors

If you get import errors, try reinstalling:

```bash
pip uninstall factory-dashboard
pip install factory-dashboard
```
