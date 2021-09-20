from django.urls import path

from . import views

app_name = "connector_s3"

urlpatterns = [
    path("<uuid:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<uuid:bucket_id>/object/<path:path>",
        views.object_detail,
        name="object_detail",
    ),
    path(
        "<uuid:bucket_id>/object_download/<path:path>",
        views.object_download,
        name="object_download",
    ),
    path(
        "<str:bucket_id>/object_upload/",
        views.object_upload,
        name="object_upload",
    ),
]
