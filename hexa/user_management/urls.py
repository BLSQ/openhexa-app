from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("account", views.account, name="account"),
    path("info", views.info, name="info"),
]
