from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.datagrids import EnvironmentGrid, RunGrid
from hexa.pipelines.models import Index
from hexa.plugins.connector_airflow.models import AirflowAPIError, DAGRun

logger = getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    environments = Index.objects.filter_for_user(request.user).roots()
    environment_grid = EnvironmentGrid(environments, request=request)

    dag_runs = DAGRun.objects.filter_for_user(request.user)
    run_grid = RunGrid(dag_runs[:5], request=request)

    return render(
        request,
        "pipelines/index.html",
        {
            "environment_grid": environment_grid,
            "run_grid": run_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def index_refresh(request: HttpRequest) -> HttpResponse:
    dag_runs = DAGRun.objects.filter_for_user(request.user)
    for run in dag_runs.filter_for_refresh():
        try:
            run.refresh()
        except AirflowAPIError:
            logger.exception(f"Refresh failed for DAGRun {run.id}")

    return index(request)
