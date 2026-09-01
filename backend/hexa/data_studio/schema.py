import logging
import pathlib

from ariadne import (
    EnumType,
    MutationType,
    ObjectType,
    QueryType,
    load_schema_from_path,
)
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest
from psycopg2 import Error as Psycopg2Error
from psycopg2.errors import QueryCanceled

from hexa.core.graphql import result_page
from hexa.databases.query_text import MultipleStatementsError
from hexa.databases.schema import database_object
from hexa.git.exceptions import GitError
from hexa.git.forgejo import ForgejoAPIError
from hexa.workspaces.models import Workspace
from hexa.workspaces.schema.types import workspace_object, workspace_permissions

from .models import QueryLog, SavedQuery
from .query_runner import run_and_log_database_query, run_saved_query

logger = logging.getLogger(__name__)

data_studio_type_defs = load_schema_from_path(
    f"{pathlib.Path(__file__).parent.resolve()}/graphql/schema.graphql"
)

saved_query_object = ObjectType("SavedQuery")
saved_query_permissions = ObjectType("SavedQueryPermissions")
data_studio_queries = QueryType()
data_studio_mutations = MutationType()

saved_query_order_by_enum = EnumType(
    "SavedQueryOrderBy",
    {
        "NAME_ASC": "name",
        "NAME_DESC": "-name",
        "UPDATED_AT_ASC": "updated_at",
        "UPDATED_AT_DESC": "-updated_at",
    },
)

# Only the origins a client may declare are bound to the GraphQL enum: the CSV export's
# origin is set server-side (see views.download_query_csv), so it cannot be claimed on an
# interactive query and means what it says in the audit log. Derived from the model enum
# rather than hand-listed, so the two stay in sync — a new client-settable value missing
# from schema.graphql fails loudly when the schema is built.
execute_sql_origin_enum = EnumType(
    "ExecuteSQLOrigin",
    {
        origin.name: origin
        for origin in QueryLog.Origin
        if origin not in (QueryLog.Origin.DATA_STUDIO_EXPORT, QueryLog.Origin.WEBAPP)
    },
)


# executeSQL extends the databases app's Database type: the field belongs to the
# database, but the execution path lives here because it writes to QueryLog. The
# resolver is attached to the imported bindable, which the databases app already
# registers — hence no database_object in data_studio_bindables below.
@database_object.field("executeSQL")
def resolve_database_execute_sql(
    workspace: Workspace,
    info,
    query: str,
    max_rows: int | None = None,
    origin: str | None = None,
    **kwargs,
):
    request: HttpRequest = info.context["request"]
    # Clients may send an explicit null, which bypasses the Python default
    origin = origin or QueryLog.Origin.OTHER
    try:
        result = run_and_log_database_query(
            request, workspace, query, origin, max_rows=max_rows
        )
        return {"success": True, "errors": [], **result}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except MultipleStatementsError as e:
        return {
            "success": False,
            "errors": ["MULTIPLE_STATEMENTS"],
            "error_message": str(e),
        }
    except QueryCanceled as e:
        return {
            "success": False,
            "errors": ["QUERY_TIMEOUT"],
            "error_message": str(e).strip(),
        }
    except Psycopg2Error as e:
        return {
            "success": False,
            "errors": ["QUERY_ERROR"],
            "error_message": str(e).strip(),
        }


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


@saved_query_permissions.field("updateVisibility")
def resolve_saved_query_permissions_update_visibility(
    saved_query: SavedQuery, info, **kwargs
):
    request: HttpRequest = info.context["request"]
    return (
        request.user.has_perm("data_studio.update_saved_query_visibility", saved_query)
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

    # `id` breaks ties so paging stays deterministic: neither `name` nor
    # `updated_at` is unique, and rows sharing a sort key could otherwise be
    # dealt to two pages (or none) across successive requests.
    qs = qs.order_by(kwargs["order_by"], "id")

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


def _visible_saved_queries(request: HttpRequest):
    return SavedQuery.objects.filter_for_user(request.user).select_related(
        "created_by", "workspace", "workspace__organization"
    )


@data_studio_queries.field("savedQuery")
def resolve_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    queryset = _visible_saved_queries(request)
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


@data_studio_queries.field("savedQueryBySlug")
def resolve_saved_query_by_slug(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    try:
        return _visible_saved_queries(request).get(slug=kwargs["slug"])
    except SavedQuery.DoesNotExist:
        return None


@data_studio_queries.field("executeSavedQuery")
def resolve_execute_saved_query(_, info, **kwargs):
    request: HttpRequest = info.context["request"]
    query_input = kwargs["input"]

    try:
        # No workspace to match on: the slug is unique across workspaces, and
        # `filter_for_user` already confines a web app to the single workspace
        # its token was issued for.
        saved_query = _visible_saved_queries(request).get(slug=query_input["slug"])
        result = run_saved_query(
            request, saved_query, max_rows=query_input.get("max_rows")
        )
        return {"success": True, "errors": [], **result}
    except SavedQuery.DoesNotExist:
        # A query that does not exist and one the caller cannot see are reported
        # the same way, so that this endpoint cannot be used to discover what
        # exists elsewhere.
        return {"success": False, "errors": ["SAVED_QUERY_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    except MultipleStatementsError as e:
        return {
            "success": False,
            "errors": ["MULTIPLE_STATEMENTS"],
            "error_message": str(e),
        }
    except QueryCanceled as e:
        return {
            "success": False,
            "errors": ["QUERY_TIMEOUT"],
            "error_message": str(e).strip(),
        }
    except Psycopg2Error as e:
        return {
            "success": False,
            "errors": ["QUERY_ERROR"],
            "error_message": str(e).strip(),
        }


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
            visibility=mutation_input.get("visibility"),
        )
        return {"success": True, "errors": [], "saved_query": saved_query}
    except Workspace.DoesNotExist:
        return {"success": False, "errors": ["WORKSPACE_NOT_FOUND"]}
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    # Recording the first version is part of creating the query, so a git failure
    # leaves nothing behind (the transaction rolls back) and is reported as such,
    # rather than as a saved query with no history.
    except (ForgejoAPIError, GitError):
        logger.exception("Could not record the first version of a saved query")
        return {"success": False, "errors": ["VERSIONING_UNAVAILABLE"]}


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
    except PermissionDenied:
        return {"success": False, "errors": ["PERMISSION_DENIED"]}
    # The alternative to failing the edit would be keeping the new content with a hole
    # in its history, which nothing afterwards could tell apart from a query nobody
    # edited. Rolled back instead, so a retry records both the change and its version.
    except (ForgejoAPIError, GitError):
        logger.exception("Could not record a new version of a saved query")
        return {"success": False, "errors": ["VERSIONING_UNAVAILABLE"]}


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
    except (ForgejoAPIError, GitError):
        logger.exception("Could not archive the history of a saved query")
        return {"success": False, "errors": ["VERSIONING_UNAVAILABLE"]}


data_studio_bindables = [
    saved_query_object,
    saved_query_permissions,
    saved_query_order_by_enum,
    data_studio_queries,
    data_studio_mutations,
    execute_sql_origin_enum,
]
