from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<uuid:cluster_id>",
        views.cluster_detail,
        name="cluster_detail",
    ),
    path(
        "<uuid:cluster_id>/refresh",
        views.cluster_detail_refresh,
        name="cluster_detail_refresh",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>",
        views.dag_detail,
        name="dag_detail",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/refresh",
        views.dag_detail_refresh,
        name="dag_detail_refresh",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/run",
        views.dag_run_create,
        name="dag_run_create",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/runs/<uuid:dag_run_id>",
        views.dag_run_detail,
        name="dag_run_detail",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/runs/<uuid:dag_run_id>/refresh",
        views.dag_run_detail_refresh,
        name="dag_run_detail_refresh",
    ),
    path(
        "<uuid:cluster_id>/sync",
        views.sync,
        name="sync",
    ),
]
