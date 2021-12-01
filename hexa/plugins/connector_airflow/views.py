import json
import uuid
from logging import getLogger

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from hexa.pipelines.datagrids import RunGrid
from hexa.plugins.connector_airflow.api import AirflowAPIError
from hexa.plugins.connector_airflow.datacards import ClusterCard, DAGCard, DAGRunCard
from hexa.plugins.connector_airflow.datagrids import DAGGrid
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRun

logger = getLogger(__name__)


def cluster_detail(request: HttpRequest, cluster_id: uuid.UUID) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.prefetch_indexes().filter_for_user(request.user),
        pk=cluster_id,
    )

    cluster_card = ClusterCard(cluster, request=request)
    if request.method == "POST" and cluster_card.save():
        return redirect(request.META["HTTP_REFERER"])

    dag_grid = DAGGrid(
        cluster.dag_set.prefetch_indexes(),
        page=int(request.GET.get("page", "1")),
        request=request,
    )

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


def cluster_detail_refresh(request: HttpRequest, cluster_id: uuid.UUID) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.filter_for_user(request.user),
        pk=cluster_id,
    )

    for dag in cluster.dag_set.all():
        last_run = dag.dagrun_set.filter_for_refresh().first()
        if last_run is not None:
            try:
                last_run.refresh()
            except AirflowAPIError:
                logger.exception(f"Refresh failed for DAGRun {last_run.id}")

    return cluster_detail(request, cluster_id=cluster_id)


def dag_detail(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.prefetch_indexes().filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(
        DAG.objects.prefetch_related().filter_for_user(request.user), pk=dag_id
    )
    dag_card = DAGCard(dag, request=request)
    if request.method == "POST" and dag_card.save():
        return redirect(request.META["HTTP_REFERER"])

    run_grid = RunGrid(
        DAGRun.objects.filter_for_user(request.user)
        .filter(dag=dag)
        .order_by("-execution_date"),
        request=request,
    )

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
            "dag": dag,
            "breadcrumbs": breadcrumbs,
            "dag_card": dag_card,
            "run_grid": run_grid,
        },
    )


def dag_detail_refresh(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    for run in dag.dagrun_set.filter_for_refresh():
        try:
            run.refresh()
        except AirflowAPIError:
            logger.exception(f"Refresh failed for DAGRun {run.id}")

    return dag_detail(request, cluster_id=cluster_id, dag_id=dag_id)


def dag_run_create(
    request: HttpRequest, cluster_id: uuid.UUID, dag_id: uuid.UUID
) -> HttpResponse:
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    dag = get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)

    error = None
    if (
        request.method == "POST"
    ):  # POST: attempt to parse and validate run config (if any)
        if "dag_config" in request.POST and len(request.POST["dag_config"]) > 0:
            try:
                run_config = json.loads(request.POST["dag_config"])
            except (KeyError, ValueError, TypeError):
                run_config = request.POST["dag_config"]
                error = _("Invalid config provided. Please use valid JSON.")
        else:
            run_config = {}
        if error is None:
            dag_run = dag.run(config=run_config)
            return redirect(dag_run.get_absolute_url())
    elif "conf_from" in request.GET:  # GET: use sample config to pre-fill the form
        cloned_dag = get_object_or_404(
            DAGRun.objects.filter_for_user(request.user).filter(
                dag=dag, pk=request.GET["conf_from"]
            )
        )
        run_config = cloned_dag.conf
    else:
        run_config = dag.sample_config

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            dag.cluster.name,
            "connector_airflow:cluster_detail",
            dag.cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
        (_("Run with config"),),
    ]

    return render(
        request,
        "connector_airflow/dag_run_create.html",
        {
            "dag": dag,
            "error": error,
            "run_config": json.dumps(run_config, indent=2)
            if error is None
            else run_config,
            "sample_config": json.dumps(dag.sample_config, indent=2),
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_run_detail(
    request: HttpRequest,
    cluster_id: uuid.UUID,
    dag_id: uuid.UUID,
    dag_run_id: uuid.UUID,
) -> HttpResponse:
    cluster = get_object_or_404(
        Cluster.objects.prefetch_indexes().filter_for_user(request.user), pk=cluster_id
    )
    dag = get_object_or_404(
        DAG.objects.prefetch_indexes().filter_for_user(request.user), pk=dag_id
    )
    dag_run = get_object_or_404(
        DAGRun.objects.filter_for_user(request.user), pk=dag_run_id
    )

    dag_run_card = DAGRunCard(dag_run, request=request)

    breadcrumbs = [
        (_("Data Pipelines"), "pipelines:index"),
        (
            cluster.name,
            "connector_airflow:cluster_detail",
            cluster_id,
        ),
        (dag, "connector_airflow:dag_detail", cluster_id, dag_id),
        (f"Run {dag_run.run_id}",),
    ]

    return render(
        request,
        "connector_airflow/dag_run_detail.html",
        {
            "dag_run": dag_run,
            "dag_run_card": dag_run_card,
            "breadcrumbs": breadcrumbs,
        },
    )


def dag_run_detail_refresh(
    request: HttpRequest,
    cluster_id: uuid.UUID,
    dag_id: uuid.UUID,
    dag_run_id: uuid.UUID,
) -> HttpResponse:
    get_object_or_404(Cluster.objects.filter_for_user(request.user), pk=cluster_id)
    get_object_or_404(DAG.objects.filter_for_user(request.user), pk=dag_id)
    dag_run = get_object_or_404(
        DAGRun.objects.filter_for_user(request.user), pk=dag_run_id
    )

    try:
        dag_run.refresh()
    except AirflowAPIError:
        logger.exception(f"Refresh failed for DAGRun {dag_run.id}")

    return dag_run_detail(
        request, cluster_id=cluster_id, dag_id=dag_id, dag_run_id=dag_run_id
    )
