from django.urls import path

from . import views

app_name = "connector_accessmod"

urlpatterns = [
    path(
        "webhook/",
        views.webhook,
        name="webhook",
    ),
]
