import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.graphql import result_page
from hexa.core.utils import send_mail
from hexa.countries.models import Country
from hexa.user_management.models import User

from .models import AlreadyExists, Workspace, WorkspaceMembership

workspaces_type_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

workspace_object = ObjectType("Workspace")
workspace_queries = QueryType()
worskspace_mutations = MutationType()


@workspace_object.field("countries")
def resolve_workspace_countries(workspace: Workspace, info, **kwargs):
    if workspace.countries is not None:
        return workspace.countries
    return []


@workspace_object.field("members")
def resolve_workspace_members(workspace: Workspace, info, **kwargs):
    request = info.context["request"]
    qs = WorkspaceMembership.objects.filter_for_user(request.user).filter(
        workspace=workspace
    )
    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage", qs.count()),
    )


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
            description=create_input.get("description"),
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


@worskspace_mutations.field("deleteWorkspace")
def resolve_delete_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            id=input["id"]
        )
        workspace.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@worskspace_mutations.field("createWorkspaceMember")
def resolve_create_workspace_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            id=input["workspaceId"]
        )
        user = (
            User.objects.get(email=input["userEmail"]) if "userEmail" in input else None
        )

        workspace_membership = WorkspaceMembership.objects.create_if_has_perm(
            principal=request.user, workspace=workspace, user=user, role=input["role"]
        )
        send_mail(
            title=gettext_lazy("You've been added to a Workspace"),
            template_name="workspaces/mails/invite_member",
            template_variables={
                "workspace": workspace.name,
                "owner": "{} {}".format(
                    request.user.first_name, request.user.last_name
                ),
                "url": "{url}/workspaces/{workspace_id}".format(
                    url=settings.NEW_FRONTEND_DOMAIN, workspace_id=workspace.id
                ),
            },
            recipient_list=[user.email],
        )
        return {
            "success": True,
            "errors": [],
            "workspace_membership": workspace_membership,
        }
    except (Workspace.DoesNotExist, User.DoesNotExist):
        return {"success": False, "errors": ["NOT_FOUND"], "workspace_membership": None}
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
            "workspace_membership": None,
        }
    except AlreadyExists:
        return {
            "success": False,
            "errors": ["ALREADY_EXISTS"],
            "workspace_membership": None,
        }


workspaces_bindables = [workspace_queries, workspace_object, worskspace_mutations]
