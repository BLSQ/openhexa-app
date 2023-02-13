from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_object(principal: User, workspace: Workspace):
    return (
        principal.has_feature_flag("workspaces")
        and workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.EDITOR
        ).exists()
    )


def delete_object(principal: User, workspace: Workspace):
    return (
        principal.has_feature_flag("workspaces")
        and workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.EDITOR
        ).exists()
    )


def download_object(principal: User, workspace: Workspace):
    return (
        principal.has_feature_flag("workspaces")
        and workspace.workspacemembership_set.filter(
            user=principal, role=WorkspaceMembershipRole.VIEWER
        ).exists()
    )
