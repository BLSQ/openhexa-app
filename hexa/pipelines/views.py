import uuid
from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from hexa.metrics.decorators import do_not_track
from hexa.pipelines.datagrids import DAGRunGrid, EnvironmentGrid
from hexa.pipelines.models import Environment, Index
from hexa.plugins.connector_airflow.models import AirflowAPIError, DAGRun

from .queue import environment_sync_queue

logger = getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    environments = Index.objects.filter_for_user(request.user).roots()
    environment_grid = EnvironmentGrid(environments, request=request)

    dag_runs = DAGRun.objects.filter_for_user(request.user)
    run_grid = DAGRunGrid(dag_runs[:5], request=request)

    return render(
        request,
        "pipelines/index.html",
        {
            "environment_grid": environment_grid,
            "run_grid": run_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


@do_not_track
def index_refresh(request: HttpRequest) -> HttpResponse:
    dag_runs = DAGRun.objects.filter_for_user(request.user)
    for run in dag_runs.filter_for_refresh():
        try:
            run.refresh()
        except AirflowAPIError:
            logger.exception(f"Refresh failed for DAGRun {run.id}")

    return index(request)


@require_http_methods(["POST"])
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
