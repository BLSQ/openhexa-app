from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_pipeline(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def update_pipeline(principal: User, pipeline: Pipeline):
    return pipeline.workspace and (
        pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
        or principal.is_organization_admin_or_owner(pipeline.workspace.organization)
    )


def delete_pipeline(principal: User, pipeline: Pipeline):
    return pipeline.workspace and (
        pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN],
        ).exists()
        or principal.is_organization_admin_or_owner(pipeline.workspace.organization)
    )


def run_pipeline(principal: User, pipeline: Pipeline):
    return pipeline.workspace and (
        pipeline.workspace.workspacemembership_set.filter(
            user=principal,
        ).exists()
        or principal.is_organization_admin_or_owner(pipeline.workspace.organization)
    )


def stop_pipeline(principal: User, pipeline: Pipeline):
    return pipeline.workspace and (
        pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
        or principal.is_organization_admin_or_owner(pipeline.workspace.organization)
    )


def schedule_pipeline(principal: User, pipeline: Pipeline):
    if principal.has_perm("pipelines.run_pipeline", pipeline) is False:
        return False
    return pipeline.is_schedulable


def create_pipeline_version(principal: User, pipeline: Pipeline):
    return pipeline.workspace and (
        pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
        or principal.is_organization_admin_or_owner(pipeline.workspace.organization)
    )


def update_pipeline_version(principal: User, version: PipelineVersion):
    return version.pipeline.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists() or principal.is_organization_admin_or_owner(
        version.pipeline.workspace.organization
    )


def delete_pipeline_version(principal: User, version: PipelineVersion):
    return (
        version.pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
        or principal.is_organization_admin_or_owner(
            version.pipeline.workspace.organization
        )
    ) and version.pipeline.versions.count() > 1


def view_pipeline_version(principal: User, pipeline_version: PipelineVersion):
    return pipeline_version.pipeline.workspace.workspacemembership_set.filter(
        user=principal,
    ).exists() or principal.is_organization_admin_or_owner(
        pipeline_version.pipeline.workspace.organization
    )
