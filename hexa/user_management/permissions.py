from hexa.user_management.models import Membership, Team, User


def create_team(principal: User):
    """Everyone can create a team."""

    return True


def update_team(principal: User, team: Team):
    """Only team admins can update the team."""

    return principal.is_admin_of(team)


def delete_team(principal: User, team: Team):
    """Only team admins can delete a team."""

    return principal.is_admin_of(team)


def create_membership(
    principal: User,
    team: Team,
):
    """Only team admins can add users to a team."""

    return principal.is_admin_of(team)


def update_membership(
    principal: User,
    membership: Membership,
):
    """Only team admins can modify a membership."""

    return principal.is_admin_of(membership.team)


def delete_membership(
    principal: User,
    membership: Membership,
):
    """Only team admins can remove users from a team, and the admin cannot remove himself from the team."""

    return principal.is_admin_of(membership.team) and principal != membership.user
