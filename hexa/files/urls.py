from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("up/", views.upload_file),
    path("up/<token:str>", views.upload_file, name="upload_file"),
    path("dl/<token:str>", views.download_file, name="download_file"),
]
