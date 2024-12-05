import pathlib
from urllib import parse

from ariadne import MutationType, QueryType, load_schema_from_path
from django.conf import settings
from django.http import HttpRequest

from hexa.analytics.api import track
from hexa.workspaces.models import Workspace

from .api import create_server, create_user, get_user, server_ready

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
    Jupyterhub.
    """
    request: HttpRequest = info.context["request"]
    workspace_slug = input["workspace_slug"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {"success": False, "server": None, "errors": ["NOT_FOUND"]}

    if not request.user.has_perm("workspaces.launch_notebooks", workspace):
        return {"success": False, "server": None, "errors": ["PERMISSION_DENIED"]}

    username = request.user.email
    server_name = workspace_slug
    # Get user, create if needed
    user_data = get_user(username)
    if user_data is None:
        create_user(username)
        user_data = get_user(username)

    if workspace_slug not in user_data["servers"]:
        create_server(
            username,
            server_name,
            {
                "sessionid": request.COOKIES.get("sessionid"),
                "csrftoken": request.COOKIES.get("csrftoken"),
            },
        )
    # When user's email contains special characters, JupyterHub encode the email prefix (part before @)
    # and add it to the generated server url. If we don't apply the same encoding we will face
    # a not found error because the return URL and the generated one doesn't match
    email_prefix = parse.quote(request.user.email.split("@")[0])
    encoded_username = "@".join([email_prefix, request.user.email.split("@")[1]])
    track(request, "notebooks.notebook_launched", {"workspace": workspace_slug})

    return {
        "success": True,
        "server": {
            "name": workspace_slug,
            "url": f"{settings.NOTEBOOKS_URL}/user/{encoded_username}/{workspace_slug}/",
            "ready": server_ready(encoded_username, server_name),
        },
        "errors": [],
    }


notebooks_bindables = [notebooks_queries, notebooks_mutations]
