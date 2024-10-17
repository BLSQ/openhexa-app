from django.urls import path, re_path

from . import views

app_name = "files"

urlpatterns = [
    path("up/<str:token>/", views.upload_file, name="upload_file"),
    path("dl/<token>/", views.download_file, name="download_file"),
    re_path(
        r"^public/(?P<workspace_slug>[\w.\-_]+)(?P<path>/[\w.\s\(\)\-_/]*)$",
        views.public_file_access,
        name="public_file_access",
    ),
]
