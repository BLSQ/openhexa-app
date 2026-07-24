import pathlib
import time

from ariadne import MutationType, ObjectType, QueryType, load_schema_from_path
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_object, workspace_permissions

from .execution import ParameterError, execute_saved_query
from .models import SavedQuery

data_studio_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

saved_query_object = ObjectType("SavedQuery")
saved_query_permissions = ObjectType("SavedQueryPermissions")
data_studio_queries = QueryType()
data_studio_mutations = MutationType()


@saved_query_object.field("permissions")
def resolve_saved_query_permissions(saved_query: SavedQuery, info, **kwargs):
    return saved_query


@saved_query_permissions.field("update")
def resolve_saved_query_permissions_update(saved_query: SavedQuery, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("data_studio.update_saved_query", saved_query)
        if request.user.is_authenticated
        else False
    )


@saved_query_permissions.field("delete")
def resolve_saved_query_permissions_delete(saved_query: SavedQuery, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("data_studio.delete_saved_query", saved_query)
        if request.user.is_authenticated
        else False
    )


@saved_query_permissions.field("run")
def resolve_saved_query_permissions_run(saved_query: SavedQuery, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("databases.run_query", saved_query.workspace)
        if request.user.is_authenticated
        else False
    )


@saved_query_permissions.field("publish")
def resolve_saved_query_permissions_publish(saved_query: SavedQuery, info, **kwargs):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("data_studio.publish_saved_query", saved_query.workspace)
        if request.user.is_authenticated
        else False
    )


@workspace_object.field("savedQueries")
def resolve_workspace_saved_queries(workspace: Workspace, info, query=None, **kwargs):
    request: HttpRequest = info.context["request"]
    qs = (
        SavedQuery.objects.filter_for_user(request.user)
        .filter(workspace=workspace)
        .select_related("created_by", "workspace", "workspace__organization")
    )

    if query is not None:
        # Deliberately not searching `content` (the SQL body): it is costly to scan on
        # large bodies and noisy (would match SQL keywords/identifiers). Revisit once the
        # frontend defines whether and how body matches should surface to users.
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return result_page(
        queryset=qs,
        page=kwargs.get("page", 1),
        per_page=kwargs.get("per_page", 15),
    )


@workspace_permissions.field("createSavedQuery")
def resolve_workspace_permissions_create_saved_query(
    workspace: Workspace, info, **kwargs
):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("data_studio.create_saved_query", workspace)
        if request.user.is_authenticated
        else False
    )


@data_studio_queries.field("savedQuery")
def resolve_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    queryset = SavedQuery.objects.filter_for_user(request.user).select_related(
        "created_by", "workspace", "workspace__organization"
    )
    # workspaceSlug is optional to keep the field's existing id-only contract;
    # when supplied it scopes the lookup to that workspace, matching where
    # saved queries live (mirrors pipelineByCode).
    workspace_slug = kwargs.get("workspace_slug")
    if workspace_slug is not None:
        queryset = queryset.filter(workspace__slug=workspace_slug)
    try:
        return queryset.get(id=kwargs["id"])
    except SavedQuery.DoesNotExist:
        return None


@data_studio_mutations.field("createSavedQuery")
def resolve_create_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        workspace = Workspace.objects.filter_for_user(request.user).get(
            slug=mutation_input["workspace_slug"]
        )
        saved_query = SavedQuery.objects.create_if_has_perm(
            principal=request.user,
            workspace=workspace,
            name=mutation_input["name"],
            content=mutation_input["content"],
            description=mutation_input.get("description") or "",
            parameters=mutation_input.get("parameters"),
            is_public=mutation_input.get("is_public") or False,
        )
        return {"success": True, "errors": [], "saved_query": saved_query}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except ParameterError:
        return {"success": False, "errors": ["INVALID_PARAMETERS"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@data_studio_mutations.field("updateSavedQuery")
def resolve_update_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        saved_query = SavedQuery.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )
        saved_query.update_if_has_perm(principal=request.user, **mutation_input)
        return {"success": True, "errors": [], "saved_query": saved_query}
    except SavedQuery.DoesNotExist:
        return {"success": False, "errors": ["SAVED_QUERY_NOT_FOUND"]}
    except ParameterError:
        return {"success": False, "errors": ["INVALID_PARAMETERS"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@data_studio_mutations.field("deleteSavedQuery")
def resolve_delete_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        saved_query = SavedQuery.objects.filter_for_user(request.user).get(
            id=mutation_input["id"]
        )
        saved_query.delete_if_has_perm(principal=request.user)
        return {"success": True, "errors": []}
    except SavedQuery.DoesNotExist:
        return {"success": False, "errors": ["SAVED_QUERY_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}


@data_studio_mutations.field("executeSavedQuery")
def resolve_execute_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]

    try:
        saved_query = SavedQuery.objects.filter_for_user(request.user).get(
            workspace__slug=mutation_input["workspace_slug"],
            slug=mutation_input["slug"],
        )
    except SavedQuery.DoesNotExist:
        return {"success": False, "errors": ["SAVED_QUERY_NOT_FOUND"]}

    if not request.user.has_perm("databases.run_query", saved_query.workspace):
        return {"success": False, "errors": ["PERMISSION_DENIED"]}

    return execute_saved_query(
        saved_query,
        mutation_input.get("parameters") or {},
        mutation_input.get("max_rows"),
    )


def _public_rate_limit_exceeded(request: HttpRequest, *key_parts: str) -> bool:
    """Fixed-window rate limit for anonymous executions, keyed by (IP, *key_parts).

    Backed by Django's cache; with the default per-process LocMemCache the limit
    is per worker rather than global (see settings for details).
    """
    limit = settings.PUBLIC_SAVED_QUERY_RATE_LIMIT
    if limit <= 0:
        return False
    window = settings.PUBLIC_SAVED_QUERY_RATE_WINDOW_SECONDS
    ip = request.META.get("REMOTE_ADDR", "unknown")
    bucket = int(time.time() // window)
    cache_key = f"public_saved_query_rl:{ip}:{':'.join(key_parts)}:{bucket}"
    cache.add(cache_key, 0, timeout=window)
    try:
        count = cache.incr(cache_key)
    except ValueError:
        # The key expired between add and incr; treat as the first hit.
        cache.add(cache_key, 1, timeout=window)
        count = 1
    return count > limit


@data_studio_mutations.field("executePublicSavedQuery")
def resolve_execute_public_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    mutation_input = kwargs["input"]
    workspace_slug = mutation_input["workspace_slug"]
    slug = mutation_input["slug"]

    if _public_rate_limit_exceeded(request, workspace_slug, slug):
        return {"success": False, "errors": ["RATE_LIMITED"]}

    # Deliberately bypasses filter_for_user: is_public is the authorization.
    # A missing, non-public or archived-workspace query is indistinguishable, so
    # the endpoint never reveals the existence of a private saved query.
    try:
        saved_query = SavedQuery.objects.get(
            workspace__slug=workspace_slug,
            slug=slug,
            is_public=True,
            workspace__archived=False,
        )
    except SavedQuery.DoesNotExist:
        return {"success": False, "errors": ["SAVED_QUERY_NOT_FOUND"]}

    public_cap = settings.PUBLIC_SAVED_QUERY_MAX_ROWS
    requested = mutation_input.get("max_rows")
    max_rows = public_cap if requested is None else min(requested, public_cap)

    return execute_saved_query(
        saved_query, mutation_input.get("parameters") or {}, max_rows
    )


data_studio_bindables = [
    saved_query_object,
    saved_query_permissions,
    data_studio_queries,
    data_studio_mutations,
]
