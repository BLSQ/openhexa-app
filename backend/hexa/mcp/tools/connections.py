from hexa.mcp.protocol import tool

from ._graphql import execute_graphql


@tool
def list_connections(user, workspace_slug: str) -> dict:
    """List connections (external data sources) configured in a workspace. Returns connection name, slug, type (S3, GCS, POSTGRESQL, DHIS2, IASO, CUSTOM), and their fields with values. Secret fields have their values hidden. Connections are used as parameters when running pipelines — use the connection slug as the parameter value."""
    data = execute_graphql(user, "ListConnections", {"slug": workspace_slug})
    if "errors" in data:
        return data
    workspace = data.get("workspace")
    if workspace is None:
        return {"error": "Workspace not found"}
    return {"connections": workspace["connections"]}
