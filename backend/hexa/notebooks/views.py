from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from hexa.app import get_hexa_app_configs
from hexa.notebooks.credentials import NotebooksCredentials


@require_POST
def authenticate(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to authenticate the current user using Django
    session authentication.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {},
            status=401,
        )

    return JsonResponse(
        {"username": request.user.email},
        status=200,
    )


@require_POST
def default_credentials(request: HttpRequest) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials as env variables.
    Every connector plugin can provide its own set of credentials (environment variables for S3 for example).
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {},
            status=401,
        )

    notebooks_credentials = NotebooksCredentials(request.user)

    # Set "Git in notebooks" feature flag
    notebooks_credentials.update_env(
        {
            "GIT_EXTENSION_ENABLED": "true"
            if notebooks_credentials.user.has_feature_flag("notebooks_git_extension")
            else "false"
        }
    )

    for app_config in get_hexa_app_configs(connector_only=True):
        credentials_functions = app_config.get_notebooks_credentials()
        for credentials_function in credentials_functions:
            credentials_function(notebooks_credentials)

    return JsonResponse(
        notebooks_credentials.to_dict(),
        status=200,
    )


@require_POST
def credentials(request: HttpRequest) -> HttpResponse:
    """This view is deprecated but is still used by Airflow when running Notebooks using Papermill.
    See https://github.com/BLSQ/openhexa-dags/blob/6fc0f54f95c4f3a6b89b3fff37c91cbeb7c6be1c/dags/papermill.py#L83

    """
    notebooks_credentials = NotebooksCredentials(request.user)

    if request.user.is_authenticated:
        # Set "Git in notebooks" feature flag
        notebooks_credentials.update_env(
            {
                "GIT_EXTENSION_ENABLED": "true"
                if notebooks_credentials.user.has_feature_flag(
                    "notebooks_git_extension"
                )
                else "false"
            }
        )

        for app_config in get_hexa_app_configs(connector_only=True):
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
