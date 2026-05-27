from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message

from ._helpers import (
    _AgentWithFailingTool,
    _AgentWithFakeTool,
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
