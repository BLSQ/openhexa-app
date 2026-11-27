from ariadne import EnumType, ObjectType
from django.db.models.functions import Length, Substr
from django.http import HttpRequest

from hexa.databases.api import database_in_use
from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspace_copier.orchestrator import WORKSPACE_COPIERS
from hexa.workspace_copier.results import StepStatus
from hexa.workspaces.models import Workspace

STEP_NAMES = [copier.name for copier in WORKSPACE_COPIERS]

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

workspace_copy_step_name_enum = EnumType(
    "WorkspaceCopyStepName",
    {name.upper(): name for name in STEP_NAMES},
)

workspace_copy_run_object = ObjectType("WorkspaceCopyRun")
workspace_object = ObjectType("Workspace")


@workspace_copy_run_object.field("error")
def resolve_workspace_copy_run_error(run: WorkspaceCopyRun, info):
    return run.error or None


@workspace_copy_run_object.field("steps")
def resolve_workspace_copy_run_steps(run: WorkspaceCopyRun, info):
    selected = {"workspace", *run.resources}
    steps = []
    for name in STEP_NAMES:
        if name not in selected:
            continue
        status = run.steps.get(name, StepStatus.PENDING)
        # A step still running when the run ended is the one that stopped it.
        if status == StepStatus.RUNNING and not run.is_active:
            status = StepStatus.FAILED
        steps.append({"name": name, "status": status})
    return steps


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


@workspace_object.field("databaseInUse")
def resolve_workspace_database_in_use(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    if not request.user.has_perm("workspaces.duplicate_workspace", workspace):
        return None
    return database_in_use(workspace.db_name)


bindables = [
    workspace_copy_resource_enum,
    workspace_copy_step_name_enum,
    workspace_copy_run_object,
    workspace_object,
]
