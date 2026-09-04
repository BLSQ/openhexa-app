import json
import logging
from collections.abc import Iterable

from django.conf import settings

from hexa.assistant.model_builder import AiModelBuilder, BuiltModel, supports
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


def _overrides() -> dict[str, str]:
    """Agent key -> logical model, parsed from ASSISTANT_AGENT_MODELS.

    Misconfiguration must never take the assistant down, so anything we cannot
    make sense of is dropped with an error and the code defaults apply. Parsed on
    every call rather than cached: it is a handful of keys, and caching would
    make the setting impossible to change without a restart.
    """
    raw = settings.ASSISTANT_AGENT_MODELS
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except ValueError:
        logger.error("ASSISTANT_AGENT_MODELS is not valid JSON; ignoring it")
        return {}
    if not isinstance(parsed, dict):
        logger.error("ASSISTANT_AGENT_MODELS must be a JSON object; ignoring it")
        return {}

    known_models = {model.value for model in AiSettings.Model}
    overrides = {}
    for agent_key, model in parsed.items():
        if model not in known_models:
            logger.error(
                "ASSISTANT_AGENT_MODELS: %r is not a known model (accepted: %s); "
                "ignoring the override for agent %r",
                model,
                sorted(known_models),
                agent_key,
            )
            continue
        overrides[str(agent_key)] = model
    return overrides


def warn_on_unknown_overrides(pinnable_agent_keys: Iterable[str]) -> None:
    """Log the ASSISTANT_AGENT_MODELS entries that will never apply.

    An entry for an agent that has not opted in is inert, which makes a typo
    look exactly like a working configuration. Called at startup so the mistake
    surfaces then rather than in a month of unchanged bills.
    """
    pinnable = set(pinnable_agent_keys)
    for agent_key in _overrides():
        if agent_key not in pinnable:
            logger.error(
                "ASSISTANT_AGENT_MODELS: %r is not an agent whose model can be "
                "pinned; the entry has no effect. Pinnable agents are %s",
                agent_key,
                sorted(pinnable),
            )


def resolve_model(
    ai_settings: AiSettings, agent_key: str | None, default_model: str | None
) -> str:
    """Logical model an agent runs on for this organization.

    `agent_key` is None for agents that run on whatever model the organization
    chose. Only agents that opt in by declaring a key can be pinned from the
    environment, so a stray entry can never quietly downgrade an organization's
    main assistant.

    A model the organization's provider does not expose is a gap in our own maps
    or a bad override rather than a user misconfiguration, so we fall back to the
    organization's model: losing the intended model beats breaking the assistant.
    """
    requested = _overrides().get(agent_key, default_model) if agent_key else None
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
    builder: AiModelBuilder, agent_key: str | None, default_model: str | None
) -> BuiltModel:
    return builder.build(resolve_model(builder.ai_settings, agent_key, default_model))
