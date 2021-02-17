from django.urls import path

from . import views

app_name = "dhis2connector"

urlpatterns = [
    path(
        "<str:datasource_id>/data-elements",
        views.data_element_list,
        name="data_element_list",
    ),
]
