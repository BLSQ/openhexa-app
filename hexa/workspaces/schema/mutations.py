from datetime import datetime

from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import Signer
from django.db import IntegrityError, transaction
from django.http import HttpRequest
from django.utils.translation import gettext_lazy, override

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
from ..utils import send_workspace_invitation_email

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
            if not user.has_feature_flag("workspaces"):
                FeatureFlag.objects.create(
                    feature=Feature.objects.get(code="workspaces"), user=user
                )

            with override(user.language):
                send_mail(
                    title=gettext_lazy(
                        "You've been added to the workspace {workspace_name}"
                    ).format(workspace_name=workspace.name),
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
            try:
                invitation = WorkspaceInvitation.objects.create_if_has_perm(
                    principal=request.user,
                    workspace=workspace,
                    email=input["userEmail"],
                    role=input["role"],
                )
                send_workspace_invitation_email(invitation)
                return {
                    "success": True,
                    "errors": [],
                }
            except IntegrityError:
                return {
                    "success": False,
                    "errors": ["ALREADY_EXISTS"],
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
def resolve_join_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = WorkspaceInvitation.objects.get(id=input["invitationId"])
        if invitation.status == WorkspaceInvitationStatus.ACCEPTED:
            return {"success": False, "errors": ["ALREADY_ACCEPTED"]}
        if request.user.email != invitation.email:
            raise PermissionDenied("You cannot accept an invitation for another user.")

        if WorkspaceMembership.objects.filter(
            user=request.user, workspace=invitation.workspace
        ).exists():
            raise AlreadyExists(
                f"Already got a membership for {request.user} and workspace {invitation.workspace.name}"
            )

        # We create the membership
        WorkspaceMembership.objects.create(
            workspace=invitation.workspace,
            user=request.user,
            role=invitation.role,
        )
        invitation.status = WorkspaceInvitationStatus.ACCEPTED
        invitation.save()

        return {
            "success": True,
            "errors": [],
            "workspace": invitation.workspace,
            "invitation": invitation,
        }

    except AlreadyExists:
        return {
            "success": False,
            "errors": ["ALREADY_EXISTS"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except WorkspaceInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }


@workspace_mutations.field("declineWorkspaceInvitation")
def resolve_decline_workspace_invitation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = WorkspaceInvitation.objects.get(id=input["invitationId"])

        if request.user.email != invitation.email:
            raise PermissionDenied("You cannot decline an invitation for another user.")
        if invitation.status in (
            WorkspaceInvitationStatus.DECLINED,
            WorkspaceInvitationStatus.ACCEPTED,
        ):
            raise PermissionDenied(
                "You cannot decline an invitation that has been declined or accepted."
            )

        invitation.status = WorkspaceInvitationStatus.DECLINED
        invitation.save()
        return {
            "success": True,
            "invitation": invitation,
            "errors": [],
        }
    except WorkspaceInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@workspace_mutations.field("resendWorkspaceInvitation")
def resolve_resend_workspace_invitation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = WorkspaceInvitation.objects.exclude(
            status=WorkspaceInvitationStatus.ACCEPTED
        ).get(id=input["invitationId"])

        if not request.user.has_perm("workspaces.manage_members", invitation.workspace):
            raise PermissionDenied

        invitation.status = WorkspaceInvitationStatus.PENDING
        invitation.updated_at = datetime.utcnow()
        invitation.save()

        send_workspace_invitation_email(invitation)
        return {
            "success": True,
            "errors": [],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except WorkspaceInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }


@workspace_mutations.field("updateWorkspaceMember")
def resolve_update_workspace_member(_, info, **kwargs):
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
        with transaction.atomic():
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

    token = Signer().sign_object(str(membership.access_token))
    return {"success": True, "errors": [], "token": token}


@workspace_mutations.field("deleteWorkspaceInvitation")
def resolve_delete_workspace_invitation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]
    try:
        invitation = WorkspaceInvitation.objects.get(id=input["invitationId"])
        if invitation.status == WorkspaceInvitationStatus.ACCEPTED:
            raise PermissionDenied(
                "Cannot delete an invitation that has already been accepted."
            )

        invitation.delete_if_has_perm(principal=request.user)
        return {"success": True, "errors": []}
    except WorkspaceInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
