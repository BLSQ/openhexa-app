"""Reads the model configuration a deployment sets in its environment.

These settings are free-form text an operator edits, so nothing here raises: an
entry we cannot make sense of is dropped with an error and the code defaults
apply. A typo must never take the assistant down, nor undo the entries set
alongside it — which may well be the deliberate ones.
"""

import json
import logging

from django.conf import settings

from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.keys import AgentKey
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)


def _json_object(raw: str, name: str) -> dict:
    """The JSON object in `raw`, or an empty one if it cannot be read."""
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except Exception:
        value = None
    if not isinstance(value, dict):
        logger.error("%s is not a JSON object; ignoring it: %r", name, raw)
        return {}
    return value


def _logical_model(value: object) -> str:
    """`value` as one of the logical models we know, or raise."""
    return AiSettings.Model(value).value


def managed_model_ids() -> dict[str, ModelId]:
    """Logical model -> model id, from ASSISTANT_MANAGED_MODELS.

    Only the entries the setting names: the managed backend merges them over its
    own defaults, so anything left out keeps the model it ships with.
    """
    overrides: dict[str, ModelId] = {}
    for model, value in _json_object(
        settings.ASSISTANT_MANAGED_MODELS, "ASSISTANT_MANAGED_MODELS"
    ).items():
        try:
            logical = _logical_model(model)
            model_id = ModelId.parse(value)
            if model_id is None:
                raise ValueError(f"{value!r} is not a '<provider>:<model>' id")
        except Exception as exc:
            logger.error(
                "ASSISTANT_MANAGED_MODELS: ignoring entry %r -> %r (%s)",
                model,
                value,
                exc,
            )
            continue
        overrides[logical] = model_id
    return overrides


def agent_model_requests() -> dict[str, ModelRequest]:
    """Agent key -> the model it is pinned to, from ASSISTANT_AGENT_MODELS.

    A pin is either a logical model, resolved for the organization's provider, or
    a model id of its own — the only way to put one agent on a different provider
    than the rest.
    """
    pins: dict[str, ModelRequest] = {}
    for key, value in _json_object(
        settings.ASSISTANT_AGENT_MODELS, "ASSISTANT_AGENT_MODELS"
    ).items():
        try:
            agent = AgentKey(key).value
            pins[agent] = ModelId.parse(value) or _logical_model(value)
        except Exception as exc:
            logger.error(
                "ASSISTANT_AGENT_MODELS: ignoring entry %r -> %r (%s)", key, value, exc
            )
    return pins


def enabled_managed_providers() -> set[str]:
    """Providers ASSISTANT_MANAGED_PROVIDERS narrows the managed backend to.

    Empty means no narrowing: the backend then serves everything it knows how to
    build.
    """
    configured = settings.ASSISTANT_MANAGED_PROVIDERS.replace(" ", "").split(",")
    return set(filter(None, configured))
