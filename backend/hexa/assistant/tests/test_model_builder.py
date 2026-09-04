from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import (
    AiModelBuilder,
    BuiltModel,
    calculate_cost,
    get_api_name,
    supports,
)
from hexa.user_management.models import AiSettings


def _make_ai_settings(provider, model, api_key: str | None = "test-key"):
    return AiSettings(provider=provider, model=model, api_key=api_key, enabled=True)


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
            get_api_name(AiSettings.Provider.MANAGED, AiSettings.MANAGED_MODEL),
            "claude-opus-4-6",
        )

    def test_managed_maps_haiku_to_vertex_id(self):
        self.assertEqual(
            get_api_name(AiSettings.Provider.MANAGED, AiSettings.Model.HAIKU),
            "claude-haiku-4-5",
        )

    def test_managed_does_not_map_unused_models(self):
        with self.assertRaises(AssistantException):
            get_api_name(AiSettings.Provider.MANAGED, AiSettings.Model.SONNET)

    def test_unknown_provider_raises_assistant_exception(self):
        with self.assertRaises(AssistantException):
            get_api_name("no-such-provider", AiSettings.Model.HAIKU)

    def test_unknown_model_raises_assistant_exception(self):
        with self.assertRaises(AssistantException):
            get_api_name(AiSettings.Provider.ANTHROPIC, "no-such-model")


class EffectiveModelTest(SimpleTestCase):
    def test_returns_stored_model_for_bring_your_own_key_provider(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.SONNET
        )
        self.assertEqual(ai_settings.effective_model, AiSettings.Model.SONNET)

    def test_managed_ignores_stored_model(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, AiSettings.Model.SONNET, api_key=None
        )
        self.assertEqual(ai_settings.effective_model, AiSettings.MANAGED_MODEL)


class AiModelBuilderTest(TestCase):
    def test_build_returns_built_model_for_anthropic(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.HAIKU)
        )
        result = builder.build()
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-haiku-4-5-20251001")
        self.assertEqual(result.provider_id, AiSettings.Provider.ANTHROPIC)

    def test_build_with_explicit_model_overrides_the_stored_one(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS)
        )
        self.assertEqual(
            builder.build(AiSettings.Model.SONNET).api_name, "claude-sonnet-4-6"
        )

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
        self.assertEqual(result.provider_id, "google-vertex")
        mock_vertex_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

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
        builder = AiModelBuilder(
            _make_ai_settings("unsupported", AiSettings.Model.HAIKU)
        )
        with self.assertRaises(AssistantException):
            builder.build()

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


class SupportsTest(SimpleTestCase):
    def test_true_when_the_provider_exposes_the_model(self):
        self.assertTrue(supports(AiSettings.Provider.MANAGED, AiSettings.Model.HAIKU))

    def test_false_when_the_provider_lacks_the_model(self):
        self.assertFalse(supports(AiSettings.Provider.MANAGED, AiSettings.Model.SONNET))

    def test_false_for_an_unknown_provider(self):
        self.assertFalse(supports("no-such-provider", AiSettings.Model.HAIKU))


class CalculateCostTest(SimpleTestCase):
    def test_returns_none_when_pricing_fails(self):
        built = BuiltModel(model=MagicMock(), api_name="?", provider_id="?")
        with self.assertLogs("hexa.assistant.model_builder", level="WARNING"):
            self.assertIsNone(calculate_cost(RunUsage(), built))
