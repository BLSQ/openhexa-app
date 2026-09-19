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

    def test_managed_runs_everything_we_know_how_to_serve_from_vertex(self):
        backend = _managed_backend()
        self.assertTrue(backend.supports("anthropic"))
        self.assertTrue(backend.supports("google-cloud"))
        self.assertTrue(backend.supports("openai-chat"))
        self.assertFalse(backend.supports("mistral"))


class ModelCandidatesTest(SimpleTestCase):
    """Each backend sets its own precedence, most specific first."""

    @override_settings(ASSISTANT_MANAGED_AGENT_MODELS='{"naming": "haiku"}')
    def test_managed_reads_the_setting_before_the_code(self):
        self.assertEqual(
            _managed_backend().model_candidates("naming", AiSettings.Model.SONNET),
            ["haiku", None, AiSettings.Model.SONNET, ManagedBackend.DEFAULT_MODEL],
        )

    @override_settings(
        ASSISTANT_MANAGED_AGENT_MODELS='{"default": "google-cloud:gemini-3-pro-preview"}'
    )
    def test_managed_falls_to_the_default_entry_for_an_agent_it_does_not_name(self):
        self.assertEqual(
            _managed_backend().model_candidates("naming", AiSettings.Model.HAIKU),
            [
                None,
                ModelId("google-cloud", "gemini-3-pro-preview"),
                AiSettings.Model.HAIKU,
                ManagedBackend.DEFAULT_MODEL,
            ],
        )

    @override_settings(ASSISTANT_MANAGED_AGENT_MODELS='{"naming": "haiku"}')
    def test_bring_your_own_key_puts_the_ui_choice_first_and_ignores_the_setting(self):
        self.assertEqual(
            _byok_backend(model=AiSettings.Model.SONNET).model_candidates(
                "naming", AiSettings.Model.HAIKU
            ),
            [AiSettings.Model.SONNET, AiSettings.Model.HAIKU],
        )


class VertexOpenAiTest(SimpleTestCase):
    """One entry serves every Model Garden publisher that is not Gemini or Claude.

    They all speak Vertex's OpenAI-compatible endpoint and differ only by the
    model name, so adding Qwen or Kimi is a model id, not a code change.
    """

    def _base_url(self) -> str:
        with patch(
            "hexa.assistant.ai_models.vertex._google_credentials"
        ) as credentials:
            credentials.return_value.valid = True
            credentials.return_value.token = "ya29.token"
            return str(_managed_backend().provider_for("openai-chat").base_url)

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_MAAS_REGION="us-south1")
    def test_a_region_is_addressed_on_its_own_host(self):
        self.assertEqual(
            self._base_url(),
            "https://us-south1-aiplatform.googleapis.com/v1/projects/test-project"
            "/locations/us-south1/endpoints/openapi/",
        )

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_MAAS_REGION="global")
    def test_the_global_endpoint_drops_the_region_from_the_host(self):
        self.assertEqual(
            self._base_url(),
            "https://aiplatform.googleapis.com/v1/projects/test-project"
            "/locations/global/endpoints/openapi/",
        )


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
    @patch("hexa.assistant.ai_models.vertex.AsyncAnthropicVertex")
    def test_managed_anthropic_goes_through_our_vertex_project(self, mock_client):
        _managed_backend().provider_for("anthropic")
        mock_client.assert_called_once_with(
            project_id="test-project", region="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID="test-project", VERTEX_REGION="europe-west1")
    @patch("hexa.assistant.ai_models.vertex.GoogleCloudProvider")
    def test_managed_google_goes_through_our_vertex_project(self, mock_provider):
        _managed_backend().provider_for("google-cloud")
        mock_provider.assert_called_once_with(
            project="test-project", location="europe-west1"
        )

    @override_settings(VERTEX_PROJECT_ID=None)
    def test_managed_without_a_project_raises(self):
        with self.assertRaises(AssistantException):
            _managed_backend().provider_for("anthropic")

    def test_a_provider_vertex_does_not_serve_raises(self):
        with self.assertRaises(AssistantException):
            _managed_backend().provider_for("mistral")

    def test_a_provider_we_hold_no_credentials_for_raises(self):
        with self.assertRaises(AssistantException):
            _byok_backend().provider_for("openai")


class StoredModelTest(SimpleTestCase):
    def test_bring_your_own_key_runs_the_model_it_stored(self):
        backend = _byok_backend(model=AiSettings.Model.SONNET)
        self.assertEqual(
            backend.model_candidates("naming", None), [AiSettings.Model.SONNET, None]
        )

    def test_managed_ignores_a_stored_model(self):
        """Managed organizations never pick a model, so a value left on their
        settings by a previous bring-your-own-key provider is not theirs to run.
        """
        backend = _managed_backend()
        backend.ai_settings.model = AiSettings.Model.SONNET
        self.assertNotIn(
            AiSettings.Model.SONNET, backend.model_candidates("naming", None)
        )
