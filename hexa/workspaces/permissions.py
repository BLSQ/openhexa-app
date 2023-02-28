from hexa.user_management.models import User

from .models import Connection, Workspace, WorkspaceMembershipRole


def create_workspace(principal: User):
    """Only superusers can create a workspace"""
    return principal.has_feature_flag("workspaces")


def update_workspace(principal: User, workspace: Workspace):
    """Only workspace admin can update a workspace"""
    return (
        True
        if workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
        else False
    )


def create_connection(principal: User, workspace: Workspace):
    """Only admin users of a workspace can create connections"""
    return workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists()


def update_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can update a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists()


def delete_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can delete a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists()


def delete_workspace(principal: User, workspace: Workspace):
    """Only superusers can delte a workspace"""
    return (
        True
        if workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.ADMIN
        ).exists()
        else False
    )


def manage_members(principal: User, workspace: Workspace):
    """Only superusers can delete a workspace"""
    return (
        True
        if workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.ADMIN
        ).exists()
        else False
    )


def launch_notebooks(principal: User, workspace: Workspace):
    """Workspace editors and admins can launch notebooks"""

    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()
