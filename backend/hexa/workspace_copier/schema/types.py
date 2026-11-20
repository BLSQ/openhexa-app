from ariadne import EnumType, ObjectType
from django.http import HttpRequest

from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspaces.models import Workspace

workspace_copy_resource_enum = EnumType(
    "WorkspaceCopyResource",
    {
        "FILES": "files",
        "DATABASE": "database",
        "CONNECTIONS": "connections",
        "PIPELINES": "pipelines",
        "DATASETS": "datasets",
        "WEBAPPS": "webapps",
    },
)

workspace_copy_run_object = ObjectType("WorkspaceCopyRun")


@workspace_copy_run_object.field("error")
def resolve_workspace_copy_run_error(run: WorkspaceCopyRun, info):
    return run.error or None


@workspace_copy_run_object.field("workspace")
def resolve_workspace_copy_run_workspace(run: WorkspaceCopyRun, info):
    if not run.result_workspace_slug:
        return None
    request: HttpRequest = info.context["request"]
    return (
        Workspace.objects.filter_for_user(request.user)
        .filter(slug=run.result_workspace_slug)
        .first()
    )


bindables = [workspace_copy_resource_enum, workspace_copy_run_object]
