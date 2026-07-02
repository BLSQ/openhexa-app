from hexa.databases.utils import get_database_definition, get_table_definition
from hexa.mcp.protocol import tool
from hexa.workspaces.models import Workspace


@tool
def get_db_schema(user, workspace_slug: str) -> dict:
    """List all tables in the workspace database with their names and approximate row counts. Use this to get an overview of what data is available. Does not return actual table contents or row data."""
    try:
        workspace = Workspace.objects.filter_for_user(user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return {"error": "Workspace not found"}
    tables = get_database_definition(workspace)
    return {"tables": [{"name": t["name"], "count": t["count"]} for t in tables]}


@tool
def get_db_table_schema(user, workspace_slug: str, table_name: str) -> dict:
    """Get column definitions for a specific table in the workspace database. Returns column names and PostgreSQL data types. Use this to understand the table structure before writing SQL queries."""
    try:
        workspace = Workspace.objects.filter_for_user(user).get(slug=workspace_slug)
    except Workspace.DoesNotExist:
        return {"error": "Workspace not found"}
    table = get_table_definition(workspace, table_name)
    if table is None:
        return {"error": f"Table '{table_name}' not found"}
    return {
        "name": table["name"],
        "count": table["count"],
        "columns": [{"name": c["name"], "type": c["type"]} for c in table["columns"]],
    }
