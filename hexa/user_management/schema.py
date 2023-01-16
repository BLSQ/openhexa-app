import logging
import pathlib

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
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode
from django_otp import devices_for_user
from django_otp.plugins.otp_email.models import EmailDevice
from graphql import default_field_resolver

from hexa.app import get_hexa_app_configs
from hexa.core.graphql import result_page
from hexa.core.templatetags.colors import hash_color
from hexa.user_management.models import (
    AlreadyExists,
    CannotDelete,
    CannotDowngradeRole,
    FeatureFlag,
    Membership,
    Organization,
    Team,
    User,
)

from .utils import default_device, has_configured_two_factor

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
                has_configured_two_factor(principal) and not principal.is_verified()
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
feature_flag_object = ObjectType("FeatureFlag")


@feature_flag_object.field("code")
def resolve_feature_flag_code(flag: FeatureFlag, info):
    return flag.feature.code


@feature_flag_object.field("config")
def resolve_feature_flag_config(flag: FeatureFlag, info):
    return flag.config


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


# FIXME: To remove once authorizedActions are completely deprecated
@me_object.field("authorizedActions")
def resolve_me_authorized_actions(_, info):
    request = info.context["request"]
    principal = request.user
    authorized_actions = []

    # Base authorized actions
    if principal.has_perm("user_management.create_team"):
        authorized_actions.append("CREATE_TEAM")

    if principal.is_staff:
        authorized_actions.append("ADMIN_PANEL")

    if principal.is_superuser:
        authorized_actions.append("SUPER_USER")

    # Loop over plugin configs and check if we have an extra resolver for this field
    for app_config in get_hexa_app_configs(connector_only=True):
        extra_authorized_actions_resolver = (
            app_config.get_extra_graphql_me_authorized_actions_resolver()
        )
        if extra_authorized_actions_resolver is not None:
            authorized_actions += extra_authorized_actions_resolver(_, info)

    return authorized_actions


@me_object.field("features")
def resolve_me_features(_, info):
    request = info.context["request"]
    principal: User = request.user

    if principal.is_authenticated:
        return principal.featureflag_set.all()
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
        per_page=kwargs.get("perPage"),
    )


team_object = ObjectType("Team")


@team_object.field("memberships")
def resolve_team_memberships(team: Team, *_, **kwargs):
    return result_page(
        queryset=team.membership_set.all(),
        page=kwargs.get("page", 1),
        per_page=kwargs.get("perPage"),
    )


# FIXME: To remove once authorizedActions are completely deprecated
@team_object.field("authorizedActions")
def resolve_team_authorized_actions(team: Team, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user

    return filter(
        bool,
        [
            "UPDATE" if user.has_perm("user_management.update_team", team) else None,
            "DELETE" if user.has_perm("user_management.delete_team", team) else None,
            "CREATE_MEMBERSHIP"
            if user.has_perm("user_management.create_membership", team)
            else None,
        ],
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


# FIXME: To remove once authorizedActions are completely deprecated
@membership_object.field("authorizedActions")
def resolve_membership_authorized_actions(membership: Membership, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user = request.user

    return filter(
        bool,
        [
            "UPDATE"
            if user.has_perm("user_management.update_membership", membership)
            else None,
            "DELETE"
            if user.has_perm("user_management.delete_membership", membership)
            else None,
        ],
    )


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
def resolve_organizations(*_):
    return [o for o in Organization.objects.all()]


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

    user_candidate = authenticate(
        request, email=mutation_input["email"], password=mutation_input["password"]
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
    return {"success": True}


@identity_mutations.field("logout")
def resolve_logout(_, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if request.user.is_authenticated:
        logout(request)

    return {"success": True}


@identity_mutations.field("resetPassword")
def resolve_reset_password(_, info, input, **kwargs):
    request: HttpRequest = info.context["request"]
    form = PasswordResetForm({"email": input["email"]})
    if form.is_valid():
        form.save(request=request, domain_override=settings.NEW_FRONTEND_DOMAIN)
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


@organization_object.field("type")
def resolve_type(obj: Organization, *_):
    return obj.get_organization_type_display()


@identity_mutations.field("createMembership")
@transaction.atomic
def resolve_create_membership(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    principal = request.user
    create_input = kwargs["input"]

    try:
        user = User.objects.get(email=create_input["userEmail"])
        team = Team.objects.get(id=create_input["teamId"])

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


@identity_mutations.field("verifyToken")
def resolve_verify_token(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    device = django_otp.match_token(request.user, mutation_input["token"])
    if device is None:
        return {"success": False, "errors": ["INVALID_OTP_OR_DEVICE"]}

    django_otp.login(request, device)
    return {"success": True}


@identity_mutations.field("generateChallenge")
def resolve_generate_challenge(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    device = default_device(request.user)

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

    device = EmailDevice(
        user=request.user, email=mutation_input.get("email", None), name="default"
    )
    device.save()

    return {"success": True}


identity_bindables = [
    identity_query,
    user_object,
    team_object,
    me_object,
    feature_flag_object,
    membership_object,
    me_permissions_object,
    team_permissions_object,
    membership_permissions_object,
    organization_object,
    identity_mutations,
]

identity_directives = {"loginRequired": LoginRequiredDirective}
