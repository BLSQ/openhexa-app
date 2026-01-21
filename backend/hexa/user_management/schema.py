import logging
import pathlib
from datetime import datetime, timezone
from urllib.parse import urlparse

import django_otp
from ariadne import (
    MutationType,
    ObjectType,
    QueryType,
    SchemaDirectiveVisitor,
    load_schema_from_path,
)
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Collate
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode
from django_otp import devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice
from graphql import default_field_resolver

from hexa.analytics.api import track
from hexa.core.graphql import result_page
from hexa.core.string import remove_whitespace
from hexa.core.templatetags.colors import hash_color
from hexa.datasets.models import Dataset, DatasetLink
from hexa.tags.models import Tag
from hexa.user_management.models import (
    AlreadyExists,
    CannotDelete,
    CannotDowngradeRole,
    Feature,
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
from hexa.utils.base64_image_encode_decode import (
    decode_base64_image,
    encode_base64_image,
)
from hexa.workspaces.models import (
    AlreadyExists as WorkspaceAlreadyExists,
)
from hexa.workspaces.models import (
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
)

from .utils import (
    DEVICE_DEFAULT_NAME,
    default_device,
    has_configured_two_factor,
    send_organization_add_user_email,
    send_organization_invite,
    send_signup_email,
)

logger = logging.getLogger(__name__)

identity_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)


class AuthenticationError(PermissionDenied):
    extensions = {"code": "UNAUTHENTICATED"}
    message = "Resolver requires an authenticated user"


class LoginRequiredDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        withoutTwoFactor = self.args.get("withoutTwoFactor")
        original_resolver = field.resolve or default_field_resolver

        def resolve(obj, info, **kwargs):
            request = info.context["request"]
            principal = request.user
            if not principal.is_authenticated:
                raise AuthenticationError

            if not withoutTwoFactor and (
                not getattr(request, "bypass_two_factor", False)
                and has_configured_two_factor(principal)
                and not principal.is_verified()
            ):
                raise AuthenticationError

            return original_resolver(obj, info, **kwargs)

        field.resolve = resolve
        return field


identity_query = QueryType()
identity_mutations = MutationType()

me_permissions_object = ObjectType("MePermissions")


