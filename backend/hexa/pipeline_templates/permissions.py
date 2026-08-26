from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_pipeline_template_version(principal: User, workspace: Workspace):
    return workspace.has_role(
        principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
    ) or principal.is_organization_admin_or_owner(workspace.organization)


def delete_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return pipeline_template.workspace and (
        pipeline_template.workspace.has_role(principal, WorkspaceMembershipRole.ADMIN)
        or principal.is_organization_admin_or_owner(
            pipeline_template.workspace.organization
        )
    )


def update_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return pipeline_template.workspace and (
        pipeline_template.workspace.has_role(
            principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
        )
        or principal.is_organization_admin_or_owner(
            pipeline_template.workspace.organization
        )
    )


def delete_pipeline_template_version(
    principal: User, pipeline_template_version: PipelineTemplateVersion
):
    return (
        pipeline_template_version.template.workspace
        and pipeline_template_version.template.versions.count() > 1
        and (
            pipeline_template_version.template.workspace.has_role(
                principal, WorkspaceMembershipRole.ADMIN
            )
            or principal.is_organization_admin_or_owner(
                pipeline_template_version.template.workspace.organization
            )
        )
    )


def update_pipeline_template_version(
    principal: User, pipeline_template_version: PipelineTemplateVersion
):
    return pipeline_template_version.template.workspace and (
        pipeline_template_version.template.workspace.has_role(
            principal, WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN
        )
        or principal.is_organization_admin_or_owner(
            pipeline_template_version.template.workspace.organization
        )
    )
