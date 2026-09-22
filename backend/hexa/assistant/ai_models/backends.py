"""Where an organization's models come from: our own Vertex project, or its key.
Each subclass has the logic specific to the provider backend (managed or BYOK)
"""

from abc import ABC, abstractmethod

from django.conf import settings
from pydantic_ai.providers import Provider, infer_provider_class

from hexa.assistant.ai_models.config import DEFAULT_KEY, managed_agent_models
from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.ai_models.vertex import PROVIDERS
from hexa.assistant.exceptions import AssistantException
from hexa.user_management.models import AiSettings


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

    @abstractmethod
    def model_candidates(
        self, agent_key: str, default_model: ModelRequest | None
    ) -> list[ModelRequest | None]:
        """Models to try for `agent_key`, in order of precedence."""

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

    # Managed provider default model. If unset in env config and agent
    # doesn't have default, it fallbacks to this one.
    # Logical rather than a model id, later selected by DEFAULT_MODEL_IDS.
    DEFAULT_MODEL = AiSettings.Model.OPUS

    # Default models to run for preset AI settings model.
    # Right now based on our Vertex available models.
    DEFAULT_MODEL_IDS: dict[str, ModelId] = {
        AiSettings.Model.HAIKU.value: ModelId("anthropic", "claude-haiku-4-5"),
        AiSettings.Model.OPUS.value: ModelId("anthropic", "claude-opus-4-6"),
    }

    # genai_prices prices managed models by the Vertex backend they really run
    # on, rather than by the provider that defines them.
    PRICING_PROVIDER = "google-vertex"

    @property
    def model_ids(self) -> dict[str, ModelId]:
        return self.DEFAULT_MODEL_IDS

    def configured_agent_models(self) -> dict[str, ModelRequest]:
        """Environment configuration of agents -> model."""
        return managed_agent_models()

    def model_candidates(
        self, agent_key: str, default_model: ModelRequest | None
    ) -> list[ModelRequest | None]:
        configured = self.configured_agent_models()
        return [
            configured.get(agent_key),
            configured.get(DEFAULT_KEY),
            default_model,
            self.DEFAULT_MODEL,
        ]

    def supports(self, provider: str) -> bool:
        return provider in PROVIDERS

    def pricing_provider(self, model_id: ModelId) -> str:
        return self.PRICING_PROVIDER

    def _build_provider(self, provider: str) -> Provider:
        if not settings.VERTEX_PROJECT_ID:
            raise AssistantException(
                "VERTEX_PROJECT_ID is not configured; cannot use the managed provider."
            )
        return PROVIDERS[provider]()


class BringYourOwnKeyBackend(ProviderBackend):
    """Models for the BYOK configured key for an organization."""

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

    def model_candidates(
        self, agent_key: str, default_model: ModelRequest | None
    ) -> list[ModelRequest | None]:
        """The model the organization chose in the UI comes first: it is theirs,
        and it runs on their key.
        """
        return [self.ai_settings.model, default_model]

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
