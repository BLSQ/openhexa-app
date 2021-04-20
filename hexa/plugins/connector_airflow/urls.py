from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:pipeline_environment_id>",
        views.pipeline_environment_detail,
        name="pipeline_environment_detail",
    ),
    path(
        "<str:pipeline_id>/sync",
        views.pipeline_environment_sync,
        name="datasource_sync",
    ),
]
