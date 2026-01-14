"""Token cost estimation for various Claude models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import Config

from .models import Session, TokenUsage


@dataclass
class ModelPricing:
    """Pricing per million tokens for a model."""

    input_per_million: float
    output_per_million: float
    cache_write_per_million: float
    cache_read_per_million: float

    def calculate_cost(self, tokens: TokenUsage) -> float:
        """Calculate cost in USD for given token usage."""
        input_cost = (tokens.input_tokens / 1_000_000) * self.input_per_million
        output_cost = (tokens.output_tokens / 1_000_000) * self.output_per_million
        cache_write_cost = (
            tokens.cache_creation_tokens / 1_000_000
        ) * self.cache_write_per_million
        cache_read_cost = (
            tokens.cache_read_tokens / 1_000_000
        ) * self.cache_read_per_million
        return input_cost + output_cost + cache_write_cost + cache_read_cost


MODEL_PRICING: dict[str, ModelPricing] = {
    "claude-opus-4-5-20251101": ModelPricing(
        input_per_million=15.0,
        output_per_million=75.0,
        cache_write_per_million=18.75,
        cache_read_per_million=1.50,
    ),
    "claude-sonnet-4-20250514": ModelPricing(
        input_per_million=3.0,
        output_per_million=15.0,
        cache_write_per_million=3.75,
        cache_read_per_million=0.30,
    ),
    "claude-3-5-sonnet-20241022": ModelPricing(
        input_per_million=3.0,
        output_per_million=15.0,
        cache_write_per_million=3.75,
        cache_read_per_million=0.30,
    ),
    "claude-3-opus-20240229": ModelPricing(
        input_per_million=15.0,
        output_per_million=75.0,
        cache_write_per_million=18.75,
        cache_read_per_million=1.50,
    ),
    "claude-3-haiku-20240307": ModelPricing(
        input_per_million=0.25,
        output_per_million=1.25,
        cache_write_per_million=0.30,
        cache_read_per_million=0.03,
    ),
}

DEFAULT_PRICING = ModelPricing(
    input_per_million=3.0,
    output_per_million=15.0,
    cache_write_per_million=3.75,
    cache_read_per_million=0.30,
)


class CostEstimator:
    """Estimates costs for sessions based on model and token usage."""

    def __init__(
        self,
        custom_pricing: dict[str, ModelPricing] | None = None,
        default_pricing: ModelPricing | None = None,
    ):
        self.pricing = {**MODEL_PRICING}
        if custom_pricing:
            self.pricing.update(custom_pricing)
        self._default_pricing = default_pricing or DEFAULT_PRICING

    @classmethod
    def from_config(cls, config: Config) -> CostEstimator:
        """Create CostEstimator from Config object."""

        # Convert config pricing to ModelPricing
        default = ModelPricing(
            input_per_million=config.default_pricing.input_per_million,
            output_per_million=config.default_pricing.output_per_million,
            cache_write_per_million=config.default_pricing.cache_write_per_million,
            cache_read_per_million=config.default_pricing.cache_read_per_million,
        )

        custom = {}
        for model_name, p in config.model_pricing.items():
            custom[model_name] = ModelPricing(
                input_per_million=p.input_per_million,
                output_per_million=p.output_per_million,
                cache_write_per_million=p.cache_write_per_million,
                cache_read_per_million=p.cache_read_per_million,
            )

        return cls(custom_pricing=custom, default_pricing=default)

    def get_pricing(self, model: str) -> ModelPricing:
        """Get pricing for a model, with fallback to default."""
        return self.pricing.get(model, self._default_pricing)

    def estimate_session_cost(self, session: Session) -> float:
        """Estimate cost for a single session."""
        pricing = self.get_pricing(session.model)
        return pricing.calculate_cost(session.tokens)

    def estimate_total_cost(self, sessions: list[Session]) -> float:
        """Estimate total cost for multiple sessions."""
        return sum(self.estimate_session_cost(s) for s in sessions)

    def estimate_cost_by_model(self, sessions: list[Session]) -> dict[str, float]:
        """Estimate costs grouped by model."""
        by_model: dict[str, float] = {}
        for session in sessions:
            model = session.model
            cost = self.estimate_session_cost(session)
            by_model[model] = by_model.get(model, 0.0) + cost
        return by_model


def format_cost(cost: float) -> str:
    """Format cost as USD string."""
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.0:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"
