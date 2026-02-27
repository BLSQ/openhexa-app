from django.urls import path

from . import views

urlpatterns = [
    path(
        "oauth-protected-resource",
        views.protected_resource_metadata,
        name="protected_resource_metadata",
    ),
    path(
        "oauth-authorization-server",
        views.oauth_server_metadata,
        name="oauth_server_metadata",
    ),
    path(
        "openid-configuration",
        views.openid_configuration,
        name="openid_configuration",
    ),
]
