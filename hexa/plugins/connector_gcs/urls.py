from django.urls import path

from . import views

app_name = "connector_gcs"

urlpatterns = [
    path("<uuid:datasource_id>/", views.datasource_detail, name="datasource_detail"),
]
