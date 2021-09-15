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
        "<str:instance_id>/indicators/<str:indicator_id>/extract",
        views.indicator_extract,
        name="indicator_extract",
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
    path(
        "<str:instance_id>/datasets/",
        views.dataset_list,
        name="dataset_list",
    ),
    path(
        "<str:instance_id>/datasets/<str:dataset_id>",
        views.dataset_detail,
        name="dataset_detail",
    ),
]
