from unittest.mock import MagicMock, patch

from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent, _is_success
from hexa.assistant.agents.pipeline_agent import PipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def _fake_tool(arg: str) -> dict:
    """A fake tool for testing."""
    return {"result": arg}


def _failing_tool(arg: str) -> dict:
    """A fake tool that returns an error response."""
    return {"errors": ["Something went wrong"]}


class _AgentWithFakeTool(BaseAgent):
    tool_names = [_fake_tool]


class _AgentWithFailingTool(BaseAgent):
    tool_names = [_failing_tool]


def _make_tool_call_model(tool_name: str, tool_args: dict) -> FunctionModel:
    """Returns a FunctionModel that calls the given tool once, then returns text."""
    calls = []

    def func(messages: list, agent_info: AgentInfo) -> ModelResponse:
        calls.append(1)
        if len(calls) == 1:
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name=tool_name,
                        args=tool_args,
                        tool_call_id="call-test-001",
                    )
                ]
            )
        return ModelResponse(parts=[TextPart(content="Done.")])

    return FunctionModel(func)


def _patch_builder(test_model):
    mock_builder = MagicMock()
    mock_builder.model_api_name = "test"
    mock_builder.provider_id = "test"
    mock_builder.build.return_value = test_model
    return patch(
        "hexa.assistant.agents.base.AiModelBuilder.from_conversation",
        return_value=mock_builder,
    )


class IsSuccessTest(TestCase):
    def test_plain_dict_without_errors_is_success(self):
        self.assertTrue(_is_success({"data": {"pipeline": {"id": "1"}}}))

    def test_dict_with_errors_key_is_failure(self):
        self.assertFalse(_is_success({"errors": ["Something failed"]}))

    def test_dict_with_nested_errors_is_failure(self):
        self.assertFalse(_is_success({"createPipeline": {"errors": ["Invalid name"]}}))

    def test_non_json_string_is_failure(self):
        self.assertFalse(_is_success("this is not json"))

    def test_json_encoded_dict_without_errors_is_success(self):
        self.assertTrue(_is_success('{"pipeline": {"id": "abc"}}'))

    def test_json_encoded_dict_with_errors_is_failure(self):
        self.assertFalse(_is_success('{"errors": ["oops"]}'))

    def test_non_dict_content_is_success(self):
        self.assertTrue(_is_success(["a", "b"]))
        self.assertTrue(_is_success(42))


class AgentRegistryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "registry-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Registry Test WS", description="For registry tests"
            )

    def test_pipeline_instruction_set_returns_pipeline_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.PIPELINE,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, PipelineAgent)

    def test_general_instruction_set_returns_base_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, BaseAgent)
            self.assertNotIsInstance(conversation.agent, PipelineAgent)

    def test_unregistered_instruction_set_defaults_to_base_agent(self):
        # WEBAPPS is a valid InstructionSet value but has no dedicated agent class.
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.WEBAPPS,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, BaseAgent)


class BaseAgentRunTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "agent-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Agent Test WS", description="For agent tests"
            )

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
        response = agent.run("What can you do?")
        self.assertEqual(response, "Hello!")
        assistant_messages = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        )
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
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
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


class BaseAgentToolCallTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "tool-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Tool Test WS", description="For tool call tests"
            )

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
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
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
