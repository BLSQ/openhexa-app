from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message

from ._helpers import _AgentWithFailingTool, _AgentWithFakeTool, _make_tool_call_model, _patch_builder
from ._testcase import AgentTestCase


class BaseAgentRunTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    def test_run_saves_user_message(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        agent.run("What can you do?")
        user_messages = self.conversation.messages.filter(role=Message.Role.USER)
        self.assertEqual(user_messages.count(), 1)
        self.assertEqual(user_messages.first().content, "What can you do?")

    def test_run_saves_assistant_message(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        agent.run("What can you do?")
        assistant_messages = self.conversation.messages.filter(role=Message.Role.ASSISTANT)
        self.assertEqual(assistant_messages.count(), 1)
        self.assertEqual(assistant_messages.first().content, "Hello!")

    def test_run_updates_messages_history(self):
        with _patch_builder(TestModel(custom_output_text="Hi")):
            agent = BaseAgent(self.conversation)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.messages_history, [])
        agent.run("Hello")
        self.conversation.refresh_from_db()
        self.assertGreater(len(self.conversation.messages_history), 0)

    def test_run_sets_conversation_name_on_first_message(self):
        with _patch_builder(TestModel(custom_output_text="Hi")):
            agent = BaseAgent(self.conversation)
        self.assertIsNone(self.conversation.name)
        agent.run("Create a pipeline")
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.name)

    def test_run_does_not_overwrite_existing_conversation_name(self):
        self.conversation.name = "Existing Name"
        self.conversation.save(update_fields=["name"])
        with _patch_builder(TestModel(custom_output_text="Hi")):
            agent = BaseAgent(self.conversation)
        agent.run("Something else")
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.name, "Existing Name")

    def test_run_updates_token_counts(self):
        with _patch_builder(TestModel(custom_output_text="Hello")):
            agent = BaseAgent(self.conversation)
        agent.run("Test")
        self.conversation.refresh_from_db()
        assistant_msg = self.conversation.messages.filter(role=Message.Role.ASSISTANT).first()
        self.assertIsNotNone(assistant_msg.input_tokens)
        self.assertIsNotNone(assistant_msg.output_tokens)

    def test_second_run_appends_to_history(self):
        with _patch_builder(TestModel(custom_output_text="Reply")):
            agent = BaseAgent(self.conversation)
        agent.run("First message")
        history_after_first = len(self.conversation.messages_history)
        agent.run("Second message")
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
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        agent.run("Use the tool")
        assistant_msg = self.conversation.messages.filter(role=Message.Role.ASSISTANT).first()
        self.assertEqual(assistant_msg.tool_invocations.count(), 1)
        invocation = assistant_msg.tool_invocations.first()
        self.assertEqual(invocation.tool_name, "_fake_tool")
        self.assertEqual(invocation.tool_call_id, "call-test-001")

    def test_successful_tool_call_sets_success_true(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        agent.run("Use the tool")
        invocation = (
            self.conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertTrue(invocation.success)

    def test_tool_call_with_error_response_sets_success_false(self):
        model = _make_tool_call_model("_failing_tool", {"arg": "oops"})
        with _patch_builder(model):
            agent = _AgentWithFailingTool(self.conversation)
        agent.run("Use the failing tool")
        invocation = (
            self.conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertFalse(invocation.success)

    def test_tool_input_is_persisted(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "my-value"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        agent.run("Use the tool")
        invocation = (
            self.conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertEqual(invocation.tool_input, {"arg": "my-value"})

    def test_tool_output_is_persisted(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "my-value"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        agent.run("Use the tool")
        invocation = (
            self.conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertEqual(invocation.tool_output, {"result": "my-value"})
