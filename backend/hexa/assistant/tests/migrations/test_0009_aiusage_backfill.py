from decimal import Decimal
from unittest.mock import patch

from django.test import TransactionTestCase

from hexa.core.test.migrator import Migrator
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


class AiUsageBackfillMigrationTest(TransactionTestCase):
    migrate_from = ("assistant", "0008_aiusage")
    migrate_to = ("assistant", "0009_aiusage_backfill")

    def setUp(self):
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)
        self.user = User.objects.create_user(
            "migration-test@example.com", "password", is_superuser=True
        )
        with patch("hexa.workspaces.models.create_database"):
            self.workspace = create_workspace(
                self.user, name="Migration Test WS", description=""
            )
        Conversation = self.migrator.apps.get_model("assistant", "Conversation")
        self.conversation = Conversation.objects.create(
            user_id=self.user.id,
            workspace_id=self.workspace.id,
            instruction_set="GENERAL",
        )

    def _message(self, role="assistant", **fields):
        Message = self.migrator.apps.get_model("assistant", "Message")
        return Message.objects.create(
            conversation=self.conversation, role=role, content=[], **fields
        )

    def test_assistant_messages_with_usage_become_rows(self):
        priced = self._message(input_tokens=120, output_tokens=30, cost=Decimal("0.5"))
        unpriced = self._message(input_tokens=10, output_tokens=5, cost=None)
        self._message(role="user")
        self._message(input_tokens=None, output_tokens=None, cost=None)

        self.migrator.migrate(*self.migrate_to)

        AiUsage = self.migrator.apps.get_model("assistant", "AiUsage")
        rows = {row.message_id: row for row in AiUsage.objects.all()}
        self.assertEqual(set(rows), {priced.id, unpriced.id})
        row = rows[priced.id]
        self.assertEqual(
            (row.organization_id, row.workspace_id, row.user_id, row.conversation_id),
            (
                self.workspace.organization_id,
                self.workspace.id,
                self.user.id,
                self.conversation.id,
            ),
        )
        self.assertEqual(
            (row.source, row.provider, row.model_name), ("conversation", "", "")
        )
        self.assertEqual((row.input_tokens, row.output_tokens), (120, 30))
        self.assertEqual(row.cost, Decimal("0.5"))
        self.assertEqual(row.created_at, priced.created_at)
        self.assertIsNone(rows[unpriced.id].cost)

    def test_already_recorded_messages_are_skipped(self):
        message = self._message(input_tokens=1, output_tokens=1, cost=Decimal("0.1"))
        AiUsage = self.migrator.apps.get_model("assistant", "AiUsage")
        AiUsage.objects.create(
            organization_id=self.workspace.organization_id,
            user_id=self.user.id,
            conversation_id=self.conversation.id,
            message_id=message.id,
            source="conversation",
            provider="anthropic",
            model_name="claude-opus-4-6",
            cost=Decimal("0.1"),
        )

        self.migrator.migrate(*self.migrate_to)

        AiUsage = self.migrator.apps.get_model("assistant", "AiUsage")
        self.assertEqual(AiUsage.objects.count(), 1)
