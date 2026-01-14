"""Configuration management for Factory Dashboard."""

import os
import tomllib  # type: ignore
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ColumnConfig:
    """Configuration for which columns to show in sessions table."""

    show_title: bool = True
    show_date: bool = True
    show_project: bool = True
    show_model: bool = True
    show_tokens: bool = True
    show_favorites: bool = True
    show_prompts: bool = True
    show_duration: bool = True


@dataclass
class DisplayConfig:
    """Display and UI preferences."""

    default_tab: str = "sessions"
    default_sort: str = "tokens_desc"
    default_group: str = "project"
    hide_empty_sessions: bool = True
    dark_mode: bool = True
    heatmap_weeks: int = 20


@dataclass
class PricingConfig:
    """Pricing per million tokens."""

    input_per_million: float = 3.0
    output_per_million: float = 15.0
    cache_write_per_million: float = 3.75
    cache_read_per_million: float = 0.30


@dataclass
class PathsConfig:
    """Path configurations."""

    sessions_dir: str = "~/.factory/sessions"


@dataclass
class Config:
    """Main configuration container."""

    display: DisplayConfig = field(default_factory=DisplayConfig)
    columns: ColumnConfig = field(default_factory=ColumnConfig)
    default_pricing: PricingConfig = field(default_factory=PricingConfig)
    model_pricing: dict[str, PricingConfig] = field(default_factory=dict)
    paths: PathsConfig = field(default_factory=PathsConfig)

    def get_sessions_dir(self) -> str:
        """Get expanded sessions directory path."""
        return os.path.expanduser(self.paths.sessions_dir)


# Default config file locations (in priority order)
CONFIG_PATHS = [
    Path.home() / ".config" / "factory-dashboard" / "config.toml",
    Path.home() / ".factory-dashboard.toml",
]


def get_default_config_path() -> Path:
    """Get the default config file path (first in priority list)."""
    return CONFIG_PATHS[0]


