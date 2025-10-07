from hexa.user_management.models import (
    Membership,
    Organization,
    Team,
    User,
)
from hexa.workspaces.models import WorkspaceMembership, WorkspaceMembershipRole


def create_team(principal: User):
    """Teams can be created by anyone"""
    return principal.is_authenticated


def update_team(principal: User, team: Team):
    """Only team admins can update the team"""
    return principal.is_admin_of(team)


def delete_team(principal: User, team: Team):
    """Only team admins can delete a team"""
    return principal.is_admin_of(team)


def create_membership(
    principal: User,
    team: Team,
):
    """We allow the creation of a membership in two cases:
    1. If the principal is the team admin
    2. If the team has no admin yet (for newly created teams)
    """
    return principal.is_admin_of(team) or team.membership_set.count() == 0


def update_membership(
    principal: User,
    membership: Membership,
):
    """Only team admins can modify a membership"""
    return principal.is_admin_of(membership.team)


def delete_membership(
    principal: User,
    membership: Membership,
):
    """Only team admins can remove users from a team, and the admin cannot remove himself from the team"""
    return principal.is_admin_of(membership.team) and principal != membership.user


def manage_members(principal: User, organization: Organization):
    """Only admin and owner users can manage members"""
    return principal.is_organization_admin_or_owner(organization)


def create_workspace(principal: User, organization: Organization):
    """Admin/owner users of the organization OR admin of any workspace in any org can create a workspace"""
    is_org_admin = principal.is_organization_admin_or_owner(organization)
    is_workspace_admin = WorkspaceMembership.objects.filter(
        user=principal,
        role=WorkspaceMembershipRole.ADMIN,
    ).exists()

    return (
        is_org_admin
        or (is_workspace_admin and principal.is_organization_member(organization))
        or principal.has_feature_flag("workspaces.create")
    ) and not principal.has_feature_flag("workspaces.prevent_create")


def archive_workspace(principal: User, organization: Organization):
    """Only admin and owner users can archive a workspace"""
    return principal.is_organization_admin_or_owner(organization)


def has_admin_privileges(principal: User, organization: Organization):
    """Check if user has admin or owner privileges in the organization"""
    return principal.is_organization_admin_or_owner(organization)


def manage_owners(principal: User, organization: Organization):
    """Only owner users can manage owner roles"""
    return principal.is_organization_owner(organization)
