from datetime import datetime, timezone
from urllib.parse import urlparse

import django_otp
from ariadne import MutationType
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode
from django_otp import devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice

from hexa.analytics.api import track
from hexa.core.string import generate_short_name, remove_whitespace
from hexa.user_management.models import (
    AlreadyExists,
    CannotDelete,
    CannotDowngradeRole,
    Membership,
    Organization,
    OrganizationInvitation,
    OrganizationInvitationStatus,
    OrganizationMembership,
    OrganizationMembershipRole,
    OrganizationSubscription,
    SignupRequest,
    SignupRequestStatus,
    Team,
    User,
    UsersLimitReached,
)
from hexa.utils.base64_image_encode_decode import decode_base64_image
from hexa.workspaces.models import (
    AlreadyExists as WorkspaceAlreadyExists,
    Workspace,
    WorkspaceInvitation,
    WorkspaceMembership,
)

from ..utils import (
    DEVICE_DEFAULT_NAME,
    default_device,
    has_configured_two_factor,
    send_organization_add_user_email,
    send_organization_invite,
    send_signup_email,
)

identity_mutations = MutationType()


def update_workspace_permissions(
    user: User, organization: Organization, workspace_permissions
):
    for workspace_permission in workspace_permissions:
        workspace_slug = workspace_permission["workspace_slug"]
        role = workspace_permission.get("role")

        try:
            workspace = Workspace.objects.get(
                slug=workspace_slug, organization=organization, archived=False
            )
        except Workspace.DoesNotExist:
            continue

        existing_membership = WorkspaceMembership.objects.filter(
            user=user, workspace=workspace
        ).first()

        if role is None:
            if existing_membership:
                existing_membership.delete()
        else:
            if existing_membership:
                existing_membership.role = role
                existing_membership.save()
            else:
                WorkspaceMembership.objects.create(
                    user=user,
                    workspace=workspace,
                    role=role,
                )


