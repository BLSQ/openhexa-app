"""Decides which model each agent runs on.

Every agent declares an `AgentKey` and, optionally, a `default_model`; the model
it actually runs on is, in order of precedence: the entry for its key in the
ASSISTANT_AGENT_MODELS setting, its own default, then the model the organization
configured. A logical model (e.g. "haiku") is resolved by the organization's
backend, while a model id (e.g. "google-cloud:gemini-3-pro-preview") is taken as
it stands — the only way to put one agent on a different provider than the rest.
"""

import logging
from functools import cached_property

from hexa.assistant.ai_models.backends import ProviderBackend
from hexa.assistant.ai_models.config import agent_model_requests
from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.exceptions import AssistantException

logger = logging.getLogger(__name__)


class ModelSelector:
    """Picks model ids for one organization; building them is the builder's job."""

    def __init__(self, backend: ProviderBackend):
        self._backend = backend

    @cached_property
    def _pins(self) -> dict[str, ModelRequest]:
        return agent_model_requests()

    def for_organization(self) -> ModelId:
        """Model id the organization's own conversations run on."""
        ai_settings = self._backend.ai_settings
        model_id = self._backend.model_ids.get(ai_settings.effective_model)
        if model_id is None:
            raise AssistantException(
                f"No model id configured for {ai_settings.effective_model!r} on "
                f"provider {ai_settings.provider!r}"
            )
        return model_id

    def for_agent(self, agent_key: str, default_model: ModelRequest | None) -> ModelId:
        """Model id `agent_key` runs on for this organization.

        A model the organization cannot run is a gap in our own configuration or
        a bad pin rather than a user misconfiguration, so we fall back to the
        organization's model: losing the intended model beats breaking the
        assistant.
        """
        requested = self._pins.get(agent_key, default_model)
        if requested is None:
            return self.for_organization()
        return self._runnable(requested, agent_key) or self.for_organization()

    def _runnable(self, requested: ModelRequest, agent_key: str) -> ModelId | None:
        """`requested` as a model id this organization can run, or None with a reason."""
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
