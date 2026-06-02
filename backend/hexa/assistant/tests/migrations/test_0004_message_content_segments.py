from datetime import timedelta
from unittest.mock import patch

from django.test import TransactionTestCase
from django.utils import timezone

from hexa.core.test.migrator import Migrator
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class MessageContentSegmentsMigrationTest(TransactionTestCase):
    migrate_from = ("assistant", "0003_conversation_generic_linked_object")
    migrate_to = ("assistant", "0004_message_content_segments")

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

        self.user = User.objects.create_user(
            "migration-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            self.workspace = Workspace.objects.create_if_has_perm(
                self.user, name="Migration Test WS", description=""
            )

        Conversation = self.migrator.apps.get_model("assistant", "Conversation")
        self.conversation = Conversation.objects.create(
            user_id=self.user.id,
            workspace_id=self.workspace.id,
            instruction_set="GENERAL",
        )

    def _get_models(self):
        Message = self.migrator.apps.get_model("assistant", "Message")
        ToolInvocation = self.migrator.apps.get_model("assistant", "ToolInvocation")
        return Message, ToolInvocation

    def test_text_only_message_becomes_text_segment(self):
        Message, _ = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="Hello world",
        )

        self.migrator.migrate(*self.migrate_to)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        self.assertEqual(
            refreshed.content,
            [{"type": "text", "content": "Hello world"}],
        )

    def test_message_with_tool_invocations_gets_tool_segments(self):
        Message, ToolInvocation = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="I'll search for that.",
        )
        ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_abc",
            tool_name="search",
            tool_input={},
            success=True,
        )

        self.migrator.migrate(*self.migrate_to)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        self.assertEqual(
            refreshed.content,
            [
                {"type": "text", "content": "I'll search for that."},
                {"type": "tool", "tool_call_id": "call_abc"},
            ],
        )

    def test_tool_segments_ordered_by_created_at(self):
        Message, ToolInvocation = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="Running tools.",
        )
        now = timezone.now()
        inv_second = ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_second",
            tool_name="tool_b",
            tool_input={},
            success=True,
        )
        inv_first = ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_first",
            tool_name="tool_a",
            tool_input={},
            success=True,
        )
        ToolInvocation.objects.filter(pk=inv_second.pk).update(created_at=now + timedelta(seconds=1))
        ToolInvocation.objects.filter(pk=inv_first.pk).update(created_at=now)

        self.migrator.migrate(*self.migrate_to)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        tool_segments = [s for s in refreshed.content if s["type"] == "tool"]
        self.assertEqual(tool_segments[0]["tool_call_id"], "call_first")
        self.assertEqual(tool_segments[1]["tool_call_id"], "call_second")

    def test_text_only_message_with_no_tool_invocations_is_not_broken(self):
        Message, _ = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="user",
            content="What can you do?",
        )

        self.migrator.migrate(*self.migrate_to)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        self.assertEqual(len(refreshed.content), 1)
        self.assertEqual(refreshed.content[0]["type"], "text")

    def test_reverse_migration_recovers_text_content(self):
        Message, _ = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="The answer is 42.",
        )

        self.migrator.migrate(*self.migrate_to)
        self.migrator.migrate(*self.migrate_from)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        self.assertEqual(refreshed.content, "The answer is 42.")

    def test_reverse_migration_recovers_first_text_segment_when_tools_present(self):
        Message, ToolInvocation = self._get_models()
        msg = Message.objects.create(
            conversation=self.conversation,
            role="assistant",
            content="Searching now.",
        )
        ToolInvocation.objects.create(
            message=msg,
            tool_call_id="call_x",
            tool_name="search",
            tool_input={},
            success=True,
        )

        self.migrator.migrate(*self.migrate_to)
        self.migrator.migrate(*self.migrate_from)

        Message = self.migrator.apps.get_model("assistant", "Message")
        refreshed = Message.objects.get(pk=msg.pk)
        self.assertEqual(refreshed.content, "Searching now.")
