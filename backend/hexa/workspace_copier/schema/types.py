from ariadne import EnumType, ObjectType
from django.db.models.functions import Length, Substr
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


@workspace_copy_run_object.field("sourceWorkspaceSlug")
def resolve_workspace_copy_run_source_slug(run: WorkspaceCopyRun, info):
    return run.source_slug


@workspace_copy_run_object.field("logs")
def resolve_workspace_copy_run_logs(run: WorkspaceCopyRun, info, offset=0):
    # One statement, so the text and its length come from the same snapshot.
    # The reporter appends whole lines, so any offset returned here falls on a
    # line boundary.
    row = (
        WorkspaceCopyRun.objects.filter(id=run.id)
        .annotate(tail=Substr("logs", max(offset, 0) + 1), length=Length("logs"))
        .values("tail", "length")
        .get()
    )
    return {"text": row["tail"], "next_offset": row["length"]}


def _visible_workspace(info, slug: str) -> Workspace | None:
    if not slug:
        return None
    request: HttpRequest = info.context["request"]
    return Workspace.objects.filter_for_user(request.user).filter(slug=slug).first()


@workspace_copy_run_object.field("sourceWorkspace")
def resolve_workspace_copy_run_source_workspace(run: WorkspaceCopyRun, info):
    return _visible_workspace(info, run.source_slug)


@workspace_copy_run_object.field("workspace")
def resolve_workspace_copy_run_workspace(run: WorkspaceCopyRun, info):
    return _visible_workspace(info, run.result_workspace_slug)


bindables = [workspace_copy_resource_enum, workspace_copy_run_object]
