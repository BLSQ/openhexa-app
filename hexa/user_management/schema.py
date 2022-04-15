import pathlib

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import HttpRequest
from django.utils.http import urlsafe_base64_decode
from django_countries import countries
from django_countries.fields import Country

from hexa.core.graphql import result_page
from hexa.core.templatetags.colors import hash_color
from hexa.user_management.models import Membership, Organization, Team, User

identity_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

identity_query = QueryType()
identity_mutations = MutationType()


@identity_query.field("me")
def resolve_me(_, info):
    request = info.context["request"]

    return request.user if request.user.is_authenticated else None


@identity_query.field("countries")
def resolve_countries(*_):
    return [Country(c) for c, _ in countries]


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


membership_object = ObjectType("Membership")


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
def resolve_login(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    user_candidate = authenticate(
        request, email=kwargs["input"]["email"], password=kwargs["input"]["password"]
    )

    if user_candidate is not None:
        login(request, user_candidate)

        return {"success": True, "me": user_candidate}
    else:
        return {"success": False}


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
        form.save(request=request)
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


country_object = ObjectType("Country")


@country_object.field("alpha3")
def resolve_alpha3(obj: Country, *_):
    return obj.alpha3


@country_object.field("flag")
def resolve_flag(obj: Country, info):
    request: HttpRequest = info.context["request"]

    return request.build_absolute_uri(obj.flag)


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
        membership = Membership.objects.create_if_has_perm(
            principal,
            user=User.objects.get(id=create_input["userId"]),
            team=Team.objects.get(id=create_input["teamId"]),
            role=create_input["role"],
        )
        return {"success": True, "membership": membership, "errors": []}
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
        membership.update_if_has_perm(principal, role=update_input["role"])

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
        membership.delete_if_has_perm(principal)

        return {"success": True, "membership": membership, "errors": []}
    except Membership.DoesNotExist:
        return {"success": False, "membership": None, "errors": ["NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "membership": None, "errors": ["PERMISSION_DENIED"]}


identity_bindables = [
    identity_query,
    user_object,
    country_object,
    team_object,
    membership_object,
    organization_object,
    identity_mutations,
]
