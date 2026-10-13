from typing import Any, Literal, Required, TypedDict

from hexa.data_studio.models import SavedQueryVisibility
from hexa.data_studio.templating import PARAMETER_TYPES
from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


class SavedQueryParameter(TypedDict, total=False):
    """Parameter definition for a saved query (mirrors SavedQueryParameterInput in GraphQL)."""

    name: Required[str]
    type: Required[Literal[*PARAMETER_TYPES]]
    multiple: bool
    required: bool
    default: Any
    help: str


@tool
def list_saved_queries(
    user, workspace_slug: str, query: str = "", page: int = 1, per_page: int = 10
) -> dict:
    """List the saved SQL queries of a workspace's Data Studio, most recently updated first.

    Returns each query's id, slug, name, description and visibility (PRIVATE: only its author
    can see it, WORKSPACE: shared with every workspace member), without the SQL content. Pass
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
    """Get a saved SQL query from the Data Studio by its slug.

    Slugs are unique across workspaces. Returns the query's metadata, SQL content,
    declared parameters, visibility, and workspace. Use the returned 'id' when calling
    update_saved_query.
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
    parameters: list[SavedQueryParameter] | None = None,
) -> dict:
    """Save a SQL query in a workspace's Data Studio.

    `content` is a single read-only SQL statement against the workspace database; use
    get_db_schema and get_db_table_schema to discover tables and columns first. The query is
    PRIVATE (visible to you only) unless visibility is set to WORKSPACE, which shares it with
    every member of the workspace. Returns the saved query's id and slug.

    To allow web apps to filter results, use `{{ name }}` placeholders in the SQL and declare
    each one in `parameters`. Supported types are STRING, INTEGER, FLOAT, BOOLEAN, and DATE.
    Set `multiple: true` for list values, which can be filtered with `= ANY({{ name }})`.
    Parameter values are bound safely at execution time. Sorting and pagination should be
    handled using `executeSavedQuery` rather than in SQL. All variables in the SQL must be
    declared in `parameters`. See the 'Query templating' section of the static web apps
    documentation for complete rules.
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
    if parameters:
        create_input["parameters"] = parameters

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
    parameters: list[SavedQueryParameter] | None = None,
) -> dict:
    """Update a saved SQL query in the Data Studio.

    Provide the saved query UUID (from list_saved_queries) and any fields to update. Only
    specified non-empty fields are updated. Only the author can change query visibility;
    workspace editors and admins can modify the name, description, content, and parameters
    of WORKSPACE queries.

    `parameters` replaces the entire list of declared parameters. When updating SQL content
    that adds or changes placeholders, supply both `content` and `parameters` together to keep
    them aligned. Pass an empty list `[]` to remove all parameters.
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
    if parameters is not None:
        update_input["parameters"] = parameters

    data = execute_graphql(user, "UpdateSavedQuery", {"input": update_input})
    if "errors" in data:
        return data
    return data["updateSavedQuery"]
