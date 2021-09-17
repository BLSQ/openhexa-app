import uuid
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.datagrids import RunGrid
from hexa.plugins.connector_airflow.datacards import ClusterCard, DagCard, DagRunCard
from hexa.plugins.connector_airflow.datagrids import DagGrid, DagConfigGrid
from hexa.plugins.connector_airflow.models import (
    Cluster,
    DAG,
    DAGConfig,
    DAGRun,
)


def cluster_detail(request: HttpRequest, cluster_id: uuid.UUID) -> HttpResponse:
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
            cluster.name,
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


def dag_detail(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_card = DagCard(dag, request=request)
    if request.method == "POST" and dag_card.save():
        return redirect(request.META["HTTP_REFERER"])

    config_grid = DagConfigGrid(
        DAGConfig.objects.filter_for_user(request.user).filter(dag=dag)
    )
    run_grid = RunGrid(DAGRun.objects.filter_for_user(request.user).filter(dag=dag))

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
    ]

    return render(
        request,
        "connector_airflow/dag_detail.html",
        {
            "breadcrumbs": breadcrumbs,
            "dag": dag,
            "dag_card": dag_card,
            "config_grid": config_grid,
            "run_grid": run_grid,
        },
    )


def dag_run_detail(
    request: HttpRequest,
    cluster_id: uuid.UUID,
    dag_id: uuid.UUID,
    dag_run_id: uuid.UUID,
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_run = get_object_or_404(
        DAGRun.objects.filter_for_user(request.user), pk=dag_run_id
    )

    dag_run_card = DagRunCard(dag_run, request=request)
    if request.method == "POST" and dag_run_card.save():
        return redirect(request.META["HTTP_REFERER"])

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
        (f"Run {dag_run}",),
    ]

    return render(
        request,
        "connector_airflow/dag_run_detail.html",
        {
            "cluster": cluster,
            "dag_run_card": dag_run_card,
            "breadcrumbs": breadcrumbs,
        },
    )
