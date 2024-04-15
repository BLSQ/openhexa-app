from django.urls import path

from . import views

app_name = "connector_s3"

urlpatterns = [
    path(
        "<uuid:bucket_id>/object_download/<path:path>/",
        views.object_download,
        name="object_download",
    ),
    path(
        "<str:bucket_id>/object_upload/",
        views.object_upload,
        name="object_upload",
    ),
]
