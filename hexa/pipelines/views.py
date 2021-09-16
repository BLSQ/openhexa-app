from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.datagrids import EnvironmentGrid, RunGrid
from hexa.pipelines.models import Index
from hexa.plugins.connector_airflow.models import DAGRun, DAGRunState


def index(request):
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    environments = Index.objects.filter_for_user(request.user).roots()
    environment_grid = EnvironmentGrid(environments)

    dag_config_runs = DAGRun.objects.filter_for_user(request.user)

    # TODO: actual refresh should be done using a CRON
    for run in dag_config_runs.filter(state=DAGRunState.RUNNING):
        run.refresh()

    run_grid = RunGrid(dag_config_runs)

    return render(
        request,
        "pipelines/index.html",
        {
            "environment_grid": environment_grid,
            "run_grid": run_grid,
            "breadcrumbs": breadcrumbs,
        },
    )
