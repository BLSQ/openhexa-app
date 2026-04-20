import json
import uuid
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse

from hexa.assistant.agents import create_agent
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
    if monthly_cost >= Decimal(str(settings.ASSISTANT_MONTHLY_LIMIT)):
        return JsonResponse({"error": "Monthly limit exceeded"}, status=429)

    agent = await sync_to_async(create_agent)(conversation)
    return sse_response(agent.run_stream(message))


# The CSRF middleware checks this attribute directly — no decorator wrapper needed,
# which would otherwise downgrade the async view to sync.
stream_assistant_message.csrf_exempt = True
