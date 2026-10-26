from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.utils import timezone

from hexa.assistant.models import AiUsage, Conversation
from hexa.core.test import TestCase
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


class ConversationCostForUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "cost@example.com", "password", is_superuser=True
        )
        cls.other = User.objects.create_user("other@example.com", "password")
        with patch("hexa.workspaces.models.create_database"):
            cls.workspace = create_workspace(cls.user, name="Cost WS", description="")

    def _usage(self, user, cost, source=AiUsage.Source.CONVERSATION) -> AiUsage:
        return AiUsage.objects.create(
            organization=self.workspace.organization,
            workspace=self.workspace,
            user=user,
            source=source,
            provider="anthropic",
            model_name="claude-opus-4-6",
            cost=cost,
        )

    def test_monthly_cost_sums_the_users_conversations_of_the_month(self):
        self.assertEqual(Conversation.get_monthly_cost_for_user(self.user), 0)
        self._usage(self.user, Decimal("1.5"))
        self._usage(self.user, Decimal("0.25"))
        self._usage(self.user, None)
        self._usage(self.other, Decimal("10"))
        AiUsage.objects.filter(pk=self._usage(self.user, Decimal("99")).pk).update(
            created_at=timezone.now() - timedelta(days=40)
        )
        self.assertEqual(
            Conversation.get_monthly_cost_for_user(self.user), Decimal("1.75")
        )

    def test_monthly_cost_leaves_the_notebooks_to_the_organization_budget(self):
        self._usage(self.user, Decimal("1"))
        self._usage(self.user, Decimal("5"), source=AiUsage.Source.NOTEBOOK)
        self.assertEqual(Conversation.get_monthly_cost_for_user(self.user), Decimal(1))

    def test_total_cost_sums_every_month(self):
        self.assertEqual(Conversation.get_total_cost_for_user(self.user), 0)
        self._usage(self.user, Decimal("1"))
        AiUsage.objects.filter(pk=self._usage(self.user, Decimal("2")).pk).update(
            created_at=timezone.now() - timedelta(days=400)
        )
        self._usage(self.other, Decimal("10"))
        self.assertEqual(Conversation.get_total_cost_for_user(self.user), Decimal(3))
