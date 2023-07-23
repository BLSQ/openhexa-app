import binascii

from ariadne import MutationType
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import BadSignature, SignatureExpired, Signer
from django.http import HttpRequest
from django.utils.translation import gettext_lazy

from config import settings
from hexa.core.utils import send_mail
from hexa.countries.models import Country
from hexa.user_management.models import Feature, FeatureFlag, User

from ..models import (
    AlreadyExists,
    Connection,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

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
            load_sample_data=create_input.get("loadSampleData"),
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
def resolve_invite_workspace_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspaceSlug"]
        )
        try:
            # If the user already exists, we add it to the workspace
            user = User.objects.get(email=input["userEmail"])
            workspace_membership = WorkspaceMembership.objects.create_if_has_perm(
                principal=request.user,
                workspace=workspace,
                user=user,
                role=input["role"],
            )
            send_mail(
                title=gettext_lazy(
                    f"You've been added to the workspace {workspace.name}"
                ),
                template_name="workspaces/mails/invite_member",
                template_variables={
                    "workspace": workspace.name,
                    "owner": request.user.display_name,
                    "workspace_url": request.build_absolute_uri(
                        f"//{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace.slug}"
                    ),
                },
                recipient_list=[user.email],
            )
            return {
                "success": True,
                "errors": [],
                "workspace_membership": workspace_membership,
            }
        except User.DoesNotExist:
            # If the user does not exist, we create an invitation to create an account and join the workspace
            invitation = WorkspaceInvitation.objects.create_if_has_perm(
                principal=request.user,
                workspace=workspace,
                email=input["userEmail"],
                role=input["role"],
            )

            token = invitation.generate_invitation_token()
            send_mail(
                title=gettext_lazy(
                    f"You've been invited to join the workspace {workspace.name} on OpenHexa"
                ),
                template_name="workspaces/mails/invite_external_user",
                template_variables={
                    "workspace": workspace.name,
                    "owner": request.user.display_name,
                    "workspace_signup_url": request.build_absolute_uri(
                        f"//{settings.NEW_FRONTEND_DOMAIN}/workspaces/{workspace.slug}/signup?email={input['userEmail']}&token={token}"
                    ),
                },
                recipient_list=[input["userEmail"]],
            )
            return {
                "success": True,
                "errors": [],
            }

    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
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


@workspace_mutations.field("joinWorkspace")
def resolver_join_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = WorkspaceInvitation.objects.get_by_token(input["token"])
        if invitation.status == WorkspaceInvitationStatus.ACCEPTED:
            raise AlreadyExists

        if WorkspaceMembership.objects.filter(
            user__email=invitation.email, workspace=invitation.workspace
        ).exists():
            raise AlreadyExists(
                f"Already got a membership for {invitation.email} and workspace {invitation.workspace.name}"
            )

        if input["password"] != input["confirmPassword"]:
            raise ValidationError("The two passwords do not match.")

        validate_password(password=input["password"])
        user = User.objects.create_user(
            email=invitation.email,
            first_name=input["firstName"],
            last_name=input["lastName"],
            password=input["password"],
        )
        FeatureFlag.objects.create(
            feature=Feature.objects.get(code="workspaces"), user=user
        )
        WorkspaceMembership.objects.create(
            workspace=invitation.workspace,
            user=user,
            role=invitation.role,
        )
        invitation.status = WorkspaceInvitationStatus.ACCEPTED
        invitation.save()
        # automatically signup user
        authenticated_user = authenticate(
            username=invitation.email, password=input["password"]
        )
        login(request, authenticated_user)
        return {"success": True, "errors": [], "workspace": invitation.workspace}

    except SignatureExpired:
        return {
            "success": False,
            "errors": ["EXPIRED_TOKEN"],
        }
    except (binascii.Error, BadSignature) as e:
        return {
            "success": False,
            "errors": ["INVALID_TOKEN"],
        }
    except AlreadyExists:
        return {
            "success": False,
            "errors": ["ALREADY_EXISTS"],
        }
    except ValidationError:
        return {
            "success": False,
            "errors": ["INVALID_CREDENTIALS"],
        }
    except WorkspaceInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
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


@workspace_mutations.field("generateWorkspaceToken")
def resolve_generate_workspace_token(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        membership = WorkspaceMembership.objects.get(
            workspace__slug=mutation_input["slug"], user=request.user
        )
    except WorkspaceMembership.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}

    if membership.role == WorkspaceMembershipRole.VIEWER:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    if not membership.access_token:
        membership.generate_access_token()

    token = Signer().sign_object(str(membership.access_token))
    return {"success": True, "errors": [], "token": token}
