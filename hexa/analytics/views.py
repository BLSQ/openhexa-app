import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.user_management.models import AnonymousUser

from .api import track


@require_POST
@csrf_exempt
def track_event(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the frontend to track events."""
    payload = json.loads(request.body.decode("utf-8"))

    if "event" not in payload:
        return JsonResponse({"Bad request": "event name is required."}, status=400)

    if isinstance(request.user, AnonymousUser) or request.user.analytics_enabled:
        track(
            request,
            payload.get("event"),
            payload.get("properties", {}),
            request.user,
        )
        return JsonResponse({}, status=200)
    else:
        return JsonResponse({"error": "Analytics not enabled."}, status=401)
