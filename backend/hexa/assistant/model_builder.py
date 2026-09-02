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

# The managed provider runs Claude through Google Vertex AI and is configured by
# us, not the organization. Managed orgs only toggle the assistant on/off and
# never pick a model, so they always run on this default; any model stored on
# their AiSettings (e.g. left over from a previous bring-your-own-key provider)
# is ignored.
MANAGED_DEFAULT_MODEL = AiSettings.Model.OPUS

# Vertex exposes Claude under bare model ids, whereas the direct Anthropic API
# expects dated ids. Keep one map per provider so the same logical model resolves
# to the right id for each backend. The managed (Vertex) map needs
# MANAGED_DEFAULT_MODEL, the only model managed orgs run their conversations on,
# plus any model reachable as a utility model (see build_utility).
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
        if organization is None:
            raise AssistantException(
                "Workspace does not belong to an organization; the assistant is unavailable"
            )
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

    def _build(self, model_api_name: str) -> BuiltModel:
        factory = _PROVIDER_FACTORIES.get(self._ai_settings.provider)
        if not factory:
            raise ValueError(f"Unsupported AI provider: {self._ai_settings.provider!r}")
        model = factory(self._ai_settings, model_api_name)
        # The managed provider runs Claude through Google Vertex AI, so genai_prices
        # must price it as "google-vertex" rather than our internal "managed" value.
        if self._ai_settings.provider == AiSettings.Provider.MANAGED:
            provider_id = "google-vertex"
        else:
            provider_id = self._ai_settings.provider
        return BuiltModel(
            model=model,
            api_name=model_api_name,
            provider_id=provider_id,
        )

    def build(self) -> BuiltModel:
        return self._build(self._model_api_name)

    def build_utility(self, model: str | None = None) -> BuiltModel:
        """Cheap model for small utility agents such as conversation naming.

        Returns the organization's main model when the optimization is disabled
        or when the provider exposes no id for the utility model, so enabling it
        for a provider later is a one-line addition to that provider's id map.

        `model` overrides ASSISTANT_UTILITY_MODEL for a single build, which lets
        callers compare models without changing the deployed setting.
        """
        utility_model = model or settings.ASSISTANT_UTILITY_MODEL
        if not utility_model:
            return self.build()
        if utility_model not in AiSettings.Model.values:
            # A typo would otherwise be indistinguishable from a model that is
            # legitimately unmapped for this provider.
            logger.warning(
                "ASSISTANT_UTILITY_MODEL=%r is not a known model; "
                "utility agents will run on the main model",
                utility_model,
            )
            return self.build()
        try:
            model_api_name = get_api_name(self._ai_settings.provider, utility_model)
        except AssistantException:
            return self.build()
        return self._build(model_api_name)
