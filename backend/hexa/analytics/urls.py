from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("track/", views.track_event, name="track"),
]
