"""Tests for configuration management."""

import tempfile
from pathlib import Path

from factory_dashboard.core.config import (
    Config,
    DisplayConfig,
    PricingConfig,
    load_config,
    save_config,
)


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.display.default_tab == "sessions"
        assert config.display.default_sort == "tokens_desc"
        assert config.display.default_group == "project"
        assert config.display.hide_empty_sessions is True
        assert config.display.dark_mode is True
        assert config.display.heatmap_weeks == 20

    def test_column_config_defaults(self):
        """Test default column visibility."""
        config = Config()

        assert config.columns.show_title is True
        assert config.columns.show_date is True
        assert config.columns.show_project is True
        assert config.columns.show_model is True
        assert config.columns.show_tokens is True
        assert config.columns.show_favorites is True
        assert config.columns.show_prompts is True
        assert config.columns.show_duration is True

    def test_pricing_config_defaults(self):
        """Test default pricing values."""
        config = Config()

        assert config.default_pricing.input_per_million == 3.0
        assert config.default_pricing.output_per_million == 15.0
        assert config.default_pricing.cache_write_per_million == 3.75
        assert config.default_pricing.cache_read_per_million == 0.30

    def test_get_sessions_dir_expands_tilde(self):
        """Test that sessions_dir path expands ~."""
        config = Config()
        config.paths.sessions_dir = "~/.factory/sessions"

        expanded = config.get_sessions_dir()
        assert not expanded.startswith("~")
        assert "/.factory/sessions" in expanded


class TestConfigSaveLoad:
    """Tests for saving and loading configuration."""

    def test_save_and_load_config(self):
        """Test saving and loading configuration roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.toml"

            # Create custom config
            config = Config()
            config.display.default_tab = "overview"
            config.display.heatmap_weeks = 15
            config.columns.show_model = False
            config.default_pricing.input_per_million = 5.0

            # Save
            result = save_config(config, config_path)
            assert result is True
            assert config_path.exists()

            # Load
            loaded = load_config(config_path)
            assert loaded.display.default_tab == "overview"
            assert loaded.display.heatmap_weeks == 15
            assert loaded.columns.show_model is False
            assert loaded.default_pricing.input_per_million == 5.0

    def test_load_nonexistent_returns_defaults(self):
        """Test loading from nonexistent file returns defaults."""
        config = load_config(Path("/nonexistent/path/config.toml"))

        assert config.display.default_tab == "sessions"
        assert config.display.default_sort == "tokens_desc"

    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "subdir" / "nested" / "config.toml"

            config = Config()
            result = save_config(config, config_path)

            assert result is True
            assert config_path.exists()


class TestDisplayConfig:
    """Tests for DisplayConfig."""

    def test_valid_sort_values(self):
        """Test that sort values are properly set."""
        config = DisplayConfig(default_sort="date_asc")
        assert config.default_sort == "date_asc"

    def test_valid_group_values(self):
        """Test that group values are properly set."""
        config = DisplayConfig(default_group="model")
        assert config.default_group == "model"


class TestPricingConfig:
    """Tests for PricingConfig."""

    def test_custom_pricing(self):
        """Test custom pricing values."""
        pricing = PricingConfig(
            input_per_million=15.0,
            output_per_million=75.0,
            cache_write_per_million=18.75,
            cache_read_per_million=1.50,
        )

        assert pricing.input_per_million == 15.0
        assert pricing.output_per_million == 75.0
