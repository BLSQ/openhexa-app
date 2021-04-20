from django.urls import path

from . import views

app_name = "connector_airflow"

urlpatterns = [
    path(
        "<str:environment_id>",
        views.environment_detail,
        name="environment_detail",
    ),
    path(
        "<str:environment_id>/sync",
        views.environment_sync,
        name="environment_sync",
    ),
]
