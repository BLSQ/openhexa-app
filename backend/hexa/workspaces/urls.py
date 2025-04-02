from django.urls import path

from . import views

app_name = "workspaces"

urlpatterns = [
    path(
        "<str:workspace_slug>/credentials/", views.credentials, name="credentials_old"
    ),  # This is deprecated and can be removed when the pipeline component is updated
    path("credentials/", views.credentials, name="credentials"),
]
