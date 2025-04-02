import base64
import binascii
import json
import uuid
from logging import getLogger

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, Signer, TimestampSigner
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.analytics.api import track
from hexa.app import get_hexa_app_configs
from hexa.core.views_utils import disable_cors
from hexa.pipelines.models import Environment, PipelineRunLogLevel

from .credentials import PipelinesCredentials
from .models import Pipeline, PipelineRunTrigger, PipelineType, PipelineVersion
from .queue import environment_sync_queue

logger = getLogger(__name__)


@require_POST
def environment_sync(
    request: HttpRequest, environment_contenttype_id: int, environment_id: uuid.UUID
):
    try:
        environment_type = ContentType.objects.get_for_id(id=environment_contenttype_id)
    except ContentType.DoesNotExist:
        raise Http404("No environment matches the given query.")
    if not issubclass(environment_type.model_class(), Environment):
        raise Http404("No environment matches the given query.")
    environment = get_object_or_404(
        environment_type.model_class().objects.filter_for_user(request.user),
        pk=environment_id,
    )

    if settings.EXTERNAL_ASYNC_REFRESH and "synchronous" not in request.GET:
        environment_sync_queue.enqueue(
            "environment_sync",
            {
                "contenttype_id": environment_contenttype_id,
                "object_id": str(environment.id),
            },
        )
        messages.success(request, _("The environment will soon be synced"))
    else:
        try:
            sync_result = environment.sync()
            messages.success(request, sync_result)
        except Exception:
            messages.error(request, _("The environment could not be synced"))
            logger.exception(f"Sync failed for environment {environment.id}")

    return JsonResponse({"success": True})


@require_POST
@csrf_exempt  # TODO: we should remove this
def credentials(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the pipelines component to get credentials for Airflow DAGs."""
    auth_type, token = request.headers.get("Authorization", " ").split(" ")
    if auth_type.lower() != "bearer":
        return JsonResponse(
            {"error": "Authorization header should start with 'bearer'"}, status=401
        )
    try:
        data = Signer().unsign_object(token)
    except BadSignature:
        return JsonResponse({"error": "Token signature is invalid"}, status=401)

    model = apps.get_model(data["app_label"], data["model"])
    pipeline = get_object_or_404(model, pk=data["id"])

    pipeline_credentials = PipelinesCredentials(pipeline)

    for app_config in get_hexa_app_configs(connector_only=True):
        credentials_functions = app_config.get_pipelines_credentials()
        for credentials_function in credentials_functions:
            credentials_function(pipeline_credentials)

    return JsonResponse(
        pipeline_credentials.to_dict(),
        status=200,
    )


@require_POST
@csrf_exempt
@disable_cors
def run_pipeline(
    request: HttpRequest, token: str, version_id: uuid.UUID = None
) -> HttpResponse:
    """Runs a pipeline. The endpoint accepts both form data and JSON payloads.

    To be runnable, the pipeline must be set as public with `webhook_enabled`.

    Returns
    -------
        HttpResponse: Returns a dict with the `run_id` key containing the ID of the created run.
    """
    try:
        # TODO: this is a temp solution to support pipeline that used UUID as webhook token
        # and will be removed once users have migrated to new webhook url system.
        pipeline = Pipeline.objects.get(id=token)
    except Pipeline.DoesNotExist:
        return JsonResponse({"error": "Pipeline not found"}, status=404)
    except ValidationError:
        try:
            signer = TimestampSigner()
            decoded_value = base64.b64decode(token).decode("utf-8")
            signer.unsign(decoded_value)
            pipeline = Pipeline.objects.get(webhook_token=token)
        except (UnicodeDecodeError, binascii.Error, BadSignature):
            return JsonResponse({"error": "Invalid token"}, status=400)
        except Pipeline.DoesNotExist:
            return JsonResponse({"error": "Pipeline not found"}, status=404)

    # Only allow pipelines with public webhooks to be run with this endpoint
    if pipeline.webhook_enabled is False:
        return JsonResponse({"error": "Pipeline has no webhook enabled"}, status=400)

    # Get the pipeline version
    pipeline_version = None
    if pipeline.type == PipelineType.ZIPFILE:
        try:
            pipeline_version = pipeline.last_version
            if version_id is not None:
                pipeline_version = PipelineVersion.objects.get(
                    pipeline=pipeline, id=version_id
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
        log_level = PipelineRunLogLevel.parse_log_level(request.POST.get("log_level"))
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
        log_level = PipelineRunLogLevel.parse_log_level(request.GET.get("log_level"))
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
            log_level=log_level,
        )
        track(
            request,
            "pipelines.pipeline_run",
            {
                "pipeline_id": pipeline.code,
                "version_name": pipeline_version.name if pipeline_version else None,
                "version_id": str(pipeline_version.id) if pipeline_version else None,
                "trigger": PipelineRunTrigger.WEBHOOK,
                "workspace": pipeline.workspace.slug,
            },
        )
        return JsonResponse({"run_id": run.id}, status=200)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
