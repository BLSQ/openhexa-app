from django.urls import include, path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
]
