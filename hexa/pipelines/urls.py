from django.urls import path

from . import views

app_name = "pipelines"

urlpatterns = [
    path(
        "<uuid:id>/run/<int:version_number>",
        views.run_pipeline,
        name="run_with_version",
    ),
    path("<uuid:id>/run", views.run_pipeline, name="run"),
]
