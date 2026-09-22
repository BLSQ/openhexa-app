from decimal import Decimal
from unittest.mock import MagicMock

from django.test import SimpleTestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.built_model import BuiltModel

_CONFIG_LOGGER = "hexa.assistant.ai_models.config"
_GLM = "zai-org/glm-5.2-maas"
_GLM_PRICE = '"%s": {"input_mtok": 0.6, "output_mtok": 2.2}' % _GLM


def _built(api_name: str, provider_id: str = "google-vertex") -> BuiltModel:
    return BuiltModel(model=MagicMock(), api_name=api_name, provider_id=provider_id)


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


class ConfiguredPriceTest(SimpleTestCase):
    """Vertex Model Garden models are unknown to genai_prices, so their price
    comes from the environment, and arrives with the model id that reaches for them.
    """

    def test_a_model_garden_model_has_no_price_of_its_own(self):
        self.assertIsNone(_built(_GLM).calculate_cost(RunUsage(input_tokens=1000)))

    @override_settings(ASSISTANT_MODEL_PRICES="{%s}" % _GLM_PRICE)
    def test_the_configured_price_bills_per_million_tokens(self):
        cost = _built(_GLM).calculate_cost(
            RunUsage(input_tokens=1_000_000, output_tokens=500_000)
        )
        self.assertEqual(cost, Decimal("0.6") + Decimal("2.2") / 2)

    @override_settings(
        ASSISTANT_MODEL_PRICES='{"claude-opus-4-6": {"input_mtok": 1, "output_mtok": 1}}'
    )
    def test_the_configured_price_outranks_the_library(self):
        cost = _built("claude-opus-4-6").calculate_cost(
            RunUsage(input_tokens=1_000_000, output_tokens=1_000_000)
        )
        self.assertEqual(cost, Decimal(2))

    @override_settings(ASSISTANT_MODEL_PRICES="{%s}" % _GLM_PRICE.replace("glm", "GLM"))
    def test_model_names_match_regardless_of_case(self):
        cost = _built(_GLM).calculate_cost(RunUsage(input_tokens=1_000_000))
        self.assertEqual(cost, Decimal("0.6"))

    @override_settings(
        ASSISTANT_MODEL_PRICES='{"typo": {"input_mtok": "cheap"}, '
        '"scalar": 0.5, "extra": {"per_call": 1}, %s}' % _GLM_PRICE
    )
    def test_a_broken_entry_is_reported_and_leaves_the_others_alone(self):
        with self.assertLogs(_CONFIG_LOGGER, level="ERROR") as logs:
            cost = _built(_GLM).calculate_cost(RunUsage(input_tokens=1_000_000))
        self.assertEqual(cost, Decimal("0.6"))
        self.assertEqual(len(logs.output), 3)
        self.assertIn("'extra'", logs.output[2])
        self.assertIn("per_call", logs.output[2])
