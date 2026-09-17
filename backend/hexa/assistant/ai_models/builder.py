"""Turns a model id into a client an organization can run.

Models are named by their pydantic-ai id, "<provider>:<model>", which is all
pydantic-ai needs to pick the right client; the organization's `ProviderBackend`
supplies the credentials the id cannot carry. Reaching for another model is
therefore a configuration change rather than a code one, and reaching for
another provider costs one entry in that backend's registry.
"""

import logging

from pydantic_ai import RunUsage
from pydantic_ai.models import infer_model

from hexa.assistant.ai_models.backends import backend_for
from hexa.assistant.ai_models.built_model import BuiltModel
from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.ai_models.selection import ModelSelector
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import Conversation
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


class AiModelBuilder:
    """Builds the models an organization's AI settings allow.

    It knows how to turn a model id into a usable client, and delegates the two
    questions around that: which models exist and what pays for them to the
    organization's `ProviderBackend`, and who gets which model to `ModelSelector`.
    """

    def __init__(self, ai_settings: AiSettings):
        self._ai_settings = ai_settings
        self._backend = backend_for(ai_settings)
        self._selector = ModelSelector(self._backend)

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
    def ai_settings(self) -> AiSettings:
        return self._ai_settings

    def build_for_agent(
        self, agent_key: str, default_model: ModelRequest | None
    ) -> BuiltModel:
        """The model an agent runs on, selected and then built."""
        return self.build(self._selector.for_agent(agent_key, default_model))

    def build(self, model_id: ModelId) -> BuiltModel:
        """Build `model_id` with this organization's credentials."""
        name = str(model_id)
        try:
            model = infer_model(name, provider_factory=self._backend.provider_for)
        except AssistantException:
            raise
        except Exception as exc:
            # Model ids are free-form configuration: an unknown provider, or one
            # whose optional dependency is not installed, only shows up here.
            raise AssistantException(f"Cannot build model {name!r}: {exc}") from exc

        built = BuiltModel(
            model=model,
            api_name=model.model_name,
            provider_id=self._backend.pricing_provider(model_id),
        )
        # Usage we cannot price never counts towards the organization's budget,
        # so an unpriceable model would run uncapped. Refuse it while the only
        # thing at stake is a configuration error.
        if built.calculate_cost(RunUsage()) is None:
            raise AssistantException(
                f"No known price for {name!r}; refusing to run a model whose "
                f"spend cannot be capped"
            )
        return built
