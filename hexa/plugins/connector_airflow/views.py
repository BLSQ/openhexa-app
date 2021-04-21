from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_airflow.models import Environment, DAG, DAGConfig


def environment_detail(request, environment_id):
    environment = get_object_or_404(
        Environment.objects.filter_for_user(request.user),
        pk=environment_id,
    )

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            environment.display_name,
            "connector_airflow:environment_detail",
            environment_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/environment_detail.html",
        {
            "environment": environment,
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_detail(request, environment_id, dag_id):
    environment = get_object_or_404(
        Environment.objects.filter_for_user(request.user), pk=environment_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            environment.display_name,
            "connector_airflow:environment_detail",
            environment_id,
        ),
        (dag.display_name, "connector_airflow:dag_detail", environment_id, dag_id),
    ]

    return render(
        request,
        "connector_airflow/dag_detail.html",
        {
            "environment": environment,
            "dag": dag,
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_config_run(request, environment_id, dag_id, dag_config_id):
    get_object_or_404(
        Environment.objects.filter_for_user(request.user), pk=environment_id
    )
    get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_config = get_object_or_404(
        DAGConfig.objects.filter_for_user(request.user), pk=dag_config_id
    )
    run_result = dag_config.run()
    messages.success(request, run_result, extra_tags="green")

    return redirect(request.META.get("HTTP_REFERER"))
