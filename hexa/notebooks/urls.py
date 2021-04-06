from django.urls import path

from . import views

app_name = "notebooks"

urlpatterns = [
    path("", views.index, name="index"),
    path("run", views.run, name="run"),
    path("credentials", views.credentials, name="credentials"),
]
