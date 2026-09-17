"""A model that is ready to run, and what its usage costs.

The output of `AiModelBuilder.build`: the pydantic-ai client an agent runs on,
carrying the two names genai_prices needs to put a price on what that run
consumed.
"""

import logging
from decimal import Decimal
from typing import NamedTuple

import genai_prices
from pydantic_ai import RunUsage
from pydantic_ai.models import Model as PydanticModel

logger = logging.getLogger(__name__)


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str

    def calculate_cost(self, usage: RunUsage) -> Decimal | None:
        """Price `usage`, or None if this model has no known price.

        Agents in one conversation may run on different models, so each prices
        its own usage. `AiModelBuilder.build` prices an empty usage to turn away
        models we cannot meter, so a None here means the price data changed under
        a model we already accepted, and that usage escapes the monthly budget.
        """
        try:
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
