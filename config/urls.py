from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from hexa.core.graphql.view import SecureGraphQLView
from hexa.plugins.app import get_connector_app_configs

from .schema import schema

admin.site.site_header = "OpenHexa Admin"
admin.site.site_title = "OpenHexa Admin"
admin.site.index_title = "Welcome to OpenHexa"

# Core URLs
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hexa.core.urls", namespace="core")),
    path("user/", include("hexa.user_management.urls", namespace="user")),
    path("catalog/", include("hexa.catalog.urls", namespace="catalog")),
    path(
        "visualizations/",
        include("hexa.visualizations.urls", namespace="visualizations"),
    ),
    path("notebooks/", include("hexa.notebooks.urls", namespace="notebooks")),
    path("pipelines/", include("hexa.pipelines.urls", namespace="pipelines")),
    path("metrics/", include("hexa.metrics.urls", namespace="metrics")),
    path("comments/", include("hexa.comments.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path(
        "graphql/",
        SecureGraphQLView.as_view(
            schema=schema, playground_options={"request.credentials": "include"}
        )
        if settings.ENABLE_GRAPHQL is True
        else TemplateView.as_view(template_name="404.html"),
        name="graphql",
    ),
]

# Connector apps URLs
for app_config in get_connector_app_configs():
    urlpatterns.append(
        path(
            app_config.route_prefix + "/",
            include(app_config.name + ".urls", namespace=app_config.label),
        )
    )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
