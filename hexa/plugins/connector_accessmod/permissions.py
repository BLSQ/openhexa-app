from __future__ import annotations

import enum
import typing

from hexa.user_management import models as user_management_models


class TeamPermissions(enum.Enum):
    @staticmethod
    def add_user_to_team(
        principal: user_management_models.User,
        user_and_team: typing.Sequence[
            user_management_models.User, user_management_models.Team
        ],
    ):
        """Only team admins can add users to a team, and the added user must be active."""

        user, team = user_and_team

        return (
            user.is_active
            and principal.membership_set.filter(
                team=team, role=user_management_models.MembershipRole.ADMIN
            ).exists()
        )

    @staticmethod
    def remove_user_from_team(
        principal: user_management_models.User,
        user_and_team: typing.Sequence[
            user_management_models.User, user_management_models.Team
        ],
    ):
        """Only team admins can remove users from a team, and the admin cannot remove himself from the team."""
        user, team = user_and_team

        return (
            not user == principal
            and principal.membership_set.filter(
                team=team, role=user_management_models.MembershipRole.ADMIN
            ).exists()
        )
