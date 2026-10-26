"""The AI configuration a notebook server is given.

The notebook images bundle Jupyter AI, whose Jupyternaut assistant talks to
models through litellm. Rather than credentials, the workspace credentials
endpoint hands the server the way to our gateway (`hexa.assistant.notebooks.gateway`),
an OpenAI-compatible endpoint that runs the organization's model here, as
HEXA_AI_* environment variables read by the image:

- HEXA_AI_PROVIDER: "openhexa", i.e. the gateway;
- HEXA_AI_MODEL: the name of the model the gateway runs for the organization,
  shown in the model picker.

The image points litellm at $HEXA_SERVER_URL/assistant/gateway/v1 with the
workspace token (HEXA_TOKEN) the server already has, so the credentials never
leave the app and the usage is charged to the organization's AI budget.

Nothing is sent when the assistant is off, so older images and organizations
without AI behave as before.
"""

import logging

from hexa.assistant.ai_models.backends import backend_for
from hexa.assistant.ai_models.selection import ModelSelector
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.keys import AgentKey
from hexa.user_management.models import Organization

logger = logging.getLogger(__name__)

GATEWAY_PROVIDER = "openhexa"


def notebooks_ai_env(organization: Organization) -> dict[str, str]:
    """The HEXA_AI_* variables for a notebook server of `organization`, or none."""
    ai_settings = organization.ai_settings_safe
    if not ai_settings.enabled:
        return {}
    try:
        model_id = ModelSelector(backend_for(ai_settings)).for_agent(
            AgentKey.NOTEBOOKS, None
        )
    except AssistantException:
        logger.warning(
            "No model is configured for the notebooks of %r organizations; the "
            "notebook AI tooling is not configured",
            ai_settings.provider,
        )
        return {}
    return {"HEXA_AI_PROVIDER": GATEWAY_PROVIDER, "HEXA_AI_MODEL": model_id.name}
