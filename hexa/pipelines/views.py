from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.models import PipelinesIndexType, PipelinesIndex
from hexa.plugins.connector_airflow.models import DAGConfigRun, DAGConfigRunState


def index(request):
    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
    ]
    environment_indexes = PipelinesIndex.objects.filter_for_user(request.user).filter(
        index_type=PipelinesIndexType.PIPELINES_ENVIRONMENT.value
    )

    # TODO: replace by indexed runs
    dag_config_runs = DAGConfigRun.objects.filter_for_user(request.user)

    # TODO: actual refresh should be done using a CRON
    for run in dag_config_runs.filter(airflow_state=DAGConfigRunState.RUNNING):
        run.refresh()

    return render(
        request,
        "pipelines/index.html",
        {
            "environment_indexes": environment_indexes,
            "dag_config_runs": dag_config_runs,
            "breadcrumbs": breadcrumbs,
        },
    )
