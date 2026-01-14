# API Reference

Droid Dash is primarily a CLI/TUI tool, but its core modules can be used programmatically.

## Core Modules

### Models

::: droid_dash.core.models
    options:
      show_root_heading: true
      members:
        - Session
        - TokenUsage
        - Project
        - ProjectGroup
        - UserPrompt
        - DashboardStats

### Parser

::: droid_dash.core.parser
    options:
      show_root_heading: true
      members:
        - SessionParser

### Cost Estimation

::: droid_dash.core.cost
    options:
      show_root_heading: true
      members:
        - CostEstimator
        - ModelPricing
        - format_cost

### Configuration

::: droid_dash.core.config
    options:
      show_root_heading: true
      members:
        - Config
        - DisplayConfig
        - ColumnConfig
        - PricingConfig
        - PathsConfig
        - load_config
        - save_config

## Usage Examples

### Parse Sessions

```python
from droid_dash.core.parser import SessionParser

parser = SessionParser("~/.factory/sessions")
sessions = parser.parse_all_sessions()

for session in sessions:
    print(f"{session.title}: {session.tokens.total_tokens} tokens")
```

### Estimate Costs

```python
from droid_dash.core.parser import SessionParser
from droid_dash.core.cost import CostEstimator, format_cost

parser = SessionParser()
sessions = parser.parse_all_sessions()

estimator = CostEstimator()
total_cost = estimator.estimate_total_cost(sessions)
print(f"Total estimated cost: {format_cost(total_cost)}")
```

### Load Configuration

```python
from droid_dash.core.config import load_config, Config

# Load from default location
config = load_config()

# Load from specific path
from pathlib import Path
config = load_config(Path("/path/to/config.toml"))

print(f"Default tab: {config.display.default_tab}")
print(f"Dark mode: {config.display.dark_mode}")
```

### Custom Cost Estimation

```python
from droid_dash.core.cost import CostEstimator, ModelPricing

# Custom pricing for a model
custom_pricing = {
    "my-custom-model": ModelPricing(
        input_per_million=1.0,
        output_per_million=5.0,
        cache_write_per_million=0.5,
        cache_read_per_million=0.1,
    )
}

estimator = CostEstimator(custom_pricing=custom_pricing)
```
