from ariadne import ObjectType
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.user_management.schema import me_permissions_object

from ..models import (
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
)

workspace_object = ObjectType("Workspace")
workspace_permissions = ObjectType("WorkspacePermissions")


@workspace_permissions.field("createConnection")
def resolve_workspace_permissions_create_connection(obj: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.create_connection", obj)
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("deleteDatabaseTable")
def resolve_workspace_permissions_delete_table(obj: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.delete_database_table", obj)
        if request.user.is_authenticated
        else False
    )


@me_permissions_object.field("createWorkspace")
def resolve_me_permissions_create_workspace(me, info):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("workspaces.create_workspace")
        if request.user.is_authenticated
        else False
    )


@workspace_permissions.field("update")
def resolve_workspace_permission_update(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.update_workspace", workspace)


@workspace_permissions.field("delete")
def resolve_workspace_permission_delete(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.delete_workspace", workspace)


@workspace_permissions.field("manageMembers")
def resolve_workspace_permission_manage(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.manage_members", workspace)


@workspace_permissions.field("launchNotebookServer")
def resolve_workspace_permission_launch_notebooks(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.launch_notebooks", workspace)


@workspace_object.field("permissions")
def resolve_workspace_permissions(workspace: Workspace, info):
    return workspace


@workspace_object.field("countries")
def resolve_workspace_countries(workspace: Workspace, info, **kwargs):
    if workspace.countries is not None:
        return workspace.countries
    return []


@workspace_object.field("members")
def resolve_workspace_members(workspace: Workspace, info, **kwargs):
    qs = workspace.workspacemembership_set.all().order_by("-updated_at")
    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", qs.count()),
    )


@workspace_object.field("invitations")
def resolve_workspace_invitations(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]

    qs = (
        WorkspaceInvitation.objects.filter_for_user(request.user)
        .filter(workspace=workspace)
        .order_by("-updated_at")
    )
    if not kwargs.get("include_accepted"):
        qs = qs.exclude(status=WorkspaceInvitationStatus.ACCEPTED)

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 5),
    )


@workspace_object.field("connections")
def resolve_workspace_connections(workspace: Workspace, info, **kwargs):
    return workspace.connections.all()


bindables = [
    workspace_object,
    workspace_permissions,
]
