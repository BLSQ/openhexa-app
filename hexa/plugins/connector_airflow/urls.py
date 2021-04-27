from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:cluster_id>",
        views.cluster_detail,
        name="cluster_detail",
    ),
    path("<str:cluster_id>/<str:dag_id>", views.dag_detail, name="dag_detail"),
    path(
        "<str:cluster_id>/<str:dag_id>/<str:dag_config_id>",
        views.dag_config_run,
        name="dag_config_run",
    ),
    path(
        "<str:cluster_id>/<str:dag_id>/configs/",
        views.dag_config_list,
        name="dag_config_list",
    ),
    path(
        "<str:cluster_id>/<str:dag_id>/config_runs/",
        views.dag_config_run_list,
        name="dag_config_run_list",
    ),
]
