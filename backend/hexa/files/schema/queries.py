from ariadne import QueryType
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

from hexa.files import storage
from hexa.files.backends.exceptions import NotFound
from hexa.workspaces.models import Workspace

files_queries = QueryType()


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


bindables = [files_queries]
