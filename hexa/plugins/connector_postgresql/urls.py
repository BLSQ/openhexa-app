from django.urls import path

from . import views

app_name = "connector_postgresql"

urlpatterns = [
    path("<str:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<str:datasource_id>/tables/",
        views.table_list,
        name="table_list",
    ),
    path(
        "<str:datasource_id>/tables/<str:table_id>",
        views.table_detail,
        name="table_detail",
    ),
    path(
        "<str:datasource_id>/sync",
        views.datasource_sync,
        name="datasource_sync",
    ),
]
