from django.test import override_settings

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import AiSettings, User

ME_MONTHLY_LIMIT_QUERY = """
    query Me {
        me {
            assistantMonthlyLimit
        }
    }
"""


class AssistantMonthlyLimitResolverTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("limit-test@example.com", "password")

    @override_settings(ASSISTANT_MONTHLY_LIMIT=200)
    def test_falls_back_to_global_for_anthropic(self):
        ai_settings = self.user.ai_settings_safe
        ai_settings.provider = AiSettings.Provider.ANTHROPIC
        ai_settings.monthly_budget_cents = 500
        ai_settings.save()

        self.client.force_login(self.user)
        result = self.run_query(ME_MONTHLY_LIMIT_QUERY)
        self.assertEqual(result["data"]["me"]["assistantMonthlyLimit"], 200 * 1_000_000)

    @override_settings(ASSISTANT_MONTHLY_LIMIT=200)
    def test_uses_per_user_budget_for_vertex(self):
        ai_settings = self.user.ai_settings_safe
        ai_settings.provider = AiSettings.Provider.ANTHROPIC_VERTEX
        ai_settings.monthly_budget_cents = 500
        ai_settings.save()

        self.client.force_login(self.user)
        result = self.run_query(ME_MONTHLY_LIMIT_QUERY)
        self.assertEqual(result["data"]["me"]["assistantMonthlyLimit"], 5 * 1_000_000)

    @override_settings(ASSISTANT_MONTHLY_LIMIT=200)
    def test_falls_back_when_vertex_budget_is_null(self):
        ai_settings = self.user.ai_settings_safe
        ai_settings.provider = AiSettings.Provider.ANTHROPIC_VERTEX
        ai_settings.monthly_budget_cents = None
        ai_settings.save()

        self.client.force_login(self.user)
        result = self.run_query(ME_MONTHLY_LIMIT_QUERY)
        self.assertEqual(result["data"]["me"]["assistantMonthlyLimit"], 200 * 1_000_000)
