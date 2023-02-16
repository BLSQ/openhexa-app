from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST


@require_POST
@login_required
def credentials(request: HttpRequest, workspace_slug: str) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    return JsonResponse(
        {"WORKSPACE_FOO": f"WORKSPACE_BAR_{workspace_slug}"},
        status=200,
    )