@me_permissions_object.field("createTeam")
def resolve_me_permissions_create_team(obj, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.is_authenticated  # TODO: Implement a real check of permissions


@me_permissions_object.field("superUser")
def resolve_can_superuser(obj, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.is_superuser


@me_permissions_object.field("adminPanel")
def resolve_can_admin_panel(obj, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.is_staff


me_object = ObjectType("Me")


@me_object.field("user")
def resolve_me_user(_, info):
    request = info.context["request"]
    if has_configured_two_factor(request.user):
        return request.user if request.user.is_verified() else None
    elif request.user.is_authenticated:
        return request.user
    return None


@me_object.field("hasTwoFactorEnabled")
def resolve_me_has_two_factor_enabled(_, info):
    request = info.context["request"]
    return has_configured_two_factor(request.user)


@me_object.field("features")
def resolve_me_features(_, info):
    request = info.context["request"]
    principal: User = request.user

    if principal.is_authenticated:
        return [
            {
                "code": feature.code,
                "config": {},
            }  # TODO: Remove the config field once the migration is done
            for feature in Feature.objects.are_enabled_for_user(user=principal)
        ]
    else:
        return []


@me_object.field("permissions")
def resolve_me_permissions(_, info):
    return me_permissions_object


@identity_query.field("me")
def resolve_me(_, info):
    return me_object


@identity_query.field("team")
def resolve_team(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    try:
        return Team.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Team.DoesNotExist:
        return None


@identity_query.field("teams")
def resolve_teams(_, info, term=None, **kwargs):
    request: HttpRequest = info.context["request"]

    queryset = Team.objects.filter_for_user(request.user)

    if term is not None:
        queryset = queryset.filter(name__icontains=term)

    return result_page(
        queryset=queryset,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page"),
    )


team_object = ObjectType("Team")


@team_object.field("memberships")
def resolve_team_memberships(team: Team, *_, **kwargs):
    return result_page(
        queryset=team.membership_set.all(),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page"),
    )


@team_object.field("permissions")
def resolve_team_permissions(team: Team, info):
    return team


team_permissions_object = ObjectType("TeamPermissions")


@team_permissions_object.field("update")
def resolve_team_permissions_update(team: Team, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("user_management.update_team", team)


@team_permissions_object.field("delete")
def resolve_team_permissions_delete(team: Team, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("user_management.delete_team", team)


@team_permissions_object.field("createMembership")
def resolve_team_permissions_create_membership(team: Team, info):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("user_management.create_membership", team)


membership_object = ObjectType("Membership")
membership_permissions_object = ObjectType("MembershipPermissions")


@membership_object.field("permissions")
def resolve_membership_permissions(membership, info, **kwargs):
    return membership


@membership_permissions_object.field("update")
def resolve_membership_permissions_update(membership: Membership, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("user_management.update_membership", membership)


@membership_permissions_object.field("delete")
def resolve_membership_permissions_delete(membership: Membership, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return request.user.has_perm("user_management.delete_membership", membership)


@identity_query.field("organizations")
def resolve_organizations(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return Organization.objects.filter_for_user(request.user).all()


@identity_query.field("users")
def resolve_users(
    _, info, query: str, workspace_slug: str = None, organization_id: str = None
):
    request = info.context["request"]
    query = query.strip()

    users = User.objects.all()

    if not workspace_slug and not organization_id:
        raise ValidationError(
            "You must specify either a workspaceSlug or an organizationId"
        )

    # If workspace_slug is provided, exclude current members of that workspace
    if workspace_slug:
        try:
            workspace = Workspace.objects.filter_for_user(request.user).get(
                slug=workspace_slug
            )

            if not request.user.has_perm("workspaces.manage_members", workspace):
                raise PermissionDenied

            # Exclude current members of the workspace
            users = users.exclude(id__in=workspace.members.values_list("id", flat=True))
        except PermissionDenied:
            return []
        except Workspace.DoesNotExist:
            return []

    # If organization_id is provided, exclude current members of that organization
    if organization_id:
        try:
            organization = Organization.objects.filter_for_user(request.user).get(
                id=organization_id
            )
            if not request.user.has_perm(
                "user_management.manage_members", organization
            ):
                raise PermissionDenied

            users = users.exclude(
                id__in=organization.organizationmembership_set.values_list(
                    "user_id", flat=True
                )
            )
        except PermissionDenied:
            return []
        except Organization.DoesNotExist:
            return []

    # Explicitly collate the email field to allow case-insensitive LIKE queries
    users = users.annotate(case_insensitive_email=Collate("email", "und-x-icu"))

    users = users.filter(
        Q(case_insensitive_email__contains=query)
        | Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
    )

    return users.order_by("email")[:10]


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


user_object = ObjectType("User")


@user_object.field("avatar")
def resolve_avatar(obj: User, *_):
    return {"initials": obj.initials, "color": hash_color(obj.email)}


organization_object = ObjectType("Organization")
organization_queries = QueryType()


@organization_object.field("type")
def resolve_type(obj: Organization, *_):
    return obj.get_organization_type_display()


@organization_object.field("logo")
def resolve_logo(obj: Organization, *_):
    """Convert binary logo to base64 for GraphQL"""
    return encode_base64_image(bytes(obj.logo)) if obj.logo else None


@organization_object.field("members")
def resolve_members(organization: Organization, info, **kwargs):
    qs = organization.organizationmembership_set

    term = kwargs.get("term")
    role = kwargs.get("role")

    if term:
        # Annotate with collated email field to handle case-insensitive email search
        qs = qs.annotate(case_insensitive_email=Collate("user__email", "und-x-icu"))
        qs = qs.filter(
            Q(user__first_name__icontains=term)
            | Q(user__last_name__icontains=term)
            | Q(case_insensitive_email__contains=term)
        )

    if role:
        qs = qs.filter(role=role.lower())

    return result_page(
        queryset=qs.order_by("-updated_at"),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", qs.count() or 10),
    )


@organization_object.field("workspaces")
def resolve_workspaces(organization: Organization, info, **kwargs):
    request = info.context["request"]
    qs = organization.filter_workspaces_for_user(user=request.user).order_by("name")
    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", qs.count() or 10),
    )


@organization_object.field("permissions")
def resolve_organization_permissions(organization: Organization, info):
    return organization


@organization_object.field("invitations")
def resolve_organization_invitations(organization: Organization, info, **kwargs):
    request: HttpRequest = info.context["request"]

    qs = (
        OrganizationInvitation.objects.filter_for_user(request.user)
        .filter(organization=organization)
        .order_by("-updated_at")
    )
    if not kwargs.get("include_accepted"):
        qs = qs.exclude(status=OrganizationInvitationStatus.ACCEPTED)

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 5),
    )


@organization_object.field("pipelineTags")
def resolve_organization_pipeline_tags(organization: Organization, info, **kwargs):
    return list(
        Tag.objects.filter(pipelines__workspace__organization=organization)
        .distinct()
        .values_list("name", flat=True)
        .order_by("name")
    )


@organization_object.field("pendingWorkspaceInvitations")
def resolve_pending_workspace_invitations(organization: Organization, info, **kwargs):
    """Resolve standalone workspace invitations across all workspaces in the organization.
    Only visible to organization admins and owners due to filter_for_user permissions.
    """
    request: HttpRequest = info.context["request"]

    qs = (
        WorkspaceInvitation.objects.filter_for_user(request.user)
        .filter(
            workspace__organization=organization,
            status=WorkspaceInvitationStatus.PENDING,
        )
        .select_related("workspace", "invited_by")
        .order_by("-updated_at")
    )

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 5),
    )


@organization_object.field("pipelineTemplateTags")
def resolve_organization_pipeline_template_tags(
    organization: Organization, info, **kwargs
):
    return (
        Tag.objects.filter(pipeline_templates__workspace__organization=organization)
        .distinct()
        .values_list("name", flat=True)
        .order_by("name")
    )


@organization_object.field("usage")
def resolve_organization_usage(organization: Organization, info, **kwargs):
    """Resolve current resource usage counts."""
    return {
        "users": organization.get_users_count(),
        "workspaces": organization.get_workspaces_count(),
        "pipeline_runs": organization.get_monthly_pipeline_runs_count(),
    }


@organization_object.field("subscription")
def resolve_organization_subscription(organization: Organization, info, **kwargs):
    """Resolve subscription details. Returns null for self-hosted deployments."""
    return organization.active_subscription


subscription_object = ObjectType("Subscription")


@subscription_object.field("limits")
def resolve_subscription_limits(subscription: OrganizationSubscription, info):
    return {
        "users": subscription.users_limit,
        "workspaces": subscription.workspaces_limit,
        "pipeline_runs": subscription.pipeline_runs_limit,
    }


@organization_object.field("datasets")
def resolve_organization_datasets(
    organization: Organization, info, query=None, **kwargs
):
    request: HttpRequest = info.context["request"]

    workspace_slugs = list(organization.workspaces.values_list("slug", flat=True))

    qs = Dataset.objects.filter_for_workspace_slugs(
        request.user, workspace_slugs
    ).filter(workspace__organization=organization)

    if query:
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(slug__icontains=query)
        )

    return result_page(
        queryset=qs.order_by("-updated_at"),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@organization_object.field("datasetLinks")
def resolve_organization_dataset_links(
    organization: Organization, info, query=None, **kwargs
):
    request: HttpRequest = info.context["request"]

    accessible_workspaces = set(organization.filter_workspaces_for_user(request.user))

    qs = DatasetLink.objects.filter_for_workspaces(
        workspaces=accessible_workspaces, query=query
    )

    page_result = result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )

    if accessible_workspaces:
        first_workspace = next(iter(accessible_workspaces))
        for obj in page_result["items"]:
            # If the dataset link is shared with the organization but the user has no access to the workspace, set it to the first accessible workspace
            if (
                obj.dataset.shared_with_organization
                and obj.workspace not in accessible_workspaces
            ):
                obj.workspace = first_workspace

    return page_result


@organization_queries.field("organization")
def resolve_organization(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Organization.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Organization.DoesNotExist:
        return None


organization_permissions_object = ObjectType("OrganizationPermissions")


@organization_permissions_object.field("createWorkspace")
def resolve_organization_permissions_create_workspace(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.create_workspace", organization)
        if user.is_authenticated
        else False
    )


@organization_permissions_object.field("archiveWorkspace")
def resolve_organization_permissions_archive_workspace(
    organization: Organization, info
):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.archive_workspace", organization)
        if user.is_authenticated
        else False
    )


@organization_permissions_object.field("manageMembers")
def resolve_organization_permissions_manage_members(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.manage_members", organization)
        if user.is_authenticated
        else False
    )


@organization_permissions_object.field("manageOwners")
def resolve_organization_permissions_manage_owners(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.manage_owners", organization)
        if user.is_authenticated
        else False
    )


@organization_permissions_object.field("update")
def resolve_organization_permissions_update(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.has_admin_privileges", organization)
        if user.is_authenticated
        else False
    )


@organization_permissions_object.field("delete")
def resolve_organization_permissions_delete(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    return (
        user.has_perm("user_management.delete_organization", organization)
        if user.is_authenticated
        else False
    )


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

        workspace_permissions = update_input.get("workspace_permissions", [])
        if workspace_permissions:
            user = membership.user

            for workspace_permission in workspace_permissions:
                workspace_slug = workspace_permission["workspace_slug"]
                role = workspace_permission.get("role")

                try:
                    workspace = Workspace.objects.get(
                        slug=workspace_slug,
                        organization=membership.organization,
                        archived=False,
                    )

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

                except Workspace.DoesNotExist:
                    continue
        return {"success": True, "membership": membership, "errors": []}
    except OrganizationMembership.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


@identity_mutations.field("deleteOrganizationMember")
@transaction.atomic
def resolve_delete_organization_member(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    delete_input = kwargs["input"]

    try:
        membership = OrganizationMembership.objects.get(id=delete_input["id"])
        with transaction.atomic():
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
                if (
                    Organization.objects.exclude(id=organization.id)
                    .filter(short_name=short_name)
                    .exists()
                ):
                    return {
                        "success": False,
                        "organization": None,
                        "errors": ["SHORT_NAME_DUPLICATE"],
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
                # Empty string means remove logo
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

        # Perform soft delete (which will also archive all workspaces)
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

    organization = Organization.objects.create(
        name=name,
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
        user = None  # User will be created when they accept the invitation

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

    try:
        subscription = OrganizationSubscription.objects.get(
            subscription_id=subscription_id
        )
        subscription.plan_code = plan_code
        subscription.start_date = subscription_start_date
        subscription.end_date = subscription_end_date
        subscription.users_limit = limits["users"]
        subscription.workspaces_limit = limits["workspaces"]
        subscription.pipeline_runs_limit = limits["pipeline_runs"]
        subscription.save()
    except OrganizationSubscription.DoesNotExist:
        OrganizationSubscription.objects.create(
            organization=organization,
            subscription_id=subscription_id,
            plan_code=plan_code,
            start_date=subscription_start_date,
            end_date=subscription_end_date,
            users_limit=limits["users"],
            workspaces_limit=limits["workspaces"],
            pipeline_runs_limit=limits["pipeline_runs"],
        )

    return {
        "success": True,
        "organization": organization,
        "errors": [],
    }


organization_membership_object = ObjectType("OrganizationMembership")


@organization_membership_object.field("role")
def resolve_organization_membership_role(
    membership: OrganizationMembership, info, **kwargs
):
    """Convert lowercase role to uppercase for GraphQL enum"""
    return membership.role.upper()


@organization_membership_object.field("workspaceMemberships")
def resolve_organization_membership_workspace_memberships(
    membership: OrganizationMembership, info, **kwargs
):
    """Return workspace memberships for this user within the organization"""
    return WorkspaceMembership.objects.filter(
        user=membership.user,
        workspace__organization=membership.organization,
        workspace__archived=False,
    ).select_related("workspace")


organization_invitation_object = ObjectType("OrganizationInvitation")


@organization_invitation_object.field("role")
def resolve_organization_invitation_role(
    invitation: OrganizationInvitation, info, **kwargs
):
    """Convert lowercase role to uppercase for GraphQL enum"""
    return invitation.role.upper()


@organization_invitation_object.field("workspaceInvitations")
def resolve_organization_invitation_workspace_invitations(
    invitation: OrganizationInvitation, info, **kwargs
):
    """Resolve workspace invitations for this organization invitation"""
    return invitation.workspace_invitations.all()


identity_bindables = [
    identity_query,
    user_object,
    team_object,
    me_object,
    membership_object,
    me_permissions_object,
    team_permissions_object,
    membership_permissions_object,
    organization_object,
    organization_queries,
    organization_permissions_object,
    organization_membership_object,
    organization_invitation_object,
    subscription_object,
    identity_mutations,
]

identity_directives = {"loginRequired": LoginRequiredDirective}
