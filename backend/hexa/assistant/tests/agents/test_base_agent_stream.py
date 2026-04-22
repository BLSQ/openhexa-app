import json
from unittest.mock import patch

from asgiref.sync import async_to_sync
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.base import BaseAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message

from ._helpers import _AgentWithFakeTool, _make_tool_call_model, _patch_builder
from ._testcase import AgentTestCase


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


class BaseAgentRunStreamTest(AgentTestCase):
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
