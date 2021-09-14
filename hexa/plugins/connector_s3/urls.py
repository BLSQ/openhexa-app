from django.urls import path

from . import views

app_name = "connector_s3"

urlpatterns = [
    path("<str:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<str:bucket_id>/object/<path:path>",
        views.object_detail,
        name="object_detail",
    ),
    path(
        "<str:bucket_id>/object_download/<path:path>",
        views.object_download,
        name="object_download",
    ),
]
