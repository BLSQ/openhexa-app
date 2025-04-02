import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .api import track


@csrf_exempt
@require_POST
def track_event(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the frontend to track events."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"Bad request": "Invalid JSON payload."}, status=400)

    if "event" not in payload:
        return JsonResponse({"Bad request": "event name is required."}, status=400)

    track(
        request,
        payload.get("event"),
        payload.get("properties", {}),
    )
    return JsonResponse({}, status=200)
