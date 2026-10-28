from unittest.mock import patch

from pydantic_ai.models.test import TestModel

from hexa.assistant.agents import create_agent
from hexa.assistant.agents.edit_saved_query_agent import (
    EditSavedQueryAgent,
    save_saved_query_version,
)
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import TestCase
from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.databases.tests.helpers import seed_demo_table
from hexa.git.forgejo import ForgejoAPIError
from hexa.git.testutils import make_git_client_mock
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

from ._helpers import FakeModelBuilder, run_agent

SHA = "d" * 40


# The save tool EXPLAINs the SQL against the real workspace database, so this
# needs a provisioned database like the generate-SQL agent tests do.
class EditSavedQueryAgentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "edit-saved-query-test@example.com", "password", is_superuser=True
        )
        cls.workspace = create_workspace(
            cls.user,
            name="Edit Saved Query Test Workspace",
            description="",
            provision_db_on=cls,
        )
        cls.viewer = User.objects.create_user("viewer@example.com", "password")
        WorkspaceMembership.objects.create(
            workspace=cls.workspace,
            user=cls.viewer,
            role=WorkspaceMembershipRole.VIEWER,
        )

    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        seed_demo_table(self.workspace, [(1, "a"), (2, "b")])
        self.saved_query = SavedQuery.objects.create_if_has_perm(
            self.user,
            self.workspace,
            name="Demo rows",
            content="SELECT id FROM demo",
            description="All the demo rows",
            visibility=SavedQueryVisibility.WORKSPACE,
        )

    def _conversation(self) -> Conversation:
        return Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_SAVED_QUERY,
            linked_object=self.saved_query,
        )

    def _make_agent(self, model=None) -> EditSavedQueryAgent:
        return EditSavedQueryAgent(
            self._conversation(), FakeModelBuilder(model or TestModel())
        )


class EditSavedQueryAgentRegistryTest(EditSavedQueryAgentTestCase):
    def test_instruction_set_returns_the_agent(self):
        self.assertIsInstance(
            create_agent(self._conversation(), FakeModelBuilder(TestModel())),
            EditSavedQueryAgent,
        )


class EditSavedQueryAgentInstructionsTest(EditSavedQueryAgentTestCase):
    def test_inlines_the_query_and_the_schema(self):
        instructions = self._make_agent()._extra_instructions()

        self.assertIn("Name: Demo rows", instructions)
        self.assertIn(f"Slug: {self.saved_query.slug}", instructions)
        self.assertIn("Description: All the demo rows", instructions)
        self.assertIn("SELECT id FROM demo", instructions)
        self.assertIn("demo(id integer, label text)", instructions)

    def test_empty_query_is_said_so(self):
        self.saved_query.content = ""
        self.saved_query.save()

        self.assertIn("still empty", self._make_agent()._extra_instructions())


class SaveSavedQueryVersionToolTest(EditSavedQueryAgentTestCase):
    def test_saves_a_validated_statement_as_a_new_version(self):
        self.client_mock.commit_files.reset_mock()

        output = save_saved_query_version(
            self.saved_query, self.user, "```sql\nSELECT label FROM demo\n```"
        )

        self.assertEqual(
            {
                "slug": self.saved_query.slug,
                "name": "Demo rows",
                "content": "SELECT label FROM demo",
            },
            output,
        )
        self.assertEqual(
            "SELECT label FROM demo",
            SavedQuery.objects.get(pk=self.saved_query.pk).content,
        )
        self.client_mock.commit_files.assert_called_once()

    def test_rejects_a_statement_that_is_not_read_only(self):
        output = save_saved_query_version(
            self.saved_query, self.user, "DELETE FROM demo"
        )

        self.assertIn("read-only", output["error"])
        self.assertEqual(
            "SELECT id FROM demo",
            SavedQuery.objects.get(pk=self.saved_query.pk).content,
        )

    def test_rejects_what_the_database_rejects(self):
        output = save_saved_query_version(
            self.saved_query, self.user, "SELECT * FROM does_not_exist"
        )

        self.assertIn("database rejected", output["error"])

    def test_rejects_multiple_statements(self):
        output = save_saved_query_version(
            self.saved_query, self.user, "SELECT 1; SELECT 2"
        )

        self.assertIn("error", output)

    def test_a_user_without_the_permission_cannot_save(self):
        output = save_saved_query_version(
            self.saved_query, self.viewer, "SELECT label FROM demo"
        )

        self.assertIn("not allowed", output["error"])

    def test_a_git_failure_saves_nothing(self):
        self.client_mock.commit_files.side_effect = ForgejoAPIError(
            "POST", "/contents", 502
        )

        output = save_saved_query_version(
            self.saved_query, self.user, "SELECT label FROM demo"
        )

        self.assertIn("nothing was saved", output["error"])
        self.assertEqual(
            "SELECT id FROM demo",
            SavedQuery.objects.get(pk=self.saved_query.pk).content,
        )


class EditSavedQueryAgentRunTest(EditSavedQueryAgentTestCase):
    def test_the_tool_runs_with_the_linked_query_bound(self):
        # TestModel calls every tool once with made-up arguments; the save tool
        # gets the linked query and the user from the context, not the model.
        agent = self._make_agent(
            TestModel(
                call_tools=["save_saved_query_version"], custom_output_text="Done"
            )
        )
        conversation = agent.conversation

        run_agent(agent, "Select the labels instead")

        invocation = (
            conversation.messages.filter(role="assistant")
            .first()
            .tool_invocations.get(tool_name="save_saved_query_version")
        )
        self.assertEqual(["content"], sorted(invocation.tool_input))
        # Made-up SQL is rejected by the validator, so it surfaces as a tool
        # error the model can act on rather than as an exception.
        self.assertFalse(invocation.success)
        self.assertIn("error", invocation.tool_output)
