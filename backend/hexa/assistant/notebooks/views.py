import json
import logging

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
from opentelemetry import trace

from hexa.assistant.exceptions import AssistantException
from hexa.assistant.models import AiUsage
from hexa.assistant.notebooks import gateway
from hexa.assistant.notebooks.env import notebooks_model
from hexa.core.sse import sse_response

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("hexa.assistant.notebooks.gateway")


def _gateway_error(status: int, message: str, error_type: str) -> JsonResponse:
    """An error the OpenAI SDKs (hence litellm) understand."""
    return JsonResponse(
        {"error": {"message": message, "type": error_type, "code": None}},
        status=status,
    )


async def _record_gateway_usage(
    completion: gateway.Completion, *, organization, workspace, user
) -> None:
    """Charge a completion to the organization. Nothing is charged when the
    model never answered.
    """
    if completion.response is None:
        return
    usage = completion.usage
    await AiUsage.arecord(
        completion.built_model,
        usage,
        source=AiUsage.Source.NOTEBOOK,
        cost=completion.built_model.calculate_cost(usage),
        organization_id=organization.id,
        workspace_id=workspace.id,
        user_id=user.id,
        external_id=completion.id,
    )


async def _stream_completion(completion: gateway.Completion, attributes: dict, record):
    with tracer.start_as_current_span(
        "notebooks chat completion", attributes=attributes
    ):
        stream = completion.stream()
        try:
            async for event in stream:
                yield event
        except Exception:
            logger.exception("gateway: completion %s failed", completion.id)
            yield gateway.error_event("The model request failed")
        finally:
            # Also when the client disconnects (this generator is then closed
            # at a yield, which does not close the one it iterates) or the
            # model fails: the tokens consumed so far are billed to us, so they
            # are charged to the organization.
            await stream.aclose()
            await record()


async def gateway_chat_completions(request: HttpRequest) -> HttpResponse:
    """OpenAI-compatible chat completions on the organization's model, for the
    AI tooling of the notebook servers. See `hexa.assistant.notebooks.gateway`.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    token = getattr(request, "workspace_token", None)
    if token is None:
        return _gateway_error(
            401, "A workspace token is required", "invalid_request_error"
        )
    workspace, user = token.workspace, token.user
    organization = await sync_to_async(lambda: workspace.organization)()
    ai_settings = await sync_to_async(lambda: organization.ai_settings_safe)()
    if not ai_settings.enabled:
        return _gateway_error(
            403,
            "The AI assistant is not enabled for this organization",
            "permission_error",
        )
    if await sync_to_async(organization.is_ai_budget_limit_reached)():
        return _gateway_error(
            403, "Organization AI budget exceeded", "permission_error"
        )

    try:
        chat_request = gateway.parse_chat_request(json.loads(request.body))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _gateway_error(400, "Invalid JSON body", "invalid_request_error")
    except gateway.GatewayError as e:
        return _gateway_error(400, str(e), "invalid_request_error")

    try:
        built_model = await sync_to_async(notebooks_model)(ai_settings)
    except AssistantException as e:
        logger.error("gateway: no model for organization %s: %s", organization.slug, e)
        return _gateway_error(503, "No model is available", "server_error")

    completion = gateway.Completion(built_model, chat_request)
    attributes = {
        "hexa.organization": organization.slug,
        "hexa.workspace": workspace.slug,
        "hexa.user": user.email,
        "gen_ai.request.model": built_model.api_name,
    }

    async def record():
        await _record_gateway_usage(
            completion, organization=organization, workspace=workspace, user=user
        )

    if chat_request.stream:
        return sse_response(_stream_completion(completion, attributes, record))

    with tracer.start_as_current_span(
        "notebooks chat completion", attributes=attributes
    ):
        try:
            payload = await completion.complete()
        except Exception:
            logger.exception("gateway: completion %s failed", completion.id)
            return _gateway_error(502, "The model request failed", "server_error")
    await record()
    return JsonResponse(payload)


# Token-authenticated API for programs, not browsers: no session, no CSRF.
gateway_chat_completions.csrf_exempt = True
