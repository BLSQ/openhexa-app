from django.urls import path

from . import views

app_name = "mcp"

urlpatterns = [
    path("", views.mcp_endpoint, name="mcp_endpoint"),
    path("tools/", views.tools_page, name="tools_page"),
    path("login/", views.oauth_login, name="oauth_login"),
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
    path(
        ".well-known/oauth-authorization-server",
        views.oauth_server_metadata,
        name="mcp_oauth_server_metadata",
    ),
    path(
        ".well-known/oauth-protected-resource",
        views.protected_resource_metadata,
        name="mcp_protected_resource_metadata",
    ),
    path(
        ".well-known/openid-configuration",
        views.openid_configuration,
        name="mcp_openid_configuration",
    ),
]
