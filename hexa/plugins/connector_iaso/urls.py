from django.urls import path

from . import views

app_name = "connector_iaso"

urlpatterns = [
    path("<uuid:datasource_id>/", views.datasource_detail, name="datasource_detail"),
    path(
        "<uuid:iasoaccount_id>/form/<int:iaso_id>/",
        views.form_detail,
        name="form_detail",
    ),
]
