from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from hexa.assistant.notebooks.env import notebooks_ai_env
from hexa.user_management.models import AiSettings


def _organization(ai_settings: AiSettings):
    return SimpleNamespace(ai_settings_safe=ai_settings)


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


class NotebooksAiEnvTest(SimpleTestCase):
    def test_disabled(self):
        self.assertEqual(notebooks_ai_env(_managed(enabled=False)), {})
        self.assertEqual(notebooks_ai_env(_byok(enabled=False)), {})

    def test_managed(self):
        self.assertEqual(
            notebooks_ai_env(_managed()),
            {"HEXA_AI_PROVIDER": "openhexa", "HEXA_AI_MODEL": "claude-opus-4-6"},
        )

    @override_settings(
        ASSISTANT_MANAGED_AGENT_MODELS='{"notebooks": "google-cloud:gemini-3-pro-preview"}'
    )
    def test_managed_follows_the_notebooks_agent_key(self):
        """Any provider the gateway can run, not only Claude."""
        self.assertEqual(
            notebooks_ai_env(_managed()),
            {"HEXA_AI_PROVIDER": "openhexa", "HEXA_AI_MODEL": "gemini-3-pro-preview"},
        )

    def test_byok(self):
        self.assertEqual(
            notebooks_ai_env(_byok()),
            {"HEXA_AI_PROVIDER": "openhexa", "HEXA_AI_MODEL": "claude-sonnet-4-6"},
        )
        self.assertEqual(
            notebooks_ai_env(_byok(model=AiSettings.Model.HAIKU))["HEXA_AI_MODEL"],
            "claude-haiku-4-5",
        )

    def test_byok_without_a_model(self):
        self.assertEqual(notebooks_ai_env(_byok(model=None)), {})
