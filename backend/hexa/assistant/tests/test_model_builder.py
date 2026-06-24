from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import AiModelBuilder, BuiltModel, get_api_name
from hexa.user_management.models import AiSettings


def _make_ai_settings(provider, model, api_key: str | None = "test-key"):
    ai_settings = MagicMock(spec=AiSettings)
    ai_settings.provider = provider
    ai_settings.model = model
    ai_settings.api_key = api_key
    ai_settings.enabled = True
    return ai_settings


class GetApiNameTest(SimpleTestCase):
    def test_anthropic_haiku_maps_to_correct_api_name(self):
        self.assertEqual(
            get_api_name(AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU),
            "claude-haiku-4-5-20251001",
        )

    def test_anthropic_sonnet_maps_to_correct_api_name(self):
        self.assertEqual(
            get_api_name(AiSettings.Provider.ANTHROPIC, AiSettings.Model.SONNET),
            "claude-sonnet-4-6",
        )

    def test_anthropic_opus_maps_to_correct_api_name(self):
        self.assertEqual(
            get_api_name(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS),
            "claude-opus-4-6",
        )

    def test_managed_maps_default_model_to_vertex_id(self):
        self.assertEqual(
            get_api_name(AiSettings.Provider.MANAGED, AiSettings.Model.OPUS),
            "claude-opus-4-6",
        )

    def test_managed_does_not_map_non_default_models(self):
        with self.assertRaises(AssistantException):
            get_api_name(AiSettings.Provider.MANAGED, AiSettings.Model.HAIKU)

    def test_unknown_provider_raises_assistant_exception(self):
        with self.assertRaises(AssistantException):
            get_api_name("no-such-provider", AiSettings.Model.HAIKU)

    def test_unknown_model_raises_assistant_exception(self):
        with self.assertRaises(AssistantException):
            get_api_name(AiSettings.Provider.ANTHROPIC, "no-such-model")


class AiModelBuilderTest(TestCase):
    def test_properties_reflect_ai_settings(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU)
        )
        self.assertEqual(builder.model_api_name, "claude-haiku-4-5-20251001")
        self.assertEqual(builder.provider_id, AiSettings.Provider.ANTHROPIC)

    def test_build_returns_built_model_for_anthropic(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU)
        )
        result = builder.build()
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-haiku-4-5-20251001")
        self.assertEqual(result.provider_id, AiSettings.Provider.ANTHROPIC)

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.model_builder.AsyncAnthropicVertex")
    def test_build_returns_built_model_for_managed(self, mock_vertex_client):
        builder = AiModelBuilder(
            _make_ai_settings(
                AiSettings.Provider.MANAGED,
                model=None,
                api_key=None,
            )
        )
        result = builder.build()
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-opus-4-6")
        self.assertEqual(result.provider_id, AiSettings.Provider.MANAGED)
        mock_vertex_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

    def test_managed_ignores_stored_model_and_uses_default(self):
        builder = AiModelBuilder(
            _make_ai_settings(
                AiSettings.Provider.MANAGED,
                AiSettings.Model.SONNET,
                api_key=None,
            )
        )
        self.assertEqual(builder.model_api_name, "claude-opus-4-6")

    @override_settings(VERTEX_PROJECT_ID=None)
    def test_build_managed_without_project_raises(self):
        builder = AiModelBuilder(
            _make_ai_settings(
                AiSettings.Provider.MANAGED,
                AiSettings.Model.HAIKU,
                api_key=None,
            )
        )
        with self.assertRaises(AssistantException):
            builder.build()

    def test_build_unsupported_provider_raises(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU
        )
        builder = AiModelBuilder(ai_settings)
        builder._ai_settings.provider = "unsupported"
        with self.assertRaises(ValueError):
            builder.build()

    def test_from_conversation_raises_when_ai_settings_disabled(self):
        mock_conversation = MagicMock()
        mock_conversation.workspace.organization.ai_settings_safe.enabled = False
        with self.assertRaises(AssistantException):
            AiModelBuilder.from_conversation(mock_conversation)
