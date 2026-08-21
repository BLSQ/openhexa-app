from hexa.data_studio.models import SavedQuery, SavedQueryVisibility
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def _is_author(principal: User, saved_query: SavedQuery) -> bool:
    # An author-less query (the account was deleted) belongs to nobody, so it must
    # not be claimed by whoever happens to have a null id.
    return (
        saved_query.created_by_id is not None
        and saved_query.created_by_id == principal.id
    )


def create_saved_query(principal: User, workspace: Workspace):
    """Any workspace member can save a query (consistent with running queries)."""
    return workspace.workspacemembership_set.filter(
        user=principal
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def update_saved_query(principal: User, saved_query: SavedQuery):
    """The author, or a workspace editor/admin, can edit a shared saved query."""
    if _is_author(principal, saved_query):
        return True
    if saved_query.visibility == SavedQueryVisibility.PRIVATE:
        # A private query is the author's alone: no workspace or organization role
        # grants access to it.
        return False
    return saved_query.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(
        saved_query.workspace.organization
    )


def update_saved_query_visibility(principal: User, saved_query: SavedQuery):
    """Only the author can share or unshare their query.

    Sharing is deliberately not part of the role-based edit rights: anyone else
    switching a query from WORKSPACE to PRIVATE would hand exclusive access to the
    author and lock themselves out of the query they just edited.

    Author-less queries (the account was deleted) therefore stay shared for good,
    which is also what keeps them reachable: making one private would hand it to
    nobody. The `data_studio_private_query_has_author` constraint is the backstop
    should this rule ever be relaxed.
    """
    return _is_author(principal, saved_query)


def delete_saved_query(principal: User, saved_query: SavedQuery):
    return update_saved_query(principal, saved_query)
