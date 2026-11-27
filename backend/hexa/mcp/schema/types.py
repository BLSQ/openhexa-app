from ariadne import EnumType, ObjectType

from hexa.mcp.models import MCPConnection, MCPResource
from hexa.mcp.protocol import get_tools_catalogue
from hexa.user_management.models import Organization
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


@mcp_connection_object.field("organizations")
def resolve_organizations(connection: MCPConnection, info):
    return (
        Organization.objects.filter_for_user(connection.user)
        .filter(mcp_connections=connection)
        .order_by("name")
    )


@mcp_connection_object.field("tools")
def resolve_tools(connection: MCPConnection, info):
    # A stored grant can name a tool removed since; sending it back on the next save
    # would be refused as TOOL_NOT_FOUND, so it is not reported.
    known = {tool["name"] for tool in get_tools_catalogue()}
    return sorted(known.intersection(connection.tools))


bindables = [mcp_connection_object, mcp_resource_enum]
