from ariadne import QueryType
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.workspaces.models import Workspace

files_queries = QueryType()

MAX_READ_SIZE = 1024 * 1024


@files_queries.field("getFileByPath")
def resolve_get_file_by_path(_, info, workspace_slug, path):
    request: HttpRequest = info.context["request"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return None

    if workspace.bucket_name is None:
        raise ImproperlyConfigured("Workspace does not have a bucket")

    try:
        return storage.get_bucket_object(workspace.bucket_name, path)
    except NotFound:
        return None


@files_queries.field("readFileContent")
def resolve_read_file_content(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    workspace_slug = kwargs["workspace_slug"]
    file_path = kwargs["file_path"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=workspace_slug
        )
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if not request.user.has_perm("files.download_object", workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    try:
        obj = storage.get_bucket_object(workspace.bucket_name, file_path)
    except NotFound:
        return {"success": False, "errors": ["NOT_FOUND"]}

    if obj.type != "file":
        return {"success": False, "errors": ["NOT_A_FILE"]}

    if obj.size > MAX_READ_SIZE:
        return {"success": False, "errors": ["FILE_TOO_LARGE"]}

    try:
        content = storage.read_object(workspace.bucket_name, file_path)
        return {
            "success": True,
            "errors": [],
            "content": content.decode("utf-8"),
            "size": len(content),
        }
    except UnicodeDecodeError:
        return {"success": False, "errors": ["NOT_UTF8"]}


bindables = [files_queries]
