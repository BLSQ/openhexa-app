from ariadne import EnumType, ObjectType

from hexa.mcp.models import MCPConnection, MCPResource
from hexa.workspaces.models import Workspace

mcp_connection_object = ObjectType("MCPConnection")
mcp_resource_enum = EnumType("MCPResource", MCPResource)


@mcp_connection_object.field("name")
def resolve_name(connection: MCPConnection, info):
    return connection.application.name


@mcp_connection_object.field("workspaces")
def resolve_workspaces(connection: MCPConnection, info):
    return (
        Workspace.objects.filter_for_user(connection.user)
        .filter(mcp_connections=connection)
        .order_by("name")
    )


@mcp_connection_object.field("tools")
def resolve_tools(connection: MCPConnection, info):
    return sorted(connection.tools)


bindables = [mcp_connection_object, mcp_resource_enum]
