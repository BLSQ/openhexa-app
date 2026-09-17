from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.ai_models.builder import AiModelBuilder
from hexa.assistant.ai_models.built_model import BuiltModel
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings

_LOGGER = "hexa.assistant.ai_models.builder"


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
    def test_a_model_we_cannot_price_still_builds(self, mock_vertex_client):
        """Reaching for a new model must not wait on genai_prices catching up, so
        an unknown price costs its usage a place in the budget, not the run. The
        log names the configured id, which is what an operator has to fix.
        """
        builder = _builder(AiSettings.Provider.MANAGED, model=None, api_key=None)
        with self.assertLogs(_LOGGER, level="ERROR") as logs:
            built = builder.build(_id("anthropic:no-such-claude"))
        self.assertEqual(built.api_name, "no-such-claude")
        self.assertIn("anthropic:no-such-claude", logs.output[0])
        self.assertIsNone(built.calculate_cost(RunUsage(input_tokens=1000)))

    @override_settings(VERTEX_PROJECT_ID="test-project")
    @patch("hexa.assistant.ai_models.backends.AsyncAnthropicVertex")
    def test_a_priced_model_builds_quietly(self, mock_vertex_client):
        builder = _builder(AiSettings.Provider.MANAGED, model=None, api_key=None)
        with self.assertNoLogs(_LOGGER, level="ERROR"):
            builder.build(_id("anthropic:claude-opus-4-6"))

    @override_settings(
        VERTEX_PROJECT_ID="test-project",
        VERTEX_MAAS_REGION="global",
        ASSISTANT_MANAGED_MODELS=(
            '{"opus": "openai-chat:qwen/qwen3-coder-480b-a35b-instruct-maas"}'
        ),
    )
    @patch("hexa.assistant.ai_models.backends._google_credentials")
    def test_a_model_garden_model_takes_only_a_setting(self, credentials):
        """The point of the openai-chat entry: Qwen, Kimi and the rest arrive as
        configuration, with no code of their own.
        """
        credentials.return_value.valid = True
        credentials.return_value.token = "ya29.token"
        built = _builder(AiSettings.Provider.MANAGED, model=None, api_key=None).build(
            _id("openai-chat:qwen/qwen3-coder-480b-a35b-instruct-maas")
        )
        self.assertEqual(built.api_name, "qwen/qwen3-coder-480b-a35b-instruct-maas")
        self.assertEqual(
            str(built.model.base_url),
            "https://aiplatform.googleapis.com/v1/projects/test-project"
            "/locations/global/endpoints/openapi/",
        )

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
