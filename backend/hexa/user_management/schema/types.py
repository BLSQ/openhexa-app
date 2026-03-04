import django_otp
from ariadne import ObjectType, SchemaDirectiveVisitor
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.functions import Collate
from django.http import HttpRequest
from graphql import default_field_resolver

from hexa.core.graphql import result_page
from hexa.core.templatetags.colors import hash_color
from hexa.datasets.models import Dataset, DatasetLink
from hexa.tags.models import Tag
from hexa.user_management.models import (
    AiSettings,
    Feature,
    Membership,
    Organization,
    OrganizationInvitation,
    OrganizationInvitationStatus,
    OrganizationMembership,
    OrganizationSubscription,
    User, Team,
)
from hexa.utils.base64_image_encode_decode import encode_base64_image
from hexa.workspaces.models import (
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
)

from ..utils import has_configured_two_factor


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


ai_labels_object = ObjectType("AiLabels")


@ai_labels_object.field("providers")
def resolve_ai_labels_providers(_, info):
    return AiSettings.provider_choices()


@ai_labels_object.field("models")
def resolve_ai_labels_models(_, info):
    return AiSettings.model_choices()


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


user_object = ObjectType("User")


@user_object.field("avatar")
def resolve_avatar(obj: User, *_):
    return {"initials": obj.initials, "color": hash_color(obj.email)}


organization_object = ObjectType("Organization")


@organization_object.field("type")
def resolve_type(obj: Organization, *_):
    return obj.get_organization_type_display()


@organization_object.field("logo")
def resolve_logo(obj: Organization, *_):
    """Convert binary logo to base64 for GraphQL"""
    return encode_base64_image(bytes(obj.logo)) if obj.logo else None


@organization_object.field("members")
def resolve_members(organization: Organization, info, **kwargs):
    request: HttpRequest = info.context["request"]

    if not request.user.has_perm("user_management.manage_members", organization):
        return result_page(
            queryset=organization.organizationmembership_set.none(),
            page=kwargs.get("page", 1),
            per_page=kwargs.get("per_page", 10),
        )

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


@organization_object.field("externalCollaborators")
def resolve_external_collaborators(organization: Organization, info, **kwargs):
    request: HttpRequest = info.context["request"]

    # Return empty result if user doesn't have manageMembers permission
    if not request.user.has_perm("user_management.manage_members", organization):
        return result_page(
            queryset=WorkspaceMembership.objects.none(),
            page=kwargs.get("page", 1),
            per_page=kwargs.get("per_page", 10),
        )

    org_member_user_ids = organization.organizationmembership_set.values_list(
        "user_id", flat=True
    )

    qs = WorkspaceMembership.objects.filter(
        workspace__organization=organization,
        workspace__archived=False,
    ).exclude(user_id__in=org_member_user_ids)

    term = kwargs.get("term")
    if term:
        qs = qs.annotate(case_insensitive_email=Collate("user__email", "und-x-icu"))
        qs = qs.filter(
            Q(user__first_name__icontains=term)
            | Q(user__last_name__icontains=term)
            | Q(case_insensitive_email__icontains=term)
        )

    # Get IDs of earliest membership per user
    earliest_membership_ids = (
        qs.order_by("user_id", "created_at").distinct("user_id").values("id")
    )

    # Query again with proper email ordering for pagination
    memberships_qs = (
        WorkspaceMembership.objects.filter(id__in=earliest_membership_ids)
        .select_related("user")
        .annotate(case_insensitive_email=Collate("user__email", "und-x-icu"))
        .order_by("case_insensitive_email")
    )

    page_result = result_page(
        queryset=memberships_qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 10),
    )

    # Add organization reference for workspace_memberships resolver
    for m in page_result["items"]:
        m.organization = organization

    return page_result


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
    return organization.current_subscription


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


organization_permissions_object = ObjectType("OrganizationPermissions")


@organization_permissions_object.field("createWorkspace")
def resolve_organization_permissions_create_workspace(organization: Organization, info):
    request: HttpRequest = info.context["request"]
    user = request.user
    has_permission = (
        user.has_perm("user_management.create_workspace", organization)
        if user.is_authenticated
        else False
    )
    workspaces_limit_reached = organization.is_workspaces_limit_reached()
    is_allowed = has_permission and not workspaces_limit_reached
    return {
        "is_allowed": is_allowed,
        "reasons": [
            msg
            for msg in [
                not has_permission and "PERMISSION_DENIED",
                workspaces_limit_reached and "WORKSPACES_LIMIT_REACHED",
            ]
            if msg
        ],
    }


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


external_collaborator_object = ObjectType("ExternalCollaborator")


@external_collaborator_object.field("id")
def resolve_external_collaborator_id(collaborator, info, **kwargs):
    """Return user ID as the external collaborator ID"""
    return collaborator.user_id


@external_collaborator_object.field("user")
def resolve_external_collaborator_user(collaborator, info, **kwargs):
    return collaborator.user


@external_collaborator_object.field("workspaceMemberships")
def resolve_external_collaborator_workspace_memberships(collaborator, info, **kwargs):
    """Return workspace memberships for this user within the organization"""
    return WorkspaceMembership.objects.filter(
        user_id=collaborator.user_id,
        workspace__organization=collaborator.organization,
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


bindables = [
    me_permissions_object,
    me_object,
    ai_labels_object,
    user_object,
    team_object,
    team_permissions_object,
    membership_object,
    membership_permissions_object,
    organization_object,
    organization_permissions_object,
    subscription_object,
    organization_membership_object,
    external_collaborator_object,
    organization_invitation_object,
]
