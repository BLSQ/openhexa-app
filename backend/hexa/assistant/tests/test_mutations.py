from unittest.mock import patch

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

RESOLVE_PROPOSAL_MUTATION = """
    mutation resolveAssistantProposal($toolInvocationId: UUID!) {
        resolveAssistantProposal(toolInvocationId: $toolInvocationId) {
            success
            errors
        }
    }
"""


class ResolveAssistantProposalMutationTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "mutation-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="Test Workspace", description=""
            )

    def _make_invocation(self, conversation, tool_name="propose_pipeline_version"):
        message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content="",
        )
        return ToolInvocation.objects.create(
            message=message,
            tool_call_id="call-1",
            tool_name=tool_name,
            tool_input={},
            tool_output={"files": []},
            success=True,
            proposal_pending=True,
        )

    def setUp(self):
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.EDIT_PIPELINE,
        )

    def test_resolving_a_proposal_also_resolves_older_unresolved_ones(self):
        proposal_1 = self._make_invocation(self.conversation)
        proposal_2 = self._make_invocation(self.conversation)

        self.client.force_login(self.user)
        result = self.run_query(
            RESOLVE_PROPOSAL_MUTATION,
            variables={"toolInvocationId": str(proposal_2.id)},
        )
        self.assertTrue(result["data"]["resolveAssistantProposal"]["success"])

        proposal_1.refresh_from_db()
        proposal_2.refresh_from_db()
        self.assertFalse(proposal_1.proposal_pending)
        self.assertFalse(proposal_2.proposal_pending)

    def test_resolving_does_not_affect_other_tool_names(self):
        other_invocation = self._make_invocation(
            self.conversation, tool_name="other_tool"
        )
        proposal = self._make_invocation(self.conversation)

        self.client.force_login(self.user)
        self.run_query(
            RESOLVE_PROPOSAL_MUTATION,
            variables={"toolInvocationId": str(proposal.id)},
        )

        other_invocation.refresh_from_db()
        self.assertTrue(other_invocation.proposal_pending)
