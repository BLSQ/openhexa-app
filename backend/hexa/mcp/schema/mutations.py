from ariadne import MutationType
from django.db import transaction
from django.http import HttpRequest
from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken

from hexa.mcp.models import MCPConnection
from hexa.mcp.protocol import get_tools_catalogue
from hexa.workspaces.models import Workspace

mcp_mutations = MutationType()


def unknown_tool_names(input) -> bool:
    names = input.get("tools")
    if names is None:
        return False
    return bool(set(names) - {tool["name"] for tool in get_tools_catalogue()})


def resolve_workspaces(user, input):
    """The workspaces named by the input, or None when it names none.

    Filtered for the user, so a grant can never name a workspace they have no
    access to themselves. Raises LookupError when a slug does not resolve.
    """
    slugs = input.get("workspace_slugs")
    if slugs is None:
        return None
    workspaces = list(Workspace.objects.filter_for_user(user).filter(slug__in=slugs))
    if len(workspaces) != len(set(slugs)):
        raise LookupError
    return workspaces


def apply_grant(connection: MCPConnection, input, workspaces) -> MCPConnection:
    with transaction.atomic():
        if "tools" in input:
            connection.tools = sorted(set(input["tools"]))
        connection.save()
        if workspaces is not None:
            connection.workspaces.set(workspaces)
    return connection


@mcp_mutations.field("authorizeMCPConnection")
def resolve_authorize_mcp_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    application = Application.objects.filter(client_id=input["client_id"]).first()
    if application is None:
        return {
            "success": False,
            "errors": ["CLIENT_NOT_FOUND"],
            "mcp_connection": None,
        }
    if unknown_tool_names(input):
        return {"success": False, "errors": ["TOOL_NOT_FOUND"], "mcp_connection": None}
    try:
        workspaces = resolve_workspaces(request.user, input)
    except LookupError:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
            "mcp_connection": None,
        }

    connection, _created = MCPConnection.objects.get_or_create(
        user=request.user, application=application
    )
    return {
        "success": True,
        "errors": [],
        "mcp_connection": apply_grant(connection, input, workspaces),
    }


@mcp_mutations.field("updateMCPConnection")
def resolve_update_mcp_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    connection = MCPConnection.objects.filter(user=request.user, id=input["id"]).first()
    if connection is None:
        return {"success": False, "errors": ["NOT_FOUND"], "mcp_connection": None}

    if unknown_tool_names(input):
        return {"success": False, "errors": ["TOOL_NOT_FOUND"], "mcp_connection": None}
    try:
        workspaces = resolve_workspaces(request.user, input)
    except LookupError:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
            "mcp_connection": None,
        }

    return {
        "success": True,
        "errors": [],
        "mcp_connection": apply_grant(connection, input, workspaces),
    }


@mcp_mutations.field("revokeMCPConnection")
def resolve_revoke_mcp_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    connection = MCPConnection.objects.filter(
        user=request.user, id=kwargs["input"]["id"]
    ).first()
    if connection is None:
        return {"success": False, "errors": ["NOT_FOUND"]}

    with transaction.atomic():
        token_filter = {"user": connection.user, "application": connection.application}
        RefreshToken.objects.filter(**token_filter).delete()
        AccessToken.objects.filter(**token_filter).delete()
        Grant.objects.filter(**token_filter).delete()
        connection.delete()

    return {"success": True, "errors": []}


bindables = [mcp_mutations]
