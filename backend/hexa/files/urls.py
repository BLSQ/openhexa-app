from django.urls import path, re_path

from . import views

app_name = "files"

urlpatterns = [
    path("up/<str:token>/", views.upload_file, name="upload_file"),
    path("dl/<token>/", views.download_file, name="download_file"),
    # `.*` rather than the `path` converter so the folder's base URL (empty path)
    # can be reversed; the view rejects it.
    re_path(
        r"^public/(?P<workspace_slug>[\w-]+)/(?P<path>.*)$",
        views.public_file,
        name="public_file",
    ),
]
