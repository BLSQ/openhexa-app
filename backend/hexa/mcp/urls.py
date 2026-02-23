from django.urls import path

from . import views

app_name = "mcp"

urlpatterns = [
    path("", views.mcp_endpoint, name="mcp_endpoint"),
    path(
        "register/",
        views.dynamic_client_registration,
        name="dynamic_client_registration",
    ),
    path(
        "register",
        views.dynamic_client_registration,
        name="dynamic_client_registration_no_slash",
    ),
]
