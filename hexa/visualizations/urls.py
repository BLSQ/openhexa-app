from django.urls import path

from hexa.core import views_utils

from . import views

app_name = "visualizations"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="visualization_index"),
    path(
        "<uuid:dashboard_id>/",
        views_utils.redirect_to_new_frontend,
        name="dashboard_detail",
    ),
    path("<uuid:dashboard_id>/image/", views.dashboard_image, name="dashboard_image"),
]
