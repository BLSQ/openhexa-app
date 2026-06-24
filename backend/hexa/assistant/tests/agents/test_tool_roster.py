from hexa.assistant.agents import (
    AGENT_TOOLS_SCHEMA_PATH,
    render_agent_tools_schema,
)
from hexa.core.test import TestCase


class AgentToolsSchemaTest(TestCase):
    def test_generated_enum_matches_registry(self):
        """The committed AssistantToolName enum must mirror the agent registry.

        GraphQL codegen turns this file into the frontend's tool enum, so it must
        never drift. If this fails you added, removed, or renamed an agent tool:
        regenerate it with `docker compose run app manage dump_agent_tools`, then
        run `npm run codegen` in the frontend.
        """
        self.assertEqual(
            AGENT_TOOLS_SCHEMA_PATH.read_text(),
            render_agent_tools_schema(),
        )
