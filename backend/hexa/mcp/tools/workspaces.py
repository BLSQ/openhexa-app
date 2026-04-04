from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_workspaces(user, query: str = "", page: int = 1, per_page: int = 10) -> dict:
    """List workspaces accessible to the current user. Optionally filter by name using the query parameter. This is typically the first tool to call to discover available workspaces before accessing pipelines, datasets, or files."""
    return execute_graphql(
        user,
        "ListWorkspaces",
        {"query": query or None, "page": page, "perPage": per_page},
    )


@tool
def get_workspace(user, slug: str) -> dict:
    """Get details of a specific workspace by its slug. Returns workspace metadata and permissions. Use list_workspaces first if you don't know the slug."""
    return execute_graphql(user, "GetWorkspace", {"slug": slug})
