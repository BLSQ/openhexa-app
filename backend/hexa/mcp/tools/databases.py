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
def execute_sql(user, workspace_slug: str, query: str, max_rows: int = 50) -> dict:
    """Execute a single read-only SQL statement (PostgreSQL) against the workspace database and return the resulting rows. Use this to inspect data, query information_schema for table structures, or verify that a query works and returns the expected result. Returned rows are capped at max_rows (itself capped server-side); 'truncated' tells whether more rows exist. Write statements are rejected: the query runs with a read-only role."""
    data = execute_graphql(
        user,
        "ExecuteSQL",
        {"workspaceSlug": workspace_slug, "query": query, "maxRows": max_rows},
    )
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    return workspace["database"]["executeSQL"]


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
