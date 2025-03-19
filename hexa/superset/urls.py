from django.urls import path

from hexa.superset.views import (
    view_superset_dashboard,
    view_superset_dashboard_by_external_id,
)

app_name = "superset"

urlpatterns = [
    path(
        "dashboard/external/<str:external_id>/",
        view_superset_dashboard_by_external_id,
        name="dashboard-external",
    ),
    path(
        "dashboard/<str:dashboard_id>/",
        view_superset_dashboard,
        name="dashboard",
    ),
]
