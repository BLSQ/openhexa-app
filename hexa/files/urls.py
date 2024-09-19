from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("up/<str:token>/", views.upload_file, name="upload_file"),
    path("dl/<token>/", views.download_file, name="download_file"),
]
