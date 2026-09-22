from hexa.data_studio.models import SavedQueryVisibility
from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_saved_queries(
    user, workspace_slug: str, query: str = "", page: int = 1, per_page: int = 15
) -> dict:
    """List the saved SQL queries of a workspace's Data Studio, most recently updated first.

    Returns each query's id, slug, name, description, SQL content and visibility (PRIVATE: only
    its author can see it, WORKSPACE: shared with every workspace member). Pass query to filter
    by name or description. Use the returned 'id' when calling update_saved_query, or the 'slug' with get_saved_query.
    """
    variables = {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page}
    if query:
        variables["query"] = query
    data = execute_graphql(user, "ListSavedQueries", variables)
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    saved_queries = workspace["savedQueries"]
    return {
        "savedQueries": saved_queries["items"],
        "pageNumber": saved_queries["pageNumber"],
        "totalPages": saved_queries["totalPages"],
        "totalItems": saved_queries["totalItems"],
    }


@tool
def get_saved_query(user, saved_query_slug: str) -> dict:
    """Get a saved SQL query of the Data Studio by its slug.

    Slugs are unique across workspaces, so no workspace slug is needed. Returns the query's
    metadata, SQL content, visibility, workspace and permissions. Use the returned 'id' when
    calling update_saved_query.
    """
    data = execute_graphql(user, "GetSavedQuery", {"slug": saved_query_slug})
    if "errors" in data:
        return data
    saved_query = data.get("savedQueryBySlug")
    if saved_query is None:
        return {"error": "Saved query not found"}
    return saved_query


@tool
def create_saved_query(
    user,
    workspace_slug: str,
    name: str,
    content: str,
    description: str = "",
    visibility: SavedQueryVisibility | None = None,
) -> dict:
    """Save a SQL query in a workspace's Data Studio.

    content is a single read-only SQL statement against the workspace database; use
    get_db_schema and get_db_table_schema to discover tables and columns first. The query is
    PRIVATE (visible to you only) unless visibility is set to WORKSPACE, which shares it with
    every member of the workspace. Returns the saved query's id and slug.
    """
    create_input: dict = {
        "workspaceSlug": workspace_slug,
        "name": name,
        "content": content,
    }
    if description:
        create_input["description"] = description
    if visibility is not None:
        create_input["visibility"] = visibility

    data = execute_graphql(user, "CreateSavedQuery", {"input": create_input})
    if "errors" in data:
        return data
    return data["createSavedQuery"]


@tool
def update_saved_query(
    user,
    saved_query_id: str,
    name: str = "",
    content: str = "",
    description: str = "",
    visibility: SavedQueryVisibility | None = None,
) -> dict:
    """Update a saved SQL query in the Data Studio.

    Provide the saved query UUID (from list_saved_queries) and any fields to change. Only
    provided non-empty fields are updated. Only the query's author can change its visibility;
    other workspace editors and admins can edit the name, description and content of a
    WORKSPACE query but not of a PRIVATE one.
    """
    update_input: dict = {"id": saved_query_id}
    if name:
        update_input["name"] = name
    if content:
        update_input["content"] = content
    if description:
        update_input["description"] = description
    if visibility is not None:
        update_input["visibility"] = visibility

    data = execute_graphql(user, "UpdateSavedQuery", {"input": update_input})
    if "errors" in data:
        return data
    return data["updateSavedQuery"]
