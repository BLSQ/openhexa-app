from hexa.plugins.connector_accessmod.models import Analysis, Fileset, Project
from hexa.user_management.models import User


def create_project():
    """Everyone can create a project"""

    return True


def update_project(principal: User, project: Project):
    """Projects can be updated:
    - For team projects, by the admins of the team
    - For personal projects, by their owner
    """

    return principal == project.owner or principal.is_admin_of(project.owner)


def delete_project(principal: User, project: Project):
    """Projects can be deleted:
    - For team projects, by the admins of the team
    - For personal projects, by their owner
    """

    return principal == project.owner or principal.is_admin_of(project.owner)


def create_fileset_in_project(principal: User, project: Project):
    """Filesets can be created in a project:
    - For team projects, by the admins of the team
    - For personal projects, by their owner
    """

    return principal == project.owner or principal.is_admin_of(project.owner)


def update_fileset(principal: User, fileset: Fileset):
    """Filesets can be updated:
    - For filesets in team projects, by the admins of the team owning the fileset's project
    - For personal filesets, by their owner
    """

    return principal == fileset.owner or principal.is_admin_of(fileset.owner)


def delete_fileset(principal: User, project: Project):
    """Filesets can be deleted:
    - For filesets in team projects, by the admins of the team owning the fileset's project
    - For personal filesets, by their owner
    """

    return principal == project.owner or principal.is_admin_of(project.owner)


def create_analysis_in_project(principal: User, project: Project):
    """Analyses can be created in a project:
    - For team projects, by the admins of the team
    - For personal projects, by their owner
    """

    return principal == project.owner or principal.is_admin_of(project.owner)


def update_analysis(principal: User, analysis: Analysis):
    """Analyses can be updated:
    - For analyses in team projects, by the admins of the team owning the fileset's project
    - For personal analyses, by their owner
    """

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
