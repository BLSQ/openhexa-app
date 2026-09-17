from unittest.mock import MagicMock

from django.test import SimpleTestCase
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.built_model import BuiltModel

_LOGGER = "hexa.assistant.ai_models.built_model"


class CalculateCostTest(SimpleTestCase):
    def test_prices_usage_with_the_model_that_produced_it(self):
        built = BuiltModel(
            model=MagicMock(), api_name="claude-opus-4-6", provider_id="anthropic"
        )
        cost = built.calculate_cost(RunUsage(input_tokens=1000, output_tokens=1000))
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)

    def test_returns_none_when_pricing_fails(self):
        """`AiModelBuilder.build` turns these away, so reaching this means the
        price data changed under a model we already accepted: log it rather than
        pass over usage that escapes the organization's budget.
        """
        built = BuiltModel(model=MagicMock(), api_name="?", provider_id="?")
        with self.assertLogs(_LOGGER, level="ERROR"):
            self.assertIsNone(built.calculate_cost(RunUsage()))
