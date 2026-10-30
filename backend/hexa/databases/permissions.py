from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def view_database_credentials(principal: User, workspace: Workspace):
    """Workspace editors and admins can have access to database credentials"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def run_query(principal: User, workspace: Workspace):
    """Any workspace member can run read-only SQL queries against the workspace database"""
    # Reached for anonymous visitors of a public saved query, who have no memberships.
    if not principal.is_authenticated:
        return False
    return workspace.workspacemembership_set.filter(
        user=principal
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)
