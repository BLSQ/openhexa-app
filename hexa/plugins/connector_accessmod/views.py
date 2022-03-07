import enum
import json
from logging import getLogger

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.metrics.decorators import do_not_track
from hexa.plugins.connector_accessmod.authentication import DAGRunUser
from hexa.plugins.connector_accessmod.models import Analysis

logger = getLogger(__name__)


class EventType(str, enum.Enum):
    STATUS_UPDATE = "status_update"


@require_http_methods(["POST"])
@csrf_exempt
@do_not_track
def webhook(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    if not request.user.is_authenticated or not isinstance(request.user, DAGRunUser):
        logger.error(
            "dag_run_authentication_middleware error",
        )
        return JsonResponse(
            {"success": False},
            status=401,
        )

    payload = json.loads(request.body.decode("utf-8"))
    event_type = payload["type"]
    event_data = payload["data"]

    if event_type == EventType.STATUS_UPDATE:
        try:
            analysis = Analysis.objects.get_subclass(dag_run=request.user.dag_run.id)
        except Analysis.DoesNotExist:
            return JsonResponse(
                {"success": False},
                status=401,
            )

        with transaction.atomic():
            analysis.update_status(event_data["status"])
            if "outputs" in event_data:
                analysis.set_outputs(**event_data["outputs"])

    return JsonResponse(
        {"success": True},
        status=200,
    )
