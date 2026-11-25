from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole
from hexa.workspaces.permissions import can_share_publicly


def create_webapp(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def delete_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(
        webapp.workspace.organization
    )


def update_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(
        webapp.workspace.organization
    )


def share_webapp(principal: User, webapp: Webapp):
    return can_share_publicly(principal, webapp.workspace, webapp.created_by_id)
