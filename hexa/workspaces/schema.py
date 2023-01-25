import pathlib
from uuid import UUID

from ariadne import (
    MutationType,
    ObjectType,
    QueryType,
    ScalarType,
    load_schema_from_path,
)
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.graphql import result_page
from hexa.core.utils import send_mail
from hexa.countries.models import Country
from hexa.user_management.models import User
from hexa.user_management.schema import me_permissions_object

from .models import AlreadyExists, Workspace, WorkspaceMembership

workspaces_type_def = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

workspace_object = ObjectType("Workspace")
workspace_queries = QueryType()
workspace_mutations = MutationType()
workspace_permissions = ObjectType("WorkspacePermissions")

uuid_scalar = ScalarType("UUID")


@uuid_scalar.value_parser
def parse_uuid_value(value):
    try:
        UUID(value, version=4)
        return str(value).upper()
    except (ValueError, TypeError):
        raise ValueError(f'"{value}" is not a valid uuid')


@me_permissions_object.field("createWorkspace")
def resolve_me_permissions_create_workspace(me, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.create_workspace")


@workspace_permissions.field("update")
def resolve_workspace_permission_update(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.update_workspace", workspace)


@workspace_permissions.field("delete")
def resolve_workspace_permission_delete(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.delete_workspace", workspace)


@workspace_permissions.field("manageMembers")
def resolve_workspace_permission_manage(workspace: Workspace, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("workspaces.manage_members", workspace)


@workspace_object.field("permissions")
def resolve_workspace_permissions(workspace: Workspace, info):
    return workspace


@workspace_object.field("countries")
def resolve_workspace_countries(workspace: Workspace, info, **kwargs):
    if workspace.countries is not None:
        return workspace.countries
    return []


@workspace_object.field("members")
def resolve_workspace_members(workspace: Workspace, info, **kwargs):
    qs = workspace.workspacemembership_set.all().order_by("-updated_at")
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


@workspace_mutations.field("createWorkspace")
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
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("updateWorkspace")
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
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("deleteWorkspace")
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


@workspace_mutations.field("inviteWorkspaceMember")
def resolve_create_workspace_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            id=input["workspaceId"]
        )
        user = User.objects.get(email=input["userEmail"])

        workspace_membership = WorkspaceMembership.objects.create_if_has_perm(
            principal=request.user, workspace=workspace, user=user, role=input["role"]
        )
        send_mail(
            title=gettext_lazy(f"You've been added to the workspace {workspace.name}"),
            template_name="workspaces/mails/invite_member",
            template_variables={
                "workspace": workspace.name,
                "owner": request.user.display_name,
                "workspace_url": request.build_absolute_uri(
                    f"//{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace.id}"
                ),
            },
            recipient_list=[user.email],
        )
        return {
            "success": True,
            "errors": [],
            "workspace_membership": workspace_membership,
        }
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
        }
    except User.DoesNotExist:
        return {
            "success": False,
            "errors": ["USER_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except AlreadyExists:
        return {
            "success": False,
            "errors": ["ALREADY_EXISTS"],
        }


@workspace_mutations.field("updateWorkspaceMember")
def resolver_update_workspace_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:

        workspace_membership = WorkspaceMembership.objects.filter_for_user(
            request.user
        ).get(id=input["membershipId"])
        workspace_membership.update_if_has_perm(
            principal=request.user, role=input["role"]
        )
        return {
            "success": True,
            "errors": [],
            "workspace_membership": workspace_membership,
        }
    except WorkspaceMembership.DoesNotExist:
        return {
            "success": False,
            "errors": ["MEMBERSHIP_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


@workspace_mutations.field("deleteWorkspaceMember")
def resolve_delete_workspace_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace_membership = WorkspaceMembership.objects.get(id=input["membershipId"])
        workspace_membership.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except WorkspaceMembership.DoesNotExist:
        return {
            "success": False,
            "errors": ["MEMBERSHIP_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }


workspaces_bindables = [
    workspace_queries,
    workspace_object,
    workspace_mutations,
    workspace_permissions,
    uuid_scalar,
]
