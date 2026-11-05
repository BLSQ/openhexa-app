from django.urls import path, re_path

from . import views

app_name = "files"

urlpatterns = [
    path("up/<str:token>/", views.upload_file, name="upload_file"),
    path("dl/<token>/", views.download_file, name="download_file"),
    # The path may be empty so that the base URL can be reversed, the view returns a 404.
    re_path(
        r"^public/(?P<workspace_slug>[-a-z0-9]+)/(?P<path>.*)$",
        views.public_file,
        name="public_file",
    ),
]
