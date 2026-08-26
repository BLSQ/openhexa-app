from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def view_database_credentials(principal: User, workspace: Workspace):
    """Workspace editors and admins can have access to database credentials"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def run_query(principal: User, workspace: Workspace):
    """Any workspace member can run read-only SQL queries against the workspace database"""
    return workspace.has_role(principal) or principal.is_organization_admin_or_owner(
        workspace.organization
    )
