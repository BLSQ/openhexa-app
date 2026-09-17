"""Where an organization's models come from: our own Vertex project, or its key.
Each subclass has the logic specific to the provider backend (managed or BYOK)
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import cached_property

from django.conf import settings
from pydantic_ai.providers import Provider, infer_provider_class

from hexa.assistant.ai_models.config import enabled_managed_providers, managed_model_ids
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.ai_models.vertex import PROVIDERS
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


class ManagedBackend(ProviderBackend):
    """Models served from our own Vertex project, on our own account."""

    # What our Vertex project runs managed organizations on, overridden entry by
    # entry from ASSISTANT_MANAGED_MODELS. It only needs the models agents ask for.
    DEFAULT_MODEL_IDS: dict[str, ModelId] = {
        AiSettings.Model.HAIKU.value: ModelId("anthropic", "claude-haiku-4-5"),
        AiSettings.Model.OPUS.value: ModelId("anthropic", "claude-opus-4-6"),
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
        enabled = enabled_managed_providers() or set(PROVIDERS)
        return {p: build for p, build in PROVIDERS.items() if p in enabled}

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
