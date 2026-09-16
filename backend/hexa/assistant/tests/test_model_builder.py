from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import (
    AiModelBuilder,
    BuiltModel,
    _managed_provider,
    calculate_cost,
    is_model_id,
    provider_of,
    supports,
)
from hexa.user_management.models import AiSettings


def _make_ai_settings(provider, model, api_key: str | None = "test-key"):
    return AiSettings(provider=provider, model=model, api_key=api_key, enabled=True)


class ModelIdTest(SimpleTestCase):
    def test_provider_of_reads_the_prefix(self):
        self.assertEqual(provider_of("anthropic:claude-opus-4-6"), "anthropic")

    def test_provider_of_a_bare_name_is_the_name_itself(self):
        self.assertEqual(provider_of("claude-opus-4-6"), "claude-opus-4-6")

    def test_is_model_id_requires_a_provider_prefix(self):
        self.assertTrue(is_model_id("anthropic:claude-opus-4-6"))
        self.assertFalse(is_model_id("opus"))


class SupportsTest(SimpleTestCase):
    def test_bring_your_own_key_runs_the_provider_it_holds_a_key_for(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertFalse(supports(ai_settings, "openai:gpt-5"))

    def test_managed_runs_what_our_vertex_project_serves(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, model=None, api_key=None
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertTrue(supports(ai_settings, "google-cloud:gemini-3-pro"))
        self.assertFalse(supports(ai_settings, "mistral:mistral-large"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="mistral, groq")
    def test_managed_also_runs_the_providers_opted_into(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, model=None, api_key=None
        )
        self.assertTrue(supports(ai_settings, "mistral:mistral-large"))
        self.assertTrue(supports(ai_settings, "groq:llama-3.3"))
        self.assertFalse(supports(ai_settings, "openai:gpt-5"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="mistral")
    def test_opting_a_provider_in_leaves_bring_your_own_key_alone(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS
        )
        self.assertFalse(supports(ai_settings, "mistral:mistral-large"))


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
        result = builder.build("anthropic:claude-haiku-4-5")
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-haiku-4-5")
        self.assertEqual(result.provider_id, AiSettings.Provider.ANTHROPIC)

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.model_builder.AsyncAnthropicVertex")
    def test_build_returns_built_model_for_managed(self, mock_vertex_client):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        result = builder.build("anthropic:claude-opus-4-6")
        self.assertIsInstance(result, BuiltModel)
        self.assertEqual(result.api_name, "claude-opus-4-6")
        self.assertEqual(result.provider_id, "google-vertex")
        mock_vertex_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    def test_build_sends_a_managed_google_model_to_our_vertex_project(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        with patch("hexa.assistant.model_builder.GoogleCloudProvider") as mock_provider:
            builder.build("google-cloud:gemini-3-pro")
        mock_provider.assert_called_once_with(
            project="test-project", location="europe-west1"
        )

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="mistral", VERTEX_PROJECT_ID=None)
    def test_an_opted_in_provider_authenticates_on_its_own(self):
        """It reads its key from its own environment variable, so it needs
        neither our Vertex project nor a key from the organization.
        """
        with patch("hexa.assistant.model_builder.infer_provider") as mock_infer:
            _managed_provider("mistral")
        mock_infer.assert_called_once_with("mistral")

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="mistral")
    def test_an_opted_in_provider_is_not_priced_as_vertex(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        with patch("hexa.assistant.model_builder.infer_model") as mock_infer_model:
            mock_infer_model.return_value = MagicMock(model_name="mistral-large")
            result = builder.build("mistral:mistral-large")
        self.assertEqual(result.provider_id, "mistral")

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="mistral")
    def test_build_a_provider_whose_dependency_is_missing_raises(self):
        """Opting a provider in does not install it, so the gap surfaces here."""
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        with self.assertRaises(AssistantException):
            builder.build("mistral:mistral-large")

    @override_settings(VERTEX_PROJECT_ID=None)
    def test_build_managed_without_project_raises(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, None, api_key=None)
        )
        with self.assertRaises(AssistantException):
            builder.build("anthropic:claude-haiku-4-5")

    def test_build_a_provider_we_hold_no_credentials_for_raises(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS)
        )
        with self.assertRaises(AssistantException):
            builder.build("openai:gpt-5")

    def test_build_an_unknown_provider_raises(self):
        """Model ids are free-form config, so an unknown one only surfaces here."""
        builder = AiModelBuilder(
            _make_ai_settings("no-such-provider", AiSettings.Model.OPUS)
        )
        with self.assertRaises(AssistantException):
            builder.build("no-such-provider:whatever")

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


class CalculateCostTest(SimpleTestCase):
    def test_returns_none_when_pricing_fails(self):
        built = BuiltModel(model=MagicMock(), api_name="?", provider_id="?")
        with self.assertLogs("hexa.assistant.model_builder", level="WARNING"):
            self.assertIsNone(calculate_cost(RunUsage(), built))
