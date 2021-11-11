from django.urls import path

from . import views

app_name = "pipelines"

urlpatterns = [
    path("", views.index, name="index"),
    path("refresh", views.index_refresh, name="index_refresh"),
    path(
        "sync/<int:environment_contenttype_id>/<uuid:environment_id>",
        views.environment_sync,
        name="environment_sync",
    ),
]
