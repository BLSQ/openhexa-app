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

# The managed provider runs Claude through Google Vertex AI and is configured by
# us, not the organization. Managed orgs only toggle the assistant on/off and
# never pick a model, so they always run on this default; any model stored on
# their AiSettings (e.g. left over from a previous bring-your-own-key provider)
# is ignored.
MANAGED_DEFAULT_MODEL = AiSettings.Model.OPUS

# Vertex exposes Claude under bare model ids, whereas the direct Anthropic API
# expects dated ids. Keep one map per provider so the same logical model resolves
# to the right id for each backend. The managed (Vertex) map only needs
# MANAGED_DEFAULT_MODEL, since that is the only model managed orgs ever run.
_DIRECT_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.HAIKU.value: "claude-haiku-4-5-20251001",
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
    AiSettings.Model.SONNET.value: "claude-sonnet-4-6",
}

_VERTEX_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
}

_MODEL_IDS_BY_PROVIDER: dict[str, dict[str, str]] = {
    AiSettings.Provider.ANTHROPIC.value: _DIRECT_ANTHROPIC_MODEL_IDS,
    AiSettings.Provider.MANAGED.value: _VERTEX_ANTHROPIC_MODEL_IDS,
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
        if ai_settings.provider == AiSettings.Provider.MANAGED:
            # We control the model for managed orgs; ignore any stored value.
            model = MANAGED_DEFAULT_MODEL
        else:
            model = ai_settings.model
        self._model_api_name = get_api_name(ai_settings.provider, model)

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> "AiModelBuilder":
        organization = conversation.workspace.organization
        ai_settings: AiSettings = organization.ai_settings_safe
        if not ai_settings.enabled:
            raise AssistantException("AI settings are not enabled")
        return cls(ai_settings)

    @property
    def model_api_name(self) -> str | None:
        return self._model_api_name

    @property
    def provider_id(self) -> str | None:
        return self._ai_settings.provider

    def build(self) -> BuiltModel:
        factory = _PROVIDER_FACTORIES.get(self._ai_settings.provider)
        if not factory:
            raise ValueError(f"Unsupported AI provider: {self._ai_settings.provider!r}")
        model = factory(self._ai_settings, self._model_api_name)
        return BuiltModel(
            model=model,
            api_name=self._model_api_name,
            provider_id=self._ai_settings.provider,
        )
