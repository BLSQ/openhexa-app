from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_conversation(principal: User, workspace: Workspace):
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)
