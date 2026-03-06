from django.urls import path

from . import views

app_name = "webapps"

urlpatterns = [
    path("<uuid:webapp_id>/", views.serve_webapp, name="serve_webapp"),
    path("<uuid:webapp_id>/<path:path>", views.serve_webapp, name="serve_webapp_file"),
]
