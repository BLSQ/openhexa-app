from __future__ import annotations

import enum

from hexa.plugins.connector_accessmod import models as accessmod_models
from hexa.user_management import models as user_management_models


class TeamPermissions(enum.Enum):
    @staticmethod
    def create_project():
        """Everyone can create a project"""

        return True

    @staticmethod
    def update_project(
        principal: user_management_models.User, project: accessmod_models.Project
    ):
        """Projects can be updated:
        - For team projects, by the admins of the team
        - For personal projects, by their owner
        """

        return principal == project.owner or principal.is_admin_of(project.owner)

    @staticmethod
    def delete_project(
        principal: user_management_models.User, project: accessmod_models.Project
    ):
        """Projects can be deleted:
        - For team projects, by the admins of the team
        - For personal projects, by their owner
        """

        return principal == project.owner or principal.is_admin_of(project.owner)

    @staticmethod
    def create_fileset_in_project(
        principal: user_management_models.User, project: accessmod_models.Project
    ):
        """Filesets can be created in a project:
        - For team projects, by the admins of the team
        - For personal projects, by their owner
        """

        return principal == project.owner or principal.is_admin_of(project.owner)

    @staticmethod
    def update_fileset(
        principal: user_management_models.User, fileset: accessmod_models.Fileset
    ):
        """Filesets can be updated:
        - For filesets in team projects, by the admins of the team owning the fileset's project
        - For personal filesets, by their owner
        """

        return principal == fileset.owner or principal.is_admin_of(fileset.owner)

    @staticmethod
    def delete_fileset(
        principal: user_management_models.User, project: accessmod_models.Project
    ):
        """Filesets can be deleted:
        - For filesets in team projects, by the admins of the team owning the fileset's project
        - For personal filesets, by their owner
        """

        return principal == project.owner or principal.is_admin_of(project.owner)

    @staticmethod
    def create_analysis_in_project(
        principal: user_management_models.User, project: accessmod_models.Project
    ):
        """Analyses can be created in a project:
        - For team projects, by the admins of the team
        - For personal projects, by their owner
        """

        return principal == project.owner or principal.is_admin_of(project.owner)

    @staticmethod
    def update_analysis(
        principal: user_management_models.User, analysis: accessmod_models.Analysis
    ):
        """Analyses can be updated:
        - For analyses in team projects, by the admins of the team owning the fileset's project
        - For personal analyses, by their owner
        """

        return principal == analysis.owner or principal.is_admin_of(analysis.owner)

    @staticmethod
    def run_analysis(
        principal: user_management_models.User, analysis: accessmod_models.Analysis
    ):
        """Analyses can be updated:
        - For analyses in team projects, by the admins of the team owning the fileset's project
        - For personal analyses, by their owner
        """

        return principal == analysis.owner or principal.is_admin_of(analysis.owner)

    @staticmethod
    def delete_analysis(
        principal: user_management_models.User, analysis: accessmod_models.Analysis
    ):
        """Filesets can be deleted:
        - For filesets in team projects, by the admins of the team owning the fileset's project
        - For personal filesets, by their owner
        """

        return principal == analysis.owner or principal.is_admin_of(analysis.owner)

    @classmethod
    def edit_team(
        cls, principal: user_management_models.User, team: user_management_models.Team
    ):
        """Only team admins can edit the team."""

        return principal.is_admin_of(team)

    @classmethod
    def delete_team(
        cls, principal: user_management_models.User, team: user_management_models.Team
    ):
        """Only team admins can delete a team."""

        return principal.is_admin_of(team)

    @classmethod
    def create_membership(
        cls,
        principal: user_management_models.User,
        team: user_management_models.Team,
    ):
        """Only team admins can add users to a team."""

        principal.is_admin_of(team)

    @classmethod
    def delete_membership(
        cls,
        principal: user_management_models.User,
        membership: user_management_models.Membership,
    ):
        """Only team admins can remove users from a team, and the admin cannot remove himself from the team."""

        return principal.is_admin_of(membership.team) and principal != membership.user
