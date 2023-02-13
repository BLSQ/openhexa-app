from ariadne import ObjectType, convert_kwargs_to_snake_case
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
def resolve_bucket_objects(workspace, info, prefix=None, page_token=None, **kwargs):
    object_page = list_bucket_objects(workspace, prefix=prefix, page_token=page_token)

    return {
        "next_page_token": object_page.next_page_token,
        "items": object_page.items,
    }


@bucket_object.field("object")
def resolve_bucket_object(workspace, info, name, **kwargs):
    try:
        return get_bucket_object(workspace, name=name)
    except NotFound:
        return None


bucket_object_object.set_alias("updatedAt", "updated")


@bucket_object_object.field("type")
def resolve_object_type(obj, info):
    return obj["type"].upper()


bindables = [bucket_object, bucket_object_object]
