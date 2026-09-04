from decimal import Decimal
from unittest.mock import MagicMock, patch

from asgiref.sync import async_to_sync
from django.test import SimpleTestCase, override_settings
from pydantic_ai import ModelRetry

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.agents.naming_agent import (
    NamingAgent,
    trim_title,
    validate_title,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings

from ._helpers import FakeModelBuilder, _make_naming_model, run_agent
from ._testcase import AgentTestCase


class TitleValidationTest(SimpleTestCase):
    def test_accepts_six_word_french_title(self):
        title = "Tableau de bord lecture dynamique CSV"
        self.assertEqual(validate_title(title), title)

    def test_rejects_title_over_word_budget(self):
        with self.assertRaises(ModelRetry) as ctx:
            validate_title("one two three four five six seven eight nine")
        self.assertIn("9 words", str(ctx.exception))

    def test_rejects_title_over_char_budget(self):
        with self.assertRaises(ModelRetry) as ctx:
            validate_title("a" * 51)
        self.assertIn("51 characters", str(ctx.exception))

    def test_rejects_empty_title(self):
        with self.assertRaises(ModelRetry) as ctx:
            validate_title("   ")
        self.assertIn("empty", str(ctx.exception))

    def test_trim_cuts_to_word_budget(self):
        self.assertEqual(
            trim_title("one two three four five six seven eight nine"),
            "one two three four five six seven eight",
        )

    def test_trim_cuts_to_char_budget_on_word_boundary(self):
        self.assertEqual(
            trim_title("aaaaaaaaaa bbbbbbbbbb cccccccccc dddddddddd eeeeeeeeee"),
            "aaaaaaaaaa bbbbbbbbbb cccccccccc dddddddddd",
        )


class NamingAgentModelTest(SimpleTestCase):
    def test_runs_on_haiku_rather_than_the_organization_model(self):
        builder = FakeModelBuilder(_make_naming_model("Title"))
        self.assertEqual(builder.ai_settings.effective_model, AiSettings.Model.OPUS)
        self.assertEqual(
            NamingAgent(builder).built_model.api_name, AiSettings.Model.HAIKU
        )

    @override_settings(ASSISTANT_AGENT_MODELS='{"naming": "sonnet"}')
    def test_environment_override_wins_over_the_default(self):
        builder = FakeModelBuilder(_make_naming_model("Title"))
        self.assertEqual(
            NamingAgent(builder).built_model.api_name, AiSettings.Model.SONNET
        )


class NamingAgentRunTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_six_word_title_is_accepted_without_retry(self):
        title = "Tableau de bord lecture dynamique CSV"
        agent = BaseAgent(
            self.conversation, FakeModelBuilder(_make_naming_model(title))
        )
        run_agent(agent, "Améliore ce tableau de bord")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, title)

    def test_over_budget_title_retries_and_uses_second_attempt(self):
        agent = BaseAgent(
            self.conversation,
            FakeModelBuilder(
                _make_naming_model(
                    "one two three four five six seven eight nine ten",
                    "Tableau de bord alertes zones santé",
                )
            ),
        )
        run_agent(agent, "Améliore ce tableau de bord")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, "Tableau de bord alertes zones santé")

    def test_retry_exhaustion_falls_back_to_model_title_not_user_input(self):
        agent = BaseAgent(
            self.conversation,
            FakeModelBuilder(
                _make_naming_model("one two three four five six seven eight nine ten")
            ),
        )
        run_agent(agent, "Améliore ce tableau de bord pour que les données soient lues")
        self.conversation.refresh_from_db()
        self.assertEqual(
            self.conversation.name, "one two three four five six seven eight"
        )

    def test_empty_title_retries_and_uses_second_attempt(self):
        agent = BaseAgent(
            self.conversation,
            FakeModelBuilder(_make_naming_model("", "Tableau de bord alertes")),
        )
        run_agent(agent, "Améliore ce tableau de bord")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, "Tableau de bord alertes")

    def test_empty_titles_fall_back_to_user_input_never_empty_name(self):
        agent = BaseAgent(
            self.conversation, FakeModelBuilder(_make_naming_model("   "))
        )
        run_agent(agent, "Améliore ce tableau de bord pour que les données soient lues")
        self.conversation.refresh_from_db()
        self.assertEqual(
            self.conversation.name, "Améliore ce tableau de bord pour que les"
        )

    def test_retry_exhaustion_still_reports_usage(self):
        naming_agent = NamingAgent(
            FakeModelBuilder(
                _make_naming_model("one two three four five six seven eight nine ten")
            )
        )
        result = async_to_sync(naming_agent.run)("Améliore ce bord")
        self.assertEqual(result.usage.requests, 2)
        self.assertGreater(result.usage.input_tokens, 0)
        self.assertGreater(result.usage.output_tokens, 0)

    def test_naming_usage_is_priced_apart_from_the_main_model(self):
        agent = BaseAgent(
            self.conversation,
            FakeModelBuilder(_make_naming_model("Tableau de bord alertes")),
        )
        with patch(
            "hexa.assistant.model_builder.genai_prices.calc_price"
        ) as calc_price:
            calc_price.return_value = MagicMock(total_price=Decimal("0"))
            run_agent(agent, "Améliore ce tableau de bord")
        priced_models = [call.args[1] for call in calc_price.call_args_list]
        self.assertIn(AiSettings.Model.HAIKU, priced_models)
        self.assertIn(AiSettings.Model.OPUS, priced_models)
