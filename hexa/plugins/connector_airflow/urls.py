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
        "<uuid:cluster_id>/<uuid:dag_id>/runs/<uuid:dag_run_id>",
        views.dag_run_detail,
        name="dag_run_detail",
    ),
]
