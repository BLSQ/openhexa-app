from ariadne import QueryType
from django.http import HttpRequest

from hexa.workspace_copier.models import WorkspaceCopyRun

workspace_copier_queries = QueryType()


@workspace_copier_queries.field("workspaceCopyRun")
def resolve_workspace_copy_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        run = WorkspaceCopyRun.objects.get(id=kwargs["id"])
    except WorkspaceCopyRun.DoesNotExist:
        return None
    if not request.user.has_perm("workspace_copier.view_workspace_copy_run", run):
        return None
    return run


bindables = [workspace_copier_queries]
