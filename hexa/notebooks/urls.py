from django.urls import path

from hexa.core import views_utils

from . import views

app_name = "notebooks"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="index"),
    path("credentials/", views.credentials, name="credentials"),
]
