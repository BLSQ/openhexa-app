from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("ready", views.ready, name="ready"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("test_logger", views.test_logger, name="test_logger"),
    path("collections/", views.collections, name="collections"),
]
