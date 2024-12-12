from ariadne import ObjectType

from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_permissions

template_permissions = ObjectType("TemplatePermissions")
template_version_permissions = ObjectType("TemplateVersionPermissions")


@workspace_permissions.field("createTemplateVersion")
def resolve_workspace_permissions_create_template_version(
    obj: Workspace, info, **kwargs
):
    request = info.context["request"]

    return request.user.is_authenticated and request.user.has_perm(
        "templates.create_template_version", obj
    )


bindables = [
    template_permissions,
    template_version_permissions,
]
