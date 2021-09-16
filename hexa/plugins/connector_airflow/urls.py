from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:cluster_id>",
        views.cluster_detail,
        name="cluster_detail",
    ),
    path(
        "<str:cluster_id>/<str:dag_id>",
        views.dag_detail,
        name="dag_detail",
    ),
    path(
        "<str:cluster_id>/<str:dag_id>/runs/<str:dag_run_id>",
        views.dag_run_detail,
        name="dag_run_detail",
    ),
]
