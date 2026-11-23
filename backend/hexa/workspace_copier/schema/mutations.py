from ariadne import MutationType
from django.http import HttpRequest

from hexa.countries.models import Country
from hexa.workspace_copier.duplicate import (
    CopyAlreadyRunning,
    DuplicateRefused,
    check_can_duplicate,
)
from hexa.workspace_copier.models import WorkspaceCopyRun
from hexa.workspace_copier.queue import queue_duplicate_workspace

NAME_MAX_LENGTH = WorkspaceCopyRun._meta.get_field("target_workspace_name").max_length

workspace_copier_mutations = MutationType()


@workspace_copier_mutations.field("duplicateWorkspace")
def resolve_duplicate_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    # A blank name would make the copier silently reuse the source's.
    name = input["name"].strip()
    if not name or len(name) > NAME_MAX_LENGTH:
        return {"success": False, "errors": ["INVALID_NAME"]}

    try:
        workspace = check_can_duplicate(request.user, input["workspace_slug"])
    except DuplicateRefused as exc:
        return {"success": False, "errors": [exc.code]}

    countries = None
    if input.get("countries") is not None:
        countries = sorted({c["code"] for c in input["countries"]})
        # Checked here: the worker would only find out mid-run, after the
        # requester has left.
        known = Country.objects.filter(code__in=countries).values("code").distinct()
        if known.count() != len(countries):
            return {"success": False, "errors": ["INVALID_COUNTRY"]}

    try:
        run = queue_duplicate_workspace(
            request.user,
            workspace,
            name=name,
            countries=countries,
            resources=input["resources"],
            include_connection_secrets=input["include_connection_secrets"],
        )
    except CopyAlreadyRunning:
        return {"success": False, "errors": ["COPY_ALREADY_RUNNING"]}
    return {"success": True, "errors": [], "run": run}


bindables = [workspace_copier_mutations]
