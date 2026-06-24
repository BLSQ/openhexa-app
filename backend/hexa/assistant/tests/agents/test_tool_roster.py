from hexa.assistant.agents import (
    AGENT_TOOLS_SCHEMA_PATH,
    render_agent_tools_schema,
)
from hexa.core.test import TestCase


class AgentToolsSchemaTest(TestCase):
    def test_generated_enum_matches_registry(self):
        """The committed AssistantToolName enum must mirror the agent registry.

        GraphQL codegen turns this file into the frontend's tool enum, so it must
        never drift from the tools the agents actually expose.
        """
        self.assertEqual(
            AGENT_TOOLS_SCHEMA_PATH.read_text(),
            render_agent_tools_schema(),
            msg=(
                f"\n\n{AGENT_TOOLS_SCHEMA_PATH.name} is out of sync with the agent "
                "registry (a tool was added, removed, or renamed). Regenerate and "
                "commit it:\n"
                "  1. docker compose run app manage dump_agent_tools\n"
                "  2. cd frontend && npm run codegen\n"
                "  3. commit the updated .generated.graphql and types.ts\n"
            ),
        )
