import json
import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Pipeline, PipelineRunTrigger, PipelineVersion

logger = getLogger(__name__)


@require_POST
@csrf_exempt
def run_pipeline(
    request: HttpRequest, id: uuid.UUID, version_number: int = None
) -> HttpResponse:
    """Runs a pipeline. The endpoint accepts both form data and JSON payloads.

    To be runnable, the pipeline must be set as public with `webhook_enabled`.

    Returns
    -------
        HttpResponse: Returns a dict with the `run_id` key containing the ID of the created run.
    """
    try:
        pipeline = Pipeline.objects.get(id=id)
    except Pipeline.DoesNotExist:
        return JsonResponse({"error": "Pipeline not found"}, status=404)

    # Only allow pipelines with public webhooks to be run with this endpoint
    if pipeline.webhook_enabled is False:
        return JsonResponse({"error": "Pipeline has no webhook enabled"}, status=400)

    # Get the pipeline version
    try:
        pipeline_version = pipeline.last_version
        if version_number is not None:
            pipeline_version = PipelineVersion.objects.get(
                pipeline=pipeline, number=version_number
            )

        if pipeline_version is None:
            return JsonResponse({"error": "Pipeline has no version"}, status=400)
    except PipelineVersion.DoesNotExist:
        return JsonResponse({"error": "Pipeline version not found"}, status=404)

    # Get the data from the request
    content_type = request.META.get("CONTENT_TYPE")
    config = {}
    if content_type == "application/x-www-form-urlencoded":
        send_mail_notifications = request.POST.get("send_mail_notifications", False)
        for parameter in pipeline_version.parameters:
            if parameter["code"] not in request.POST:
                continue
            if parameter["type"] == "bool":
                config[parameter["code"]] = request.POST.get(
                    parameter["code"]
                ).lower() in (
                    "1",
                    "true",
                )
                continue

            values = request.POST.getlist(parameter["code"])
            if parameter["type"] == "int":
                values = [int(v) for v in values]
            elif parameter["type"] == "float":
                values = [float(v) for v in values]

            if parameter.get("multiple", False):
                config[parameter["code"]] = values
            else:
                config[parameter["code"]] = values[0]

    elif content_type == "application/json":
        send_mail_notifications = request.GET.get("send_mail_notifications", False)
        try:
            config = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse(
            {"error": f"Unsupported content type '{content_type}'"}, status=400
        )

    try:
        run = pipeline.run(
            user=None,
            pipeline_version=pipeline_version,
            trigger_mode=PipelineRunTrigger.WEBHOOK,
            config=config,
            send_mail_notifications=send_mail_notifications,
        )
        return JsonResponse({"run_id": run.id}, status=200)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
