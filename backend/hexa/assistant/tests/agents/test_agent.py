import json
from unittest.mock import MagicMock, patch

from asgiref.sync import async_to_sync

from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent, _is_success
from hexa.assistant.agents.create_pipeline_agent import CreatePipelineAgent
from hexa.assistant.agents.edit_pipeline_agent import EditPipelineAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.core.test import TestCase
from hexa.pipelines.models import Pipeline
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def _fake_tool(arg: str) -> dict:
    """A fake tool for testing."""
    return {"result": arg}


def _failing_tool(arg: str) -> dict:
    """A fake tool that returns an error response."""
    return {"errors": ["Something went wrong"]}


class _AgentWithFakeTool(BaseAgent):
    tools = [_fake_tool]


class _AgentWithFailingTool(BaseAgent):
    tools = [_failing_tool]


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

    stream_calls = []

    async def stream_func(messages, agent_info):
        stream_calls.append(1)
        if len(stream_calls) == 1:
            yield {0: DeltaToolCall(name=tool_name, json_args=json.dumps(tool_args), tool_call_id="call-test-001")}
        else:
            yield "Done."

    return FunctionModel(func, stream_function=stream_func)


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
            instruction_set=InstructionSet.CREATE_PIPELINE,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, CreatePipelineAgent)

    def test_general_instruction_set_returns_base_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, BaseAgent)
            self.assertNotIsInstance(conversation.agent, CreatePipelineAgent)

    def test_unregistered_instruction_set_defaults_to_base_agent(self):
        # CREATE_WEBAPPS is a valid InstructionSet value but has no dedicated agent class.
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.CREATE_WEBAPPS,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, BaseAgent)

    def test_edit_pipeline_instruction_set_returns_edit_pipeline_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        with _patch_builder(TestModel()):
            self.assertIsInstance(conversation.agent, EditPipelineAgent)


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
        agent.run("What can you do?")
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
        cls.pipeline = Pipeline.objects.create(
            code="tool-pipeline", name="Tool Pipeline", workspace=cls.workspace
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

    def test_propose_pipeline_version_call_is_persisted(self):
        files_arg = [{"name": "pipeline.py", "content": "print('v2')"}]
        model = _make_tool_call_model(
            "propose_pipeline_version", {"modified_files": files_arg}
        )
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )
        conversation.linked_object = self.pipeline
        conversation.save()
        with _patch_builder(model):
            agent = EditPipelineAgent(conversation)
        agent.run("Update the pipeline")
        invocation = (
            conversation.messages.filter(role=Message.Role.ASSISTANT)
            .first()
            .tool_invocations.first()
        )
        self.assertEqual(invocation.tool_name, "propose_pipeline_version")
        self.assertTrue(invocation.success)
        self.assertIn("files", invocation.tool_output)
        self.assertEqual(invocation.tool_output["files"][0]["name"], "pipeline.py")


def _parse_sse(raw: str) -> dict:
    result = {}
    for line in raw.strip().split("\n"):
        if line.startswith("event: "):
            result["type"] = line[7:].strip()
        elif line.startswith("data: "):
            result["data"] = json.loads(line[6:])
    return result


def _collect_stream(agent, user_input: str) -> list[dict]:
    async def _run():
        events = []
        async for raw in agent.run_stream(user_input):
            events.append(_parse_sse(raw))
        return events

    return async_to_sync(_run)()


class BaseAgentRunStreamTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "stream-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Stream Test WS", description=""
            )

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    # --- Event sequence ---

    def test_first_event_is_user_message(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "What can you do?")
        self.assertEqual(events[0]["type"], "user_message")
        self.assertEqual(events[0]["data"]["content"], "What can you do?")

    def test_last_event_is_done(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "What can you do?")
        self.assertEqual(events[-1]["type"], "done")

    def test_text_deltas_reconstruct_full_response(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "What can you do?")
        deltas = [e["data"]["delta"] for e in events if e["type"] == "text_delta"]
        self.assertEqual("".join(deltas), "Hello!")

    def test_done_event_includes_message_id(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "What can you do?")
        done = events[-1]
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
        self.assertEqual(done["data"]["message_id"], str(assistant_msg.id))

    def test_done_event_includes_name_on_first_message(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "What can you do?")
        self.assertIsNotNone(events[-1]["data"]["name"])

    def test_done_event_name_is_none_on_subsequent_message(self):
        self.conversation.name = "Existing Name"
        self.conversation.save(update_fields=["name"])
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        events = _collect_stream(agent, "A follow-up question")
        self.assertEqual(events[-1]["data"]["name"], "Existing Name")

    # --- Error path ---

    def test_error_event_yielded_on_llm_exception(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        with patch.object(agent.agent, "run_stream", side_effect=Exception("LLM down")):
            events = _collect_stream(agent, "What can you do?")
        error_events = [e for e in events if e["type"] == "error"]
        self.assertEqual(len(error_events), 1)

    def test_user_message_is_saved_before_error(self):
        with _patch_builder(TestModel(custom_output_text="Hello!")):
            agent = BaseAgent(self.conversation)
        with patch.object(agent.agent, "run_stream", side_effect=Exception("LLM down")):
            _collect_stream(agent, "What can you do?")
        self.assertEqual(
            self.conversation.messages.filter(role=Message.Role.USER).count(), 1
        )

    # --- Tool events ---

    def test_tool_call_and_result_events_are_yielded(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        events = _collect_stream(agent, "Use the tool")
        event_types = [e["type"] for e in events]
        self.assertIn("tool_call", event_types)
        self.assertIn("tool_result", event_types)

    def test_tool_call_event_contains_tool_name(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        events = _collect_stream(agent, "Use the tool")
        tool_call = next(e for e in events if e["type"] == "tool_call")
        self.assertEqual(tool_call["data"]["tool_name"], "_fake_tool")

    def test_tool_result_event_indicates_success(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        with _patch_builder(model):
            agent = _AgentWithFakeTool(self.conversation)
        events = _collect_stream(agent, "Use the tool")
        tool_result = next(e for e in events if e["type"] == "tool_result")
        self.assertTrue(tool_result["data"]["success"])
