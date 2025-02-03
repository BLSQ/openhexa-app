from ariadne import ObjectType

from hexa.pipeline_templates.models import PipelineTemplate
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

pipeline_template_permissions = ObjectType("PipelineTemplatePermissions")
pipeline_template_version_permissions = ObjectType("PipelineTemplateVersionPermissions")

pipeline_template_object = ObjectType("PipelineTemplate")


@workspace_permissions.field("createPipelineTemplateVersion")
def resolve_workspace_permissions_create_pipeline_template_version(
    obj: Workspace, info, **kwargs
):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "pipeline_templates.create_pipeline_template_version", obj
    )


@pipeline_template_object.field("versions")
def resolve_pipeline_template_versions(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.versions.all()


@pipeline_template_object.field("currentVersion")
def resolve_pipeline_template_current_version(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.last_version


@pipeline_template_object.field("sourcePipeline")
def resolve_pipeline_template_source_pipeline(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.source_pipeline


@pipeline_template_object.field("permissions")
def resolve_pipeline_permissions(pipeline_template: PipelineTemplate, info, **kwargs):
    return pipeline_template


@pipeline_template_permissions.field("delete")
def resolve_pipeline_template_permissions_delete(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    request = info.context["request"]
    user = request.user
    return user.is_authenticated and user.has_perm(
        "pipeline_templates.delete_pipeline_template", pipeline_template
    )


bindables = [
    pipeline_template_object,
    pipeline_template_permissions,
    pipeline_template_version_permissions,
]
