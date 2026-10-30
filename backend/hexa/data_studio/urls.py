from django.urls import path

from . import views

app_name = "data_studio"

urlpatterns = [
    path(
        "<str:workspace_slug>/query/download/",
        views.download_query_csv,
        name="download_query_csv",
    ),
    path(
        "queries/<str:slug>/download/",
        views.download_saved_query_csv,
        name="download_saved_query_csv",
    ),
]
