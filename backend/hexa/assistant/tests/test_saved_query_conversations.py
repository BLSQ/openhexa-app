from unittest.mock import patch

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation
from hexa.core.test import GraphQLTestCase
from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.git.testutils import make_git_client_mock
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole
from hexa.workspaces.tests.testutils import create_workspace

CREATE_CONVERSATION = """
  mutation ($input: CreateAssistantConversationInput!) {
    createAssistantConversation(input: $input) {
      success
      errors
      conversation { id }
    }
  }
"""

SAVED_QUERY_CONVERSATIONS = """
  query ($slug: String!) {
    savedQueryBySlug(slug: $slug) {
      assistantConversations { id }
    }
  }
"""


class SavedQueryConversationTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "author@example.com", "password", is_superuser=True
        )
        cls.other = User.objects.create_user("other@example.com", "password")
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = create_workspace(
                cls.user, name="Conversations WS", description=""
            )
        WorkspaceMembership.objects.create(
            workspace=cls.workspace,
            user=cls.other,
            role=WorkspaceMembershipRole.EDITOR,
        )
        # Superuser only to create the workspace: the tests are about a member.
        cls.user.is_superuser = False
        cls.user.save()
        with patch(
            "hexa.git.mixins.get_forgejo_client",
            return_value=make_git_client_mock(),
        ):
            cls.saved_query = SavedQuery.objects.create_if_has_perm(
                cls.user,
                cls.workspace,
                name="Private query",
                content="SELECT 1",
                visibility=SavedQueryVisibility.PRIVATE,
            )

    def _create(self, user):
        self.client.force_login(user)
        return self.run_query(
            CREATE_CONVERSATION,
            {
                "input": {
                    "workspaceSlug": self.workspace.slug,
                    "linkedObjectId": str(self.saved_query.id),
                    "linkedObjectType": "SavedQuery",
                }
            },
        )["data"]["createAssistantConversation"]

    def test_a_conversation_about_a_saved_query_uses_the_edit_agent(self):
        result = self._create(self.user)

        self.assertTrue(result["success"], result)
        conversation = Conversation.objects.get(id=result["conversation"]["id"])
        self.assertEqual(InstructionSet.EDIT_SAVED_QUERY, conversation.instruction_set)
        self.assertEqual(self.saved_query, conversation.linked_object)

        self.client.force_login(self.user)
        data = self.run_query(
            SAVED_QUERY_CONVERSATIONS, {"slug": self.saved_query.slug}
        )
        self.assertEqual(
            [{"id": str(conversation.id)}],
            data["data"]["savedQueryBySlug"]["assistantConversations"],
        )

    def test_a_query_the_user_cannot_see_cannot_be_linked(self):
        result = self._create(self.other)

        self.assertFalse(result["success"])
        self.assertEqual(["LINKED_OBJECT_NOT_FOUND"], result["errors"])
