import json
import logging
import uuid

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.utils import timezone
from opentelemetry import trace

from hexa.assistant import gateway
from hexa.assistant.ai_models import AiModelBuilder
from hexa.assistant.exceptions import AssistantException
from hexa.assistant.keys import AgentKey
from hexa.assistant.models import AiUsage, Conversation
from hexa.core.sse import sse_response, with_keepalive

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("hexa.assistant.gateway")

# What the gateway's usage rows name as their source.
GATEWAY_USAGE_SOURCE = "notebooks"


async def stream_assistant_message(
    request: HttpRequest, conversation_id: uuid.UUID
) -> HttpResponse:
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid request body"}, status=400)

    if not message:
        return JsonResponse({"error": "Message is required"}, status=400)

    try:
        conversation = await Conversation.objects.filter_for_user(request.user).aget(
            id=conversation_id
        )
    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)

    organization = await sync_to_async(lambda: conversation.workspace.organization)()
    ai_budget_limit_reached = await sync_to_async(
        organization.is_ai_budget_limit_reached
    )()
    if ai_budget_limit_reached:
        return JsonResponse(
            {
                "error": "Organization AI budget exceeded",
                "error_code": "AI_BUDGET_EXCEEDED",
            },
            status=403,
        )

    agent = await sync_to_async(lambda: conversation.agent)()
    return sse_response(with_keepalive(agent.run_stream(message)))


# CSRF is safe to skip here: the endpoint requires an authenticated session cookie,
# the Content-Type is application/json (a non-simple request), so browsers always
# send a CORS preflight before crossing origins, and CORS_ALLOW_CREDENTIALS restricts
# which origins are permitted. We set the attribute directly rather than using
# @csrf_exempt because that decorator wraps the view in a sync adapter, downgrading
# an async view to sync.
# If Django ever supports @method_decorator(csrf_exempt) cleanly on async views, prefer that instead.
stream_assistant_message.csrf_exempt = True


def _gateway_error(status: int, message: str, error_type: str) -> JsonResponse:
    """An error the OpenAI SDKs (hence litellm) understand."""
    return JsonResponse(
        {"error": {"message": message, "type": error_type, "code": None}},
        status=status,
    )


async def _record_gateway_usage(
    completion: gateway.Completion, *, organization, workspace, user
) -> None:
    """Charge a completion to the organization. Never fails the response: it
    is already (being) sent.
    """
    try:
        usage = completion.usage
        await AiUsage.objects.acreate(
            organization=organization,
            workspace=workspace,
            user=user,
            source=GATEWAY_USAGE_SOURCE,
            model=completion.model_name[:100],
            input_tokens=usage.input_tokens,
            cache_read_tokens=usage.cache_read_tokens,
            cache_write_tokens=usage.cache_write_tokens,
            output_tokens=usage.output_tokens,
            cost=completion.built_model.calculate_cost(usage),
            occurred_at=timezone.now(),
            external_id=completion.id,
        )
    except Exception:
        logger.exception("Could not record the usage of completion %s", completion.id)


async def _stream_completion(completion: gateway.Completion, attributes: dict, record):
    with tracer.start_as_current_span(
        "notebooks chat completion", attributes=attributes
    ):
        try:
            async for event in completion.stream():
                yield event
        except Exception:
            logger.exception("gateway: completion %s failed", completion.id)
            yield gateway.error_event("The model request failed")
            return
    await record()


async def gateway_chat_completions(request: HttpRequest) -> HttpResponse:
    """OpenAI-compatible chat completions on the organization's model, for the
    AI tooling of the notebook servers. See `hexa.assistant.gateway`.
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
        built_model = await sync_to_async(
            lambda: AiModelBuilder(ai_settings).build_for_agent(
                AgentKey.NOTEBOOKS, None
            )
        )()
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
