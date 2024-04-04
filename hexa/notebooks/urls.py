from django.urls import path

from . import views

app_name = "notebooks"

urlpatterns = [
    path("authenticate/", views.authenticate, name="authenticate"),
]