def find_config_file() -> Path | None:
    """Find existing config file from priority list."""
    for path in CONFIG_PATHS:
        if path.exists():
            return path
    return None


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from file or return defaults.

    Args:
        config_path: Explicit path to config file. If None, searches default locations.

    Returns:
        Config object with loaded or default values.
    """
    if tomllib is None:
        return Config()

    path = config_path or find_config_file()
    if path is None or not path.exists():
        return Config()

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return _parse_config(data)
    except Exception:
        return Config()


def _parse_config(data: dict[str, Any]) -> Config:
    """Parse TOML data into Config object."""
    config = Config()

    # Parse display settings
    if "display" in data:
        d = data["display"]
        config.display = DisplayConfig(
            default_tab=d.get("default_tab", config.display.default_tab),
            default_sort=d.get("default_sort", config.display.default_sort),
            default_group=d.get("default_group", config.display.default_group),
            hide_empty_sessions=d.get(
                "hide_empty_sessions", config.display.hide_empty_sessions
            ),
            dark_mode=d.get("dark_mode", config.display.dark_mode),
            heatmap_weeks=d.get("heatmap_weeks", config.display.heatmap_weeks),
        )

    # Parse column settings
    if "columns" in data:
        c = data["columns"].get("sessions", {})
        config.columns = ColumnConfig(
            show_title=c.get("show_title", config.columns.show_title),
            show_date=c.get("show_date", config.columns.show_date),
            show_project=c.get("show_project", config.columns.show_project),
            show_model=c.get("show_model", config.columns.show_model),
            show_tokens=c.get("show_tokens", config.columns.show_tokens),
            show_favorites=c.get("show_favorites", config.columns.show_favorites),
            show_prompts=c.get("show_prompts", config.columns.show_prompts),
            show_duration=c.get("show_duration", config.columns.show_duration),
        )

    # Parse pricing settings
    if "pricing" in data:
        pricing = data["pricing"]
        if "default" in pricing:
            p = pricing["default"]
            config.default_pricing = PricingConfig(
                input_per_million=p.get(
                    "input_per_million", config.default_pricing.input_per_million
                ),
                output_per_million=p.get(
                    "output_per_million", config.default_pricing.output_per_million
                ),
                cache_write_per_million=p.get(
                    "cache_write_per_million",
                    config.default_pricing.cache_write_per_million,
                ),
                cache_read_per_million=p.get(
                    "cache_read_per_million",
                    config.default_pricing.cache_read_per_million,
                ),
            )
        if "models" in pricing:
            for model_name, p in pricing["models"].items():
                config.model_pricing[model_name] = PricingConfig(
                    input_per_million=p.get(
                        "input_per_million", config.default_pricing.input_per_million
                    ),
                    output_per_million=p.get(
                        "output_per_million", config.default_pricing.output_per_million
                    ),
                    cache_write_per_million=p.get(
                        "cache_write_per_million",
                        config.default_pricing.cache_write_per_million,
                    ),
                    cache_read_per_million=p.get(
                        "cache_read_per_million",
                        config.default_pricing.cache_read_per_million,
                    ),
                )

    # Parse paths
    if "paths" in data:
        config.paths = PathsConfig(
            sessions_dir=data["paths"].get("sessions_dir", config.paths.sessions_dir),
        )

    return config


def save_config(config: Config, config_path: Path | None = None) -> bool:
    """Save configuration to file.

    Args:
        config: Config object to save.
        config_path: Path to save to. If None, uses default location.

    Returns:
        True if saved successfully, False otherwise.
    """
    path = config_path or get_default_config_path()

    try:
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Build TOML content
        lines = []
        lines.append("[display]")
        lines.append(f'default_tab = "{config.display.default_tab}"')
        lines.append(f'default_sort = "{config.display.default_sort}"')
        lines.append(f'default_group = "{config.display.default_group}"')
        lines.append(
            f"hide_empty_sessions = {str(config.display.hide_empty_sessions).lower()}"
        )
        lines.append(f"dark_mode = {str(config.display.dark_mode).lower()}")
        lines.append(f"heatmap_weeks = {config.display.heatmap_weeks}")
        lines.append("")

        lines.append("[columns.sessions]")
        lines.append(f"show_title = {str(config.columns.show_title).lower()}")
        lines.append(f"show_date = {str(config.columns.show_date).lower()}")
        lines.append(f"show_project = {str(config.columns.show_project).lower()}")
        lines.append(f"show_model = {str(config.columns.show_model).lower()}")
        lines.append(f"show_tokens = {str(config.columns.show_tokens).lower()}")
        lines.append(f"show_favorites = {str(config.columns.show_favorites).lower()}")
        lines.append(f"show_prompts = {str(config.columns.show_prompts).lower()}")
        lines.append(f"show_duration = {str(config.columns.show_duration).lower()}")
        lines.append("")

        lines.append("[pricing.default]")
        lines.append(f"input_per_million = {config.default_pricing.input_per_million}")
        lines.append(
            f"output_per_million = {config.default_pricing.output_per_million}"
        )
        lines.append(
            f"cache_write_per_million = {config.default_pricing.cache_write_per_million}"
        )
        lines.append(
            f"cache_read_per_million = {config.default_pricing.cache_read_per_million}"
        )
        lines.append("")

        for model_name, pricing in config.model_pricing.items():
            lines.append(f'[pricing.models."{model_name}"]')
            lines.append(f"input_per_million = {pricing.input_per_million}")
            lines.append(f"output_per_million = {pricing.output_per_million}")
            lines.append(f"cache_write_per_million = {pricing.cache_write_per_million}")
            lines.append(f"cache_read_per_million = {pricing.cache_read_per_million}")
            lines.append("")

        lines.append("[paths]")
        lines.append(f'sessions_dir = "{config.paths.sessions_dir}"')
        lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))

        return True
    except Exception:
        return False


def get_config_path_display() -> str:
    """Get a display string showing where config is loaded from."""
    found = find_config_file()
    if found:
        return str(found)
    return f"{get_default_config_path()} (not created yet)"
