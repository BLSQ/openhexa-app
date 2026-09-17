from unittest.mock import MagicMock

from django.test import SimpleTestCase
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.built_model import BuiltModel


class CalculateCostTest(SimpleTestCase):
    def test_prices_usage_with_the_model_that_produced_it(self):
        built = BuiltModel(
            model=MagicMock(), api_name="claude-opus-4-6", provider_id="anthropic"
        )
        cost = built.calculate_cost(RunUsage(input_tokens=1000, output_tokens=1000))
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)

    def test_returns_none_when_pricing_fails(self):
        """Dropping the usage is the whole answer: `AiModelBuilder.build` has
        already reported that this model has no price.
        """
        built = BuiltModel(model=MagicMock(), api_name="?", provider_id="?")
        self.assertIsNone(built.calculate_cost(RunUsage()))
