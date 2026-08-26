from hexa.user_management.models import User

from .models import Connection, Workspace, WorkspaceMembershipRole


def update_workspace(principal: User, workspace: Workspace):
    """Only workspace admin can update a workspace"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def create_connection(principal: User, workspace: Workspace):
    """Only admin users of a workspace can create connections"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def generate_workspace_token(principal: User, workspace: Workspace):
    """Anyone with access to the workspace can get a token, except viewers.

    Members get a token tied to their membership; users whose access is implicit
    (organization admins/owners, superusers) get a short-lived identity token.
    The branches below mirror Workspace.objects.filter_for_user, so the two must
    be kept in sync.
    """
    membership = workspace.get_membership(principal)
    if membership is not None:
        return membership.role != WorkspaceMembershipRole.VIEWER
    return principal.is_superuser or principal.is_organization_admin_or_owner(
        workspace.organization
    )


def update_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can update a connection"""
    return connection.workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR
    ) or principal.is_organization_admin_or_owner(connection.workspace.organization)


def delete_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can delete a connection"""
    return connection.workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR
    ) or principal.is_organization_admin_or_owner(connection.workspace.organization)


def delete_workspace(principal: User, workspace: Workspace):
    """Only admin users of a workspace can delete a workspace"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def archive_workspace(principal: User, workspace: Workspace):
    """Only admin users of a workspace can archive a workspacce"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def manage_members(principal: User, workspace: Workspace):
    """Only admin users of a workspace can manage members"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def launch_notebooks(principal: User, workspace: Workspace):
    """Workspace editors and admins can launch notebooks"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def delete_database_table(principal: User, workspace: Workspace):
    """Workspace editors and admins can delete database table"""
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)
