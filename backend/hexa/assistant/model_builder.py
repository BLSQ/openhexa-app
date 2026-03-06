from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings


def _build_anthropic(model_api_name: str, api_key: str) -> Model:
    return AnthropicModel(model_api_name, provider=AnthropicProvider(api_key=api_key))


# Maps each AiSettings.Provider value to a callable (model_api_name, api_key) -> Model.
# Register new providers here.
_PROVIDER_FACTORIES = {
    AiSettings.Provider.ANTHROPIC: _build_anthropic,
}


def get_api_name(model: AiSettings.Model) -> str:
    model_to_api = {
        AiSettings.Model.HAIKU: "claude-haiku-4-5-20251001",
        AiSettings.Model.OPUS: "claude-opus-4-6",
        AiSettings.Model.SONNET: "claude-sonnet-4-6",
    }
    return model_to_api.get(model)


class AiModelBuilder:
    def __init__(self):
        self._provider = None
        self._model_api_name = None
        self._api_key = None

    def provider(self, provider: str) -> "AiModelBuilder":
        self._provider = provider
        return self

    def model(self, model: AiSettings.Model) -> "AiModelBuilder":
        self._model_api_name = get_api_name(model)
        return self

    def api_key(self, api_key: str) -> "AiModelBuilder":
        self._api_key = api_key
        return self

    @classmethod
    def from_conversation(cls, conversation: Conversation) -> "AiModelBuilder":
        ai_settings: AiSettings = conversation.user.ai_settings_safe
        if not ai_settings.enabled:
            raise AssistantException("AI settings are not enabled")
        return (
            cls()
            .provider(
                ai_settings.provider
            )  # TODO what happens if user changes provider
            .model(conversation.model)
            .api_key(ai_settings.api_key)
        )

    def build(self) -> Model:
        factory = _PROVIDER_FACTORIES.get(self._provider)
        if not factory:
            raise ValueError(f"Unsupported AI provider: {self._provider!r}")
        return factory(self._model_api_name, self._api_key)
