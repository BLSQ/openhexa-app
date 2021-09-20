from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hexa.notebooks.credentials import NotebooksCredentials
from hexa.plugins.app import get_connector_app_configs


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request, "notebooks/index.html", {"notebooks_url": settings.NOTEBOOKS_URL}
    )


@require_http_methods(["POST"])
@csrf_exempt  # TODO: we should remove this
def credentials(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    notebooks_credentials = NotebooksCredentials(request.user)

    if request.user.is_authenticated:
        for app_config in get_connector_app_configs():
            credentials_functions = app_config.get_notebooks_credentials()
            for credentials_function in credentials_functions:
                credentials_function(notebooks_credentials)

    if notebooks_credentials.authenticated:
        return JsonResponse(
            notebooks_credentials.to_dict(),
            status=200,
        )

    return JsonResponse(
        {},
        status=401,
    )
