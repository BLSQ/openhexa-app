from hexa.pipelines.models import Pipeline, PipelineVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_pipeline(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()


def update_pipeline(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
    )


def delete_pipeline(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN],
        ).exists()
    )


def run_pipeline(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
        ).exists()
    )


def stop_pipeline(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
        ).exists()
    )


def create_pipeline_version(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
    )


def update_pipeline_version(principal: User, version: PipelineVersion):
    return version.pipeline.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def delete_pipeline_version(principal: User, pipeline: Pipeline):
    return pipeline.workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.ADMIN, WorkspaceMembershipRole.EDITOR],
    ).exists()


def view_pipeline_version(principal: User, pipeline_version: PipelineVersion):
    return pipeline_version.pipeline.workspace.workspacemembership_set.filter(
        user=principal,
    ).exists()
