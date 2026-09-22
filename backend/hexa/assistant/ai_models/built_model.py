"""A model that is ready to run, and what its usage costs.

The output of `AiModelBuilder.build`: the pydantic-ai client an agent runs on.
Carries the logic of calculation the cost of its usage.
"""

import logging
from decimal import Decimal
from typing import NamedTuple

import genai_prices
from pydantic_ai import RunUsage
from pydantic_ai.models import Model as PydanticModel

from hexa.assistant.ai_models.config import model_prices

logger = logging.getLogger(__name__)


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str

    def calculate_cost(self, usage: RunUsage) -> Decimal | None:
        """Price `usage`, or None if this model has no known price.

        Agents in one conversation may run on different models, so each prices
        its own usage. A price configured in the environment outranks the one
        genai_prices knows, if any. Unpriced usage is caught by Sentry so we
        know we need to add a new pricing ASAP.
        """
        try:
            price = model_prices().get(self.api_name.lower())
            if price is not None:
                return price.calc_price(usage)["total_price"]

            return genai_prices.calc_price(
                usage, self.api_name, provider_id=self.provider_id
            ).total_price
        except Exception:
            logger.error(
                "cost calculation failed for model=%s provider=%s; "
                "its usage will not count towards any spend limit",
                self.api_name,
                self.provider_id,
            )
            return None
