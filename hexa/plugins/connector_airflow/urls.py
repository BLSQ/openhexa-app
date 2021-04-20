from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:pipeline_server_id>",
        views.pipeline_server_detail,
        name="pipeline_server_detail",
    ),
    path(
        "<str:pipeline_id>/sync",
        views.pipeline_server_sync,
        name="datasource_sync",
    ),
]
