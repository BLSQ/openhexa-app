from ariadne import QueryType
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.db.models.functions import Collate
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.user_management.models import Organization, Team, User
from hexa.workspaces.models import Workspace

from .types import ai_labels_object, me_object

identity_query = QueryType()
organization_queries = QueryType()


@identity_query.field("me")
def resolve_me(_, info):
    return me_object


@identity_query.field("aiLabels")
def resolve_ai_labels(_, info):
    return ai_labels_object


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


@identity_query.field("organizations")
def resolve_organizations(_, info, direct_membership_only: bool = False, **kwargs):
    request: HttpRequest = info.context["request"]
    return Organization.objects.filter_for_user(
        request.user, direct_membership_only=direct_membership_only
    ).all()


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


@organization_queries.field("organization")
def resolve_organization(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Organization.objects.filter_for_user(request.user).get(id=kwargs["id"])
    except Organization.DoesNotExist:
        return None


bindables = [
    identity_query,
    organization_queries,
]
