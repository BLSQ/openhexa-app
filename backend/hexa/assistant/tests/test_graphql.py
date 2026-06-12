from unittest.mock import patch

from hexa.assistant.instructions import InstructionSet
from hexa.assistant.models import Conversation, Message, ToolInvocation
from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

CONVERSATION_MESSAGES_QUERY = """
  query AssistantConversationMessages($id: UUID!) {
    assistantConversation(id: $id) {
      messages {
        items {
          id
          role
          content {
            __typename
            ... on AssistantTextSegment {
              content
            }
            ... on AssistantToolSegment {
              toolCallId
              toolName
              toolInput
              toolOutput
              success
            }
          }
        }
      }
    }
  }
"""


class AssistantConversationMessagesQueryTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "graphql-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = Workspace.objects.create_if_has_perm(
                cls.user, name="GraphQL Test WS", description=""
            )

    def setUp(self):
        super().setUp()
        self.conversation = Conversation.objects.create(
            user=self.user,
            workspace=self.workspace,
            instruction_set=InstructionSet.GENERAL,
        )
        self.client.force_login(self.user)

    def _query(self):
        return self.run_query(
            CONVERSATION_MESSAGES_QUERY,
            variables={"id": str(self.conversation.id)},
        )

    def _items(self):
        return self._query()["data"]["assistantConversation"]["messages"]["items"]

    def test_text_only_message_returns_text_segment(self):
        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=[{"type": "text", "content": "Hello!"}],
        )

        items = self._items()
        self.assertEqual(len(items), 1)
        segments = items[0]["content"]
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["__typename"], "AssistantTextSegment")
        self.assertEqual(segments[0]["content"], "Hello!")

    def test_tool_segment_joined_with_invocation_data(self):
        msg = Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=[
                {"type": "text", "content": "Searching."},
                {"type": "tool", "tool_call_id": "call_abc"},
            ],
        )
        ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_abc",
            tool_name="search_tool",
            tool_input={"query": "openhexa"},
            tool_output={"results": []},
            success=True,
        )

        items = self._items()
        segments = items[0]["content"]
        self.assertEqual(len(segments), 2)

        text_seg = segments[0]
        self.assertEqual(text_seg["__typename"], "AssistantTextSegment")
        self.assertEqual(text_seg["content"], "Searching.")

        tool_seg = segments[1]
        self.assertEqual(tool_seg["__typename"], "AssistantToolSegment")
        self.assertEqual(tool_seg["toolCallId"], "call_abc")
        self.assertEqual(tool_seg["toolName"], "search_tool")
        self.assertEqual(tool_seg["toolInput"], {"query": "openhexa"})
        self.assertEqual(tool_seg["toolOutput"], {"results": []})
        self.assertTrue(tool_seg["success"])

    def test_tool_segment_without_invocation_has_success_false(self):
        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=[{"type": "tool", "tool_call_id": "call_orphan"}],
        )

        items = self._items()
        tool_seg = items[0]["content"][0]
        self.assertEqual(tool_seg["__typename"], "AssistantToolSegment")
        self.assertFalse(tool_seg["success"])

    def test_failed_tool_invocation_sets_success_false(self):
        msg = Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=[{"type": "tool", "tool_call_id": "call_fail"}],
        )
        ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_fail",
            tool_name="risky_tool",
            tool_input={},
            tool_output={"errors": ["Something broke"]},
            success=False,
        )

        items = self._items()
        tool_seg = items[0]["content"][0]
        self.assertFalse(tool_seg["success"])

    def test_segments_returned_in_stored_order(self):
        Message.objects.create(
            conversation=self.conversation,
            role=Message.Role.ASSISTANT,
            content=[
                {"type": "text", "content": "First"},
                {"type": "tool", "tool_call_id": "call_1"},
                {"type": "text", "content": "Second"},
            ],
        )

        items = self._items()
        segments = items[0]["content"]
        self.assertEqual(segments[0]["__typename"], "AssistantTextSegment")
        self.assertEqual(segments[0]["content"], "First")
        self.assertEqual(segments[1]["__typename"], "AssistantToolSegment")
        self.assertEqual(segments[2]["__typename"], "AssistantTextSegment")
        self.assertEqual(segments[2]["content"], "Second")
