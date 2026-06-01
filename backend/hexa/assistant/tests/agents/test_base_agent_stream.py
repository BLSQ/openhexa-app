from contextlib import asynccontextmanager
from unittest.mock import patch

from pydantic_ai.exceptions import IncompleteToolCall, UnexpectedModelBehavior, UsageLimitExceeded

from asgiref.sync import async_to_sync
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message
from hexa.core.test.utils import parse_sse_stream

from ._helpers import (
    _AgentWithFakeTool,
    _make_tool_call_model,
    make_built_model,
)
from ._testcase import AgentTestCase


def _collect_stream(agent, user_input: str) -> list[dict]:
    async def _run():
        parts = []
        async for raw in agent.run_stream(user_input):
            parts.append(raw)
        return "".join(parts)

    return parse_sse_stream(async_to_sync(_run)())


class BaseAgentRunStreamTest(AgentTestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )

    # --- Event sequence ---

    def test_first_event_is_user_message(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "What can you do?")
        self.assertEqual(events[0]["event"], "user_message")
        self.assertEqual(events[0]["data"]["content"], "What can you do?")

    def test_last_event_is_done(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "What can you do?")
        self.assertEqual(events[-1]["event"], "done")

    def test_text_deltas_reconstruct_full_response(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "What can you do?")
        deltas = [e["data"]["delta"] for e in events if e["event"] == "text_delta"]
        self.assertEqual("".join(deltas), "Hello!")

    def test_done_event_includes_message_id(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "What can you do?")
        done = events[-1]
        assistant_msg = self.conversation.messages.filter(
            role=Message.Role.ASSISTANT
        ).first()
        self.assertEqual(done["data"]["message_id"], str(assistant_msg.id))

    def test_done_event_includes_name_on_first_message(self):
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "What can you do?")
        self.assertIsNotNone(events[-1]["data"]["name"])

    def test_done_event_returns_existing_name_on_subsequent_message(self):
        self.conversation.name = "Existing Name"
        self.conversation.save(update_fields=["name"])
        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        events = _collect_stream(agent, "A follow-up question")
        self.assertEqual(events[-1]["data"]["name"], "Existing Name")

    # --- Error path ---

    def test_error_event_yielded_on_llm_exception(self):
        @asynccontextmanager
        async def _failing_iter(*args, **kwargs):
            raise Exception("LLM down")
            yield  # pragma: no cover

        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        with patch.object(agent.agent, "iter", _failing_iter):
            events = _collect_stream(agent, "What can you do?")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertEqual(len(error_events), 1)

    def test_user_message_is_saved_before_error(self):
        @asynccontextmanager
        async def _failing_iter(*args, **kwargs):
            raise Exception("LLM down")
            yield  # pragma: no cover

        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hello!"))
        )
        with patch.object(agent.agent, "iter", _failing_iter):
            _collect_stream(agent, "What can you do?")
        self.assertEqual(
            self.conversation.messages.filter(role=Message.Role.USER).count(), 1
        )

    # --- Tool events ---

    def test_tool_call_and_result_events_are_yielded(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        events = _collect_stream(agent, "Use the tool")
        event_types = [e["event"] for e in events]
        self.assertIn("tool_call", event_types)
        self.assertIn("tool_result", event_types)

    def test_tool_call_event_contains_tool_name(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        events = _collect_stream(agent, "Use the tool")
        tool_call = next(e for e in events if e["event"] == "tool_call")
        self.assertEqual(tool_call["data"]["tool_name"], "_fake_tool")

    def test_tool_result_event_indicates_success(self):
        model = _make_tool_call_model("_fake_tool", {"arg": "hello"})
        agent = _AgentWithFakeTool(self.conversation, make_built_model(model))
        events = _collect_stream(agent, "Use the tool")
        tool_result = next(e for e in events if e["event"] == "tool_result")
        self.assertTrue(tool_result["data"]["success"])

    def test_incomplete_tool_call_yields_user_friendly_error(self):
        @asynccontextmanager
        async def _incomplete_iter(*args, **kwargs):
            raise IncompleteToolCall("Tool call was cut off by token limit")
            yield  # pragma: no cover

        agent = _AgentWithFakeTool(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        with patch.object(agent.agent, "iter", _incomplete_iter):
            events = _collect_stream(agent, "Use the tool")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertEqual(len(error_events), 1)
        self.assertIn("maximum token limit", error_events[0]["data"]["message"])

    def test_incomplete_tool_call_does_not_yield_generic_error(self):
        @asynccontextmanager
        async def _incomplete_iter(*args, **kwargs):
            raise IncompleteToolCall("Tool call was cut off by token limit")
            yield  # pragma: no cover

        agent = _AgentWithFakeTool(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        with patch.object(agent.agent, "iter", _incomplete_iter):
            events = _collect_stream(agent, "Use the tool")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertNotEqual(error_events[0]["data"]["message"], "An error occurred")

    def test_usage_limit_exceeded_token_limit_yields_user_friendly_error(self):
        @asynccontextmanager
        async def _usage_limit_iter(*args, **kwargs):
            raise UsageLimitExceeded("Exceeded the output_tokens_limit of 32768")
            yield  # pragma: no cover

        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        with patch.object(agent.agent, "iter", _usage_limit_iter):
            events = _collect_stream(agent, "Do something complex")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertEqual(len(error_events), 1)
        self.assertIn("maximum token limit", error_events[0]["data"]["message"])

    def test_usage_limit_exceeded_request_limit_yields_loop_error(self):
        @asynccontextmanager
        async def _loop_iter(*args, **kwargs):
            raise UsageLimitExceeded("Exceeded the request_limit of 10")
            yield  # pragma: no cover

        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        with patch.object(agent.agent, "iter", _loop_iter):
            events = _collect_stream(agent, "Do something complex")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertEqual(len(error_events), 1)
        self.assertIn("loop", error_events[0]["data"]["message"])

    def test_other_unexpected_model_behavior_yields_generic_error(self):
        @asynccontextmanager
        async def _unexpected_iter(*args, **kwargs):
            raise UnexpectedModelBehavior("Model returned something totally unexpected")
            yield  # pragma: no cover

        agent = BaseAgent(
            self.conversation, make_built_model(TestModel(custom_output_text="Hi"))
        )
        with patch.object(agent.agent, "iter", _unexpected_iter):
            events = _collect_stream(agent, "Do something")
        error_events = [e for e in events if e["event"] == "error"]
        self.assertEqual(len(error_events), 1)
        self.assertEqual(error_events[0]["data"]["message"], "An error occurred")

