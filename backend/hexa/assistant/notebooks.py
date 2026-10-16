"""The AI credentials a notebook server is given.

The notebook images bundle Jupyter AI, Claude Code and Gemini CLI. They run inside
the user's container, where the organization's AI settings are out of reach, so the
workspace credentials endpoint hands them what they need as HEXA_AI_* environment
variables, read by `hexa-ai-env.sh` in openhexa-docker-images:

- HEXA_AI_PROVIDER: "managed" (our Vertex project) or "anthropic" (the
  organization's own key), and HEXA_AI_MODEL, the Claude model to use;
- managed: HEXA_AI_VERTEX_PROJECT_ID, HEXA_AI_VERTEX_REGION and a short-lived
  HEXA_AI_VERTEX_ACCESS_TOKEN (with HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT, epoch
  seconds), minted from our own service account. The token lives for an hour and
  the notebook server cannot renew it; it is restarted on logout, like the storage
  token it already gets this way;
- anthropic: HEXA_AI_ANTHROPIC_API_KEY.

Nothing is sent when the assistant is off or the organization's monthly AI
budget is spent, so older images and organizations without AI behave as before.

The images report the usage made on these credentials back to
/notebooks/telemetry (see `hexa.assistant.telemetry`), which is how it counts
towards the budget.
"""

import logging
from datetime import UTC

from django.conf import settings

from hexa.assistant.ai_models.backends import backend_for
from hexa.assistant.ai_models.ids import ModelId
from hexa.assistant.ai_models.vertex import access_token
from hexa.assistant.keys import AgentKey
from hexa.user_management.models import AiSettings, Organization

logger = logging.getLogger(__name__)

# Claude Code only runs Claude, so the notebooks get the first Claude among the
# candidates for the `notebooks` agent key and skip, say, a Gemini default.
CLAUDE_PROVIDER = "anthropic"


def _claude_model(ai_settings: AiSettings) -> ModelId | None:
    backend = backend_for(ai_settings)
    for requested in backend.model_candidates(AgentKey.NOTEBOOKS, None):
        if requested is None:
            continue
        model_id = (
            requested
            if isinstance(requested, ModelId)
            else backend.model_ids.get(requested)
        )
        if model_id is not None and model_id.provider == CLAUDE_PROVIDER:
            return model_id
    return None


def notebooks_ai_env(organization: Organization) -> dict[str, str]:
    """The HEXA_AI_* variables for a notebook server of `organization`, or none."""
    ai_settings = organization.ai_settings_safe
    if not ai_settings.enabled:
        return {}
    if organization.is_ai_budget_limit_reached():
        # The usage the notebooks report counts towards the same budget as the
        # app's agents; once it is spent, new servers get no credentials.
        logger.info(
            "Organization %s has reached its AI budget; the notebook AI tooling "
            "is not configured",
            organization.slug,
        )
        return {}

    model = _claude_model(ai_settings)
    if model is None:
        logger.warning(
            "No Claude model is available to %r organizations; the notebook AI "
            "tooling is not configured",
            ai_settings.provider,
        )
        return {}
    env = {"HEXA_AI_PROVIDER": ai_settings.provider, "HEXA_AI_MODEL": model.name}

    if ai_settings.provider == AiSettings.Provider.MANAGED:
        if not settings.VERTEX_PROJECT_ID:
            logger.warning(
                "VERTEX_PROJECT_ID is not configured; the notebook AI tooling is "
                "not configured"
            )
            return {}
        try:
            token, expiry = access_token()
        except Exception:
            # A notebook server must still start without its AI tooling.
            logger.exception(
                "Could not obtain a Vertex AI access token; the notebook AI "
                "tooling is not configured"
            )
            return {}
        env.update(
            {
                "HEXA_AI_VERTEX_PROJECT_ID": settings.VERTEX_PROJECT_ID,
                "HEXA_AI_VERTEX_REGION": model.region or settings.VERTEX_REGION,
                "HEXA_AI_VERTEX_ACCESS_TOKEN": token,
                "HEXA_AI_VERTEX_ACCESS_TOKEN_EXPIRES_AT": str(
                    int(expiry.replace(tzinfo=UTC).timestamp())
                ),
            }
        )
    else:
        if not ai_settings.api_key:
            return {}
        env["HEXA_AI_ANTHROPIC_API_KEY"] = ai_settings.api_key

    return env
