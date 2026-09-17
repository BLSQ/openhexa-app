from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from hexa.assistant.ai_models.backends import (
    BringYourOwnKeyBackend,
    ManagedBackend,
    backend_for,
)
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings


def _managed_backend():
    return backend_for(
        AiSettings(
            provider=AiSettings.Provider.MANAGED, model=None, api_key=None, enabled=True
        )
    )


def _byok_backend(provider=AiSettings.Provider.ANTHROPIC, model=AiSettings.Model.OPUS):
    return backend_for(
        AiSettings(provider=provider, model=model, api_key="test-key", enabled=True)
    )


class BackendForTest(SimpleTestCase):
    def test_managed_organizations_run_on_our_vertex_project(self):
        self.assertIsInstance(_managed_backend(), ManagedBackend)

    def test_everyone_else_runs_on_the_key_they_brought(self):
        self.assertIsInstance(_byok_backend(), BringYourOwnKeyBackend)


class SupportsTest(SimpleTestCase):
    def test_bring_your_own_key_runs_the_provider_it_holds_a_key_for(self):
        backend = _byok_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertFalse(backend.supports("openai"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="")
    def test_managed_runs_everything_we_know_how_to_serve_from_vertex(self):
        backend = _managed_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertTrue(backend.supports("google-cloud"))
        self.assertFalse(backend.supports("mistral"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_the_setting_narrows_managed_to_what_the_project_has_enabled(self):
        backend = _managed_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertFalse(backend.supports("google-cloud"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic, mistral")
    def test_the_setting_cannot_add_a_provider_we_have_no_wiring_for(self):
        """It only ever narrows the registry, so naming something absent from it
        does not conjure credentials for that provider.
        """
        backend = _managed_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertFalse(backend.supports("mistral"))

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_the_setting_leaves_bring_your_own_key_alone(self):
        backend = _byok_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertFalse(backend.supports("google-cloud"))


class PricingProviderTest(SimpleTestCase):
    def test_managed_models_are_priced_as_the_vertex_backend_they_run_on(self):
        self.assertEqual(
            _managed_backend().pricing_provider(
                ModelId("anthropic", "claude-opus-4-6")
            ),
            ManagedBackend.PRICING_PROVIDER,
        )

    def test_bring_your_own_key_models_are_priced_by_their_own_provider(self):
        self.assertEqual(
            _byok_backend().pricing_provider(ModelId("anthropic", "claude-opus-4-6")),
            "anthropic",
        )


class ProviderForTest(SimpleTestCase):
    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.ai_models.backends.AsyncAnthropicVertex")
    def test_managed_anthropic_goes_through_our_vertex_project(self, mock_client):
        _managed_backend().provider_for("anthropic")
        mock_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.ai_models.backends.GoogleCloudProvider")
    def test_managed_google_goes_through_our_vertex_project(self, mock_provider):
        _managed_backend().provider_for("google-cloud")
        mock_provider.assert_called_once_with(
            project="test-project", location="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID=None)
    def test_managed_without_a_project_raises(self):
        with self.assertRaises(AssistantException):
            _managed_backend().provider_for("anthropic")

    @override_settings(ASSISTANT_MANAGED_PROVIDERS="anthropic")
    def test_a_provider_the_project_has_not_enabled_raises(self):
        with self.assertRaises(AssistantException):
            _managed_backend().provider_for("google-cloud")

    def test_a_provider_we_hold_no_credentials_for_raises(self):
        with self.assertRaises(AssistantException):
            _byok_backend().provider_for("openai")


class EffectiveModelTest(SimpleTestCase):
    def test_returns_stored_model_for_bring_your_own_key_provider(self):
        ai_settings = _byok_backend(model=AiSettings.Model.SONNET).ai_settings
        self.assertEqual(ai_settings.effective_model, AiSettings.Model.SONNET)

    def test_managed_ignores_stored_model(self):
        ai_settings = _managed_backend().ai_settings
        ai_settings.model = AiSettings.Model.SONNET
        self.assertEqual(ai_settings.effective_model, AiSettings.MANAGED_MODEL)
