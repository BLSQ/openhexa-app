from django.urls import include, path

from . import views

app_name = "auth"

urlpatterns = [
    path("logout/", views.logout, name="logout"),  # prioritize over Django default
    path("account/", views.account, name="account"),
    path("", include("django.contrib.auth.urls")),
]
