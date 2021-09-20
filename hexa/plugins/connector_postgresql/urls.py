from django.urls import path

from . import views

app_name = "connector_postgresql"

urlpatterns = [
    path("<uuid:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<uuid:datasource_id>/tables/",
        views.table_list,
        name="table_list",
    ),
    path(
        "<uuid:datasource_id>/tables/<uuid:table_id>",
        views.table_detail,
        name="table_detail",
    ),
]
