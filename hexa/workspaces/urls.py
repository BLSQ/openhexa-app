from django.urls import path

from . import views

app_name = "workspaces"

urlpatterns = [
    path("credentials/<str:workspace_slug>", views.credentials, name="credentials"),
]
