"""Tests for cost estimation."""

import pytest

from droid_dash.core.config import Config, PricingConfig
from droid_dash.core.cost import (
    DEFAULT_PRICING,
    MODEL_PRICING,
    CostEstimator,
    ModelPricing,
    format_cost,
)
from droid_dash.core.models import TokenUsage


class TestModelPricing:
    """Tests for ModelPricing."""

    def test_calculate_cost(self):
        """Test cost calculation for token usage."""
        pricing = ModelPricing(
            input_per_million=3.0,
            output_per_million=15.0,
            cache_write_per_million=3.75,
            cache_read_per_million=0.30,
        )

        tokens = TokenUsage(
            input_tokens=1_000_000,  # $3.00
            output_tokens=1_000_000,  # $15.00
            cache_creation_tokens=1_000_000,  # $3.75
            cache_read_tokens=1_000_000,  # $0.30
            thinking_tokens=0,
        )

        cost = pricing.calculate_cost(tokens)
        assert cost == pytest.approx(22.05, rel=0.01)

    def test_calculate_cost_small_usage(self):
        """Test cost calculation for small token usage."""
        pricing = ModelPricing(
            input_per_million=3.0,
            output_per_million=15.0,
            cache_write_per_million=3.75,
            cache_read_per_million=0.30,
        )

        tokens = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=0,
            cache_read_tokens=0,
            thinking_tokens=0,
        )

        # (1000/1M * 3) + (500/1M * 15) = 0.003 + 0.0075 = 0.0105
        cost = pricing.calculate_cost(tokens)
        assert cost == pytest.approx(0.0105, rel=0.01)


class TestCostEstimator:
    """Tests for CostEstimator."""

    def test_get_pricing_known_model(self):
        """Test getting pricing for known model."""
        estimator = CostEstimator()
        pricing = estimator.get_pricing("claude-sonnet-4-20250514")

        assert pricing.input_per_million == 3.0
        assert pricing.output_per_million == 15.0

    def test_get_pricing_unknown_model_returns_default(self):
        """Test getting pricing for unknown model returns default."""
        estimator = CostEstimator()
        pricing = estimator.get_pricing("unknown-model-xyz")

        assert pricing == DEFAULT_PRICING

    def test_custom_pricing_override(self):
        """Test custom pricing override."""
        custom = {
            "my-custom-model": ModelPricing(
                input_per_million=1.0,
                output_per_million=2.0,
                cache_write_per_million=0.5,
                cache_read_per_million=0.1,
            )
        }
        estimator = CostEstimator(custom_pricing=custom)

        pricing = estimator.get_pricing("my-custom-model")
        assert pricing.input_per_million == 1.0

    def test_from_config(self):
        """Test creating estimator from Config object."""
        config = Config()
        config.default_pricing = PricingConfig(
            input_per_million=5.0,
            output_per_million=25.0,
            cache_write_per_million=6.0,
            cache_read_per_million=0.5,
        )

        estimator = CostEstimator.from_config(config)

        # Unknown model should use config's default pricing
        pricing = estimator.get_pricing("unknown-model")
        assert pricing.input_per_million == 5.0
        assert pricing.output_per_million == 25.0


class TestFormatCost:
    """Tests for format_cost function."""

    def test_format_cost_large(self):
        """Test formatting large cost."""
        assert format_cost(1234.56) == "$1234.56"

    def test_format_cost_small(self):
        """Test formatting small cost."""
        assert format_cost(0.123) == "$0.123"

    def test_format_cost_tiny(self):
        """Test formatting tiny cost."""
        assert format_cost(0.001234) == "$0.0012"

    def test_format_cost_zero(self):
        """Test formatting zero cost."""
        assert format_cost(0) == "$0.0000"


class TestBuiltInPricing:
    """Tests for built-in model pricing."""

    def test_opus_pricing_exists(self):
        """Test Opus pricing is defined."""
        assert "claude-opus-4-5-20251101" in MODEL_PRICING
        pricing = MODEL_PRICING["claude-opus-4-5-20251101"]
        assert pricing.input_per_million == 15.0
        assert pricing.output_per_million == 75.0

    def test_sonnet_pricing_exists(self):
        """Test Sonnet pricing is defined."""
        assert "claude-sonnet-4-20250514" in MODEL_PRICING
        pricing = MODEL_PRICING["claude-sonnet-4-20250514"]
        assert pricing.input_per_million == 3.0
        assert pricing.output_per_million == 15.0

    def test_haiku_pricing_exists(self):
        """Test Haiku pricing is defined."""
        assert "claude-3-haiku-20240307" in MODEL_PRICING
        pricing = MODEL_PRICING["claude-3-haiku-20240307"]
        assert pricing.input_per_million == 0.25
        assert pricing.output_per_million == 1.25
