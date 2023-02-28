from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from hexa.workspaces.models import Workspace


@require_POST
@login_required
def credentials(request: HttpRequest, workspace_slug: str) -> HttpResponse:
    """This API endpoint is called by the notebooks component to get credentials for Jupyterhub.
    In addition to basic user information, every connector plugin can provide its own set of credentials (environment
    variables for S3 for example)."""

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return JsonResponse(
            {},
            status=404,
        )

    if not request.user.has_perm("workspaces.launch_notebooks", workspace):
        return JsonResponse(
            {},
            status=401,
        )

    connections = workspace.connections.filter_for_user(request.user)
    env = {}
    for connection in connections:
        env.update(connection.env_variables)

    # TODO: Database / Filesystem credentials

    return JsonResponse(
        {"env": env},
        status=200,
    )
