from ariadne import ObjectType

from hexa.core.graphql import result_page
from hexa.template_pipelines.models import Template
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

template_permissions = ObjectType("TemplatePermissions")
template_version_permissions = ObjectType("TemplateVersionPermissions")

template_object = ObjectType("Template")


@workspace_permissions.field("createTemplateVersion")
def resolve_workspace_permissions_create_template_version(
    obj: Workspace, info, **kwargs
):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "templates.create_template_version", obj
    )


@template_object.field("versions")
def resolve_pipeline_versions(template: Template, info, **kwargs):
    qs = template.versions.all()
    return result_page(
        queryset=qs, page=kwargs.get("page", 1), per_page=kwargs.get("per_page")
    )


bindables = [
    template_object,
    template_permissions,
    template_version_permissions,
]
