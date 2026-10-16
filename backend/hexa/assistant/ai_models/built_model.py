"""A model that is ready to run, and what its usage costs.

The output of `AiModelBuilder.build`: the pydantic-ai client an agent runs on.
Carries the logic of calculation the cost of its usage.
"""

import logging
from decimal import Decimal
from typing import NamedTuple

import genai_prices
from genai_prices.types import ModelPrice
from pydantic_ai import RunUsage
from pydantic_ai.models import Model as PydanticModel

logger = logging.getLogger(__name__)


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str
    price_override: ModelPrice | None = None

    def calculate_cost(self, usage: RunUsage) -> Decimal | None:
        """Price `usage`, or None if this model has no known price.

        Agents in one conversation may run on different models, so each prices
        its own usage. A model's price can be overridden by a backend ENV setting.
        """
        return price_usage(usage, self.api_name, self.provider_id, self.price_override)


def price_usage(
    usage: RunUsage,
    api_name: str,
    provider_id: str,
    price_override: ModelPrice | None = None,
) -> Decimal | None:
    """Price `usage` of model `api_name` at `provider_id`, or None if its price
    is unknown. `price_override` outranks genai_prices.

    Shared by the app's agents (through `BuiltModel`) and the usage reported by
    the notebook servers, so that a token costs the same wherever it was spent.
    """
    try:
        if price_override is not None:
            return price_override.calc_price(usage)["total_price"]

        return genai_prices.calc_price(
            usage, api_name, provider_id=provider_id
        ).total_price
    except Exception:
        logger.error(
            "cost calculation failed for model=%s provider=%s; "
            "its usage will not count towards any spend limit",
            api_name,
            provider_id,
        )
        return None
