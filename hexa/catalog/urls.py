from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("quick-search", views.quick_search, name="quick_search"),
    path("search", views.search, name="search"),
    path(
        "sync/<int:datasource_contenttype>/<str:datasource_id>",
        views.datasource_sync,
        name="datasource_sync",
    ),
]
