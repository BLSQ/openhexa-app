from hexa.user_management.models import User
from hexa.webapps.models import Webapp
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_webapp(principal: User, workspace: Workspace):
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def delete_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(webapp.workspace.organization)


def update_webapp(principal: User, webapp: Webapp):
    return webapp.workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(webapp.workspace.organization)
