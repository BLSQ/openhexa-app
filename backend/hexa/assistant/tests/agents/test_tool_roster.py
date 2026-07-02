from types import SimpleNamespace

from graphql import EnumTypeDefinitionNode, parse

from hexa.assistant.agents import all_agent_tool_names
from hexa.assistant.schema import assistant_type_defs
from hexa.assistant.schema.types import tool_segment
from hexa.core.test import TestCase


def _enum_values(sdl: str, enum_name: str) -> set[str]:
    for definition in parse(sdl).definitions:
        if (
            isinstance(definition, EnumTypeDefinitionNode)
            and definition.name.value == enum_name
        ):
            return {value.name.value for value in definition.values}
    raise AssertionError(f"enum {enum_name} not found in schema")


class AgentToolsSchemaTest(TestCase):
    def test_enum_matches_registry(self):
        """The AssistantToolName enum must mirror the agent registry exactly.

        GraphQL codegen turns this enum into the frontend's tool roster, so it
        must not drift from the tools the agents actually expose: a missing member
        leaves a new tool untyped/unlabelled in the UI, and a stale member is dead.
        """
        self.assertEqual(
            _enum_values(assistant_type_defs, "AssistantToolName"),
            all_agent_tool_names(),
            msg=(
                "AssistantToolName in hexa/assistant/graphql/schema.graphql is out "
                "of sync with the agent registry (a tool was added, removed, or "
                "renamed). Update the enum, then run `npm run codegen` in the "
                "frontend and commit the updated types.ts."
            ),
        )


def _invocation(tool_name: str) -> SimpleNamespace:
    return SimpleNamespace(
        id="8b9c6f0e-0000-0000-0000-000000000000",
        tool_name=tool_name,
        tool_input={},
        tool_output=None,
        success=True,
        proposal_pending=False,
    )


class ToolSegmentTest(TestCase):
    """`tool` is the typed view of the persisted `tool_name` string."""

    def test_known_tool_resolves_to_its_name(self):
        known = next(iter(all_agent_tool_names()))
        segment = tool_segment(_invocation(known), "call-1")
        self.assertEqual(segment["tool"], known)
        self.assertEqual(segment["tool_name"], known)

    def test_unknown_tool_resolves_to_none(self):
        # A tool removed/renamed since a conversation was stored must degrade to
        # null rather than break enum serialization for that message.
        segment = tool_segment(_invocation("since_removed_tool"), "call-1")
        self.assertIsNone(segment["tool"])
        self.assertEqual(segment["tool_name"], "since_removed_tool")

    def test_missing_invocation_resolves_to_none(self):
        # Without an invocation record the segment falls back to the call id as
        # its display name, which is never a roster member.
        segment = tool_segment(None, "toolu_01abc")
        self.assertIsNone(segment["tool"])
        self.assertEqual(segment["tool_name"], "toolu_01abc")
        self.assertIsNone(segment["id"])
