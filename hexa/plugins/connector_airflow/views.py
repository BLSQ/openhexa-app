from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.plugins.connector_airflow.datacards import ClusterCard
from hexa.plugins.connector_airflow.datagrids import DagGrid
from hexa.plugins.connector_airflow.models import (
    Cluster,
    DAG,
    DAGConfig,
    DAGConfigRun,
    DAGConfigRunState,
)


def cluster_detail(request, cluster_id):
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user),
        pk=cluster_id,
    )

    cluster_card = ClusterCard(cluster, request=request)
    if request.method == "POST" and cluster_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dag_grid = DagGrid(cluster.dag_set.all(), page=int(request.GET.get("page", "1")))

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.display_name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
    ]

    return render(
        request,
        "connector_airflow/cluster_detail.html",
        {
            "cluster": cluster,
            "cluster_card": cluster_card,
            "dag_grid": dag_grid,
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_detail(request, cluster_id, dag_id):
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_configs = DAGConfig.objects.filter_for_user(request.user).filter(dag=dag)
    dag_config_runs = DAGConfigRun.objects.filter_for_user(request.user).filter_by_dag(
        dag
    )

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.display_name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag.display_name, "connector_airflow:dag_detail", cluster_id, dag_id),
    ]

    return render(
        request,
        "connector_airflow/dag_detail.html",
        {
            "breadcrumbs": breadcrumbs,
            "cluster": cluster,
            "dag": dag,
            "dag_configs": dag_configs,
            "dag_config_runs": dag_config_runs,
        },
    )


def dag_config_run(request, cluster_id, dag_id, dag_config_id):
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_config = get_object_or_404(
        DAGConfig.objects.filter_for_user(request.user), pk=dag_config_id
    )
    run_result = dag_config.run()
    messages.success(request, run_result)

    return redirect(f"{request.META.get('HTTP_REFERER')}#dag_config_runs")


def dag_config_list(request, cluster_id, dag_id):
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_configs = DAGConfig.objects.filter_for_user(request.user).filter(dag=dag)

    return render(
        request,
        "connector_airflow/components/dag_config_list.html",
        {
            "dag": dag,
            "dag_configs": dag_configs,
        },
    )


def dag_config_run_list(request, cluster_id, dag_id):
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_configs = DAGConfig.objects.filter_for_user(request.user).filter(dag=dag)
    dag_config_runs = DAGConfigRun.objects.filter_for_user(request.user).filter(
        dag_config__dag=dag
    )

    # TODO: actual refresh should be done using a CRON
    for run in dag_config_runs.filter(airflow_state=DAGConfigRunState.RUNNING):
        run.refresh()

    return render(
        request,
        "connector_airflow/components/dag_config_run_list.html",
        {
            "dag": dag,
            "dag_configs": dag_configs,
            "dag_config_runs": dag_config_runs,
        },
    )
