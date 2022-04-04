from __future__ import annotations

import enum

from hexa.user_management import models as user_management_models


class TeamPermissions(enum.Enum):
    @staticmethod
    def add_user_to_team(
        user: user_management_models.User, team: user_management_models.Team
    ):
        """Only team admins can add users to a team"""

        return user.membership_set.filter(
            team=team, role=user_management_models.MembershipRole.ADMIN
        ).exists()