@identity_mutations.field("createTeam")
def resolve_create_team(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        team = Team.objects.create_if_has_perm(
            principal,
            name=create_input["name"],
        )
        return {"success": True, "team": team, "errors": []}
    except PermissionDenied:
        return {"success": False, "team": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("updateTeam")
def resolve_update_team(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    input = kwargs["input"]

    try:
        team: Team = Team.objects.get(id=input["id"])
        team.update_if_has_perm(principal, name=input["name"])
        return {"success": True, "team": team, "errors": []}
    except Team.DoesNotExist:
        return {"success": False, "team": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "team": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("deleteTeam")
def resolve_delete_team(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    input = kwargs["input"]

    try:
        team: Team = Team.objects.get(id=input["id"])
        team.delete_if_has_perm(principal)
        return {"success": True, "errors": []}
    except Team.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("login")
@transaction.atomic
def resolve_login(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    trimmed_email = remove_whitespace(mutation_input["email"])

    user_candidate = authenticate(
        request,
        email=trimmed_email,
        password=mutation_input["password"],
    )

    if user_candidate is None:
        return {"success": False, "errors": ["INVALID_CREDENTIALS"]}

    if has_configured_two_factor(user_candidate):
        device = default_device(user_candidate)
        if not mutation_input.get("token"):
            device.generate_challenge()
            return {"success": False, "errors": ["OTP_REQUIRED"]}
        if not device.verify_token(mutation_input["token"]):
            return {"success": False, "errors": ["INVALID_OTP"]}
        user_candidate.otp_device = device

    login(request, user_candidate)
    track(request, "users.user_logged_in", user=request.user)
    return {"success": True}


@identity_mutations.field("logout")
def resolve_logout(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if request.user.is_authenticated:
        logout(request)

    return {"success": True}


@identity_mutations.field("signup")
def resolve_signup(_, info, **kwargs):
    """Handle self-registration signup request."""
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    if not settings.ALLOW_SELF_REGISTRATION:
        return {"success": False, "errors": ["SELF_REGISTRATION_DISABLED"]}

    email = remove_whitespace(mutation_input["email"]).lower()

    if User.objects.filter(email=email).exists():
        return {"success": True, "errors": []}

    existing = SignupRequest.objects.filter(
        email=email,
        status=SignupRequestStatus.PENDING,
    ).first()

    signup_request = existing or SignupRequest.objects.create(email=email)
    send_signup_email(signup_request)

    track(request, "users.signup_requested", properties={"email": email})

    return {"success": True, "errors": []}


@identity_mutations.field("register")
def resolve_register(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    if request.user.is_authenticated:
        return {"success": False, "errors": ["ALREADY_LOGGED_IN"]}

    token = mutation_input["invitation_token"]
    invitation = (
        WorkspaceInvitation.objects.get_pending_by_token(token)
        or OrganizationInvitation.objects.get_pending_by_token(token)
        or SignupRequest.objects.get_pending_by_token(token)
    )
    if not invitation:
        return {"success": False, "errors": ["INVALID_TOKEN"]}

    if User.objects.filter(email=invitation.email).exists():
        return {"success": False, "errors": ["EMAIL_TAKEN"]}

    if mutation_input["password1"] != mutation_input["password2"]:
        return {"success": False, "errors": ["PASSWORD_MISMATCH"]}

    try:
        validate_password(password=mutation_input["password1"])
    except ValidationError:
        return {"success": False, "errors": ["INVALID_PASSWORD"]}

    with transaction.atomic():
        user = User.objects.create_user(
            email=invitation.email,
            password=mutation_input["password1"],
            first_name=mutation_input["first_name"],
            last_name=mutation_input["last_name"],
        )
        invitation.accept(user)

    track(
        request,
        event="emails.registration_complete",
        properties={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **invitation.get_tracking_properties(),
        },
    )

    authenticated_user = authenticate(
        username=user.email, password=mutation_input["password1"]
    )
    login(request, authenticated_user)
    return {"success": True, "errors": []}


@identity_mutations.field("resetPassword")
def resolve_reset_password(_, info, input, **kwargs):
    request: HttpRequest = info.context["request"]
    form = PasswordResetForm({"email": input["email"]})
    if form.is_valid():
        parsed_url = urlparse(settings.NEW_FRONTEND_DOMAIN)
        domain_override = parsed_url.netloc
        use_https = parsed_url.scheme == "https"
        form.save(request=request, domain_override=domain_override, use_https=use_https)
        return {"success": True}
    else:
        return {"success": False}


@identity_mutations.field("setPassword")
def resolve_set_password(_, info, input, **kwargs):
    try:
        uid = urlsafe_base64_decode(input["uidb64"]).decode()
        user = User._default_manager.get(pk=uid)
    except User.DoesNotExist:
        return {"success": False, "error": "USER_NOT_FOUND"}
    except (TypeError, ValueError, OverflowError, ValidationError):
        return {"success": False, "error": "INVALID_TOKEN"}

    if default_token_generator.check_token(user, input["token"]):
        password1 = input["password1"]
        password2 = input["password2"]

        if not password1 or not password2 or password1 != password2:
            return {"success": False, "error": "PASSWORD_MISMATCH"}
        try:
            password_validation.validate_password(
                password1,
            )
        except ValidationError:
            return {"success": False, "error": "INVALID_PASSWORD"}

        user.set_password(password1)
        user.save()
        return {"success": True}
    else:
        return {"success": False, "error": "INVALID_TOKEN"}


@identity_mutations.field("createMembership")
@transaction.atomic
def resolve_create_membership(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        user = User.objects.get(email=create_input["user_email"])
        team = Team.objects.get(id=create_input["team_id"])

        try:
            membership = Membership.objects.create_if_has_perm(
                principal,
                user=user,
                team=team,
                role=create_input["role"],
            )
            return {"success": True, "membership": membership, "errors": []}
        except AlreadyExists:
            return {"success": False, "membership": None, "errors": ["ALREADY_EXISTS"]}

    except (Team.DoesNotExist, User.DoesNotExist):
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("updateMembership")
@transaction.atomic
def resolve_update_membership(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        membership = Membership.objects.filter_for_user(user=principal).get(
            id=update_input["id"]
        )
        try:
            membership.update_if_has_perm(principal, role=update_input["role"])
        except CannotDowngradeRole:
            return {
                "success": False,
                "membership": membership,
                "errors": ["INVALID_ROLE"],
            }

        return {"success": True, "membership": membership, "errors": []}

    except Membership.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("deleteMembership")
@transaction.atomic
def resolve_delete_membership(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        membership = Membership.objects.filter_for_user(user=principal).get(
            id=delete_input["id"]
        )
        try:
            membership.delete_if_has_perm(principal)

            return {"success": True, "membership": membership, "errors": []}
        except CannotDelete:
            return {
                "success": True,
                "membership": membership,
                "errors": ["CANNOT_DELETE"],
            }

    except Membership.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("verifyDevice")
def resolve_verify_token(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]
    token = mutation_input.get("token")

    user_device = default_device(request.user, confirmed=False)

    if user_device is None:
        return {"success": False, "errors": ["NO_DEVICE"]}
    elif user_device.verify_token(token):
        user_device.confirmed = True
        user_device.save()
        django_otp.login(request, user_device)
        return {"success": True, "errors": []}

    return {"success": False, "errors": ["INVALID_OTP"]}


@identity_mutations.field("generateChallenge")
def resolve_generate_challenge(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    device = default_device(request.user) or default_device(request.user, None)

    if device is None or device.user != request.user:
        return {"success": False, "errors": ["DEVICE_NOT_FOUND"]}

    try:
        device.generate_challenge()
    except Exception:
        return {"success": False, "errors": ["CHALLENGE_ERROR"]}

    return {"success": True}


@identity_mutations.field("disableTwoFactor")
def resolve_disable_two_factor(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]
    token = mutation_input["token"]

    if not django_otp.match_token(request.user, token):
        return {"success": False, "errors": ["INVALID_OTP"]}

    devices = devices_for_user(request.user)
    if devices is None:
        return {"success": False, "errors": ["NOT_ENABLED"]}

    for device in devices:
        device.delete()

    return {"success": True}


@identity_mutations.field("enableTwoFactor")
def resolve_enable_two_factor(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs.get("input", {})

    if has_configured_two_factor(request.user):
        return {"success": False, "errors": ["ALREADY_ENABLED"]}

    if "email" in mutation_input and request.user.email != mutation_input["email"]:
        return {"success": False, "errors": ["EMAIL_MISMATCH"]}

    device = default_device(request.user, confirmed=None)
    if device is None:
        device = EmailDevice(
            user=request.user,
            email=mutation_input.get("email", None),
            name=DEVICE_DEFAULT_NAME,
            confirmed=False,  # Do not confirm the device yet as user has to verify it.
        )
    device.generate_challenge()
    device.save()

    return {"success": True, "verified": False, "errors": []}


@identity_mutations.field("updateUser")
def resolve_update_user(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]
    user = request.user
    for field_name in ["first_name", "last_name"]:
        if field_name in mutation_input:
            setattr(user, field_name, mutation_input[field_name])

    if mutation_input.get("language", None):
        if mutation_input["language"] not in dict(settings.LANGUAGES):
            return {
                "success": False,
                "errors": ["INVALID_LANGUAGE"],
            }
        user.language = mutation_input["language"]

    user.save()
    return {"success": True, "errors": [], "user": user}


@identity_mutations.field("updateUserAiSettings")
def resolve_update_user_ai_settings(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]
    user = request.user
    ai_settings = user.ai_settings_safe
    for field_name in ["enabled", "provider", "model", "api_key"]:
        if field_name in mutation_input:
            setattr(ai_settings, field_name, mutation_input[field_name])

    ai_settings.save()
    return {"success": True, "errors": [], "user": user}


@identity_mutations.field("updateOrganizationMember")
@transaction.atomic
def resolve_update_organization_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        membership = OrganizationMembership.objects.get(id=update_input["id"])
        new_role = update_input["role"].lower()
        if new_role != membership.role:
            membership.update_if_has_perm(principal=principal, role=new_role)

        update_workspace_permissions(
            user=membership.user,
            organization=membership.organization,
            workspace_permissions=update_input.get("workspace_permissions", []),
        )

        return {"success": True, "membership": membership, "errors": []}
    except OrganizationMembership.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("updateExternalCollaborator")
@transaction.atomic
def resolve_update_external_collaborator(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        user = User.objects.get(id=update_input["user_id"])
        organization = Organization.objects.filter_for_user(principal).get(
            id=update_input["organization_id"]
        )
        if not principal.has_perm("user_management.manage_members", organization):
            raise PermissionDenied()

        update_workspace_permissions(
            user=user,
            organization=organization,
            workspace_permissions=update_input.get("workspace_permissions", []),
        )

        return {"success": True, "errors": []}

    except User.DoesNotExist:
        return {"success": False, "errors": ["USER_NOT_FOUND"]}
    except Organization.DoesNotExist:
        return {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("deleteExternalCollaborator")
@transaction.atomic
def resolve_delete_external_collaborator(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        user = User.objects.get(id=delete_input["user_id"])
        organization = Organization.objects.filter_for_user(principal).get(
            id=delete_input["organization_id"]
        )
        if not principal.has_perm("user_management.manage_members", organization):
            raise PermissionDenied()

        WorkspaceMembership.objects.filter(
            user=user, workspace__organization=organization
        ).delete()

        return {"success": True, "errors": []}

    except User.DoesNotExist:
        return {"success": False, "errors": ["USER_NOT_FOUND"]}
    except Organization.DoesNotExist:
        return {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("convertExternalCollaboratorToMember")
@transaction.atomic
def resolve_convert_external_collaborator_to_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    input_data = kwargs["input"]

    try:
        user = User.objects.get(id=input_data["user_id"])
        organization = Organization.objects.filter_for_user(principal).get(
            id=input_data["organization_id"]
        )

        is_already_org_member = OrganizationMembership.objects.filter(
            user=user, organization=organization
        ).exists()
        if is_already_org_member:
            return {
                "success": False,
                "membership": None,
                "errors": ["NOT_EXTERNAL_COLLABORATOR"],
            }

        has_workspace_membership = WorkspaceMembership.objects.filter(
            user=user, workspace__organization=organization, workspace__archived=False
        ).exists()
        if not has_workspace_membership:
            return {
                "success": False,
                "membership": None,
                "errors": ["NOT_EXTERNAL_COLLABORATOR"],
            }

        membership = OrganizationMembership.create_if_has_perm(
            principal=principal,
            organization=organization,
            user=user,
            role=input_data["role"].lower(),
        )

        return {"success": True, "membership": membership, "errors": []}

    except User.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["USER_NOT_FOUND"]}
    except Organization.DoesNotExist:
        return {
            "success": False,
            "membership": None,
            "errors": ["ORGANIZATION_NOT_FOUND"],
        }
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}
    except UsersLimitReached:
        return {"success": False, "membership": None, "errors": ["USERS_LIMIT_REACHED"]}


@identity_mutations.field("deleteOrganizationMember")
@transaction.atomic
def resolve_delete_organization_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        membership = OrganizationMembership.objects.get(id=delete_input["id"])
        WorkspaceMembership.objects.filter(
            user=membership.user, workspace__organization=membership.organization
        ).delete()
        membership.delete_if_has_perm(principal=principal)

        return {"success": True, "errors": []}

    except OrganizationMembership.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("inviteOrganizationMember")
def resolve_invite_organization_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    input = kwargs["input"]

    try:
        organization: Organization = Organization.objects.filter_for_user(
            request.user
        ).get(id=input["organization_id"])

        workspace_slugs = [
            ws["workspace_slug"] for ws in input["workspace_invitations"]
        ]
        if workspace_slugs:
            existing_workspace_slugs = set(
                organization.workspaces.filter(
                    slug__in=workspace_slugs, archived=False
                ).values_list("slug", flat=True)
            )
            if not set(workspace_slugs).issubset(existing_workspace_slugs):
                return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}

        user = User.objects.filter(email=input["user_email"]).first()

        if user:
            is_organization_member = OrganizationMembership.objects.filter(
                user=user, organization=organization
            ).exists()
            if is_organization_member:
                raise AlreadyExists

            with transaction.atomic():
                OrganizationMembership.create_if_has_perm(
                    principal=principal,
                    organization=organization,
                    user=user,
                    role=input["organization_role"].lower(),
                )
                for workspace_invitation in input["workspace_invitations"]:
                    try:
                        workspace = Workspace.objects.get(
                            slug=workspace_invitation["workspace_slug"],
                            organization=organization,
                            archived=False,
                        )
                        WorkspaceMembership.objects.create_if_has_perm(
                            principal=request.user,
                            workspace=workspace,
                            user=user,
                            role=workspace_invitation["role"],
                        )
                    except WorkspaceAlreadyExists:
                        continue
                    except Workspace.DoesNotExist:
                        continue

                send_organization_add_user_email(
                    invited_by=request.user,
                    organization=organization,
                    invitee=user,
                    role=input["organization_role"].lower(),
                    workspace_invitations=input["workspace_invitations"],
                )
        else:
            is_already_invited = OrganizationInvitation.objects.filter(
                organization=organization,
                email=input["user_email"],
                status=OrganizationInvitationStatus.PENDING,
            ).exists()
            if is_already_invited:
                raise AlreadyExists

            with transaction.atomic():
                invitation = OrganizationInvitation.objects.create_if_has_perm(
                    principal=request.user,
                    organization=organization,
                    email=input["user_email"],
                    role=input["organization_role"].lower(),
                    workspace_invitations=input["workspace_invitations"],
                )
                send_organization_invite(invitation)

        return {"success": True, "errors": []}
    except Organization.DoesNotExist:
        return {"success": False, "errors": ["ORGANIZATION_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except AlreadyExists:
        return {"success": False, "errors": ["ALREADY_MEMBER"]}
    except UsersLimitReached:
        return {"success": False, "errors": ["USERS_LIMIT_REACHED"]}


@identity_mutations.field("deleteOrganizationInvitation")
def resolve_delete_organization_invitation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = OrganizationInvitation.objects.get(id=input["id"])

        if not request.user.has_perm(
            "user_management.manage_members", invitation.organization
        ):
            raise PermissionDenied

        invitation.delete()
        return {"success": True, "errors": []}
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except OrganizationInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }


@identity_mutations.field("resendOrganizationInvitation")
def resolve_resend_organization_invitation(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    input = kwargs["input"]

    try:
        invitation = OrganizationInvitation.objects.exclude(
            status=OrganizationInvitationStatus.ACCEPTED
        ).get(id=input["id"])

        if not request.user.has_perm(
            "user_management.manage_members", invitation.organization
        ):
            raise PermissionDenied

        invitation.status = OrganizationInvitationStatus.PENDING
        invitation.updated_at = datetime.now(timezone.utc)
        invitation.save()

        send_organization_invite(invitation)
        return {
            "success": True,
            "errors": [],
        }
    except PermissionDenied:
        return {
            "success": False,
            "errors": ["PERMISSION_DENIED"],
        }
    except OrganizationInvitation.DoesNotExist:
        return {
            "success": False,
            "errors": ["INVITATION_NOT_FOUND"],
        }


@identity_mutations.field("updateOrganization")
@transaction.atomic
def resolve_update_organization(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    update_input = kwargs["input"]

    try:
        organization = Organization.objects.filter_for_user(principal).get(
            id=update_input["id"]
        )

        if not principal.has_perm("user_management.has_admin_privileges", organization):
            raise PermissionDenied

        if "name" in update_input and update_input["name"]:
            new_name = update_input["name"].strip()
            if (
                Organization.objects.exclude(id=organization.id)
                .filter(name=new_name)
                .exists()
            ):
                return {
                    "success": False,
                    "organization": None,
                    "errors": ["NAME_DUPLICATE"],
                }
            organization.name = new_name

        if "short_name" in update_input:
            short_name_input = update_input["short_name"]
            short_name = short_name_input.strip()
            if short_name:
                if (
                    not short_name
                    or not short_name.isupper()
                    or not short_name.isalpha()
                    or len(short_name) > 5
                ):
                    return {
                        "success": False,
                        "organization": None,
                        "errors": ["INVALID_SHORT_NAME"],
                    }
                organization.short_name = short_name

        if "logo" in update_input:
            if update_input["logo"]:
                try:
                    logo_bytes = decode_base64_image(update_input["logo"])
                    organization.logo = logo_bytes
                except Exception:
                    return {
                        "success": False,
                        "organization": None,
                        "errors": ["INVALID_LOGO"],
                    }
            else:
                organization.logo = None

        organization.save()
        return {"success": True, "organization": organization, "errors": []}

    except Organization.DoesNotExist:
        return {"success": False, "organization": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {
            "success": False,
            "organization": None,
            "errors": ["PERMISSION_DENIED"],
        }


@identity_mutations.field("deleteOrganization")
@transaction.atomic
def resolve_delete_organization(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        organization = Organization.objects.filter_for_user(principal).get(
            id=delete_input["id"]
        )

        if not principal.has_perm("user_management.delete_organization", organization):
            raise PermissionDenied

        organization.delete()

        return {"success": True, "errors": []}

    except Organization.DoesNotExist:
        return {"success": False, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("createOrganization")
@transaction.atomic
def resolve_create_organization(_, info, **kwargs):
    """
    Create a new organization with subscription.
    Requires 'manage_all_organizations' permission (for service accounts).
    """
    request: HttpRequest = info.context["request"]
    principal = request.user

    if not principal.has_perm("user_management.manage_all_organizations"):
        return {
            "success": False,
            "organization": None,
            "user": None,
            "errors": ["PERMISSION_DENIED"],
        }

    create_input = kwargs["input"]
    owner_email = create_input["owner_email"].strip().lower()
    name = create_input["name"].strip()
    short_name_input = (create_input.get("short_name") or "").strip()
    subscription_id = create_input["subscription_id"]
    plan_code = create_input["plan_code"]
    subscription_start_date = create_input["subscription_start_date"]
    subscription_end_date = create_input["subscription_end_date"]
    limits = create_input["limits"]

    if Organization.objects.filter(name=name).exists():
        return {
            "success": False,
            "organization": None,
            "user": None,
            "errors": ["NAME_DUPLICATE"],
        }

    if short_name_input and (
        not short_name_input.isupper()
        or not short_name_input.isalpha()
        or len(short_name_input) > 5
    ):
        return {
            "success": False,
            "organization": None,
            "user": None,
            "errors": ["INVALID_SHORT_NAME"],
        }

    organization = Organization.objects.create(
        name=name,
        short_name=short_name_input or generate_short_name(name),
        organization_type="CORPORATE",
    )

    OrganizationSubscription.objects.create(
        organization=organization,
        subscription_id=subscription_id,
        plan_code=plan_code,
        start_date=subscription_start_date,
        end_date=subscription_end_date,
        users_limit=limits["users"],
        workspaces_limit=limits["workspaces"],
        pipeline_runs_limit=limits["pipeline_runs"],
        max_pipeline_timeout=limits.get("max_pipeline_timeout"),
        pipeline_cpu_limit=limits.get("pipeline_cpu_limit"),
        pipeline_memory_limit=limits.get("pipeline_memory_limit"),
        notebook_profile=limits.get("notebook_profile"),
    )

    try:
        user = User.objects.get(email__iexact=owner_email)
        OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role=OrganizationMembershipRole.OWNER,
        )
        send_organization_add_user_email(
            invited_by=principal,
            organization=organization,
            invitee=user,
            role=OrganizationMembershipRole.OWNER,
        )
    except User.DoesNotExist:
        invitation = OrganizationInvitation.objects.create(
            email=owner_email,
            organization=organization,
            invited_by=principal,
            role=OrganizationMembershipRole.OWNER,
        )
        send_organization_invite(invitation)
        user = None

    return {
        "success": True,
        "organization": organization,
        "user": user,
        "errors": [],
    }


@identity_mutations.field("updateOrganizationSubscription")
@transaction.atomic
def resolve_update_organization_subscription(_, info, **kwargs):
    """
    Create or update organization subscription.
    Used by the Bluesquare Console when subscription changes.
    Requires 'manage_all_organizations' permission (for service accounts).

    Behavior:
    - If subscription with subscriptionId exists → update it
    - If subscription with subscriptionId doesn't exist → create new record
    """
    request: HttpRequest = info.context["request"]
    principal = request.user

    if not principal.has_perm("user_management.manage_all_organizations"):
        return {
            "success": False,
            "organization": None,
            "errors": ["PERMISSION_DENIED"],
        }

    update_input = kwargs["input"]
    organization_id = update_input["organization_id"]
    subscription_id = update_input["subscription_id"]
    plan_code = update_input["plan_code"]
    subscription_start_date = update_input["subscription_start_date"]
    subscription_end_date = update_input["subscription_end_date"]
    limits = update_input["limits"]

    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        return {
            "success": False,
            "organization": None,
            "errors": ["NOT_FOUND"],
        }

    OrganizationSubscription.objects.update_or_create(
        subscription_id=subscription_id,
        defaults={
            "organization": organization,
            "plan_code": plan_code,
            "start_date": subscription_start_date,
            "end_date": subscription_end_date,
            "users_limit": limits["users"],
            "workspaces_limit": limits["workspaces"],
            "pipeline_runs_limit": limits["pipeline_runs"],
            "max_pipeline_timeout": limits.get("max_pipeline_timeout"),
            "pipeline_cpu_limit": limits.get("pipeline_cpu_limit"),
            "pipeline_memory_limit": limits.get("pipeline_memory_limit"),
            "notebook_profile": limits.get("notebook_profile"),
        },
    )

    return {
        "success": True,
        "organization": organization,
        "errors": [],
    }


bindables = [
    identity_mutations,
]
