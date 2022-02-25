import enum
import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.plugins.connector_accessmod.models import Analysis, AnalysisStatus


class EventType(str, enum.Enum):
    SUCCESS = "success"


@require_http_methods(["POST"])
@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False},
            status=401,
        )

    payload = json.loads(request.body.decode("utf-8"))
    event_type = payload["type"]
    event_data = payload["data"]

    if event_type == EventType.SUCCESS:
        try:
            analysis = Analysis.objects.get_subclass(id=event_data["analysis_id"])
            analysis.status = AnalysisStatus.SUCCESS
            analysis.set_outputs(**event_data["outputs"])
        except Analysis.DoesNotExist:
            return JsonResponse(
                {"success": False},
                status=401,
            )

    return JsonResponse(
        {"success": True},
        status=200,
    )
