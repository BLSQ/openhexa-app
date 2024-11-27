from ariadne import QueryType, convert_kwargs_to_snake_case

from hexa.core.graphql import result_page

from ..models import (
    Connection,
    User,
    Workspace,
    WorkspaceInvitation,
    WorkspaceInvitationStatus,
    WorkspaceMembership,
    WorkspaceMembershipRole,
)

workspace_queries = QueryType()


@workspace_queries.field("workspaces")
def resolve_workspaces(_, info, query=None, page=1, perPage=15):
    request = info.context["request"]
    queryset = Workspace.objects.filter_for_user(request.user).order_by("-updated_at")
    if query is not None:
        queryset = queryset.filter(name__icontains=query)
    return result_page(queryset=queryset, page=page, per_page=perPage)


@workspace_queries.field("workspace")
def resolve_workspace(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Workspace.objects.filter_for_user(request.user).get(slug=kwargs["slug"])
    except Workspace.DoesNotExist:
        return None


@workspace_queries.field("connection")
def resolve_workspace_connection(_, info, id):
    request = info.context["request"]
    try:
        return Connection.objects.filter_for_user(request.user).get(id=id)
    except Connection.DoesNotExist:
        return None


@workspace_queries.field("connectionBySlug")
def resolve_workspace_connection_by_slug(_, info, **kwargs):
    request = info.context["request"]
    try:
        return Connection.objects.filter_for_user(request.user).get(
            workspace__slug=kwargs["workspaceSlug"], slug=kwargs["connectionSlug"]
        )
    except Connection.DoesNotExist:
        return None


@workspace_queries.field("pendingWorkspaceInvitations")
@convert_kwargs_to_snake_case
def resolve_pending_workspace_invitations(_, info, page=1, per_page=10):
    request = info.context["request"]
    if not request.user.is_authenticated:
        return []
    qs = WorkspaceInvitation.objects.filter(
        email=request.user.email, status=WorkspaceInvitationStatus.PENDING
    ).order_by("-created_at")
    return result_page(qs, page=page, per_page=per_page)


@workspace_queries.field("workspaceCandidates")
def resolve_users(_, info, **kwargs):
    request = info.context["request"]
    query = kwargs["query"].strip()
    workspaceSlug = kwargs["workspace"].strip()

    try:
        workspace = Workspace.objects.get(slug=workspaceSlug)
        members = WorkspaceMembership.objects.all().filter(workspace=workspace)

        is_admin = (
            members.filter(user=request.user).first().role
            == WorkspaceMembershipRole.ADMIN
        )

        if not is_admin:
            return {
                "items": [],
            }

        queryset = User.objects.all()

        if query is not None:
            queryset = (
                queryset.filter(email__icontains=query)
                .exclude(email__in=members.values_list("user__email", flat=True))
                .order_by("email")[:10:1]
            )

        return {
            "items": queryset,
        }
    except Exception:
        return {
            "items": [],
        }


bindables = [
    workspace_queries,
]
