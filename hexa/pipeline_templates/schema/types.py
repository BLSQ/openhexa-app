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


bindables = [
    pipeline_template_object,
    pipeline_template_permissions,
    pipeline_template_version_permissions,
]
