from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_object(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()


def delete_object(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()


def download_object(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(user=principal).exists()
