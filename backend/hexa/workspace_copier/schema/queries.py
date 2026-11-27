from ariadne import QueryType
from django.http import HttpRequest

from hexa.workspace_copier.models import WorkspaceCopyRun, WorkspaceCopyRunStatus

workspace_copier_queries = QueryType()

# Logs can run to megabytes; the `logs` field reads only the part it needs.
_runs = WorkspaceCopyRun.objects.defer("logs", "summary")


@workspace_copier_queries.field("workspaceCopyRun")
def resolve_workspace_copy_run(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        run = _runs.get(id=kwargs["id"])
    except WorkspaceCopyRun.DoesNotExist:
        return None
    if not request.user.has_perm("workspace_copier.view_workspace_copy_run", run):
        return None
    return run


@workspace_copier_queries.field("activeWorkspaceCopyRun")
def resolve_active_workspace_copy_run(_, info):
    request: HttpRequest = info.context["request"]
    return _runs.filter(
        created_by=request.user,
        acts_as_requester=True,
        status__in=[WorkspaceCopyRunStatus.QUEUED, WorkspaceCopyRunStatus.RUNNING],
    ).first()


bindables = [workspace_copier_queries]
