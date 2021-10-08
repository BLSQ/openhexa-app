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
        "<uuid:cluster_id>/<uuid:dag_id>",
        views.dag_detail,
        name="dag_detail",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/refresh",
        views.dag_run_list_refresh,
        name="dag_run_list_refresh",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/run",
        views.new_dag_run,
        name="new_dag_run",
    ),
    path(
        "<uuid:cluster_id>/sync",
        views.sync,
        name="sync",
    ),
    path(
        "<uuid:cluster_id>/<uuid:dag_id>/runs/<uuid:dag_run_id>",
        views.dag_run_detail,
        name="dag_run_detail",
    ),
]
