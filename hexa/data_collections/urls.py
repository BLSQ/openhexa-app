from django.urls import path

from hexa.core import views_utils

app_name = "data_collections"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="index"),
    path(
        "<uuid:collection_id>",
        views_utils.redirect_to_new_frontend,
        name="collection_details",
    ),
    path("add", views_utils.redirect_to_new_frontend, name="manage_collections"),
]
