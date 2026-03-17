from django.urls import path

from . import views

app_name = "mcp"

urlpatterns = [
    path("", views.mcp_endpoint, name="mcp_endpoint"),
    path("tools.json", views.tools_json, name="tools_json"),
]
