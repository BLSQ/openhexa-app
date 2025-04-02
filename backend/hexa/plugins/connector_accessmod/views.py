import enum
import json
from logging import getLogger

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.plugins.connector_accessmod.models import Analysis
from hexa.plugins.connector_accessmod.queue import validate_fileset_queue
from hexa.plugins.connector_airflow.authentication import DAGRunUser
from hexa.plugins.connector_airflow.views import webhook as AirflowWebhook

logger = getLogger(__name__)


class EventType(str, enum.Enum):
    STATUS_UPDATE = "status_update"
    ACQUISITION_FINISHED = "acquisition_completed"


@require_POST
@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated or not isinstance(request.user, DAGRunUser):
        logger.error(
            "dag_run_authentication_middleware error",
        )
        return JsonResponse(
            {"success": False},
            status=401,
        )

    payload = json.loads(request.body.decode("utf-8"))
    if "type" not in payload or "data" not in payload:
        return JsonResponse(
            {"success": False, "message": "Malformed JSON"},
            status=500,
        )

    event_type = payload["type"]
    event_data = payload["data"]

    if event_type == EventType.STATUS_UPDATE:
        try:
            analysis = Analysis.objects.get_subclass(dag_run=request.user.dag_run.id)
        except Analysis.DoesNotExist:
            return JsonResponse(
                {"success": False},
                status=400,
            )

        with transaction.atomic():
            analysis.update_status(event_data["status"])
            if "outputs" in event_data:
                filesets = analysis.set_outputs(**event_data["outputs"])
            else:
                filesets = []
        for fileset in filesets:
            validate_fileset_queue.enqueue(
                "validate_fileset",
                {
                    "fileset_id": str(fileset.id),
                },
            )

        return JsonResponse(
            {"success": True},
            status=200,
        )

    elif event_type == EventType.ACQUISITION_FINISHED:
        try:
            analysis = Analysis.objects.get_subclass(dag_run=request.user.dag_run.id)
        except Analysis.DoesNotExist:
            return JsonResponse(
                {"success": False},
                status=400,
            )

        try:
            fileset = analysis.set_input(
                input=event_data["acquisition_type"],
                uri=event_data["uri"],
                mime_type=event_data["mime_type"],
                metadata=event_data.get("metadata"),
            )
        except Exception:
            logger.exception("webhook update acquisition")
            return JsonResponse(
                {"success": False},
                status=500,
            )

        validate_fileset_queue.enqueue(
            "validate_fileset",
            {
                "fileset_id": str(fileset.id),
            },
        )

        return JsonResponse(
            {"success": True},
            status=200,
        )
    else:
        return AirflowWebhook(request)
