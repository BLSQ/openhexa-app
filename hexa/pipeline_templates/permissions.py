from hexa.pipeline_templates.models import PipelineTemplate
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_pipeline_template_version(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists()


def delete_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return (
        pipeline_template.workspace
        and pipeline_template.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN],
        ).exists()
    )


def update_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return (
        pipeline_template.workspace
        and pipeline_template.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
    )
