import enum
import json
from logging import getLogger

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.plugins.connector_airflow.authentication import DAGRunUser
from hexa.plugins.connector_airflow.models import DAGRun, DAGRunState

logger = getLogger(__name__)


class EventType(str, enum.Enum):
    ADD_OUTPUT_FILE = "add_output_file"
    LOG_MESSAGE = "log_message"
    PROGRESS_UPDATE = "progress_update"


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

    try:
        dag_run = DAGRun.objects.get(pk=request.user.dag_run.id)
    except DAGRun.DoesNotExist:
        return JsonResponse(
            {"success": False},
            status=400,
        )

    if dag_run.state in [DAGRunState.SUCCESS, DAGRunState.FAILED]:
        return JsonResponse(
            {"success": False, "message": "Pipeline already completed"},
            status=500,
        )

    payload = json.loads(request.body.decode("utf-8"))
    if "type" not in payload or "data" not in payload:
        return JsonResponse(
            {"success": False, "message": "Malformed JSON"},
            status=500,
        )

    event_type = payload["type"]
    event_data = payload["data"]

    if event_type == EventType.ADD_OUTPUT_FILE:
        dag_run.set_output(**event_data)

    elif event_type == EventType.LOG_MESSAGE:
        dag_run.log_message(**event_data)

    elif event_type == EventType.PROGRESS_UPDATE:
        try:
            progress = int(event_data)
        except ValueError:
            return JsonResponse(
                {"success": False, "message": f"Can't convert {event_data} to integer"},
                status=400,
            )
        dag_run.progress_update(progress)

    return JsonResponse(
        {"success": True},
        status=200,
    )
