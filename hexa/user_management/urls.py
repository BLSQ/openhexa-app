from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("accept_tos/", views.accept_tos, name="accept_tos"),
]
