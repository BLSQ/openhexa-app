from django.urls import path

from . import views

app_name = "connector_dhis2"

urlpatterns = [
    path("<str:instance_id>", views.instance_detail, name="instance_detail"),
    path(
        "<str:instance_id>/data-elements/",
        views.data_element_list,
        name="data_element_list",
    ),
    path(
        "<str:instance_id>/data-elements/<str:data_element_id>",
        views.data_element_detail,
        name="data_element_detail",
    ),
    path(
        "<str:instance_id>/data-elements/<str:data_element_id>/update",
        views.data_element_update,
        name="data_element_update",
    ),
    path(
        "<str:instance_id>/data-elements/<str:data_element_id>/extract",
        views.data_element_extract,
        name="data_element_extract",
    ),
    path(
        "<str:instance_id>/indicators/",
        views.indicator_list,
        name="indicator_list",
    ),
    path(
        "<str:instance_id>/indicators/<str:indicator_id>",
        views.indicator_detail,
        name="indicator_detail",
    ),
    path(
        "<str:instance_id>/indicators/<str:indicator_id>/update",
        views.indicator_update,
        name="indicator_update",
    ),
    path(
        "<str:instance_id>/indicators/<str:indicator_id>/extract",
        views.indicator_extract,
        name="indicator_extract",
    ),
    path(
        "<str:instance_id>/sync",
        views.instance_sync,
        name="instance_sync",
    ),
    path(
        "extract/<str:extract_id>",
        views.extract_detail,
        name="extract_detail",
    ),
    path(
        "extract/<str:extract_id>/delete",
        views.extract_delete,
        name="extract_delete",
    ),
]
