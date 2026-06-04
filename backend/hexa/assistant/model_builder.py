from typing import Callable, NamedTuple

from anthropic.lib.vertex import AsyncAnthropicVertex
from django.conf import settings
from pydantic_ai.models import Model as PydanticModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings


class BuiltModel(NamedTuple):
    model: PydanticModel
    api_name: str
    provider_id: str


_DIRECT_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.HAIKU.value: "claude-haiku-4-5-20251001",
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
    AiSettings.Model.SONNET.value: "claude-sonnet-4-6",
}

_VERTEX_ANTHROPIC_MODEL_IDS: dict[str, str] = {
    AiSettings.Model.HAIKU.value: "claude-haiku-4-5",
    AiSettings.Model.OPUS.value: "claude-opus-4-6",
    AiSettings.Model.SONNET.value: "claude-sonnet-4-6",
}

_MODEL_IDS_BY_PROVIDER: dict[str, dict[str, str]] = {
    AiSettings.Provider.ANTHROPIC.value: _DIRECT_ANTHROPIC_MODEL_IDS,
    AiSettings.Provider.ANTHROPIC_VERTEX.value: _VERTEX_ANTHROPIC_MODEL_IDS,
}


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


def _build_anthropic_vertex(
    ai_settings: AiSettings, model_api_name: str
) -> PydanticModel:
    if not settings.VERTEX_PROJECT_ID:
        raise AssistantException(
            "VERTEX_PROJECT_ID is not configured; cannot use the Vertex provider."
        )
    client = AsyncAnthropicVertex(
        project_id=settings.VERTEX_PROJECT_ID,
        region=settings.VERTEX_REGION,
    )
    return AnthropicModel(
        model_api_name, provider=AnthropicProvider(anthropic_client=client)
    )


_PROVIDER_FACTORIES: dict[str, Callable[[AiSettings, str], PydanticModel]] = {
    AiSettings.Provider.ANTHROPIC.value: _build_anthropic,
    AiSettings.Provider.ANTHROPIC_VERTEX.value: _build_anthropic_vertex,
}


class AiModelBuilder:
    def __init__(self, ai_settings: AiSettings):
        self._ai_settings = ai_settings
        self._model_api_name = get_api_name(ai_settings.provider, ai_settings.model)

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> "AiModelBuilder":
        ai_settings: AiSettings = conversation.user.ai_settings_safe
        if not ai_settings.enabled:
            raise AssistantException("AI settings are not enabled")
        return cls(ai_settings=ai_settings)

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
