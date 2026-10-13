from ariadne import ObjectType
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from hexa.files import storage
from hexa.files.backends.base import ObjectsPage, StorageObject
from hexa.files.utils import PUBLIC_FOLDER, is_safe_path
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


def _is_public_folder(obj: StorageObject) -> bool:
    # Directory keys end with a slash on the cloud backends and not on the
    # filesystem one.
    return obj.type == "directory" and str(obj.key).rstrip("/") == PUBLIC_FOLDER


def _find_public_folder(bucket_name: str) -> StorageObject | None:
    for key in (f"{PUBLIC_FOLDER}/", PUBLIC_FOLDER):
        try:
            obj = storage.get_bucket_object(bucket_name, key)
        except storage.exceptions.NotFound:
            continue
        if obj.type == "directory":
            return obj
    # A folder that only exists through the files under it (uploaded by the SDK,
    # for instance) has no object of its own on the cloud backends.
    if storage.list_bucket_objects(
        bucket_name, prefix=f"{PUBLIC_FOLDER}/", per_page=1
    ).items:
        return StorageObject(
            name=PUBLIC_FOLDER,
            key=f"{PUBLIC_FOLDER}/",
            path=f"{bucket_name}/{PUBLIC_FOLDER}/",
            type="directory",
        )
    return None


def pin_public_folder(page: ObjectsPage, bucket_name: str) -> ObjectsPage:
    """Put the public folder first in a root listing, whichever page it fell on."""
    items = [obj for obj in page.items if not _is_public_folder(obj)]
    if page.page_number == 1:
        folder = next(
            (obj for obj in page.items if _is_public_folder(obj)), None
        ) or _find_public_folder(bucket_name)
        if folder is not None:
            items.insert(0, folder)
    page.items = items
    return page


@bucket_object.field("objects")
def resolve_bucket_objects(
    workspace,
    info,
    prefix=None,
    query=None,
    page=1,
    per_page=15,
    ignore_hidden_files=True,
    **kwargs,
):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")
    if prefix and not is_safe_path(prefix):
        return {
            "has_previous_page": False,
            "has_next_page": False,
            "page_number": 1,
            "items": [],
        }
    page = storage.list_bucket_objects(
        workspace.bucket_name,
        prefix=prefix,
        page=page,
        per_page=per_page,
        query=query,
        ignore_hidden_files=ignore_hidden_files,
    )
    if workspace.public_files_enabled and not prefix and not query:
        page = pin_public_folder(page, workspace.bucket_name)

    return page


@bucket_object.field("object")
def resolve_bucket_object(workspace, info, key, **kwargs):
    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")
    if not is_safe_path(key):
        return None
    try:
        return storage.get_bucket_object(workspace.bucket_name, key)
    except storage.exceptions.NotFound:
        return None


@bucket_object_object.field("type")
def resolve_object_type(obj: StorageObject, info):
    return obj.type.upper()


bindables = [bucket_object, bucket_object_object]
