import json

from hexa.mcp.models import MCPUser
from hexa.mcp.protocol import scope_refusal_message, tool
from hexa.workspaces.models import Workspace

from ._graphql import execute_graphql


def _matches_ungranted_workspace(user: MCPUser, query: str) -> bool:
    """Whether the search matches a workspace the person can access but not this connection."""
    return (
        Workspace.objects.filter_for_user(user.real_user)
        .exclude(pk__in=user.workspace_ids)
        .filter_by_query(query)
        .exists()
    )


@tool
def list_workspaces(user, query: str = "", page: int = 1, per_page: int = 10) -> dict:
    """List workspaces accessible to the current user. Optionally filter by name using the query parameter. This is typically the first tool to call to discover available workspaces before accessing pipelines, datasets, or files."""
    data = execute_graphql(
        user,
        "ListWorkspaces",
        {"query": query or None, "page": page, "perPage": per_page},
    )
    listing = data.get("workspaces") or {}
    if (
        query
        and isinstance(user, MCPUser)
        and listing.get("totalItems") == 0
        and _matches_ungranted_workspace(user, query)
    ):
        data["message"] = scope_refusal_message(user.connection)
    return data


@tool
def get_workspace(user, slug: str) -> dict:
    """Get details of a specific workspace by its slug. Returns workspace metadata, countries and dockerImage. Use list_workspaces first if you don't know the slug."""
    return execute_graphql(user, "GetWorkspace", {"slug": slug})


@tool(write=True)
def update_workspace(
    user,
    slug: str,
    name: str = "",
    description: str = "",
    countries: str = "",
    docker_image: str = "",
) -> dict:
    """Update a workspace's properties. Provide the workspace slug and any fields to change.
    - name: new display name
    - description: new description
    - countries: JSON array of ISO alpha-2 country codes, e.g. '["US", "FR", "KE"]'
    - docker_image: custom Docker image for pipeline execution, e.g. 'eu.gcr.io/my-org/my-image:latest'
    Only provided non-empty fields are updated. Requires update permission on the workspace (ADMIN role or higher).
    """
    update_input = {"slug": slug}
    if name:
        update_input["name"] = name
    if description:
        update_input["description"] = description
    if countries:
        try:
            codes = json.loads(countries)
        except json.JSONDecodeError:
            return {
                "error": 'countries must be a valid JSON array of ISO country codes, e.g. \'["US", "FR"]\''
            }
        update_input["countries"] = [{"code": code} for code in codes]
    if docker_image:
        update_input["dockerImage"] = docker_image

    data = execute_graphql(user, "UpdateWorkspace", {"input": update_input})
    if "errors" in data:
        return data
    return data.get("updateWorkspace", {})
