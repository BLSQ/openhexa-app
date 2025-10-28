from ariadne import ObjectType

from hexa.core.graphql import result_page
from hexa.pipeline_templates.models import PipelineTemplate, PipelineTemplateVersion
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

pipeline_template_permissions = ObjectType("PipelineTemplatePermissions")
pipeline_template_version_permissions = ObjectType("PipelineTemplateVersionPermissions")

pipeline_template_object = ObjectType("PipelineTemplate")
pipeline_template_version_object = ObjectType("PipelineTemplateVersion")


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
    qs = pipeline_template.versions.order_by("-created_at")
    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


@pipeline_template_object.field("currentVersion")
def resolve_pipeline_template_current_version(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.last_version


@pipeline_template_object.field("workspace")
def resolve_pipeline_template_workspace(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.workspace


@pipeline_template_object.field("updatedAt")
def resolve_pipeline_template_updated_at(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.updated_at


@pipeline_template_object.field("sourcePipeline")
def resolve_pipeline_template_source_pipeline(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    return pipeline_template.source_pipeline


@pipeline_template_object.field("permissions")
def resolve_pipeline_permissions(pipeline_template: PipelineTemplate, info, **kwargs):
    return pipeline_template


@pipeline_template_object.field("tags")
def resolve_pipeline_template_tags(pipeline_template: PipelineTemplate, info, **kwargs):
    return pipeline_template.tags.all()


@pipeline_template_object.field("publisher")
def resolve_pipeline_template_publisher(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    if not pipeline_template.workspace or not pipeline_template.workspace.organization:
        return None

    org_name = pipeline_template.workspace.organization.name
    if org_name == "Bluesquare":
        return "Bluesquare"
    return "Community"


@pipeline_template_permissions.field("delete")
def resolve_pipeline_template_permissions_delete(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    request = info.context["request"]
    user = request.user
    return user.is_authenticated and user.has_perm(
        "pipeline_templates.delete_pipeline_template", pipeline_template
    )


@pipeline_template_permissions.field("update")
def resolve_pipeline_template_permissions_update(
    pipeline_template: PipelineTemplate, info, **kwargs
):
    request = info.context["request"]
    user = request.user
    return user.is_authenticated and user.has_perm(
        "pipeline_templates.update_pipeline_template", pipeline_template
    )


@pipeline_template_version_object.field("isLatestVersion")
def resolve_pipeline_version_is_latest(
    version: PipelineTemplateVersion, info, **kwargs
):
    return version.is_latest_version


@pipeline_template_version_object.field("permissions")
def resolve_template_version_permissions(
    version: PipelineTemplateVersion, info, **kwargs
):
    return version


@pipeline_template_version_permissions.field("delete")
def resolve_template_version_permissions_delete(
    pipeline_template_version: PipelineTemplateVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipeline_templates.delete_pipeline_template_version", pipeline_template_version
    )


@pipeline_template_version_permissions.field("update")
def resolve_template_version_permissions_update(
    pipeline_template_version: PipelineTemplateVersion, info, **kwargs
):
    request = info.context["request"]
    return request.user.is_authenticated and request.user.has_perm(
        "pipeline_templates.update_pipeline_template_version", pipeline_template_version
    )


bindables = [
    pipeline_template_object,
    pipeline_template_version_object,
    pipeline_template_permissions,
    pipeline_template_version_permissions,
]
