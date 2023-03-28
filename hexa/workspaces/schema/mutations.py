from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.utils import send_mail
from hexa.countries.models import Country
from hexa.user_management.models import User

from ..models import AlreadyExists, Connection, Workspace, WorkspaceMembership

workspace_mutations = MutationType()


@workspace_mutations.field("createWorkspace")
def resolve_create_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        workspace = Workspace.objects.create_if_has_perm(
            principal,
            create_input["name"],
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
            slug=input["slug"]
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
            slug=input["slug"]
        )
        workspace.delete_if_has_perm(principal=request.user)

        return {"success": True, "errors": []}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("archiveWorkspace")
def resolve_archive_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["slug"]
        )
        workspace.archive_if_has_perm(principal=request.user)

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
            slug=input["workspaceSlug"]
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


@workspace_mutations.field("createConnection")
def resolve_create_workspace_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input.pop("workspaceSlug")
        )
        mutation_input["connection_type"] = mutation_input.pop("type")

        connection = Connection.objects.create_if_has_perm(
            request.user, workspace, **mutation_input
        )

        return {"success": True, "errors": [], "connection": connection}
    except ValidationError:
        return {"success": False, "errors": ["INVALID_SLUG"]}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("updateConnection")
def resolve_update_workspace_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        connection_id = mutation_input.pop("id")
        connection = Connection.objects.filter_for_user(request.user).get(
            id=connection_id
        )

        connection.update_if_has_perm(request.user, **mutation_input)
        return {"success": True, "errors": [], "connection": connection}
    except ValidationError as e:
        return {"success": False, "errors": ["INVALID_SLUG"]}
    except Connection.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_CONNECTION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("deleteConnection")
def resolve_delete_workspace_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        connection = Connection.objects.filter_for_user(request.user).get(
            id=mutation_input.pop("id")
        )
        connection.delete_if_has_perm(request.user)
        return {"success": True, "errors": []}
    except Connection.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


bindables = [
    workspace_mutations,
]
