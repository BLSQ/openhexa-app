from django.urls import path

from . import views

app_name = "dhis2connector"

urlpatterns = [
    path("<str:datasource_id>", views.datasource_detail, name="datasource_detail"),
    path(
        "<str:datasource_id>/data-elements",
        views.data_element_list,
        name="data_element_list",
    ),
    path(
        "<str:datasource_id>/data-elements/<str:data_element_id>",
        views.data_element_detail,
        name="data_element_detail",
    ),
    path(
        "<str:datasource_id>/indicators",
        views.indicator_list,
        name="indicator_list",
    ),
    path(
        "<str:datasource_id>/indicators/<str:data_element_id>",
        views.data_element_detail,
        name="indicator_detail",
    ),
]
