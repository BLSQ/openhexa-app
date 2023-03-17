from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole
from hexa.pipelines.models import Pipeline


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
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
    )


def run_pipeline(principal: User, pipeline: Pipeline):
    return (
        pipeline.workspace
        and pipeline.workspace.workspacemembership_set.filter(
            user=principal,
        ).exists()
    )
