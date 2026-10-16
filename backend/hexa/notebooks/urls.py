from django.urls import path

from hexa.core import views_utils

from . import views

app_name = "notebooks"

urlpatterns = [
    path("", views_utils.redirect_to_new_frontend, name="index"),
    path("authenticate/", views.authenticate, name="authenticate"),
    path("default-credentials/", views.default_credentials, name="default-credentials"),
    path("credentials/", views.credentials, name="credentials"),
]
