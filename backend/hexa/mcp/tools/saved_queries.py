from hexa.data_studio.models import SavedQueryVisibility
from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_saved_queries(
    user, workspace_slug: str, query: str = "", page: int = 1, per_page: int = 10
) -> dict:
    """List the saved SQL queries of a workspace's Data Studio, most recently updated first.

    Returns each query's id, slug, name, description and visibility (PRIVATE: only its author
    can see it, WORKSPACE: shared with every workspace member, PUBLIC: also runnable by anyone
    with its permalink, without an account), without the SQL content. Pass
    query to filter by name or description. Use get_saved_query with the returned 'slug' to
    get the SQL content, or the returned 'id' when calling update_saved_query.
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
    return {"savedQueries": workspace["savedQueries"]}


@tool
def get_saved_query(user, saved_query_slug: str) -> dict:
    """Get a saved SQL query of the Data Studio by its slug.

    Slugs are unique across workspaces, so no workspace slug is needed. Returns the query's
    metadata, SQL content, visibility and workspace. Use the returned 'id' when
    calling update_saved_query.
    """
    data = execute_graphql(user, "GetSavedQuery", {"slug": saved_query_slug})
    if "errors" in data:
        return data
    saved_query = data.get("savedQueryBySlug")
    if saved_query is None:
        return {"error": "Saved query not found"}
    return saved_query


@tool(write=True)
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
    every member of the workspace, or to PUBLIC, which also lets anyone with its permalink run
    it without an account (workspace viewers cannot create PUBLIC queries). Returns the saved
    query's id and slug.
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


@tool(write=True)
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
    provided non-empty fields are updated. Only the query's author can change its visibility,
    except that workspace and organization admins can also make a WORKSPACE query PUBLIC
    (runnable by anyone with its permalink, without an account) and take it back to WORKSPACE;
    an author who is only a workspace viewer cannot make it PUBLIC. Other workspace editors
    and admins can edit the name, description and content of a WORKSPACE query, and the name
    and description of a PUBLIC one, but nothing of a PRIVATE one. The content of a PUBLIC
    query can only be changed by those who may make it PUBLIC.
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
