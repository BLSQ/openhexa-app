from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("ready", views.ready, name="ready"),
    path("dashboard", views.dashboard, name="dashboard"),
]
