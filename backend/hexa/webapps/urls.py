from django.urls import path

from . import views

app_name = "webapps"

urlpatterns = [
    path("<uuid:webapp_id>/auth-token/", views.auth_token, name="auth_token"),
    path("dev.js", views.dev_js, name="dev_js"),
    path("dev-auth/", views.dev_auth, name="dev_auth"),
]
