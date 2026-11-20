from ariadne import MutationType
from django.http import HttpRequest

from hexa.countries.models import Country
from hexa.workspace_copier.queue import queue_duplicate_workspace
from hexa.workspaces.models import Workspace

workspace_copier_mutations = MutationType()


@workspace_copier_mutations.field("duplicateWorkspace")
def resolve_duplicate_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    workspace = (
        Workspace.objects.filter_for_user(request.user)
        .filter(slug=input["workspace_slug"])
        .select_related("organization")
        .first()
    )
    if workspace is None:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    if not request.user.has_perm("workspaces.duplicate_workspace", workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    if workspace.organization.is_workspaces_limit_reached():
        return {"success": False, "errors": ["WORKSPACES_LIMIT_REACHED"]}

    countries = None
    if input.get("countries") is not None:
        countries = sorted({c["code"] for c in input["countries"]})
        # Checked here: the worker would only find out mid-run, after the
        # requester has left.
        known = Country.objects.filter(code__in=countries).values("code").distinct()
        if known.count() != len(countries):
            return {"success": False, "errors": ["INVALID_COUNTRY"]}

    run = queue_duplicate_workspace(
        request.user,
        workspace,
        name=input["name"].strip(),
        countries=countries,
        resources=input["resources"],
        include_connection_secrets=input["include_connection_secrets"],
    )
    return {"success": True, "errors": [], "run": run}


bindables = [workspace_copier_mutations]
