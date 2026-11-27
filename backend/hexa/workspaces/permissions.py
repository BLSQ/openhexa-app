from uuid import UUID

from django.conf import settings

from hexa.user_management.models import User

from .models import Connection, Workspace, WorkspaceMembershipRole


def update_workspace(principal: User, workspace: Workspace):
    """Workspace admins and editors, and organization admins and owners."""
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


def can_share_publicly(
    principal: User, workspace: Workspace, author_id: UUID | None = None
) -> bool:
    """The rule shared by every resource that can be made public (datasets, saved
    queries, web apps, public files): organization admins/owners, workspace admins, and
    the resource's author while they are still a workspace editor.

    Editors are only trusted with their own resources: exposing someone else's to the
    internet would hand out what its author never meant to publish. Workspace-level
    settings have no author, so `author_id` is omitted for them.
    """
    if principal.is_organization_admin_or_owner(workspace.organization):
        return True
    membership = workspace.get_membership(principal)
    if membership is None:
        return False
    if membership.role == WorkspaceMembershipRole.ADMIN:
        return True
    return (
        author_id is not None
        and author_id == principal.id
        and membership.role == WorkspaceMembershipRole.EDITOR
    )


def manage_public_files(principal: User, workspace: Workspace):
    """Whether the principal may expose the public folder of the workspace
    (`can_share_publicly`).

    Refused while the instance flag is off, so that no workspace sits in an enabled state
    that would silently go live the day the flag is turned on.
    """
    if not settings.PUBLIC_FILES_ENABLED:
        return False
    return can_share_publicly(principal, workspace)


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


def is_workspace_admin(principal: User, workspace: Workspace):
    """Workspace admins, and organization admins and owners."""
    return workspace.workspacemembership_set.filter(
        user=principal, role=WorkspaceMembershipRole.ADMIN
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def duplicate_workspace(principal: User, workspace: Workspace):
    """Workspace admins can duplicate a workspace, if they may create one.

    Editors and viewers are excluded: the requester becomes admin of the
    duplicate, which would hand them the connection secrets and member
    management they do not have in the source.
    Organization admins and owners can duplicate any workspace of their
    organization, secrets included, without being a member of it.
    """
    return (
        workspace.organization is not None
        and principal.has_perm(
            "user_management.create_workspace", workspace.organization
        )
        and is_workspace_admin(principal, workspace)
    )
