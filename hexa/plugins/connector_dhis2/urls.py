from django.urls import path

from . import views

app_name = "connector_dhis2"

urlpatterns = [
    path("<uuid:instance_id>", views.instance_detail, name="instance_detail"),
    path(
        "<uuid:instance_id>/data-elements/",
        views.data_element_list,
        name="data_element_list",
    ),
    path(
        "<uuid:instance_id>/data-elements/download",
        views.data_element_download,
        name="data_element_download",
    ),
    path(
        "<uuid:instance_id>/data-elements/<uuid:data_element_id>",
        views.data_element_detail,
        name="data_element_detail",
    ),
    path(
        "<uuid:instance_id>/org-units/",
        views.organisation_unit_list,
        name="organisation_unit_list",
    ),
    path(
        "<uuid:instance_id>/org-units/download",
        views.organisation_unit_download,
        name="organisation_unit_download",
    ),
    path(
        "<uuid:instance_id>/org-units/<uuid:organisation_unit_id>",
        views.organisation_unit_detail,
        name="organisation_unit_detail",
    ),
    path(
        "<uuid:instance_id>/indicators/",
        views.indicator_list,
        name="indicator_list",
    ),
    path(
        "<uuid:instance_id>/indicators/download",
        views.indicator_download,
        name="indicator_download",
    ),
    path(
        "<uuid:instance_id>/indicators/<uuid:indicator_id>",
        views.indicator_detail,
        name="indicator_detail",
    ),
    path(
        "<uuid:instance_id>/datasets/",
        views.dataset_list,
        name="dataset_list",
    ),
    path(
        "<uuid:instance_id>/datasets/download",
        views.dataset_download,
        name="dataset_download",
    ),
    path(
        "<uuid:instance_id>/datasets/<uuid:dataset_id>",
        views.dataset_detail,
        name="dataset_detail",
    ),
]
