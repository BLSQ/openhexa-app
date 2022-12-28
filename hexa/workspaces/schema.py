import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.countries.models import Country

from .models import Workspace

workspaces_type_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

workspace_object = ObjectType("Workspace")
workspace_queries = QueryType()
worskspace_mutations = MutationType()


@workspace_queries.field("workspaces")
def resolve_workspaces(_, info, page=1, perPage=15):
    request = info.context["request"]
    queryset = Workspace.objects.filter_for_user(request.user).order_by("-updated_at")
    return result_page(queryset=queryset, page=page, per_page=perPage)


@workspace_queries.field("workspace")
def resolve_workspace(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Workspace.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Workspace.DoesNotExist:
        return None


@worskspace_mutations.field("createWorkspace")
def resolve_create_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        workspace = Workspace.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
            description=create_input.get(
                "description", "This is a workspace for {}".format(create_input["name"])
            ),
            countries=[
                Country.objects.get(code=c["code"]) for c in create_input["countries"]
            ]
            if "countries" in create_input
            else None,
        )
        return {"success": True, "workspace": workspace, "errors": []}
    except PermissionDenied:
        return {"success": False, "workspace": None, "errors": ["PERMISSION_DENIED"]}


@worskspace_mutations.field("updateWorkspace")
def resolve_update_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            id=input["id"]
        )
        args = {}
        if input.get("name", None):
            args["name"] = input["name"]
        if input.get("description", None):
            args["description"] = input["description"]

        if "countries" in input:
            countries = [
                Country.objects.get(code=c["code"]) for c in input["countries"]
            ]
            args["countries"] = countries

        workspace.update_if_has_perm(principal=request.user, **args)

        return {"success": True, "workspace": workspace, "errors": []}
    except Workspace.DoesNotExist:
        return {"success": False, "workspace": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "workspace": None, "errors": ["PERMISSION_DENIED"]}


workspaces_bindables = [workspace_queries, workspace_object, worskspace_mutations]
