from django.urls import path

from . import views

urlpatterns = [
    path("authorize/", views.OAuthAuthorizeView.as_view(), name="oauth2_authorize"),
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
        "token/.well-known/openid-configuration",
        views.openid_configuration,
        name="oauth_token_openid_configuration",
    ),
]
