from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace, WorkspaceMembershipRole


def create_pipeline_template_version(principal: User, workspace: Workspace):
    return workspace.workspacemembership_set.filter(
        user=principal,
        role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
    ).exists() or principal.is_organization_admin_or_owner(workspace.organization)


def delete_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return pipeline_template.workspace and (
        pipeline_template.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.ADMIN],
        ).exists()
        or principal.is_organization_admin_or_owner(
            pipeline_template.workspace.organization
        )
    )


def update_pipeline_template(principal: User, pipeline_template: PipelineTemplate):
    return pipeline_template.workspace and (
        pipeline_template.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
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
            pipeline_template_version.template.workspace.workspacemembership_set.filter(
                user=principal,
                role__in=[WorkspaceMembershipRole.ADMIN],
            ).exists()
            or principal.is_organization_admin_or_owner(
                pipeline_template_version.template.workspace.organization
            )
        )
    )


def update_pipeline_template_version(
    principal: User, pipeline_template_version: PipelineTemplateVersion
):
    return pipeline_template_version.template.workspace and (
        pipeline_template_version.template.workspace.workspacemembership_set.filter(
            user=principal,
            role__in=[WorkspaceMembershipRole.EDITOR, WorkspaceMembershipRole.ADMIN],
        ).exists()
        or principal.is_organization_admin_or_owner(
            pipeline_template_version.template.workspace.organization
        )
    )
