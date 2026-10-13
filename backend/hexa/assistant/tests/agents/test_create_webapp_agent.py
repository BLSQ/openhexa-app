from unittest.mock import patch

from hexa.assistant.agents.create_webapp_agent import CreateWebappAgent
from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.webapps.models import GitWebapp, Webapp

from ._helpers import FakeModelBuilder, _make_tool_call_model, run_agent
from ._testcase import AgentTestCase

_TOOL_ARGS = {
    "name": "My App",
    "files_json": '[{"path": "index.html", "content": "<html></html>"}]',
}


class CreateWebappAgentToolCallTest(AgentTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        with patch("hexa.git.mixins.get_forgejo_client"):
            cls.webapp = GitWebapp.objects.create(
                workspace=cls.workspace,
                name="My App",
                slug="my-app",
                subdomain="my-app",
                type=Webapp.WebappType.STATIC,
                created_by=cls.user,
                repository="ws-webapp-my-app",
            )

    def _run(self, graphql_response: dict) -> Conversation:
        conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.CREATE_WEBAPPS,
        )
        model = _make_tool_call_model("create_static_webapp", _TOOL_ARGS)
        with patch(
            "hexa.mcp.tools.webapps.execute_graphql", return_value=graphql_response
        ):
            run_agent(
                CreateWebappAgent(conversation, FakeModelBuilder(model)),
                "Build me a dashboard",
            )
        conversation.refresh_from_db()
        return conversation

    def test_created_webapp_is_linked_and_conversation_switches_to_edit(self):
        conversation = self._run(
            {
                "createWebapp": {
                    "success": True,
                    "errors": [],
                    "webapp": {"id": str(self.webapp.id), "slug": self.webapp.slug},
                }
            }
        )
        self.assertEqual(conversation.linked_object, self.webapp)
        self.assertEqual(conversation.instruction_set, InstructionSet.EDIT_WEBAPP)

    def test_failed_creation_leaves_conversation_unlinked(self):
        conversation = self._run(
            {"createWebapp": {"success": False, "errors": ["ALREADY_EXISTS"]}}
        )
        self.assertIsNone(conversation.linked_object)
        self.assertEqual(conversation.instruction_set, InstructionSet.CREATE_WEBAPPS)
