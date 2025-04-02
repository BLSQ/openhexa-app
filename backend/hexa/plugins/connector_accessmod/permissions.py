import typing

from django.contrib.auth.models import AnonymousUser

from hexa.plugins.connector_accessmod.models import (
    AccessmodProfile,
    Analysis,
    Fileset,
    Project,
    ProjectPermission,
)
from hexa.user_management.models import Team, User


def create_project(principal: User):
    """Projects can be created by anyone"""
    return principal.is_authenticated


def update_project(principal: User, project: Project):
    """Projects can be updated:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(project.owner)
        if isinstance(project.owner, Team)
        else principal == project.owner
    )


def delete_project(principal: User, project: Project):
    """Projects can be deleted:
    - Within team projects, by the admins of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_admin_of(project.owner)
        if isinstance(project.owner, Team)
        else principal == project.owner
    )


def create_project_permission(
    principal: User,
    project_user_and_team: typing.Optional[
        typing.Tuple[Project, typing.Optional[User], typing.Optional[Team]]
    ] = None,
):
    """Project permissions can be created:
    - Within team projects, by the admins of the team owning the project
    - Within personal projects, by their owner
    - For projects that haven't any permission yet, by the author
    """
    project, user, team = project_user_and_team

    if (user is None) == (team is None):
        raise ValueError("Please provider either a user or a team - not both")

    owns_project = (
        principal.is_admin_of(project.owner)
        if isinstance(project.owner, Team)
        else principal == project.owner
    )
    is_or_belong_to_new_grantee = (
        principal.is_member_of(team) if team is not None else principal == user
    )

    return (owns_project and is_or_belong_to_new_grantee) or (
        project.projectpermission_set.count() == 0 and principal == project.author
    )


def update_project_permission(principal: User, permission: ProjectPermission):
    """Project permissions can be updated:
    - Within team projects, by the admins of the team owning the project (except for own permissions)
    - Within personal projects, by their owner (except for own permissions)
    """
    return permission.user != principal and (
        principal.is_admin_of(permission.owner)
        if isinstance(permission.owner, Team)
        else principal == permission.owner
    )


def delete_project_permission(principal: User, permission: ProjectPermission):
    """Project permissions can be deleted:
    - Within team projects, by the admins of the team owning the project (except for own permissions)
    - Within personal projects, by their owner (except for own permissions)
    """
    return permission.user != principal and (
        principal.is_admin_of(permission.owner)
        if isinstance(permission.owner, Team)
        else principal == permission.owner
    )


def create_fileset(principal: User, project: Project):
    """Filesets can be created:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(project.owner)
        if isinstance(project.owner, Team)
        else principal == project.owner
    )


def update_fileset(principal: User, fileset: Fileset):
    """Filesets can be updated:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(fileset.owner)
        if isinstance(fileset.owner, Team)
        else principal == fileset.owner
    )


def delete_fileset(principal: User, fileset: Fileset):
    """Filesets can be deleted:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(fileset.owner)
        if isinstance(fileset.owner, Team)
        else principal == fileset.owner
    )


def create_file(principal: User, fileset: Fileset):
    """Files can be created:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(fileset.owner)
        if isinstance(fileset.owner, Team)
        else principal == fileset.owner
    )


def create_analysis(principal: User, project: Project):
    """Analyses can be created:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(project.owner)
        if isinstance(project.owner, Team)
        else principal == project.owner
    )


def update_analysis(principal: User, analysis: Analysis):
    """Analyses can be updated:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(analysis.owner)
        if isinstance(analysis.owner, Team)
        else principal == analysis.owner
    )


def run_analysis(principal: User, analysis: Analysis):
    """Analyses can be run:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(analysis.owner)
        if isinstance(analysis.owner, Team)
        else principal == analysis.owner
    )


def delete_analysis(principal: User, analysis: Analysis):
    """Filesets can be deleted:
    - Within team projects, by the members of the team owning the project
    - Within personal projects, by their owner
    """
    return (
        principal.is_member_of(analysis.owner)
        if isinstance(analysis.owner, Team)
        else principal == analysis.owner
    )


def create_access_request(principal: typing.Union[User, AnonymousUser]) -> bool:
    """Access requests can be only be created by anonymous users."""
    return isinstance(principal, AnonymousUser)


def manage_access_requests(principal: typing.Union[User, AnonymousUser]) -> bool:
    """Access requests can be approved either by global superusers or by AccessMod superusers"""
    if isinstance(principal, AnonymousUser):
        return False

    if principal.is_superuser:
        return True

    try:
        admin_profile = principal.accessmod_admin_profile

        return admin_profile.is_accessmod_superuser
    except AccessmodProfile.DoesNotExist:
        return False
