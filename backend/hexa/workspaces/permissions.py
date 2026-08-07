from hexa.user_management.models import User

from .models import Connection, Workspace, WorkspaceMembershipRole


def update_workspace(principal: User, workspace: Workspace):
    """Only workspace admin can update a workspace"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def create_connection(principal: User, workspace: Workspace):
    """Only admin users of a workspace can create connections"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def update_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can update a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(
        connection.workspace.organization
    )


def delete_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can delete a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(
        connection.workspace.organization
    )


def delete_workspace(principal: User, workspace: Workspace):
    """Only admin users of a workspace can delete a workspace"""
    return workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def archive_workspace(principal: User, workspace: Workspace):
    """Only admin users of a workspace can archive a workspacce"""
    return workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def manage_tags(principal: User, workspace: Workspace):
    """Only organization admins and owners can tag a workspace.

    Unlike the other workspace permissions, workspace admins are excluded on purpose:
    tags are an organization-level taxonomy used for cross-workspace administration.
    """
    return principal.is_organization_admin_or_owner(workspace.organization)


def manage_members(principal: User, workspace: Workspace):
    """Only admin users of a workspace can manage members"""
    return workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def launch_notebooks(principal: User, workspace: Workspace):
    """Workspace editors and admins can launch notebooks"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def delete_database_table(principal: User, workspace: Workspace):
    """Workspace editors and admins can delete database table"""
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)
