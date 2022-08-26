"""hexa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from ariadne_django.views import GraphQLView
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from hexa.app import get_hexa_app_configs

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
    # Order matters, we override the default logout view defined later
    # We do this to logout the user from jupyterhub at the end of the openhexa
    # session. the jupyterhub will redirect to the openhexa login after it
    # TODO: use API (https://github.com/jupyterhub/jupyterhub/issues/3688)
    path(
        "auth/logout/",
        auth_views.LogoutView.as_view(next_page=f"{settings.NOTEBOOKS_URL}/hub/logout"),
        name="logout",
    ),
    path("auth/", include("django.contrib.auth.urls")),
    re_path(
        r"^graphql/([\w+\/]*?)?$",
        GraphQLView.as_view(
            schema=schema, playground_options={"request.credentials": "include"}
        )
        if settings.ENABLE_GRAPHQL is True
        else TemplateView.as_view(template_name="404.html"),
        name="graphql",
    ),
]

# Connector apps URLs
for app_config in get_hexa_app_configs(connector_only=True):
    urlpatterns.append(
        path(
            app_config.route_prefix + "/",
            include(app_config.name + ".urls", namespace=app_config.label),
        )
    )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
