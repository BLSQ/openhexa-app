from hexa.user_management.models import (
    Membership,
    Organization,
    OrganizationMembershipRole,
    Team,
    User,
)


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
    return organization.organizationmembership_set.filter(
        user=principal,
        role__in=[OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER],
    ).exists()


def create_workspace(principal: User, organization: Organization):
    """Only admin and owner users can create a workspace"""
    return organization.organizationmembership_set.filter(
        user=principal,
        role__in=[OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER],
    ).exists()


def archive_workspace(principal: User, organization: Organization):
    """Only admin and owner users can archive a workspace"""
    return organization.organizationmembership_set.filter(
        user=principal,
        role__in=[OrganizationMembershipRole.ADMIN, OrganizationMembershipRole.OWNER],
    ).exists()
