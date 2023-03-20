import base64
import json
import uuid
from logging import getLogger

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.signing import BadSignature, Signer
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.app import get_hexa_app_configs
from hexa.databases.api import get_db_server_credentials
from hexa.pipelines.models import Environment
from hexa.plugins.connector_gcs.api import build_app_short_lived_credentials
from hexa.workspaces.models import Connection, ConnectionType

from .credentials import PipelinesCredentials
from .models import Pipeline, PipelineRun
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

    return redirect(request.META.get("HTTP_REFERER", environment.get_absolute_url()))


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
def credentials2(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the Pipelines v2 to get credentials"""
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
    workspace = pipeline.workspace

    # should follow the same logic as workspace.views.credentials
    # FIXME: when workspace bucket credentials are working -> refactor/merge

    env = {}
    gcs_buckets = []

    connections = Connection.objects.filter(workspace=workspace)
    for connection in connections:
        if connection.connection_type == ConnectionType.GCS:
            gcs_buckets.append({"name": connection.name, "mode": "RW"})
        else:
            env.update(connection.env_variables)

    db_credentials = get_db_server_credentials()
    env.update(
        {
            "WORKSPACE_DATABASE_HOST": db_credentials["host"],
            "WORKSPACE_DATABASE_PORT": db_credentials["port"],
            "WORKSPACE_DATABASE_USERNAME": workspace.db_name,
            "WORKSPACE_DATABASE_PASSWORD": workspace.db_password,
            "WORKSPACE_DATABASE_URL": f"postgresql://{workspace.db_name}:{workspace.db_password}@{db_credentials['host']}:{db_credentials['port']}/{workspace.db_name}",
        }
    )

    gcs_buckets.append({"name": pipeline.workspace.bucket_name, "mode": "RW"})
    env["WORKSPACE_BUCKET"] = pipeline.workspace.bucket_name
    env["GCS_TOKEN"] = build_app_short_lived_credentials().access_token
    env["GCS_BUCKETS"] = base64.b64encode(
        json.dumps({"buckets": gcs_buckets}).encode()
    ).decode()

    return JsonResponse(
        {"env": env, "files": {}},
        status=200,
    )


def pipelines_status(request: HttpRequest) -> HttpResponse:
    """Temporary endpoint for a status page"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        raise Http404("not authorized")  # FIXME

    return render(
        request,
        "pipelines/status.html",
        {
            "pipelines": Pipeline.objects.all(),
            "pipeline_runs": PipelineRun.objects.all(),
        },
    )
