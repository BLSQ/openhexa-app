"""Reads the model configuration a deployment sets in its environment.

These settings are free-form text an operator edits, so nothing here raises: an
entry we cannot make sense of is dropped with an error and the code defaults
apply. A typo must never take the assistant down.
"""

import json
import logging
from dataclasses import replace

from django.conf import settings

from hexa.assistant.ai_models.ids import ModelId, ModelRequest
from hexa.assistant.keys import AgentKey
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)

# Default key for config agent models. If unset, fallbacks to the model in the default key
DEFAULT_KEY = "default"

MODEL_OBJECT_KEYS = {"model", "region"}


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


def _model_request(value: object) -> ModelRequest:
    """`value` as a model request, or raise.

    A string is a logical model or a model id. An object is a model id pinned to
    the region that serves it: {"model": "<provider>:<model>", "region": "eu"}.
    """
    if not isinstance(value, dict):
        return ModelId.parse(value) or _logical_model(value)
    unknown = set(value) - MODEL_OBJECT_KEYS
    if unknown:
        # A misspelled "region" would otherwise silently run in the default one.
        raise ValueError(f"unknown keys {sorted(unknown)}")
    return replace(ModelId.parse(value["model"]), region=value.get("region"))


def _override_key(value: str) -> str:
    """Config key for `value`. It can be an agent key or the default key."""
    return DEFAULT_KEY if value == DEFAULT_KEY else AgentKey(value).value


def managed_agent_models() -> dict[str, ModelRequest]:
    """Agent key -> model set via env config.

    The model is either a logical model (from the available ones in AI settings),
    or a `ModelId`, optionally pinned to a region.
    """
    overrides: dict[str, ModelRequest] = {}
    setting = "ASSISTANT_MANAGED_AGENT_MODELS"
    for key, value in _json_object(
        settings.ASSISTANT_MANAGED_AGENT_MODELS, setting
    ).items():
        try:
            overrides[_override_key(key)] = _model_request(value)
        except Exception as exc:
            logger.error("%s: ignoring entry %r -> %r (%s)", setting, key, value, exc)
    return overrides
