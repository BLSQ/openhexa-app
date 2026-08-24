from unittest.mock import patch

from asgiref.sync import async_to_sync
from pydantic_ai import ModelRetry
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents import create_agent
from hexa.assistant.agents.generate_sql_agent import GenerateSqlAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import TestCase
from hexa.core.test.utils import parse_sse_stream
from hexa.databases.tests.helpers import seed_demo_table
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace

from ._helpers import make_built_model


def _collect_stream(agent, user_input: str) -> list[dict]:
    async def _run():
        parts = []
        async for raw in agent.run_stream(user_input):
            parts.append(raw)
        return "".join(parts)

    return parse_sse_stream(async_to_sync(_run)())


# GenerateSqlAgent inlines the workspace schema and validates its output against
# the real workspace database, so (unlike most agent tests) we need a workspace
# backed by an actual Postgres database rather than one with create_database mocked away.
class GenerateSqlAgentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "generate-sql-test@example.com", "password", is_superuser=True
        )
        cls.workspace = create_workspace(
            cls.user,
            name="Generate SQL Test Workspace",
            description="",
            provision_db_on=cls,
        )

    def _make_agent(self, built_model=None) -> GenerateSqlAgent:
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERATE_SQL,
        )
        return GenerateSqlAgent(
            conversation, built_model or make_built_model(TestModel())
        )


class GenerateSqlAgentRegistryTest(GenerateSqlAgentTestCase):
    def test_generate_sql_instruction_set_returns_generate_sql_agent(self):
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERATE_SQL,
        )
        self.assertIsInstance(
            create_agent(conversation, make_built_model(TestModel())),
            GenerateSqlAgent,
        )


class GenerateSqlAgentExtraInstructionsTest(GenerateSqlAgentTestCase):
    def test_empty_database_mentions_no_tables(self):
        agent = self._make_agent()
        self.assertIn("no tables", agent._extra_instructions())

    def test_schema_includes_table_and_columns(self):
        seed_demo_table(self.workspace, [(1, "a")])
        agent = self._make_agent()
        instructions = agent._extra_instructions()
        self.assertIn("demo(", instructions)
        self.assertIn("id integer", instructions)
        self.assertIn("label text", instructions)
        # Row counts are dropped: they would need a COUNT(*) per table on every turn.
        self.assertNotIn("count", instructions.lower())

    def test_large_schema_falls_back_to_table_names_only(self):
        seed_demo_table(self.workspace, [(1, "a")])
        agent = self._make_agent()
        with patch("hexa.assistant.agents.generate_sql_agent._SCHEMA_MAX_CHARS", 0):
            instructions = agent._extra_instructions()
        self.assertIn("- demo", instructions)
        self.assertIn("get_db_table_schema", instructions)
        self.assertNotIn("id integer", instructions)

    def test_schema_load_failure_falls_back_gracefully(self):
        agent = self._make_agent()
        with patch(
            "hexa.assistant.agents.generate_sql_agent.get_full_database_definition",
            side_effect=Exception("boom"),
        ):
            instructions = agent._extra_instructions()
        self.assertIn("could not be loaded", instructions)
        self.assertIn("get_db_schema", instructions)


class GenerateSqlAgentValidateSqlTest(GenerateSqlAgentTestCase):
    def setUp(self):
        seed_demo_table(self.workspace, [(1, "a"), (2, "b")])
        self.agent = self._make_agent()

    def test_accepts_select_query(self):
        query = async_to_sync(self.agent._validate_sql)(
            "SELECT id FROM demo ORDER BY id"
        )
        self.assertEqual("SELECT id FROM demo ORDER BY id", query)

    def test_accepts_with_query(self):
        query = "WITH t AS (SELECT id FROM demo) SELECT * FROM t"
        self.assertEqual(query, async_to_sync(self.agent._validate_sql)(query))

    def test_strips_markdown_fences(self):
        query = async_to_sync(self.agent._validate_sql)(
            "```sql\nSELECT id FROM demo\n```"
        )
        self.assertEqual("SELECT id FROM demo", query)

    def test_rejects_non_select_statement(self):
        with self.assertRaises(ModelRetry):
            async_to_sync(self.agent._validate_sql)("DELETE FROM demo")

    def test_rejects_unknown_table(self):
        with self.assertRaises(ModelRetry) as ctx:
            async_to_sync(self.agent._validate_sql)("SELECT * FROM does_not_exist")
        self.assertIn("database rejected", str(ctx.exception))

    def test_rejects_multiple_statements(self):
        with self.assertRaises(ModelRetry):
            async_to_sync(self.agent._validate_sql)("SELECT 1; SELECT 2")


class GenerateSqlAgentStreamTest(GenerateSqlAgentTestCase):
    def test_done_event_carries_validated_sql_as_output(self):
        seed_demo_table(self.workspace, [(1, "a")])
        agent = self._make_agent(
            make_built_model(
                TestModel(custom_output_text="SELECT id FROM demo ORDER BY id")
            )
        )
        events = _collect_stream(agent, "List the ids in the demo table")
        done = next(e for e in events if e["event"] == "done")
        self.assertEqual(done["data"]["output"], "SELECT id FROM demo ORDER BY id")
