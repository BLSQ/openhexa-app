from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def get_db_schema(user, workspace_slug: str, page: int = 1, per_page: int = 15) -> dict:
    """List tables in the workspace database with their names and approximate row counts. Use this to get an overview of what data is available. Results are paginated; increase page to fetch more tables. Does not return actual table contents or row data."""
    data = execute_graphql(
        user,
        "GetDatabaseTables",
        {"workspaceSlug": workspace_slug, "page": page, "perPage": per_page},
    )
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    tables = workspace["database"]["tables"]
    return {
        "tables": tables["items"],
        "pageNumber": tables["pageNumber"],
        "totalPages": tables["totalPages"],
        "totalItems": tables["totalItems"],
    }


@tool
def get_db_table_schema(user, workspace_slug: str, table_name: str) -> dict:
    """Get column definitions for a specific table in the workspace database. Returns column names and PostgreSQL data types. Use this to understand the table structure before writing SQL queries."""
    data = execute_graphql(
        user,
        "GetDatabaseTable",
        {"workspaceSlug": workspace_slug, "tableName": table_name},
    )
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    table = workspace["database"]["table"]
    if table is None:
        return {"error": f"Table '{table_name}' not found"}
    return table
