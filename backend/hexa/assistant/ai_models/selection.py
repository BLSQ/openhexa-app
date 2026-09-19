"""Decides which model each agent runs on.

Every agent declares an `AgentKey` and, optionally, a `default_model`;
the model it runs on is, in order of precedence for managed backends:
- env configured agent key
- env configured default
- agent default in code
- generic default in code
And for BYOK backends:
- UI choice
- agent default in code
- generic default in code
A logical model (e.g. "haiku") is resolved by the provider backend,
while a model id (e.g. "google-cloud:gemini-3-pro-preview") is taken as it comes.
"""

import logging
from functools import cached_property

from hexa.assistant.ai_models.backends import ProviderBackend
from hexa.assistant.ai_models.config import DEFAULT_KEY
from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.exceptions import AssistantException

logger = logging.getLogger(__name__)


class ModelSelector:
    """Picks model ids for an organization; then builder builds them."""

    def __init__(self, backend: ProviderBackend):
        self._backend = backend

    @cached_property
    def _overrides(self) -> dict[str, ModelRequest]:
        return self._backend.configured_agent_models()

    def for_organization(self) -> ModelId:
        """Default model id for the organization's agent conversations."""
        requested = self._overrides.get(DEFAULT_KEY)
        overridden = self._runnable(requested, DEFAULT_KEY) if requested else None
        return overridden or self._default_model()

    def for_agent(self, agent_key: str, default_model: ModelRequest | None) -> ModelId:
        """Model id for each `agent_key`.

        An agent model we cannot run is a gap in our config or a bad override,
        so we fall back to the organization's default model: we rather use the
        wrong model than breaking the assistant.
        """
        requested = self._overrides.get(agent_key, default_model)
        if requested is None:
            return self.for_organization()
        return self._runnable(requested, agent_key) or self.for_organization()

    def _default_model(self) -> ModelId:
        """Model id for the logical model default."""
        ai_settings = self._backend.ai_settings
        model_id = self._backend.model_ids.get(ai_settings.effective_model)
        if model_id is None:
            raise AssistantException(
                f"No model id configured for {ai_settings.effective_model!r} on "
                f"provider {ai_settings.provider!r}"
            )
        return model_id

    def _runnable(self, requested: ModelRequest, agent_key: str) -> ModelId | None:
        """`requested`: model id this organization can run, or None with a reason."""
        ai_settings = self._backend.ai_settings
        model_id = (
            requested
            if isinstance(requested, ModelId)
            else self._backend.model_ids.get(requested)
        )
        if model_id is None:
            logger.error(
                "Provider %r has no model id for %r requested by agent %r; "
                "falling back to the organization's model",
                ai_settings.provider,
                requested,
                agent_key,
            )
            return None
        if not self._backend.supports(model_id.provider):
            logger.error(
                "Agent %r requested %r, which %r organizations hold no credentials "
                "for; falling back to the organization's model",
                agent_key,
                str(model_id),
                ai_settings.provider,
            )
            return None
        return model_id
