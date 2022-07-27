from django.urls import path

from . import views

app_name = "connector_iaso"

urlpatterns = [
    path("<uuid:datasource_id>/", views.datasource_index, name="datasource_index"),
    path(
        "<uuid:iasoaccount_id>/form/<int:iaso_id>/",
        views.iasoform_detail,
        name="iasoform_detail",
    ),
]
