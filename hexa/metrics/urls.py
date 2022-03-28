from django.urls import path

from . import views

app_name = "metrics"

urlpatterns = [
    path("save_redirect/", views.save_redirect, name="save_redirect"),
]
