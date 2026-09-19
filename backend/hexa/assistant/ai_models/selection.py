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
A logical model (e.g. "haiku") is resolved by the provider backend,
while a model id (e.g. "google-cloud:gemini-3-pro-preview") is taken as it comes.
"""

import logging

from hexa.assistant.ai_models.backends import ProviderBackend
from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.exceptions import AssistantException

logger = logging.getLogger(__name__)


class ModelSelector:
    """Picks model ids for an organization; then builder builds them."""

    def __init__(self, backend: ProviderBackend):
        self._backend = backend

    def for_agent(self, agent_key: str, default_model: ModelRequest | None) -> ModelId:
        """Model id for each `agent_key`: the first candidate we can actually run.

        A candidate we cannot run is a gap in our config or a bad override, so we
        move on to the next one: we rather use the wrong model than break the
        assistant.
        """
        for requested in self._backend.model_candidates(agent_key, default_model):
            if requested is None:
                continue
            model_id = self._runnable(requested, agent_key)
            if model_id is not None:
                return model_id
        raise AssistantException(
            f"No model {self._backend.ai_settings.provider!r} organizations can run "
            f"is configured for agent {agent_key!r}"
        )

    def _runnable(self, requested: ModelRequest, agent_key: str) -> ModelId | None:
        """`requested` as a model id this organization can run, or None with a reason."""
        ai_settings = self._backend.ai_settings
        model_id = (
            requested
            if isinstance(requested, ModelId)
            else self._backend.model_ids.get(requested)
        )
        if model_id is None:
            logger.warning(
                "Provider %r has no model id for %r requested by agent %r; "
                "trying the next candidate",
                ai_settings.provider,
                requested,
                agent_key,
            )
            return None
        if not self._backend.supports(model_id.provider):
            logger.warning(
                "Agent %r requested %r, which %r organizations hold no credentials "
                "for; trying the next candidate",
                agent_key,
                str(model_id),
                ai_settings.provider,
            )
            return None
        return model_id
