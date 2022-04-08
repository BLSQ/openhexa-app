from hexa.plugins.connector_accessmod.models import Analysis, Fileset, Project
from hexa.user_management.models import User


def create_project():
    """Everyone can create a project"""

    return True


def update_project(principal: User, project: Project):
    """Projects can be updated by their owner."""

    return principal == project.owner or principal.is_admin_of(project.owner)


def delete_project(principal: User, project: Project):
    """Projects can be deleted by their owners."""

    return principal == project.owner or principal.is_admin_of(project.owner)


def create_project_permission(principal: User, project: Project):
    """Only project owners can create project permissions."""

    return principal == project.owner or principal.is_admin_of(project.owner)


def update_project_permission(principal: User, project: Project):
    """Only project owners can update a project permission"""

    return principal == project.owner or principal.is_admin_of(project.owner)


def delete_project_permission(principal: User, project: Project):
    """Only project owners can delete a project permission"""

    return principal == project.owner or principal.is_admin_of(project.owner)


def create_fileset(principal: User, project: Project):
    """Filesets can be created by project owners."""

    return principal == project.owner or principal.is_admin_of(project.owner)


def update_fileset(principal: User, fileset: Fileset):
    """Filesets can be updated only by their owners."""

    return principal == fileset.owner or principal.is_admin_of(fileset.owner)


def delete_fileset(principal: User, fileset: Fileset):
    """Filesets can be deleted by their owners."""

    return principal == fileset.owner or principal.is_admin_of(fileset.owner)


def create_file(principal: User, fileset: Fileset):
    """Files (within filesets) can be created by fileset owners."""

    return principal == fileset.owner or principal.is_admin_of(fileset.owner)


def create_analysis(principal: User, project: Project):
    """Analyses can be created within a project by the project owners."""

    return principal == project.owner or principal.is_admin_of(project.owner)


def update_analysis(principal: User, analysis: Analysis):
    """Analyses can be updated by their owners."""

    return principal == analysis.owner or principal.is_admin_of(analysis.owner)


def run_analysis(principal: User, analysis: Analysis):
    """Analyses can be updated:
    - For analyses in team projects, by the admins of the team owning the fileset's project
    - For personal analyses, by their owner
    """

    return principal == analysis.owner or principal.is_admin_of(analysis.owner)


def delete_analysis(principal: User, analysis: Analysis):
    """Filesets can be deleted:
    - For filesets in team projects, by the admins of the team owning the fileset's project
    - For personal filesets, by their owner
    """

    return principal == analysis.owner or principal.is_admin_of(analysis.owner)
