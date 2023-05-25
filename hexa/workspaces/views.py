from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from hexa.databases.api import get_db_server_credentials
from hexa.files.credentials import notebooks_credentials as files_notebooks_credentials
from hexa.workspaces.models import Workspace, WorkspaceMembership


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
        membership = workspace.workspacemembership_set.get(user=request.user)
    except (Workspace.DoesNotExist, WorkspaceMembership.DoesNotExist):
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

    # Database credentials
    db_credentials = get_db_server_credentials()
    env.update(
        {
            "WORKSPACE_DATABASE_DB_NAME": workspace.db_name,
            "WORKSPACE_DATABASE_HOST": db_credentials["host"],
            "WORKSPACE_DATABASE_PORT": db_credentials["port"],
            "WORKSPACE_DATABASE_USERNAME": workspace.db_name,
            "WORKSPACE_DATABASE_PASSWORD": workspace.db_password,
            "WORKSPACE_DATABASE_URL": workspace.db_url,
        }
    )

    # Bucket credentials
    env.update(files_notebooks_credentials(request.user, workspace))

    return JsonResponse(
        {"env": env, "notebooks_server_hash": membership.notebooks_server_hash},
        status=200,
    )
