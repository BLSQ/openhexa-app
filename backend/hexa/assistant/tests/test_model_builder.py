from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import (
    _MODEL_IDS_BY_PROVIDER,
    UTILITY_MODEL,
    AiModelBuilder,
    BuiltModel,
    get_api_name,
    utility_model_for,
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

    def test_managed_maps_utility_model_to_vertex_id(self):
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


class UtilityModelForTest(SimpleTestCase):
    def test_every_provider_exposes_the_utility_model(self):
        """A provider whose map lacks it silently loses the cost saving, so catch
        it here rather than in production logs.
        """
        for provider, model_ids in _MODEL_IDS_BY_PROVIDER.items():
            with self.subTest(provider=provider):
                self.assertIn(UTILITY_MODEL, model_ids)

    def test_returns_utility_model(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS
        )
        self.assertEqual(utility_model_for(ai_settings), UTILITY_MODEL)

    @override_settings(ASSISTANT_UTILITY_MODEL_ENABLED=False)
    def test_falls_back_to_main_model_when_disabled(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.SONNET
        )
        self.assertEqual(utility_model_for(ai_settings), AiSettings.Model.SONNET)

    def test_falls_back_to_main_model_when_provider_lacks_it(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS
        )
        maps = {AiSettings.Provider.ANTHROPIC.value: {AiSettings.Model.OPUS.value: "x"}}
        with (
            patch.dict(_MODEL_IDS_BY_PROVIDER, maps, clear=True),
            self.assertLogs("hexa.assistant.model_builder", level="ERROR"),
        ):
            self.assertEqual(utility_model_for(ai_settings), AiSettings.Model.OPUS)


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


class BuildUtilityModelTest(TestCase):
    def test_uses_utility_model_for_anthropic(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS)
        )
        self.assertEqual(builder.build_utility().api_name, "claude-haiku-4-5-20251001")

    @override_settings(VERTEX_PROJECT_ID="test-project")
    @patch("hexa.assistant.model_builder.AsyncAnthropicVertex")
    def test_uses_utility_model_for_managed(self, mock_vertex_client):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        built = builder.build_utility()
        self.assertEqual(built.api_name, "claude-haiku-4-5")
        self.assertEqual(built.provider_id, "google-vertex")
