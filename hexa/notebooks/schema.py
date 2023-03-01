import pathlib

import requests
from ariadne import MutationType, QueryType, load_schema_from_path
from django.conf import settings
from django.http import HttpRequest

from hexa.workspaces.models import Workspace

notebooks_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

notebooks_queries = QueryType()
notebooks_mutations = MutationType()


@notebooks_queries.field("notebooksUrl")
def resolve_notebooks_url(_, info, **kwargs):
    return settings.NOTEBOOKS_URL


@notebooks_mutations.field("launchNotebookServer")
def resolve_launch_notebook_server(_, info, input, **kwargs):
    """Note: this is only used for workspaces for now. Default servers (outside workspaces) are spawned by
    Jupyterhub."""

    request: HttpRequest = info.context["request"]
    workspace_slug = input["workspaceSlug"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {"success": False, "server": None, "errors": ["NOT_FOUND"]}

    if not request.user.has_perm("workspaces.launch_notebooks", workspace):
        return {"success": False, "server": None, "errors": ["PERMISSION_DENIED"]}

    headers = {
        "Authorization": f"token {settings.HUB_API_TOKEN}",
    }

    # Get user, create if needed
    user_response = requests.get(
        f"{settings.NOTEBOOKS_API_URL}/users/{request.user.email}", headers=headers
    )
    if user_response.status_code == 404:
        user_response = requests.post(
            f"{settings.NOTEBOOKS_API_URL}/users/{request.user.email}", headers=headers
        )
        if user_response.status_code != 201:
            return {"success": False, "errors": ["UNKNOWN_ERROR"]}

    if workspace_slug not in user_response.json()["servers"]:
        server_response = requests.post(
            f"{settings.NOTEBOOKS_API_URL}/users/{request.user.email}/servers/{workspace_slug}",
            headers=headers,
            cookies={
                "sessionid": request.COOKIES.get("sessionid"),
                "csrftoken": request.COOKIES.get("csrftoken"),
            },
        )
        if server_response.status_code != 201:
            return {"success": False, "errors": ["UNKNOWN_ERROR"]}

    return {
        "success": True,
        "server": {
            "name": workspace_slug,
            "url": f"{settings.NOTEBOOKS_URL}/user/{request.user.email}/{workspace_slug}/",
        },
        "errors": [],
    }


notebooks_bindables = [notebooks_queries, notebooks_mutations]
