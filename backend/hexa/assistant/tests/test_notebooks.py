from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from hexa.assistant.notebooks import notebooks_ai_env
from hexa.user_management.models import AiSettings

# google-auth reports token expiry as a naive UTC datetime.
_TOKEN = ("ya29.test-token", datetime(2026, 10, 13, 15, 0, 0))  # noqa: DTZ001
_TOKEN_EXPIRES_AT = "1791903600"  # 2026-10-13T15:00:00Z


def _organization(ai_settings: AiSettings, budget_reached=False):
    return SimpleNamespace(
        slug="org",
        ai_settings_safe=ai_settings,
        is_ai_budget_limit_reached=lambda: budget_reached,
    )


def _managed(enabled=True):
    return _organization(
        AiSettings(provider=AiSettings.Provider.MANAGED, enabled=enabled)
    )


def _byok(model=AiSettings.Model.SONNET, api_key="sk-ant-test", enabled=True):
    return _organization(
        AiSettings(
            provider=AiSettings.Provider.ANTHROPIC,
            model=model,
            api_key=api_key,
            enabled=enabled,
        )
    )


@override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
@patch("hexa.assistant.notebooks.access_token", return_value=_TOKEN)
class NotebooksAiEnvTest(SimpleTestCase):
    def test_disabled(self, access_token):
        self.assertEqual(notebooks_ai_env(_managed(enabled=False)), {})
        self.assertEqual(notebooks_ai_env(_byok(enabled=False)), {})
        access_token.assert_not_called()

    def test_budget_spent(self, access_token):
        organization = _organization(
            AiSettings(provider=AiSettings.Provider.MANAGED, enabled=True),
            budget_reached=True,
        )
        self.assertEqual(notebooks_ai_env(organization), {})
        access_token.assert_not_called()

    def test_managed(self, access_token):
        self.assertEqual(
            notebooks_ai_env(_managed()),
            {
                "HEXA_AI_PROVIDER": "managed",
                "HEXA_AI_MODEL": "claude-opus-4-6",
                "HEXA_AI_VERTEX_PROJECT_ID": "test-project",
                "HEXA_AI_VERTEX_REGION": "europe-west1",
                "HEXA_AI_VERTEX_ACCESS_TOKEN": "ya29.test-token",
                "HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT": _TOKEN_EXPIRES_AT,
            },
        )

    @override_settings(
        ASSISTANT_MANAGED_AGENT_MODELS='{"notebooks": "anthropic:claude-sonnet-4-6"}'
    )
    def test_managed_configured_model(self, access_token):
        env = notebooks_ai_env(_managed())
        self.assertEqual(env["HEXA_AI_MODEL"], "claude-sonnet-4-6")

    @override_settings(
        ASSISTANT_MANAGED_AGENT_MODELS=(
            '{"default": {"model": "google-cloud:gemini-3-pro-preview", "region": "eu"}}'
        )
    )
    def test_managed_skips_non_claude_models(self, access_token):
        """Claude Code only runs Claude: a Gemini default falls through to the
        generic Claude default.
        """
        env = notebooks_ai_env(_managed())
        self.assertEqual(env["HEXA_AI_MODEL"], "claude-opus-4-6")
        self.assertEqual(env["HEXA_AI_VERTEX_REGION"], "europe-west1")

    @override_settings(
        ASSISTANT_MANAGED_AGENT_MODELS=(
            '{"notebooks": {"model": "anthropic:claude-sonnet-4-6", "region": "eu"}}'
        )
    )
    def test_managed_model_region(self, access_token):
        env = notebooks_ai_env(_managed())
        self.assertEqual(env["HEXA_AI_VERTEX_REGION"], "eu")

    @override_settings(VERTEX_PROJECT_ID=None)
    def test_managed_without_vertex_project(self, access_token):
        with self.assertLogs("hexa.assistant.notebooks", level="WARNING"):
            self.assertEqual(notebooks_ai_env(_managed()), {})
        access_token.assert_not_called()

    def test_managed_token_failure_does_not_block_the_notebook(self, access_token):
        access_token.side_effect = RuntimeError("no credentials")
        with self.assertLogs("hexa.assistant.notebooks", level="ERROR"):
            self.assertEqual(notebooks_ai_env(_managed()), {})

    def test_byok(self, access_token):
        self.assertEqual(
            notebooks_ai_env(_byok()),
            {
                "HEXA_AI_PROVIDER": "anthropic",
                "HEXA_AI_MODEL": "claude-sonnet-4-6",
                "HEXA_AI_ANTHROPIC_API_KEY": "sk-ant-test",
            },
        )
        access_token.assert_not_called()

    def test_byok_without_key(self, access_token):
        self.assertEqual(notebooks_ai_env(_byok(api_key="")), {})
