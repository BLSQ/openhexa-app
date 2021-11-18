from django.urls import path

from . import views

app_name = "dashboards"

urlpatterns = [
    path("", views.dashboard_index, name="dashboard_index"),
    path("<uuid:dashboard_id>", views.dashboard_detail, name="dashboard_detail"),
    path("<uuid:dashboard_id>/image", views.dashboard_image, name="dashboard_image"),
]
