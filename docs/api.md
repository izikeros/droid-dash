# API Reference

Factory Dashboard is primarily a CLI/TUI tool, but its core modules can be used programmatically.

## Core Modules

### Models

::: factory_dashboard.core.models
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

::: factory_dashboard.core.parser
    options:
      show_root_heading: true
      members:
        - SessionParser

### Cost Estimation

::: factory_dashboard.core.cost
    options:
      show_root_heading: true
      members:
        - CostEstimator
        - ModelPricing
        - format_cost

### Configuration

::: factory_dashboard.core.config
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
from factory_dashboard.core.parser import SessionParser

parser = SessionParser("~/.factory/sessions")
sessions = parser.parse_all_sessions()

for session in sessions:
    print(f"{session.title}: {session.tokens.total_tokens} tokens")
```

### Estimate Costs

```python
from factory_dashboard.core.parser import SessionParser
from factory_dashboard.core.cost import CostEstimator, format_cost

parser = SessionParser()
sessions = parser.parse_all_sessions()

estimator = CostEstimator()
total_cost = estimator.estimate_total_cost(sessions)
print(f"Total estimated cost: {format_cost(total_cost)}")
```

### Load Configuration

```python
from factory_dashboard.core.config import load_config, Config

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
from factory_dashboard.core.cost import CostEstimator, ModelPricing

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
