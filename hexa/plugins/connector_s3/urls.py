from django.urls import path

from . import views

app_name = "connector_s3"

urlpatterns = [
    path("<str:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<str:datasource_id>/sync",
        views.datasource_sync,
        name="datasource_sync",
    ),
]
