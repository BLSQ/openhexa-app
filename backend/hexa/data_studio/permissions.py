from hexa.data_studio.models import SavedQuery
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_saved_query(principal: User, workspace: Workspace):
    """Any workspace member can save a query (consistent with running queries)."""
    return workspace.workspacemembership_set.filter(
        user=principal
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def update_saved_query(principal: User, saved_query: SavedQuery):
    """The author, or a workspace editor/admin, can edit a saved query."""
    if saved_query.created_by_id == principal.id:
        return True
    return saved_query.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(
        saved_query.workspace.organization
    )


def delete_saved_query(principal: User, saved_query: SavedQuery):
    return update_saved_query(principal, saved_query)


def publish_saved_query(principal: User, workspace: Workspace):
    """Only workspace admins (or org admins/owners) can make a saved query public.

    Publishing exposes the query to anonymous callers, so it is a stricter gate
    than editing (which editors and the author can also do).
    """
    return workspace.workspacemembership_set.filter(
        user=principal,
        role=WorkspaceMembershipRole.ADMIN,
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)
