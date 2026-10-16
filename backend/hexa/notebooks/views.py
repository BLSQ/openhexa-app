import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from hexa.app import get_hexa_app_configs
from hexa.assistant import telemetry
from hexa.notebooks.credentials import NotebooksCredentials
from hexa.workspaces.authentication import WorkspaceToken

logger = logging.getLogger(__name__)


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


def _workspace_token(request: HttpRequest) -> WorkspaceToken | None:
    """The workspace token of a telemetry request.

    The middleware already resolved a "Bearer <token>" header. OpenTelemetry
    exporters configure headers through a `key=value` string whose values
    cannot always carry a space, so the bare token is accepted too, as
    Logfire's own OTLP endpoint does.
    """
    token = getattr(request, "workspace_token", None)
    if token is not None:
        return token
    raw_token = request.headers.get("Authorization", "").strip()
    if not raw_token or " " in raw_token:
        return None
    return WorkspaceToken.authenticate(raw_token)


@require_POST
@csrf_exempt
def telemetry_view(request: HttpRequest, signal: str) -> HttpResponse:
    """OTLP/HTTP receiver for the AI tooling of the notebook servers.

    Records the token usage of the organization's models and forwards the
    payload to Logfire; see `hexa.assistant.telemetry`. Always answers 200 once
    the payload was understood: the exporter would otherwise send it again.
    """
    token = _workspace_token(request)
    if token is None:
        return JsonResponse({"error": "Invalid workspace token"}, status=401)
    if signal not in telemetry.SIGNALS:
        return JsonResponse({"error": f"Unknown signal {signal!r}"}, status=404)
    try:
        message = telemetry.parse_request(
            signal,
            request.body,
            content_type=request.content_type,
            content_encoding=request.headers.get("Content-Encoding"),
        )
    except telemetry.TelemetryError as e:
        return JsonResponse({"error": str(e)}, status=400)

    workspace = token.workspace
    if signal == "traces":
        try:
            telemetry.record_usage(
                message,
                organization=workspace.organization,
                workspace=workspace,
                user=token.user,
            )
        except Exception:
            logger.exception("Could not record the AI usage of %s", workspace.slug)

    target = telemetry.logfire_target()
    if target is not None:
        telemetry.stamp_identity(
            message,
            organization=workspace.organization,
            workspace=workspace,
            user=token.user,
        )
        telemetry.forward_to_logfire(signal, message.SerializeToString(), target)

    # An empty Export<Signal>ServiceResponse: full success.
    return HttpResponse(b"", content_type=telemetry.PROTOBUF_CONTENT_TYPE)
