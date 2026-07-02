from django.urls import path

from hexa.git import views

app_name = "git"

urlpatterns = [
    path("authorize", views.authorize, name="authorize"),
]
