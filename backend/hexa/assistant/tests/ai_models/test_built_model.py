from decimal import Decimal
from unittest.mock import MagicMock

from django.test import SimpleTestCase
from genai_prices.types import ModelPrice
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.built_model import BuiltModel

_GLM = "zai-org/glm-5.2-maas"
_GLM_PRICE = ModelPrice(input_mtok=Decimal("0.6"), output_mtok=Decimal("2.2"))


def _built(
    api_name: str,
    provider_id: str = "google-vertex",
    price_override: ModelPrice | None = None,
) -> BuiltModel:
    return BuiltModel(
        model=MagicMock(),
        api_name=api_name,
        provider_id=provider_id,
        price_override=price_override,
    )


class CalculateCostTest(SimpleTestCase):
    def test_prices_usage_with_the_model_that_produced_it(self):
        built = _built("claude-opus-4-6", provider_id="anthropic")
        cost = built.calculate_cost(RunUsage(input_tokens=1000, output_tokens=1000))
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)

    def test_a_managed_gemini_is_priced_by_the_library(self):
        cost = _built("gemini-3.7-flash").calculate_cost(
            RunUsage(input_tokens=1000, output_tokens=1000)
        )
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)

    def test_returns_none_when_pricing_fails(self):
        """Dropping the usage is the whole answer: `AiModelBuilder.build` has
        already reported that this model has no price.
        """
        self.assertIsNone(_built("?", provider_id="?").calculate_cost(RunUsage()))


class BackendPriceTest(SimpleTestCase):
    """A backend may price a model itself, for the Vertex Model Garden models
    genai_prices does not know; that price arrives on the built model.
    """

    def test_a_model_garden_model_has_no_price_of_its_own(self):
        self.assertIsNone(_built(_GLM).calculate_cost(RunUsage(input_tokens=1000)))

    def test_the_backend_price_bills_per_million_tokens(self):
        cost = _built(_GLM, price_override=_GLM_PRICE).calculate_cost(
            RunUsage(input_tokens=1_000_000, output_tokens=500_000)
        )
        self.assertEqual(cost, Decimal("0.6") + Decimal("2.2") / 2)

    def test_the_backend_price_outranks_the_library(self):
        cost = _built(
            "claude-opus-4-6",
            price_override=ModelPrice(input_mtok=Decimal(1), output_mtok=Decimal(1)),
        ).calculate_cost(RunUsage(input_tokens=1_000_000, output_tokens=1_000_000))
        self.assertEqual(cost, Decimal(2))
