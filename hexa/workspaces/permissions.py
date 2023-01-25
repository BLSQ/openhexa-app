from hexa.user_management.models import User

from .models import Workspace, WorkspaceMembershipRole


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
    """Only superusers can delte a workspace"""
    return (
        True
        if workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.ADMIN
        ).exists()
        else False
    )
