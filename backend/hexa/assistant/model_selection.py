"""Decides which model each agent runs on.

Models are named by their pydantic-ai id, "<provider>:<model>". ASSISTANT_MODELS
maps each provider's logical models (the ones organizations pick from) to such an
id, so moving everyone from one model — or one provider — to another is an env
change rather than a release.

Every agent declares an `AgentKey` and, optionally, a `default_model`; the model
it actually runs on is, in order of precedence: the entry for its key in the
ASSISTANT_AGENT_MODELS setting, its own default, then the model the organization
configured. An entry is either a logical model (e.g. "haiku"), resolved through
ASSISTANT_MODELS for the organization's provider, or a model id of its own
(e.g. "google-cloud:gemini-3-pro"), which is the only way to put one agent on a
different provider than the rest.
"""

import json
import logging

from django.conf import settings

from hexa.assistant.agents.keys import AgentKey
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.model_builder import (
    AiModelBuilder,
    BuiltModel,
    is_model_id,
    supports,
)
from hexa.user_management.models import AiSettings

logger = logging.getLogger(__name__)

# Model ids per provider, overridden entry by entry from ASSISTANT_MODELS. The
# managed map only needs the models we actually run managed organizations on.
_DEFAULT_MODELS: dict[str, dict[str, str]] = {
    AiSettings.Provider.MANAGED.value: {
        AiSettings.Model.HAIKU.value: "anthropic:claude-haiku-4-5",
        AiSettings.Model.OPUS.value: "anthropic:claude-opus-4-6",
    },
    AiSettings.Provider.ANTHROPIC.value: {
        AiSettings.Model.HAIKU.value: "anthropic:claude-haiku-4-5",
        AiSettings.Model.OPUS.value: "anthropic:claude-opus-4-6",
        AiSettings.Model.SONNET.value: "anthropic:claude-sonnet-4-6",
    },
}


def _json_object(raw: str, name: str) -> dict:
    """The JSON object in `raw`, or an empty one if it cannot be read.

    A misconfiguration must never take the assistant down, so anything we cannot
    make sense of is dropped with an error and the code defaults apply.
    """
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


def _models() -> dict[str, dict[str, str]]:
    """Provider -> logical model -> model id, ASSISTANT_MODELS over the defaults.

    Entries are merged one by one: a typo should not undo the models set
    alongside it, nor the defaults for everything left out.
    """
    models = {provider: dict(ids) for provider, ids in _DEFAULT_MODELS.items()}
    configured = _json_object(settings.ASSISTANT_MODELS, "ASSISTANT_MODELS")
    for provider, ids in configured.items():
        try:
            known_provider = AiSettings.Provider(provider).value
            if not isinstance(ids, dict):
                raise ValueError(f"{ids!r} is not an object of models")
        except Exception as exc:
            logger.error("ASSISTANT_MODELS: ignoring %r (%s)", provider, exc)
            continue
        for model, model_id in ids.items():
            try:
                if not isinstance(model_id, str) or not is_model_id(model_id):
                    raise ValueError(f"{model_id!r} is not a '<provider>:<model>' id")
                models[known_provider][AiSettings.Model(model).value] = model_id
            except Exception as exc:
                logger.error(
                    "ASSISTANT_MODELS: ignoring entry %r -> %r -> %r (%s)",
                    provider,
                    model,
                    model_id,
                    exc,
                )
    return models


def _pins() -> dict[str, str]:
    """Agent key -> logical model or model id, parsed from ASSISTANT_AGENT_MODELS.

    Entries are dropped one by one: a typo should not undo the pins set alongside
    it, which may be the deliberate ones.
    """
    pins = {}
    for key, model in _json_object(
        settings.ASSISTANT_AGENT_MODELS, "ASSISTANT_AGENT_MODELS"
    ).items():
        try:
            agent = AgentKey(key).value
            pins[agent] = (
                model
                if isinstance(model, str) and is_model_id(model)
                else AiSettings.Model(model).value
            )
        except Exception as exc:
            logger.error(
                "ASSISTANT_AGENT_MODELS: ignoring entry %r -> %r (%s)", key, model, exc
            )
    return pins


def organization_model_id(ai_settings: AiSettings) -> str:
    """Model id the organization's own conversations run on."""
    model_id = _models().get(ai_settings.provider, {}).get(ai_settings.effective_model)
    if model_id is None:
        raise AssistantException(
            f"No model id configured for {ai_settings.effective_model!r} on provider "
            f"{ai_settings.provider!r}"
        )
    return model_id


def resolve_model_id(
    ai_settings: AiSettings, agent_key: str, default_model: str | None
) -> str:
    """Model id an agent runs on for this organization.

    A model the organization cannot run is a gap in our own configuration or a
    bad pin rather than a user misconfiguration, so we fall back to the
    organization's model: losing the intended model beats breaking the assistant.
    """
    requested = _pins().get(agent_key, default_model)
    if requested is not None:
        model_id = (
            requested
            if is_model_id(requested)
            else _models().get(ai_settings.provider, {}).get(requested)
        )
        if model_id is None:
            logger.error(
                "Provider %r has no model id for %r requested by agent %r; "
                "falling back to the organization's model",
                ai_settings.provider,
                requested,
                agent_key,
            )
        elif not supports(ai_settings, model_id):
            logger.error(
                "Agent %r requested %r, which %r organizations hold no credentials "
                "for; falling back to the organization's model",
                agent_key,
                model_id,
                ai_settings.provider,
            )
        else:
            return model_id
    return organization_model_id(ai_settings)


def build_agent_model(
    builder: AiModelBuilder, agent_key: str, default_model: str | None
) -> BuiltModel:
    return builder.build(
        resolve_model_id(builder.ai_settings, agent_key, default_model)
    )
