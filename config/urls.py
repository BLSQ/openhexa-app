"""hexa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/

Examples
--------
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
from django.urls import include, path, re_path

from hexa.app import get_hexa_app_configs
from hexa.user_management.views import LogoutView

from .schema import schema

admin.site.site_header = "OpenHEXA Admin"
admin.site.site_title = "OpenHEXA Admin"
admin.site.index_title = "Welcome to OpenHEXA"

# Core URLs
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hexa.core.urls", namespace="core")),
    path("notebooks/", include("hexa.notebooks.urls", namespace="notebooks")),
    path("pipelines/", include("hexa.pipelines.urls", namespace="pipelines")),
    path("workspaces/", include("hexa.workspaces.urls", namespace="workspaces")),
    path("files/", include("hexa.files.urls", namespace="files")),
    path("analytics/", include("hexa.analytics.urls", namespace="analytics")),
    path("superset/", include("hexa.superset.urls", namespace="superset")),
    # Order matters, we override the default logout view defined later
    # We do this to logout the user from jupyterhub at the end of the openhexa
    # session. the jupyterhub will redirect to the openhexa login after it
    # TODO: use API (https://github.com/jupyterhub/jupyterhub/issues/3688)
    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("auth/", include("django.contrib.auth.urls")),
    re_path(
        r"^graphql/([\w+\/]*?)?$",
        GraphQLView.as_view(
            schema=schema, playground_options={"request.credentials": "include"}
        ),
        name="graphql",
    ),
]

# Connector apps URLs
for app_config in get_hexa_app_configs(connector_only=True):
    try:
        prefix = app_config.route_prefix or ""
        urlpatterns.append(
            path(
                prefix + "/",
                include(app_config.name + ".urls", namespace=app_config.label),
            )
        )
    except (NotImplementedError, ModuleNotFoundError):
        pass

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
