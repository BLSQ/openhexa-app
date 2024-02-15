from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def view_database_credentials(principal: User, workspace: Workspace):
    """Workspace editors and admins can have access to database credentials"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()
