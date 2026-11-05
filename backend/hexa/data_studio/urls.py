from django.urls import path

from . import views

app_name = "data_studio"

urlpatterns = [
    path(
        "<str:workspace_slug>/query/download/",
        views.download_query_csv,
        name="download_query_csv",
    ),
    # One segment longer than the route above on purpose: any `<x>/<slug>/download/`
    # would be caught by it when the slug is "query", the slug generator's fallback.
    path(
        "public/queries/<str:slug>/download/",
        views.download_saved_query_csv,
        name="download_saved_query_csv",
    ),
]
