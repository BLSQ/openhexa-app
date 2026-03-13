from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_conversation(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)
