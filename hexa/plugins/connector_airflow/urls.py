from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:environment_id>",
        views.environment_detail,
        name="environment_detail",
    ),
    path("<str:environment_id>/<str:airflow_id>", views.dag_detail, name="dag_detail"),
    path(
        "<str:environment_id>/<str:airflow_id>/<str:dag_config_id>",
        views.dag_config_run,
        name="dag_config_run",
    ),
    path(
        "<str:environment_id>/<str:airflow_id>/<str:dag_config_id>/<str:dag_config_run_id>",
        views.dag_config_run_status,
        name="dag_config_run_status",
    ),
]
