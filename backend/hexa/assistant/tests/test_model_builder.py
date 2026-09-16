from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings
from pydantic_ai import RunUsage

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import (
    AiModelBuilder,
    BuiltModel,
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

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="")
    def test_managed_runs_everything_we_know_how_to_serve_from_vertex(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, model=None, api_key=None
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertTrue(supports(ai_settings, "google-cloud:gemini-3-pro-preview"))
        self.assertFalse(supports(ai_settings, "mistral:mistral-large"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_the_setting_narrows_managed_to_what_the_project_has_enabled(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, model=None, api_key=None
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertFalse(supports(ai_settings, "google-cloud:gemini-3-pro-preview"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic, mistral")
    def test_the_setting_cannot_add_a_provider_we_have_no_wiring_for(self):
        """It only ever narrows the registry, so naming something absent from it
        does not conjure credentials for that provider.
        """
        ai_settings = _make_ai_settings(
            AiSettings.Provider.MANAGED, model=None, api_key=None
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertFalse(supports(ai_settings, "mistral:mistral-large"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_the_setting_leaves_bring_your_own_key_alone(self):
        ai_settings = _make_ai_settings(
            AiSettings.Provider.ANTHROPIC, AiSettings.Model.OPUS
        )
        self.assertTrue(supports(ai_settings, "anthropic:claude-opus-4-6"))
        self.assertFalse(supports(ai_settings, "google-cloud:gemini-3-pro-preview"))


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
            builder.build("google-cloud:gemini-3-pro-preview")
        mock_provider.assert_called_once_with(
            project="test-project", location="europe-west1"
        )

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_build_a_provider_the_project_has_not_enabled_raises(self):
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        with self.assertRaises(AssistantException):
            builder.build("google-cloud:gemini-3-pro-preview")

    @override_settings(VERTEX_PROJECT_ID="test-project")
    @patch("hexa.assistant.model_builder.AsyncAnthropicVertex")
    def test_build_a_model_we_cannot_price_raises(self, mock_vertex_client):
        """Usage we cannot price never reaches the organization's budget, so a
        model id genai_prices does not know would run uncapped.
        """
        builder = AiModelBuilder(
            _make_ai_settings(AiSettings.Provider.MANAGED, model=None, api_key=None)
        )
        with self.assertLogs("hexa.assistant.model_builder", level="ERROR"):
            with self.assertRaises(AssistantException):
                builder.build("anthropic:no-such-claude")

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
    def test_prices_usage_with_the_model_that_produced_it(self):
        built = BuiltModel(
            model=MagicMock(), api_name="claude-opus-4-6", provider_id="anthropic"
        )
        cost = built.calculate_cost(RunUsage(input_tokens=1000, output_tokens=1000))
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)

    def test_returns_none_when_pricing_fails(self):
        """`build` turns these away, so reaching this means the price data
        changed under a model we already accepted: log it rather than pass over
        usage that escapes the organization's budget.
        """
        built = BuiltModel(model=MagicMock(), api_name="?", provider_id="?")
        with self.assertLogs("hexa.assistant.model_builder", level="ERROR"):
            self.assertIsNone(built.calculate_cost(RunUsage()))
