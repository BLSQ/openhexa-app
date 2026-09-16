"""Decides which model each agent runs on.

Every agent declares an `AgentKey` and, optionally, a `default_model`; the model
it actually runs on is, in order of precedence: the entry for its key in the
ASSISTANT_AGENT_MODELS setting, its own default, then the model the organization
configured. Setting ASSISTANT_AGENT_MODELS to a JSON object of agent key to model
(e.g. {"naming": "haiku", "generate_sql": "sonnet"}) therefore retunes any agent
without a deploy; emptying an entry reverts it to the code default.
"""

import json
import logging

from django.conf import settings

from hexa.assistant.agents.keys import AgentKey
from hexa.assistant.model_builder import AiModelBuilder, BuiltModel, supports
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


def _overrides() -> dict[str, str]:
    """Agent key -> logical model, parsed from ASSISTANT_AGENT_MODELS.

    A misconfiguration must never take the assistant down, so an unusable
    setting is dropped whole and the code defaults apply. Dropped whole rather
    than entry by entry: a typo that reverts every agent is noticed, one that
    silently ignores a single line looks exactly like a working configuration.
    """
    raw = settings.ASSISTANT_AGENT_MODELS
    if not raw:
        return {}
    try:
        return {
            AgentKey(key).value: AiSettings.Model(model).value
            for key, model in json.loads(raw).items()
        }
    except Exception:
        logger.error(
            "ASSISTANT_AGENT_MODELS is not a JSON object mapping an agent key (%s) "
            "to a model (%s); ignoring it: %r",
            sorted(AgentKey.values),
            sorted(AiSettings.Model.values),
            raw,
        )
        return {}


def resolve_model(
    ai_settings: AiSettings, agent_key: str, default_model: str | None
) -> str:
    """Logical model an agent runs on for this organization.

    A model the organization's provider does not expose is a gap in our own maps
    or a bad override rather than a user misconfiguration, so we fall back to the
    organization's model: losing the intended model beats breaking the assistant.
    """
    requested = _overrides().get(agent_key, default_model)
    if requested is None:
        return ai_settings.effective_model
    if supports(ai_settings.provider, requested):
        return requested
    logger.error(
        "Provider %r exposes no id for model %r requested by agent %r; "
        "falling back to the organization's model",
        ai_settings.provider,
        requested,
        agent_key,
    )
    return ai_settings.effective_model


def build_agent_model(
    builder: AiModelBuilder, agent_key: str, default_model: str | None
) -> BuiltModel:
    return builder.build(resolve_model(builder.ai_settings, agent_key, default_model))
