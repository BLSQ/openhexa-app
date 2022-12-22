from django.urls import path

from . import views

app_name = "pipelines"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "sync/<int:environment_contenttype_id>/<uuid:environment_id>",
        views.environment_sync,
        name="environment_sync",
    ),
    path("credentials/", views.credentials, name="credentials"),
]
