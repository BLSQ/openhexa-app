import pathlib

import requests
from ariadne import MutationType, QueryType, load_schema_from_path
from django.conf import settings
from django.http import HttpRequest

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
    request: HttpRequest = info.context["request"]

    if not request.user.has_perm("notebooks.create_server"):  # TODO: check workspace
        return {"success": False, "server": None, "errors": ["PERMISSION_DENIED"]}

    workspace_slug = input["workspaceSlug"]
    headers = {
        "Authorization": f"token {settings.NOTEBOOKS_APP_HUB_AUTH_TOKEN}",
    }

    # Get user, create if needed
    user_response = requests.get(
        f"{settings.NOTEBOOKS_API_URL}/users/{request.user.email}", headers=headers
    )
    if user_response.status_code != 200:
        user_response = requests.post(
            f"{settings.NOTEBOOKS_API_URL}/users/{request.user.email}", headers=headers
        )
        if user_response.status_code != 201:
            return {"success": False, "server": None, "errors": ["UNKNOWN_ERROR"]}

    # TODO: check  # https://discourse.jupyter.org/t/setting-environment-variables-dynamically/9982
    # TODO: and https://github.com/jupyterhub/zero-to-jupyterhub-k8s/issues/2087

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
            return {"success": False, "server": None, "errors": ["UNKNOWN_ERROR"]}

    return {
        "success": True,
        "server": {
            "name": workspace_slug,
            "url": f"{settings.NOTEBOOKS_URL}/user/{request.user.email}/{workspace_slug}/",
            "errors": [],
        },
    }


notebooks_bindables = [notebooks_queries, notebooks_mutations]
