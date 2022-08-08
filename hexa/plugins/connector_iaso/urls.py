from django.urls import path

from . import views

app_name = "connector_iaso"

urlpatterns = [
    path("<uuid:datasource_id>/", views.datasource_detail, name="datasource_detail"),
    path("<uuid:datasource_id>/forms/", views.form_index, name="form_index"),
    path(
        "<uuid:account_id>/form/<int:iaso_id>/",
        views.form_detail,
        name="form_detail",
    ),
    path("<uuid:datasource_id>/ou/", views.orgunit_index, name="orgunit_index"),
    path(
        "<uuid:account_id>/ou/<int:iaso_id>/",
        views.orgunit_detail,
        name="orgunit_detail",
    ),
]
