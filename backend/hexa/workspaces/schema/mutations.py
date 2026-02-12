from datetime import datetime, timezone

from ariadne import MutationType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import Signer
from django.db import transaction
from django.http import HttpRequest

from hexa.countries.models import Country
from hexa.databases.utils import TableNotFound, delete_table
from hexa.user_management.models import Organization, User

from ..jwt_utils import (
    JWTConfigurationError,
    JWTGenerationError,
    generate_workspace_jwt,
)
from ..models import (
    AlreadyExists,
    Connection,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
    WorkspacesLimitReached,
)
from ..utils import (
    send_workspace_add_user_email,
    send_workspace_invite_new_user_email,
    test_connection,
)

workspace_mutations = MutationType()


@workspace_mutations.field("createWorkspace")
def resolve_create_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]
    organization_id = create_input.get("organization_id", None)

    try:
        organization = (
            Organization.objects.get(id=organization_id)
            if organization_id
            else Organization.objects.get(name="Bluesquare")
        )

        workspace = Workspace.objects.create_if_has_perm(
            principal,
            create_input["name"],
            description=create_input.get("description"),
            countries=(
                [Country.objects.get(code=c["code"]) for c in create_input["countries"]]
                if "countries" in create_input
                else None
            ),
            load_sample_data=create_input.get("load_sample_data"),
            organization=organization,
            configuration=create_input.get("configuration"),
        )

        return {"success": True, "workspace": workspace, "errors": []}
    except Organization.DoesNotExist:
        return {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except WorkspacesLimitReached:
        return {"success": False, "errors": ["WORKSPACES_LIMIT_REACHED"]}


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

        if input.get("docker_image", None) is not None:
            args["docker_image"] = input["docker_image"]

        if "countries" in input:
            countries = [
                Country.objects.get(code=c["code"]) for c in input["countries"]
            ]
            args["countries"] = countries

        if "configuration" in input:
            args["configuration"] = input["configuration"]

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
            slug=input["workspace_slug"]
        )
        user = User.objects.filter(email=input["user_email"]).first()

        if user:
            is_workspace_member = WorkspaceMembership.objects.filter(
                user=user, workspace=workspace
            ).exists()
            if is_workspace_member:
                raise AlreadyExists

            # We directly add existing users to the workspace
            with transaction.atomic():
                WorkspaceMembership.objects.create(
                    workspace=workspace,
                    user=user,
                    role=input["role"],
                )

                send_workspace_add_user_email(
                    invited_by=request.user,
                    workspace=workspace,
                    invitee=user,
                    role=input["role"],
                )
        else:
            is_already_invited = WorkspaceInvitation.objects.filter(
                workspace=workspace,
                email=input["user_email"],
                status=WorkspaceInvitationStatus.PENDING,
            ).exists()
            if is_already_invited:
                raise AlreadyExists

            with transaction.atomic():
                invitation = WorkspaceInvitation.objects.create_if_has_perm(
                    principal=request.user,
                    workspace=workspace,
                    email=input["user_email"],
                    role=input["role"],
                )
                send_workspace_invite_new_user_email(invitation)

        return {"success": True, "errors": []}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except AlreadyExists:
        return {"success": False, "errors": ["ALREADY_EXISTS"]}


@workspace_mutations.field("joinWorkspace")
def resolve_join_workspace(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = WorkspaceInvitation.objects.get(id=input["invitation_id"])
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

        # Create workspace membership
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
        invitation = WorkspaceInvitation.objects.get(id=input["invitation_id"])

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
        ).get(id=input["invitation_id"])

        if not request.user.has_perm("workspaces.manage_members", invitation.workspace):
            raise PermissionDenied

        invitation.status = WorkspaceInvitationStatus.PENDING
        invitation.updated_at = datetime.now(timezone.utc)
        invitation.save()

        send_workspace_invite_new_user_email(invitation)
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
        ).get(id=input["membership_id"])
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
        workspace_membership = WorkspaceMembership.objects.get(
            id=input["membership_id"]
        )
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
            slug=mutation_input.pop("workspace_slug")
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
    except ValidationError:
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


@workspace_mutations.field("testConnection")
def resolve_test_connection(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
    except Workspace.DoesNotExist:
        return {"success": False, "error": "Workspace not found"}

    if not request.user.has_perm("workspaces.create_connection", workspace):
        return {"success": False, "error": "Permission denied"}

    fields = {f["code"]: f["value"] for f in mutation_input["fields"]}
    connection_type = mutation_input["type"]

    success, error = test_connection(connection_type, fields)
    return {"success": success, "error": error}


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
        invitation = WorkspaceInvitation.objects.get(id=input["invitation_id"])
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


@workspace_mutations.field("deleteWorkspaceDatabaseTable")
def resolve_delete_workspace_database_table(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        workspace: Workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=input["workspace_slug"]
        )
        if not request.user.has_perm("workspaces.delete_database_table", workspace):
            return {
                "success": False,
                "errors": ["PERMISSION_DENIED"],
            }

        delete_table(workspace, input.get("table"))
        return {
            "success": True,
            "errors": [],
        }
    except TableNotFound:
        return {
            "success": False,
            "errors": ["TABLE_NOT_FOUND"],
        }
    except Workspace.DoesNotExist:
        return {
            "success": False,
            "errors": ["WORKSPACE_NOT_FOUND"],
        }


@workspace_mutations.field("issueWorkspaceToken")
def resolve_issue_workspace_token(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    if not request.user or not request.user.is_authenticated:
        return {
            "success": False,
            "errors": ["AUTH_UNAUTHENTICATED"],
        }

    workspace_id = mutation_input.get("workspace_id")
    workspace_slug = mutation_input.get("workspace_slug")

    if (workspace_id and workspace_slug) or (not workspace_id and not workspace_slug):
        return {
            "success": False,
            "errors": ["INPUT_INVALID"],
        }

    try:
        if workspace_id:
            membership = WorkspaceMembership.objects.get(
                workspace__id=workspace_id, user=request.user
            )
        else:
            membership = WorkspaceMembership.objects.get(
                workspace__slug=workspace_slug, user=request.user
            )
    except WorkspaceMembership.DoesNotExist:
        try:
            if workspace_id:
                Workspace.objects.get(id=workspace_id)
            else:
                Workspace.objects.get(slug=workspace_slug)
            return {
                "success": False,
                "errors": ["MEMBERSHIP_REQUIRED"],
            }
        except Workspace.DoesNotExist:
            return {
                "success": False,
                "errors": ["WORKSPACE_NOT_FOUND"],
            }

    if not membership.role:
        return {
            "success": False,
            "errors": ["ROLE_UNRESOLVED"],
        }

    try:
        jwt_data = generate_workspace_jwt(
            user_id=str(request.user.id),
            user_email=request.user.email,
            workspace_id=str(membership.workspace.id),
            workspace_slug=membership.workspace.slug,
            role=membership.role,
        )

        return {
            "success": True,
            "token": jwt_data["token"],
            "expires_at": jwt_data["expires_at"],
            "workspace": {
                "id": str(membership.workspace.id),
                "slug": membership.workspace.slug,
            },
            "role": membership.role,
            "errors": [],
        }
    except JWTConfigurationError:
        return {
            "success": False,
            "errors": ["CONFIG_MISSING_PRIVATE_KEY"],
        }
    except JWTGenerationError as e:
        if "clock" in str(e).lower():
            return {
                "success": False,
                "errors": ["CLOCK_ERROR"],
            }
        return {
            "success": False,
            "errors": ["CONFIG_MISSING_PRIVATE_KEY"],
        }
