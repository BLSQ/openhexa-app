from decimal import Decimal
from unittest.mock import MagicMock, patch

from asgiref.sync import async_to_sync
from django.test import SimpleTestCase
from pydantic_ai import ModelRetry
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import (
    BaseAgent,
    _trim_conversation_title,
    _validate_conversation_title,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message

from ._helpers import (
    _AgentWithFailingTool,
    _AgentWithFakeTool,
    _make_naming_model,
    _make_tool_call_model,
    make_built_model,
    run_agent,
)
from ._testcase import AgentTestCase


class BaseAgentRunTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_run_saves_user_message(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        run_agent(agent, "What can you do?")
        user_messages = self.conversation.messages.filter(role=Message.Role.USER)
        self.assertEqual(user_messages.count(), 1)
        self.assertEqual(
            user_messages.first().content,
            [{"type": "text", "content": "What can you do?"}],
        )

    def test_run_saves_assistant_message(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        run_agent(agent, "What can you do?")
        assistant_messages = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        )
        self.assertEqual(assistant_messages.count(), 1)
        self.assertEqual(
            assistant_messages.first().content, [{"type": "text", "content": "Hello!"}]
        )

    def test_run_updates_messages_history(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.messages_history, [])
        run_agent(agent, "Hello")
        self.conversation.refresh_from_db()
        self.assertGreater(len(self.conversation.messages_history), 0)

    def test_run_sets_conversation_name_on_first_message(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        self.assertIsNone(self.conversation.name)
        run_agent(agent, "Create a pipeline")
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.name)

    def test_run_does_not_overwrite_existing_conversation_name(self):
        self.conversation.name = "Existing Name"
        self.conversation.save(update_fields=["name"])
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        run_agent(agent, "Something else")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, "Existing Name")

    def test_run_updates_token_counts(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello"))
        )
        run_agent(agent, "Test")
        self.conversation.refresh_from_db()
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
        self.assertIsNotNone(assistant_msg.input_tokens)
        self.assertIsNotNone(assistant_msg.output_tokens)

    def test_second_run_appends_to_history(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Reply"))
        )
        run_agent(agent, "First message")
        history_after_first = len(self.conversation.messages_history)
        run_agent(agent, "Second message")
        self.conversation.refresh_from_db()
        self.assertGreater(len(self.conversation.messages_history), history_after_first)


class BaseAgentToolCallTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_tool_call_creates_tool_invocation_record(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        run_agent(agent, "Use the tool")
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
        self.assertEqual(assistant_msg.tool_invocations.count(), 1)
        invocation = assistant_msg.tool_invocations.first()
        self.assertEqual(invocation.tool_name, "_fake_tool")
        self.assertEqual(invocation.tool_call_id, "call-test-001")

    def test_successful_tool_call_sets_success_true(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        run_agent(agent, "Use the tool")
        self.assertTrue(self.first_tool_invocation(self.conversation).success)

    def test_tool_call_with_error_response_sets_success_false(self):
        model = _make_tool_call_model("_failing_tool", {"arg": "oops"})
        agent = _AgentWithFailingTool(self.conversation, make_built_model(model))
        run_agent(agent, "Use the failing tool")
        self.assertFalse(self.first_tool_invocation(self.conversation).success)

    def test_tool_input_is_persisted(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "my-value"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        run_agent(agent, "Use the tool")
        self.assertEqual(
            self.first_tool_invocation(self.conversation).tool_input,
            {"arg": "my-value"},
        )

    def test_tool_output_is_persisted(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "my-value"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        run_agent(agent, "Use the tool")
        self.assertEqual(
            self.first_tool_invocation(self.conversation).tool_output,
            {"result": "my-value"},
        )


class ConversationTitleValidationTest(SimpleTestCase):
    def test_accepts_six_word_french_title(self):
        title = "Tableau de bord lecture dynamique CSV"
        self.assertEqual(_validate_conversation_title(title), title)

    def test_rejects_title_over_word_budget(self):
        with self.assertRaises(ModelRetry) as ctx:
            _validate_conversation_title("one two three four five six seven eight nine")
        self.assertIn("9 words", str(ctx.exception))

    def test_rejects_title_over_char_budget(self):
        with self.assertRaises(ModelRetry) as ctx:
            _validate_conversation_title("a" * 51)
        self.assertIn("51 characters", str(ctx.exception))

    def test_rejects_empty_title(self):
        with self.assertRaises(ModelRetry) as ctx:
            _validate_conversation_title("   ")
        self.assertIn("empty", str(ctx.exception))

    def test_trim_cuts_to_word_budget(self):
        self.assertEqual(
            _trim_conversation_title("one two three four five six seven eight nine"),
            "one two three four five six seven eight",
        )

    def test_trim_cuts_to_char_budget_on_word_boundary(self):
        self.assertEqual(
            _trim_conversation_title(
                "aaaaaaaaaa bbbbbbbbbb cccccccccc dddddddddd eeeeeeeeee"
            ),
            "aaaaaaaaaa bbbbbbbbbb cccccccccc dddddddddd",
        )


class ConversationNamingTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_six_word_title_is_accepted_without_retry(self):
        title = "Tableau de bord lecture dynamique CSV"
        agent = BaseAgent(
            self.conversation, make_built_model(_make_naming_model(title))
        )
        run_agent(agent, "Améliore ce tableau de bord")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, title)

    def test_over_budget_title_retries_and_uses_second_attempt(self):
        agent = BaseAgent(
            self.conversation,
            make_built_model(
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
            make_built_model(
                _make_naming_model("one two three four five six seven eight nine ten")
            ),
        )
        run_agent(agent, "Améliore ce tableau de bord pour que les données soient lues")
        self.conversation.refresh_from_db()
        self.assertEqual(
            self.conversation.name, "one two three four five six seven eight"
        )

    def test_naming_usage_is_priced_with_the_utility_model(self):
        naming_model = _make_naming_model("Tableau de bord alertes")
        agent = BaseAgent(
            self.conversation,
            make_built_model(naming_model, api_name="main-model"),
            make_built_model(naming_model, api_name="utility-model"),
        )
        with patch("hexa.assistant.agents.base.genai_prices.calc_price") as calc_price:
            calc_price.return_value = MagicMock(total_price=Decimal("0"))
            run_agent(agent, "Améliore ce tableau de bord")
        priced_models = [call.args[1] for call in calc_price.call_args_list]
        self.assertIn("utility-model", priced_models)
        self.assertIn("main-model", priced_models)

    def test_retry_exhaustion_still_reports_usage(self):
        agent = BaseAgent(
            self.conversation,
            make_built_model(
                _make_naming_model("one two three four five six seven eight nine ten")
            ),
        )
        _, usage = async_to_sync(agent._generate_conversation_name)("Améliore ce bord")
        self.assertEqual(usage.requests, 2)
        self.assertGreater(usage.input_tokens, 0)
        self.assertGreater(usage.output_tokens, 0)

    def test_empty_title_retries_and_uses_second_attempt(self):
        agent = BaseAgent(
            self.conversation,
            make_built_model(_make_naming_model("", "Tableau de bord alertes")),
        )
        run_agent(agent, "Améliore ce tableau de bord")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, "Tableau de bord alertes")

    def test_empty_titles_fall_back_to_user_input_never_empty_name(self):
        agent = BaseAgent(
            self.conversation, make_built_model(_make_naming_model("   "))
        )
        run_agent(agent, "Améliore ce tableau de bord pour que les données soient lues")
        self.conversation.refresh_from_db()
        self.assertEqual(
            self.conversation.name, "Améliore ce tableau de bord pour que les"
        )
