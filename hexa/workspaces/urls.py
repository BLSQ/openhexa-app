from django.urls import path

from . import views

app_name = "workspaces"

urlpatterns = [
    path("<str:workspace_slug>/credentials/", views.credentials, name="credentials"),
]
