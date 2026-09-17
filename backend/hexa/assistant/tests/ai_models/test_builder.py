from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from hexa.assistant.ai_models.builder import AiModelBuilder
from hexa.assistant.ai_models.built_model import BuiltModel
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings

_PRICING_LOGGER = "hexa.assistant.ai_models.built_model"


def _builder(provider, model, api_key: str | None = "test-key") -> AiModelBuilder:
    return AiModelBuilder(
        AiSettings(provider=provider, model=model, api_key=api_key, enabled=True)
    )


def _id(value: str) -> ModelId:
    return ModelId.parse(value)


class AiModelBuilderTest(TestCase):
    def test_build_returns_built_model_for_anthropic(self):
        builder = _builder(AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU)
        result = builder.build(_id("anthropic:claude-haiku-4-5"))
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-haiku-4-5")
        self.assertEqual(result.provider_id, AiSettings.Provider.ANTHROPIC)

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.ai_models.backends.AsyncAnthropicVertex")
    def test_build_returns_built_model_for_managed(self, mock_vertex_client):
        builder = _builder(AiSettings.Provider.MANAGED, model=None, api_key=None)
        result = builder.build(_id("anthropic:claude-opus-4-6"))
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-opus-4-6")
        self.assertEqual(result.provider_id, "google-vertex")
        mock_vertex_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID="test-project")
    @patch("hexa.assistant.ai_models.backends.AsyncAnthropicVertex")
    def test_build_a_model_we_cannot_price_raises(self, mock_vertex_client):
        """Usage we cannot price never reaches the organization's budget, so a
        model id genai_prices does not know would run uncapped.
        """
        builder = _builder(AiSettings.Provider.MANAGED, model=None, api_key=None)
        with self.assertLogs(_PRICING_LOGGER, level="ERROR"):
            with self.assertRaises(AssistantException):
                builder.build(_id("anthropic:no-such-claude"))

    def test_build_a_provider_we_hold_no_credentials_for_raises(self):
        builder = _builder(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS)
        with self.assertRaises(AssistantException):
            builder.build(_id("openai:gpt-5"))

    def test_build_an_unknown_provider_raises(self):
        """Model ids are free-form config, so an unknown one only surfaces here."""
        builder = _builder("no-such-provider", AiSettings.Model.OPUS)
        with self.assertRaises(AssistantException):
            builder.build(_id("no-such-provider:whatever"))

    def test_build_for_agent_builds_the_model_selection_picked(self):
        builder = _builder(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS)
        result = builder.build_for_agent("naming", AiSettings.Model.HAIKU)
        self.assertEqual(result.api_name, "claude-haiku-4-5")

    def test_from_conversation_raises_when_workspace_has_no_organization(self):
        mock_conversation = MagicMock()
        mock_conversation.workspace.organization = None
        with self.assertRaises(AssistantException):
            AiModelBuilder.from_conversation(mock_conversation)

    def test_from_conversation_raises_when_ai_settings_disabled(self):
        mock_conversation = MagicMock()
        mock_conversation.workspace.organization.ai_settings_safe.enabled = False
        with self.assertRaises(AssistantException):
            AiModelBuilder.from_conversation(mock_conversation)
