from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:datasource_id>/", views.datasource_detail, name="datasource_detail"),
    path("refresh/<str:datasource_id>/", views.datasource_refresh, name="datasource_refresh"),
]
