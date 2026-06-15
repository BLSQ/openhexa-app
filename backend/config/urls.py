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

import allauth.urls
from ariadne_django.views import GraphQLView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from hexa.app import get_hexa_app_configs
from hexa.mcp.views import mcp_endpoint
from hexa.user_management.sso.sso_views import (
    make_compat_callback_view,
    make_compat_login_view,
)
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
    path("assistant/", include("hexa.assistant.urls", namespace="assistant")),
    path("pipelines/", include("hexa.pipelines.urls", namespace="pipelines")),
    path("workspaces/", include("hexa.workspaces.urls", namespace="workspaces")),
    path("files/", include("hexa.files.urls", namespace="files")),
    path("analytics/", include("hexa.analytics.urls", namespace="analytics")),
    path("superset/", include("hexa.superset.urls", namespace="superset")),
    path("oauth/", include("hexa.oauth.urls")),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("mcp", mcp_endpoint, name="mcp_endpoint_no_slash"),
    path("mcp/", include("hexa.mcp.urls", namespace="mcp")),
    path(".well-known/", include("hexa.oauth.wellknown_urls")),
    path("webapps/", include("hexa.webapps.urls", namespace="webapps")),
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

# allauth URLs are mounted unconditionally (not only when OIDC_PROVIDERS is
# set): reverse("openid_connect_login") must work regardless of the
# environment — the GraphQL config resolver builds provider login URLs with
# it, and tests override OIDC_PROVIDERS after the URLconf has been built at
# import time. allauth raises Http404 for providers that are not configured,
# and login_required_middleware keeps everything except the ANONYMOUS_URLS
# names behind the login screen.
urlpatterns.append(path("accounts/", include(allauth.urls)))

if settings.OIDC_PROVIDERS:
    for _provider in settings.OIDC_PROVIDERS:
        _callback_path = _provider.get("callback_path", "")
        if _callback_path:
            urlpatterns.append(
                path(
                    _callback_path,
                    make_compat_callback_view(_provider["id"], _callback_path),
                )
            )
            _login_path = _provider.get("login_path", "")
            if _login_path:
                urlpatterns.append(
                    path(
                        _login_path,
                        make_compat_login_view(_provider["id"], _callback_path),
                    )
                )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
