"""Reads the model configuration a deployment sets in its environment.

These settings are free-form text an operator edits, so nothing here raises: an
entry we cannot make sense of is dropped with an error and the code defaults
apply. A typo must never take the assistant down.
"""

import json
import logging

from django.conf import settings

from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.keys import AgentKey
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)

# Default key for config agent models. If unset, fallbacks to the model in the default key
DEFAULT_KEY = "default"


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


def _override_key(value: str) -> str:
    """Config key for `value`. It can be an agent key or the default key."""
    return DEFAULT_KEY if value == DEFAULT_KEY else AgentKey(value).value


def managed_agent_models() -> dict[str, ModelRequest]:
    """Agent key -> model set via env config.

    The model is either a logical model (from the available ones in AI settings),
    or a `ModelId`.
    """
    overrides: dict[str, ModelRequest] = {}
    setting = "ASSISTANT_MANAGED_AGENT_MODELS"
    for key, value in _json_object(
        settings.ASSISTANT_MANAGED_AGENT_MODELS, setting
    ).items():
        try:
            overrides[_override_key(key)] = ModelId.parse(value) or _logical_model(
                value
            )
        except Exception as exc:
            logger.error("%s: ignoring entry %r -> %r (%s)", setting, key, value, exc)
    return overrides
