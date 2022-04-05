from __future__ import annotations

import enum
import typing

from hexa.user_management import models as user_management_models


class TeamPermissions(enum.Enum):
    @classmethod
    def edit_team(
        cls, principal: user_management_models.User, team: user_management_models.Team
    ):
        """Only team admins can edit the team."""

        return cls._has_admin_membership(principal, team)

    @classmethod
    def delete_team(
        cls, principal: user_management_models.User, team: user_management_models.Team
    ):
        """Only team admins can delete a team."""

        return cls._has_admin_membership(principal, team)

    @classmethod
    def add_user_to_team(
        cls,
        principal: user_management_models.User,
        user_and_team: typing.Sequence[
            user_management_models.User, user_management_models.Team
        ],
    ):
        """Only team admins can add users to a team, and the added user must be active."""

        user, team = user_and_team

        return user.is_active and cls._has_admin_membership(principal, team)

    @classmethod
    def remove_user_from_team(
        cls,
        principal: user_management_models.User,
        user_and_team: typing.Sequence[
            user_management_models.User, user_management_models.Team
        ],
    ):
        """Only team admins can remove users from a team, and the admin cannot remove himself from the team."""
        user, team = user_and_team

        return not user == principal and cls._has_admin_membership(principal, team)

    @staticmethod
    def _has_admin_membership(
        principal: user_management_models.User, team: user_management_models.Team
    ):
        return principal.membership_set.filter(
            team=team, role=user_management_models.MembershipRole.ADMIN
        ).exists()
