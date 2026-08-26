from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_object(principal: User, workspace: Workspace):
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def delete_object(principal: User, workspace: Workspace):
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def download_object(principal: User, workspace: Workspace):
    return workspace.has_role(principal) or principal.is_organization_admin_or_owner(
        workspace.organization
    )
