from django.urls import path

from hexa.webapps.views import serve_webapp_bundle, serve_webapp_html

app_name = "webapps"

urlpatterns = [
    path(
        "<str:workspace_slug>/<str:webapp_slug>/html/",
        serve_webapp_html,
        name="serve-html",
    ),
    path(
        "<str:workspace_slug>/<str:webapp_slug>/bundle/",
        serve_webapp_bundle,
        name="serve-bundle-root",
    ),
    path(
        "<str:workspace_slug>/<str:webapp_slug>/bundle/<path:path>",
        serve_webapp_bundle,
        name="serve-bundle",
    ),
]
