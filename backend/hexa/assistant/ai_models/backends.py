"""Where an organization's models come from: our own Vertex project, or its key.
Each subclass has the logic specific to the provider backend (managed or BYOK)
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import cache, cached_property

import google.auth
from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from google.auth.transport.requests import Request as GoogleAuthRequest
from pydantic_ai.providers import Provider, infer_provider_class
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google_cloud import GoogleCloudProvider
from pydantic_ai.providers.openai import OpenAIProvider

from hexa.assistant.ai_models.config import enabled_managed_providers, managed_model_ids
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


class ProviderBackend(ABC):
    """The models an organization can run, and the credentials to run them.

    Instances are cheap and short-lived — one per `AiModelBuilder`, so per request
    """

    def __init__(self, ai_settings: AiSettings):
        self.ai_settings = ai_settings

    @property
    @abstractmethod
    def model_ids(self) -> dict[str, ModelId]:
        """Logical model -> the model id it stands for on this backend."""

    @abstractmethod
    def supports(self, provider: str) -> bool:
        """Whether this backend holds credentials for `provider`."""

    @abstractmethod
    def pricing_provider(self, model_id: ModelId) -> str:
        """The genai_prices provider for the model in this backend."""

    @abstractmethod
    def _build_provider(self, provider: str) -> Provider:
        """Build `provider` pydantic-ai class."""

    def provider_for(self, provider: str) -> Provider:
        """Build `provider` pydantic-ai class if supported."""
        if not self.supports(provider):
            raise AssistantException(
                f"Provider {provider!r} cannot run with the credentials of "
                f"{self.ai_settings.provider!r} organizations"
            )
        return self._build_provider(provider)


def _vertex_anthropic() -> Provider:
    # pydantic-ai has no Anthropic-on-Vertex provider of its own: Claude on
    # Vertex is the Anthropic provider wrapped around Google's client.
    return AnthropicProvider(
        anthropic_client=AsyncAnthropicVertex(
            project_id=settings.VERTEX_PROJECT_ID,
            region=settings.VERTEX_REGION,
        )
    )


def _vertex_google() -> Provider:
    return GoogleCloudProvider(
        project=settings.VERTEX_PROJECT_ID, location=settings.VERTEX_REGION
    )


@cache
def _google_credentials():
    """Our service account, read once and refreshed in place as it expires."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return credentials


def _vertex_openai() -> Provider:
    """Vertex's OpenAI-compatible endpoint, which serves every Model Garden
    publisher that is neither Gemini nor Claude: Qwen, Kimi, DeepSeek, Llama, gpt-oss.
    Example: "openai-chat:qwen/qwen3-coder-480b-a35b-instruct-maas"

    It authenticates with a bearer token rather than a key,
    which is why it builds its own client
    """
    credentials = _google_credentials()
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())
    region = settings.VERTEX_MAAS_REGION
    host = (
        "aiplatform.googleapis.com"
        if region == "global"
        else f"{region}-aiplatform.googleapis.com"
    )
    return OpenAIProvider(
        base_url=(
            f"https://{host}/v1/projects/{settings.VERTEX_PROJECT_ID}"
            f"/locations/{region}/endpoints/openapi"
        ),
        api_key=credentials.token,
    )


class ManagedBackend(ProviderBackend):
    """Models served from our own Vertex project, on our own account."""

    # What our Vertex project runs managed organizations on, overridden entry by
    # entry from ASSISTANT_MANAGED_MODELS. It only needs the models agents ask for.
    DEFAULT_MODEL_IDS: dict[str, ModelId] = {
        AiSettings.Model.HAIKU.value: ModelId("anthropic", "claude-haiku-4-5"),
        AiSettings.Model.OPUS.value: ModelId("anthropic", "claude-opus-4-6"),
    }

    # What we know how to serve from Vertex. Providers name their credentials
    # differently, so each gets an entry rather than one call that happens to
    # fit: this registry is what adding a provider costs.
    PROVIDERS: dict[str, Callable[[], Provider]] = {
        "anthropic": _vertex_anthropic,
        "google-cloud": _vertex_google,
        "openai-chat": _vertex_openai,
    }

    # genai_prices prices managed models by the Vertex backend they really run
    # on, rather than by the provider that defines them.
    PRICING_PROVIDER = "google-vertex"

    @cached_property
    def model_ids(self) -> dict[str, ModelId]:
        return {
            **self._reachable(self.DEFAULT_MODEL_IDS),
            **self._reachable(managed_model_ids()),
        }

    def _reachable(self, model_ids: dict[str, ModelId]) -> dict[str, ModelId]:
        """Filters out models with non-supported providers
        (env var ASSISTANT_MANAGED_PROVIDERS contains our accepted providers)
        """
        reachable = {}
        for model, model_id in model_ids.items():
            if self.supports(model_id.provider):
                reachable[model] = model_id
            else:
                logger.error(
                    "Model %r is served by %r, which ASSISTANT_MANAGED_PROVIDERS "
                    "does not enable on this deployment; ignoring it",
                    model,
                    model_id.provider,
                )
        return reachable

    @cached_property
    def _enabled_providers(self) -> dict[str, Callable[[], Provider]]:
        """Provider factory filtering only the ones actually enabled in our managed backend."""
        enabled = enabled_managed_providers() or set(self.PROVIDERS)
        return {p: build for p, build in self.PROVIDERS.items() if p in enabled}

    def supports(self, provider: str) -> bool:
        return provider in self._enabled_providers

    def pricing_provider(self, model_id: ModelId) -> str:
        return self.PRICING_PROVIDER

    def _build_provider(self, provider: str) -> Provider:
        if not settings.VERTEX_PROJECT_ID:
            raise AssistantException(
                "VERTEX_PROJECT_ID is not configured; cannot use the managed provider."
            )
        return self._enabled_providers[provider]()


class BringYourOwnKeyBackend(ProviderBackend):
    """Models for the BYOK configured key for an organization."""

    # BYOK organizations pick their own model, so these are not ours to switch
    # from the environment the way managed ones are.
    MODEL_IDS: dict[str, dict[str, ModelId]] = {
        AiSettings.Provider.ANTHROPIC.value: {
            AiSettings.Model.HAIKU.value: ModelId("anthropic", "claude-haiku-4-5"),
            AiSettings.Model.OPUS.value: ModelId("anthropic", "claude-opus-4-6"),
            AiSettings.Model.SONNET.value: ModelId("anthropic", "claude-sonnet-4-6"),
        },
    }

    @property
    def model_ids(self) -> dict[str, ModelId]:
        return self.MODEL_IDS.get(self.ai_settings.provider, {})

    def supports(self, provider: str) -> bool:
        return provider == self.ai_settings.provider

    def pricing_provider(self, model_id: ModelId) -> str:
        return model_id.provider

    def _build_provider(self, provider: str) -> Provider:
        return infer_provider_class(provider)(api_key=self.ai_settings.api_key)


def backend_for(ai_settings: AiSettings) -> ProviderBackend:
    if ai_settings.provider == AiSettings.Provider.MANAGED:
        return ManagedBackend(ai_settings)
    return BringYourOwnKeyBackend(ai_settings)
