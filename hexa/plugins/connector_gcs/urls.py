from django.urls import path

from . import views

app_name = "connector_gcs"

urlpatterns = [
    path("<uuid:datasource_id>/", views.datasource_detail, name="datasource_detail"),
    path(
        "<uuid:bucket_id>/object/<path:path>/",
        views.object_detail,
        name="object_detail",
    ),
    path(
        "<str:bucket_id>/bucket_refresh/",
        views.bucket_refresh,
        name="bucket_refresh",
    ),
]
