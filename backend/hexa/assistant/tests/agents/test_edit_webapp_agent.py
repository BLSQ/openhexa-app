from unittest.mock import patch

from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_webapp_agent import EditWebappAgent
from hexa.assistant.instructions import InstructionSet, get_instructions
from hexa.assistant.models import Conversation
from hexa.git.testutils import make_git_client_mock
from hexa.webapps.models import GitWebapp, Webapp

from ._helpers import FakeModelBuilder, _make_tool_call_model, run_agent
from ._testcase import AgentTestCase

SHA = "a" * 40
NEW_SHA = "b" * 40


class EditWebappAgentTestCase(AgentTestCase):
    def setUp(self):
        super().setUp()
        self.client_mock = make_git_client_mock(SHA)
        patcher = patch(
            "hexa.git.mixins.get_forgejo_client", return_value=self.client_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _make_webapp(self, name="Test App", slug="test-app", description=""):
        return GitWebapp.objects.create(
            workspace=self.workspace,
            name=name,
            slug=slug,
            subdomain=slug,
            description=description,
            type=Webapp.WebappType.STATIC,
            created_by=self.user,
            repository=f"ws-webapp-{slug}",
            published_commit=SHA,
        )

    def _make_agent(self, webapp=None, model=None):
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )
        if webapp is not None:
            conversation.linked_object = webapp
        conversation.save()
        return EditWebappAgent(conversation, FakeModelBuilder(model or TestModel()))


class EditWebappAgentExtraInstructionsTest(EditWebappAgentTestCase):
    def test_no_webapp_returns_empty_string(self):
        agent = self._make_agent(webapp=None)
        self.assertEqual(agent._extra_instructions(), "")

    def test_webapp_includes_name_and_slug(self):
        webapp = self._make_webapp(name="My Dashboard", slug="my-dashboard")
        agent = self._make_agent(webapp=webapp)
        instructions = agent._extra_instructions()
        self.assertIn("My Dashboard", instructions)
        self.assertIn("my-dashboard", instructions)

    def test_webapp_slug_is_included_in_file_manifest_hint(self):
        webapp = self._make_webapp(name="Workspace App", slug="workspace-app")
        agent = self._make_agent(webapp=webapp)
        instructions = agent._extra_instructions()
        self.assertIn("workspace-app", instructions)
        self.assertNotIn("workspace_slug", instructions)

    def test_webapp_description_is_included(self):
        webapp = self._make_webapp(
            name="Described App",
            slug="described-app",
            description="Shows health indicators.",
        )
        agent = self._make_agent(webapp=webapp)
        self.assertIn("Shows health indicators.", agent._extra_instructions())

    def test_webapp_without_description_omits_description_line(self):
        webapp = self._make_webapp(
            name="No Desc App", slug="no-desc-app", description=""
        )
        agent = self._make_agent(webapp=webapp)
        self.assertNotIn("Description:", agent._extra_instructions())

    def test_webapp_id_is_injected_into_context(self):
        webapp = self._make_webapp(name="Context App", slug="context-app")
        agent = self._make_agent(webapp=webapp)
        self.assertEqual(agent._context["webapp_id"], str(webapp.id))
        self.assertNotIn("webapp", agent._context)

    def test_no_webapp_leaves_context_without_webapp_id(self):
        agent = self._make_agent(webapp=None)
        self.assertNotIn("webapp_id", agent._context)

    def test_file_manifest_inlines_the_entry_point(self):
        self.client_mock.get_repository_files.return_value = [
            {
                "path": "index.html",
                "type": "file",
                "content": "<h1>Hi</h1>",
                "encoding": "TEXT",
            },
            {
                "path": "style.css",
                "type": "file",
                "content": "body {}",
                "encoding": "TEXT",
            },
        ]
        webapp = self._make_webapp(name="Manifest App", slug="manifest-app")
        agent = self._make_agent(webapp=webapp)
        instructions = agent._extra_instructions()
        self.assertIn("index.html", instructions)
        self.assertIn("style.css", instructions)
        self.assertIn("<h1>Hi</h1>", instructions)
        self.assertNotIn("body {}", instructions)
        self.assertIn("get_static_webapp_file", instructions)

    def test_binary_files_marked_in_manifest(self):
        self.client_mock.get_repository_files.return_value = [
            {
                "path": "index.html",
                "type": "file",
                "content": "<h1>Hi</h1>",
                "encoding": "TEXT",
            },
            {"path": "logo.png", "type": "file", "content": None, "encoding": "BASE64"},
        ]
        webapp = self._make_webapp(name="Binary App", slug="binary-app")
        agent = self._make_agent(webapp=webapp)
        instructions = agent._extra_instructions()
        self.assertIn("logo.png", instructions)
        self.assertIn("binary", instructions)


