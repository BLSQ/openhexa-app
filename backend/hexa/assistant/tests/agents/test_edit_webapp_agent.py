from unittest.mock import patch

from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_webapp_agent import _MAX_INLINE_LINES, EditWebappAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.webapps.models import GitWebapp, Webapp

from ._helpers import _make_tool_call_model, make_built_model, run_agent
from ._testcase import AgentTestCase


class EditWebappAgentExtraInstructionsTest(AgentTestCase):
    def setUp(self):
        super().setUp()
        patcher = patch("hexa.git.mixins.get_forgejo_client")
        self.mock_forgejo = patcher.start()
        self.mock_forgejo.return_value.get_repository_files.return_value = []
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
        )

    def _make_agent(self, webapp=None):
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )
        if webapp is not None:
            conversation.linked_object = webapp
        conversation.save()
        return EditWebappAgent(conversation, make_built_model(TestModel()))

    def _make_pending_invocation(self, conversation, files):
        message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=[],
        )
        return ToolInvocation.objects.create(
            message=message,
            tool_name="propose_webapp_version",
            tool_call_id="call-pending-001",
            tool_input={},
            success=True,
            proposal_pending=True,
            tool_output={"files": files},
        )

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

    def test_webapp_is_injected_into_context(self):
        webapp = self._make_webapp(name="Context App", slug="context-app")
        agent = self._make_agent(webapp=webapp)
        self.assertIn("webapp", agent._context)
        self.assertEqual(agent._context["webapp"], webapp)

    def test_no_webapp_context_is_none(self):
        agent = self._make_agent(webapp=None)
        self.assertIn("webapp", agent._context)
        self.assertIsNone(agent._context["webapp"])

    def test_conversation_is_injected_into_context(self):
        agent = self._make_agent(webapp=None)
        self.assertIn("conversation", agent._context)
        self.assertEqual(agent._context["conversation"], agent.conversation)

    def test_file_manifest_shown_when_no_pending_proposal(self):
        self.mock_forgejo.return_value.get_repository_files.return_value = [
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
        self.assertIn("get_static_webapp_file", instructions)

    def test_binary_files_marked_in_manifest(self):
        self.mock_forgejo.return_value.get_repository_files.return_value = [
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

    def test_pending_proposal_small_file_is_inlined(self):
        webapp = self._make_webapp(name="Pending App", slug="pending-app")
        agent = self._make_agent(webapp=webapp)
        self._make_pending_invocation(
            agent.conversation,
            [{"path": "index.html", "content": "<h1>Draft</h1>"}],
        )
        instructions = agent._extra_instructions()
        self.assertIn("Pending Proposed Version", instructions)
        self.assertIn("index.html", instructions)
        self.assertIn("<h1>Draft</h1>", instructions)

    def test_pending_proposal_large_file_is_not_inlined(self):
        webapp = self._make_webapp(name="Large App", slug="large-app")
        agent = self._make_agent(webapp=webapp)
        large_content = "\n".join(f"line {i}" for i in range(_MAX_INLINE_LINES + 1))
        self._make_pending_invocation(
            agent.conversation,
            [{"path": "bundle.js", "content": large_content}],
        )
        instructions = agent._extra_instructions()
        self.assertIn("bundle.js", instructions)
        self.assertNotIn("line 0", instructions)
        self.assertIn("not shown", instructions)


class EditWebappAgentToolCallTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.webapp = GitWebapp.objects.create(
            workspace=cls.workspace,
            name="Tool Test App",
            slug="tool-test-app",
            subdomain="tool-test-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.user,
            repository="ws-webapp-tool-test-app",
        )

    @patch("hexa.git.mixins.get_forgejo_client")
    def test_propose_webapp_version_call_is_persisted(self, mock_get_client):
        mock_client = mock_get_client.return_value
        mock_client.get_repository_files.return_value = []

        files_arg = [{"path": "index.html", "content": "<h1>New</h1>"}]
        model = _make_tool_call_model(
            "propose_webapp_version", {"modified_files": files_arg}
        )
        conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )
        conversation.linked_object = self.webapp
        conversation.save()
        agent = EditWebappAgent(conversation, make_built_model(model))
        run_agent(agent, "Update the web app")
        invocation = self.first_tool_invocation(conversation)
        self.assertEqual(invocation.tool_name, "propose_webapp_version")
        self.assertTrue(invocation.success)
        self.assertIn("files", invocation.tool_output)
        self.assertEqual(invocation.tool_output["files"][0]["path"], "index.html")
