import json
import uuid
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse

from hexa.assistant.models import Conversation
from hexa.core.sse import sse_response


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

    monthly_cost = await sync_to_async(Conversation.get_monthly_cost_for_user)(
        request.user
    )
    if monthly_cost >= Decimal(settings.ASSISTANT_MONTHLY_LIMIT):
        return JsonResponse({"error": "Monthly limit exceeded"}, status=429)

    return JsonResponse({"error": "Server error"}, status=400)
    agent = await sync_to_async(lambda: conversation.agent)()
    return sse_response(agent.run_stream(message))


# CSRF is safe to skip here: the endpoint requires an authenticated session cookie,
# the Content-Type is application/json (a non-simple request), so browsers always
# send a CORS preflight before crossing origins, and CORS_ALLOW_CREDENTIALS restricts
# which origins are permitted. We set the attribute directly rather than using
# @csrf_exempt because that decorator wraps the view in a sync adapter, downgrading
# an async view to sync.
# If Django ever supports @method_decorator(csrf_exempt) cleanly on async views, prefer that instead.
stream_assistant_message.csrf_exempt = True
