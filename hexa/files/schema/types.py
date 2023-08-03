from ariadne import ObjectType, convert_kwargs_to_snake_case
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from hexa.files.api import NotFound, get_bucket_object, list_bucket_objects
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_object, workspace_permissions


@workspace_permissions.field("createObject")
def resolve_workspace_permission_create_object(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("files.create_object", workspace)


@workspace_permissions.field("deleteObject")
def resolve_workspace_permission_delete_object(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("files.delete_object", workspace)


@workspace_permissions.field("downloadObject")
def resolve_workspace_permission_download_object(workspace: Workspace, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("files.download_object", workspace)


@workspace_object.field("bucket")
def resolve_workspace_bucket(workspace, info, **kwargs):
    return workspace


bucket_object = ObjectType("Bucket")
bucket_object_object = ObjectType("BucketObject")


@bucket_object.field("name")
def resolve_bucket_name(workspace, info, **kwargs):
    return workspace.bucket_name


@bucket_object.field("objects")
@convert_kwargs_to_snake_case
def resolve_bucket_objects(
    workspace,
    info,
    prefix=None,
    page=1,
    per_page=15,
    ignore_hidden_files=True,
    **kwargs
):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")
    page = list_bucket_objects(
        workspace.bucket_name,
        prefix=prefix,
        page=page,
        per_page=per_page,
        ignore_hidden_files=ignore_hidden_files,
    )

    return page


@bucket_object.field("object")
def resolve_bucket_object(workspace, info, key, **kwargs):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")
    try:
        return get_bucket_object(workspace.bucket_name, key)
    except NotFound:
        return None


bucket_object_object.set_alias("updatedAt", "updated")


@bucket_object_object.field("type")
def resolve_object_type(obj, info):
    return obj["type"].upper()


bindables = [bucket_object, bucket_object_object]
