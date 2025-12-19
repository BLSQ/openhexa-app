from django.urls import path

from hexa.superset.views import view_superset_dashboard

app_name = "superset"

urlpatterns = [
    path(
        "dashboard/<str:dashboard_id>/",
        view_superset_dashboard,
        name="dashboard",
    ),
]
