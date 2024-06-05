from django.urls import path

from hexa.core import views_utils

from . import views

app_name = "pipelines"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="index"),
    path(
        "sync/<int:environment_contenttype_id>/<uuid:environment_id>",
        views.environment_sync,
        name="environment_sync",
    ),
    path("credentials/", views.credentials, name="credentials"),
    path(
        "<token>/run/<uuid:version_id>",
        views.run_pipeline,
        name="run_with_version",
    ),
    path("<token>/run", views.run_pipeline, name="run"),
]
