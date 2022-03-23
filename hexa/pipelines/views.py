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

from hexa.pipelines.datagrids import EnvironmentGrid, PipelineIndexGrid
from hexa.pipelines.models import Environment, Index

from ..plugins.app import get_connector_app_configs
from .credentials import PipelinesCredentials
from .queue import environment_sync_queue

logger = getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    pipelines = (
        Index.objects.filter_for_user(request.user).prefetch_related("object").leaves(1)
    )
    pipeline_grid = PipelineIndexGrid(pipelines, request=request)

    environments = Index.objects.filter_for_user(request.user).roots()
    environment_grid = EnvironmentGrid(environments, request=request)

    return render(
        request,
        "pipelines/index.html",
        {
            "pipeline_grid": pipeline_grid,
            "environment_grid": environment_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


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
        data = Signer().unsign(token)
    except BadSignature:
        return JsonResponse({"error": "Token signature is invalid"}, status=401)

    model = apps.get_model(data["app_label"], data["model"])
    pipeline = get_object_or_404(model, pk=data["id"])

    pipeline_credentials = PipelinesCredentials(pipeline)

    for app_config in get_connector_app_configs():
        credentials_functions = app_config.get_pipelines_credentials()
        for credentials_function in credentials_functions:
            credentials_function(pipeline_credentials)

    return JsonResponse(
        pipeline_credentials.to_dict(),
        status=200,
    )
