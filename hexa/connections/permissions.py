from hexa.connections.models import Connection
from hexa.user_management.models import User
from hexa.workspaces.models import WorkspaceMembershipRole


def update_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can update a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def delete_connection(principal: User, connection: Connection):
    """Only admin users of a workspace can delete a connection"""
    return connection.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()
