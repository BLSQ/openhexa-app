"""Where an organization's models come from: our own Vertex project, or its key.

Managed organizations run on models we serve and pay for; everyone else brings a
key for the single provider they configured. Everything that differs between the
two — which logical models exist, which providers are reachable, how credentials
are built, how usage is priced — lives in one subclass each, so the rest of the
assistant never has to ask which kind of organization it is holding.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import cached_property

from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from pydantic_ai.providers import Provider, infer_provider_class
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

from hexa.assistant.ai_models.config import enabled_managed_providers, managed_model_ids
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


class ProviderBackend(ABC):
    """The models an organization can run, and the credentials to run them.

    Instances are cheap and short-lived — one per `AiModelBuilder`, so per
    request — which is what lets them cache the environment they read.
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
        """The provider genai_prices knows this model by."""

    @abstractmethod
    def _build_provider(self, provider: str) -> Provider:
        """Credentials for `provider`, which `supports` has already allowed."""

    def provider_for(self, provider: str) -> Provider:
        """Credentials for `provider`, as pydantic-ai's `provider_factory`."""
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
    }

    # genai_prices prices managed models by the Vertex backend they really run
    # on, rather than by the provider that defines them.
    PRICING_PROVIDER = "google-vertex"

    @cached_property
    def model_ids(self) -> dict[str, ModelId]:
        return {**self.DEFAULT_MODEL_IDS, **managed_model_ids()}

    @cached_property
    def _enabled_providers(self) -> dict[str, Callable[[], Provider]]:
        """The entries of the registry this deployment may actually use.

        A publisher has to be enabled on a Vertex project before it answers,
        which staging and production do not agree on, so the setting narrows what
        we know how to build down to what is really there. It only ever narrows:
        naming a provider we have no wiring for does not conjure credentials.
        """
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
    """Models the organization runs on the key it brought, for its one provider."""

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
