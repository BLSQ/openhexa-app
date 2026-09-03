import logging
from collections.abc import Callable
from typing import NamedTuple

from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from pydantic_ai.models import Model as PydanticModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)

# Small "utility agents" such as conversation naming do not need the
# organization's main model, so they run on this cheaper one. Every provider map
# below must expose it (a unit test enforces this).
UTILITY_MODEL = AiSettings.Model.HAIKU

# Vertex exposes Claude under bare model ids, whereas the direct Anthropic API
# expects dated ids. Keep one map per provider so the same logical model resolves
# to the right id for each backend. The managed (Vertex) map only needs
# AiSettings.MANAGED_MODEL, the model managed orgs run their conversations on,
# plus UTILITY_MODEL.
_DIRECT_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.HAIKU.value: "claude-haiku-4-5-20251001",
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
    AiSettings.Model.SONNET.value: "claude-sonnet-4-6",
}

_VERTEX_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.HAIKU.value: "claude-haiku-4-5",
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
}

_MODEL_IDS_BY_PROVIDER: dict[str, dict[str, str]] = {
    AiSettings.Provider.ANTHROPIC.value: _DIRECT_ANTHROPIC_MODEL_IDS,
    AiSettings.Provider.MANAGED.value: _VERTEX_ANTHROPIC_MODEL_IDS,
}

# genai_prices knows the managed provider as the Google Vertex backend it really
# runs on, not by our internal "managed" value.
_PRICING_PROVIDER_IDS: dict[str, str] = {
    AiSettings.Provider.MANAGED.value: "google-vertex",
}


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str


def get_api_name(provider: str, model: str) -> str:
    model_to_api = _MODEL_IDS_BY_PROVIDER.get(provider)
    if model_to_api is None:
        raise AssistantException(f"Unsupported AI provider: {provider!r}")

    model_api_name = model_to_api.get(model)
    if model_api_name is None:
        raise AssistantException(
            f"Model {model} is not known for provider {provider}. "
            f"Accepted models are {[*model_to_api]}"
        )
    return model_api_name


def utility_model_for(ai_settings: AiSettings) -> str:
    """Logical model utility agents run on for this organization.

    Falls back to the organization's main model when the provider exposes no id
    for UTILITY_MODEL: that is a bug in the maps above rather than a
    misconfiguration, and losing the cost saving beats breaking the assistant.
    """
    if UTILITY_MODEL in _MODEL_IDS_BY_PROVIDER.get(ai_settings.provider, {}):
        return UTILITY_MODEL
    logger.error(
        "Provider %r exposes no id for the utility model %r; "
        "utility agents will run on the main model",
        ai_settings.provider,
        UTILITY_MODEL.value,
    )
    return ai_settings.effective_model


def _build_anthropic(ai_settings: AiSettings, model_api_name: str) -> PydanticModel:
    return AnthropicModel(
        model_api_name, provider=AnthropicProvider(api_key=ai_settings.api_key)
    )


def _build_managed(ai_settings: AiSettings, model_api_name: str) -> PydanticModel:
    if not settings.VERTEX_PROJECT_ID:
        raise AssistantException(
            "VERTEX_PROJECT_ID is not configured; cannot use the managed provider."
        )
    client = AsyncAnthropicVertex(
        project_id=settings.VERTEX_PROJECT_ID,
        region=settings.VERTEX_REGION,
    )
    return AnthropicModel(
        model_api_name, provider=AnthropicProvider(anthropic_client=client)
    )


# Maps each AiSettings.Provider value to a callable (ai_settings, model_api_name) -> Model.
# Register new providers here.
_PROVIDER_FACTORIES: dict[str, Callable[[AiSettings, str], PydanticModel]] = {
    AiSettings.Provider.ANTHROPIC.value: _build_anthropic,
    AiSettings.Provider.MANAGED.value: _build_managed,
}


class AiModelBuilder:
    def __init__(self, ai_settings: AiSettings):
        self._ai_settings = ai_settings

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> "AiModelBuilder":
        organization = conversation.workspace.organization
        if organization is None:
            raise AssistantException(
                "Workspace does not belong to an organization; the assistant is unavailable"
            )
        ai_settings: AiSettings = organization.ai_settings_safe
        if not ai_settings.enabled:
            raise AssistantException("AI settings are not enabled")
        return cls(ai_settings)

    def build(self, model: str | None = None) -> BuiltModel:
        """Build `model` (an AiSettings.Model value), defaulting to the org's own."""
        provider = self._ai_settings.provider
        factory = _PROVIDER_FACTORIES.get(provider)
        if not factory:
            raise AssistantException(f"Unsupported AI provider: {provider!r}")

        model_api_name = get_api_name(
            provider, model or self._ai_settings.effective_model
        )
        return BuiltModel(
            model=factory(self._ai_settings, model_api_name),
            api_name=model_api_name,
            provider_id=_PRICING_PROVIDER_IDS.get(provider, provider),
        )

    def build_utility(self) -> BuiltModel:
        return self.build(utility_model_for(self._ai_settings))