class EditWebappAgentToolCallTest(EditWebappAgentTestCase):
    """The MCP tools run in a worker thread with their own database connection, so
    the GraphQL layer is mocked here; the MCP and webapp suites cover what it does.
    """

    def _run_tool(self, tool_name, tool_args, graphql_response):
        webapp = self._make_webapp(name="Tool Test App", slug="tool-test-app")
        agent = self._make_agent(
            webapp=webapp, model=_make_tool_call_model(tool_name, tool_args)
        )
        calls = []

        def fake_execute_graphql(user, operation_name, variables=None):
            calls.append((user, operation_name, variables))
            return graphql_response

        with patch(
            "hexa.mcp.tools.webapps.execute_graphql", side_effect=fake_execute_graphql
        ):
            run_agent(agent, "Update the web app")
        return webapp, self.first_tool_invocation(agent.conversation), calls

    def test_update_static_webapp_runs_with_the_linked_webapp_bound(self):
        webapp, invocation, calls = self._run_tool(
            "update_static_webapp",
            {
                "files_json": '[{"path": "index.html", "content": "<h1>New</h1>"}]',
                "commit_message": "feat: greet the user",
            },
            {"updateWebapp": {"success": True, "errors": [], "webapp": {}}},
        )

        self.assertEqual(invocation.tool_name, "update_static_webapp")
        self.assertTrue(invocation.success, invocation.tool_output)
        self.assertFalse(invocation.proposal_pending)
        # The id and the user come from the context, never from the model.
        self.assertNotIn("webapp_id", invocation.tool_input)
        user, operation_name, variables = calls[0]
        self.assertEqual(user, self.user)
        self.assertEqual(operation_name, "UpdateStaticWebapp")
        self.assertEqual(
            variables["input"],
            {
                "id": str(webapp.id),
                "files": [{"path": "index.html", "content": "<h1>New</h1>"}],
                "commitMessage": "feat: greet the user",
            },
        )

    def test_edit_static_webapp_file_runs_with_the_linked_webapp_bound(self):
        webapp, invocation, calls = self._run_tool(
            "edit_static_webapp_file",
            {
                "path": "index.html",
                "old_string": "Old",
                "new_string": "New",
                "commit_message": "fix: update the heading",
            },
            {"editWebappFile": {"success": True, "errors": [], "webapp": {}}},
        )

        self.assertTrue(invocation.success, invocation.tool_output)
        _, operation_name, variables = calls[0]
        self.assertEqual(operation_name, "EditWebappFile")
        self.assertEqual(variables["input"]["id"], str(webapp.id))
        self.assertEqual(variables["input"]["commitMessage"], "fix: update the heading")

    def test_a_failed_save_is_not_a_success(self):
        _, invocation, _ = self._run_tool(
            "update_static_webapp",
            {"files_json": '[{"path": "index.html", "content": "<h1>New</h1>"}]'},
            {
                "updateWebapp": {
                    "success": False,
                    "errors": ["SAVE_FAILED"],
                    "webapp": None,
                }
            },
        )

        self.assertFalse(invocation.success)
        self.assertEqual(invocation.tool_output["errors"], ["SAVE_FAILED"])

    def test_invalid_input_never_reaches_graphql(self):
        _, invocation, calls = self._run_tool(
            "update_static_webapp", {"files_json": "not json"}, {}
        )

        self.assertFalse(invocation.success)
        self.assertIn("error", invocation.tool_output)
        self.assertEqual(calls, [])


class EditWebappAgentToolsTest(AgentTestCase):
    def test_writes_through_the_mcp_tools(self):
        names = {tool.__name__ for tool in EditWebappAgent.tools}
        self.assertIn("update_static_webapp", names)
        self.assertIn("edit_static_webapp_file", names)
        self.assertNotIn("propose_webapp_version", names)
        self.assertEqual(EditWebappAgent.history_strip_tools, set())

    def test_exposes_saved_query_and_schema_tools(self):
        # The webapp proxy only reaches the database through executeSavedQuery, so
        # the agent must be able to find, inspect and write the saved query it
        # wires the web app to.
        names = {tool.__name__ for tool in EditWebappAgent.tools}
        self.assertLessEqual(
            {
                "list_saved_queries",
                "get_saved_query",
                "create_saved_query",
                "update_saved_query",
                "get_db_schema",
                "get_db_table_schema",
            },
            names,
        )

    def test_instructions_explain_database_access(self):
        instructions = get_instructions(InstructionSet.EDIT_WEBAPP)
        self.assertIn("executeSavedQuery", instructions)
        self.assertIn("create_saved_query", instructions)
        self.assertIn("WORKSPACE", instructions)

    def test_instructions_describe_auto_save(self):
        instructions = get_instructions(InstructionSet.EDIT_WEBAPP)
        self.assertIn("update_static_webapp", instructions)
        self.assertIn("NOT published", instructions)
        self.assertIn("commit_message", instructions)
        self.assertNotIn("propose", instructions)
        self.assertNotIn("pending", instructions)

    def test_pipeline_instructions_keep_the_pending_proposal_rule(self):
        instructions = get_instructions(InstructionSet.EDIT_PIPELINE)
        self.assertIn("pending proposal", instructions)
        self.assertIn("Conventional Commits", instructions)
