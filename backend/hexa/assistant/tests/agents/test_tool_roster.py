from graphql import EnumTypeDefinitionNode, parse

from hexa.assistant.agents import all_agent_tool_names
from hexa.assistant.schema import assistant_type_defs
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
