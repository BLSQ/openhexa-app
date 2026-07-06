import json
from unittest.mock import patch

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ToolReturnPart
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel
from pydantic_ai.models.test import TestModel

from hexa.assistant.agents.edit_webapp_agent import _MAX_INLINE_LINES, EditWebappAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.webapps.models import GitWebapp, Webapp

from ._helpers import _make_tool_call_model, make_built_model, run_agent
from ._testcase import AgentTestCase


def _make_capturing_tool_call_model(
    tool_name: str, tool_args: dict, captured_requests: list
) -> FunctionModel:
    """Like _make_tool_call_model, but records the messages each request receives."""

    def func(messages: list, agent_info: AgentInfo) -> ModelResponse:
        return ModelResponse(parts=[TextPart(content="Chat title")])

    stream_calls = []

    async def stream_func(messages, agent_info):
        stream_calls.append(1)
        captured_requests.append(list(messages))
        if len(stream_calls) == 1:
            yield {
                0: DeltaToolCall(
                    name=tool_name,
                    json_args=json.dumps(tool_args),
                    tool_call_id="call-test-001",
                )
            }
        else:
            yield "Done."

    return FunctionModel(func, stream_function=stream_func)


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


class EditWebappAgentProposalPendingTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.webapp = GitWebapp.objects.create(
            workspace=cls.workspace,
            name="Pending Test App",
            slug="pending-test-app",
            subdomain="pending-test-app",
            type=Webapp.WebappType.STATIC,
            created_by=cls.user,
            repository="ws-webapp-pending-test-app",
        )

    def setUp(self):
        patcher = patch("hexa.git.mixins.get_forgejo_client")
        self.mock_forgejo = patcher.start()
        self.mock_forgejo.return_value.get_repository_files.return_value = []
        self.addCleanup(patcher.stop)
        self.conversation = Conversation(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_WEBAPP,
        )
        self.conversation.linked_object = self.webapp
        self.conversation.save()

    def _run_proposal(self, tool_args, captured_requests=None):
        if captured_requests is None:
            model = _make_tool_call_model("propose_webapp_version", tool_args)
        else:
            model = _make_capturing_tool_call_model(
                "propose_webapp_version", tool_args, captured_requests
            )
        agent = EditWebappAgent(self.conversation, make_built_model(model))
        run_agent(agent, "Update the web app")

    def test_successful_proposal_is_marked_pending(self):
        self._run_proposal(
            {"modified_files": [{"path": "index.html", "content": "<h1>New</h1>"}]}
        )
        invocation = self.first_tool_invocation(self.conversation)
        self.assertTrue(invocation.success)
        self.assertTrue(invocation.proposal_pending)

    def test_new_proposal_supersedes_earlier_pending_one(self):
        earlier_message = Message.objects.create(
            conversation=self.conversation, role=Message.Role.ASSISTANT, content=[]
        )
        earlier = ToolInvocation.objects.create(
            message=earlier_message,
            tool_name="propose_webapp_version",
            tool_call_id="call-earlier-001",
            tool_input={},
            success=True,
            proposal_pending=True,
            tool_output={"files": [{"path": "index.html", "content": "<h1>Old</h1>"}]},
        )
        self._run_proposal(
            {"modified_files": [{"path": "index.html", "content": "<h1>New</h1>"}]}
        )
        earlier.refresh_from_db()
        self.assertFalse(earlier.proposal_pending)
        latest = ToolInvocation.objects.get(tool_call_id="call-test-001")
        self.assertTrue(latest.proposal_pending)

    def test_failed_proposal_is_not_marked_pending(self):
        self._run_proposal({})
        invocation = self.first_tool_invocation(self.conversation)
        self.assertIn("error", invocation.tool_output)
        self.assertFalse(invocation.success)
        self.assertFalse(invocation.proposal_pending)

    def test_model_requests_receive_stripped_proposal_output(self):
        captured_requests = []
        self._run_proposal(
            {"modified_files": [{"path": "index.html", "content": "<h1>New</h1>"}]},
            captured_requests=captured_requests,
        )
        # The request following the tool call must carry the summary, not the echo.
        returns = [
            part
            for messages in captured_requests
            for msg in messages
            if isinstance(msg, ModelRequest)
            for part in msg.parts
            if isinstance(part, ToolReturnPart)
            and part.tool_name == "propose_webapp_version"
        ]
        self.assertEqual(len(returns), 1)
        self.assertEqual(returns[0].content, {"status": "ok", "files": ["index.html"]})

    def test_persisted_history_keeps_full_proposal_output(self):
        self._run_proposal(
            {"modified_files": [{"path": "index.html", "content": "<h1>New</h1>"}]}
        )
        self.conversation.refresh_from_db()
        self.assertIn("<h1>New</h1>", json.dumps(self.conversation.messages_history))
