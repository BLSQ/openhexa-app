from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_webapp(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()


def delete_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN],
    ).exists()


def update_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()
