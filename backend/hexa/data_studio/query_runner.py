import logging
import time
from typing import Iterator

import psycopg2
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.databases.query_text import (
    MultipleStatementsError,
    OrderBy,
    PreparedQuery,
    paginate_cursor,
    paginate_offset,
)
from hexa.databases.utils import (
    count_database_rows,
    elapsed_ms,
    execute_database_query,
    stream_database_query,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

from .models import QueryLog
from .pagination import (
    CursorPage,
    OffsetPage,
    PageRequest,
    PaginationError,
    build_page_info,
    build_page_request,
    resolve_per_page,
)

logger = logging.getLogger(__name__)


def _log_executed_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    status: str,
    **fields,
) -> QueryLog:
    user = request.user
    if not isinstance(user, User):
        # Service principals (PipelineRunUser, ...) expose the triggering human
        user = getattr(user, "real_user", None)
    return QueryLog.objects.create(
        workspace=workspace,
        user=user,
        query=query,
        origin=origin,
        status=status,
        target="workspace_database",
        **fields,
    )


def ensure_can_run_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    saved_query=None,
) -> None:
    """Check the permission both SQL paths share, recording a DENIED entry when it fails.

    Split out of the execution helpers below so a caller can enforce it *before*
    reserving anything: the CSV export holds a concurrency slot for its whole download
    and must not spend one on a request it is going to refuse.

    The permission is ``databases.run_query``: whether a user may run SQL against a
    workspace database is a property of the database, not of the Data Studio.
    """
    # A webapp may only run SQL the workspace already stored, never SQL of its own
    # (``saved_query is None`` is exactly the caller-supplied case): the GraphQL proxy
    # validates top-level fields only, so the `workspace` field that `USER_READ` grants
    # would otherwise reach executeSQL through `workspace { database { executeSQL } }`
    # and turn the narrowest scope into an unrestricted read of the whole database.
    if saved_query is None and getattr(request, "webapp", None) is not None:
        _log_executed_query(
            request,
            workspace,
            query,
            origin,
            QueryLog.Status.DENIED,
        )
        raise PermissionDenied
    if not request.user.has_perm("databases.run_query", workspace):
        _log_executed_query(
            request,
            workspace,
            query,
            origin,
            QueryLog.Status.DENIED,
            saved_query=saved_query,
        )
        raise PermissionDenied


def log_rejected_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    error_message: str,
    saved_query=None,
) -> None:
    """Record a query the server refused to run before it reached the database."""
    _log_executed_query(
        request,
        workspace,
        query,
        origin,
        QueryLog.Status.REJECTED,
        error_message=error_message,
        saved_query=saved_query,
    )


def _execute_and_log(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    statement: PreparedQuery,
    *,
    saved_query=None,
    max_rows: int | None = None,
    count: PreparedQuery | None = None,
) -> tuple[dict, int | None]:
    """Run ``statement`` and record the outcome, re-raising errors for the caller.

    ``count`` is run first when given: a failing count then reaches the log as
    the one ERROR entry of the request, rather than following a SUCCESS entry.
    ``query`` is the text logged, raw, for every outcome.
    """
    max_rows_kwarg = {} if max_rows is None else {"max_rows": max_rows}
    started_at = time.perf_counter()
    try:
        total_items = (
            count_database_rows(workspace, count) if count is not None else None
        )
        result = execute_database_query(workspace, statement, **max_rows_kwarg)
    except psycopg2.Error as e:
        # QueryCanceled (statement timeout) is a psycopg2.Error subclass and
        # needs no dedicated handling here: both outcomes log the same fields.
        _log_executed_query(
            request,
            workspace,
            query,
            origin,
            QueryLog.Status.ERROR,
            result_code=e.pgcode,
            error_message=str(e).strip(),
            duration_ms=elapsed_ms(started_at),
            saved_query=saved_query,
        )
        raise
    _log_executed_query(
        request,
        workspace,
        query,
        origin,
        QueryLog.Status.SUCCESS,
        result_code=QueryLog.SQLSTATE_SUCCESS,
        duration_ms=result["duration_ms"],
        row_count=result["row_count"],
        truncated=result["truncated"],
        saved_query=saved_query,
    )
    return result, total_items


def run_and_log_database_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    max_rows: int | None = None,
    saved_query=None,
):
    """Execute caller-supplied SQL on behalf of an API request.

    Checks the permission, delegates to ``hexa.databases.utils.execute_database_query``
    and records a ``QueryLog`` entry for every outcome, re-raising errors so that
    callers only have to translate them into API responses. Never wrapped: the
    ``page_info`` it attaches only reports what the row cap saw.
    """
    ensure_can_run_query(request, workspace, query, origin, saved_query=saved_query)
    try:
        prepared = PreparedQuery.from_text(query)
    except MultipleStatementsError as e:
        log_rejected_query(
            request, workspace, query, origin, str(e), saved_query=saved_query
        )
        raise
    result, _ = _execute_and_log(
        request,
        workspace,
        query,
        origin,
        prepared,
        saved_query=saved_query,
        max_rows=max_rows,
    )
    result["page_info"] = build_page_info(
        None,
        first_row=result["first_row"],
        last_row=result["last_row"],
        truncated=result["truncated"],
        sql_text=prepared.body,
    )
    return result


def _wrap(prepared: PreparedQuery, page_request: PageRequest | None) -> PreparedQuery:
    if isinstance(page_request, OffsetPage):
        return paginate_offset(
            prepared,
            order_by=page_request.order_by,
            per_page=page_request.per_page,
            offset=page_request.offset,
        )
    if isinstance(page_request, CursorPage):
        return paginate_cursor(
            prepared,
            order_by=page_request.order_by,
            per_page=page_request.per_page,
            keyset=page_request.keyset,
            before=page_request.backward,
        )
    return prepared


def _restore_order(result: dict, page_request: PageRequest | None) -> None:
    """Put a backward page, read against the reversed ordering, back in order."""
    if isinstance(page_request, CursorPage) and page_request.backward:
        result["rows"].reverse()
        result["first_row"], result["last_row"] = (
            result["last_row"],
            result["first_row"],
        )


def run_saved_query(
    request: HttpRequest,
    saved_query,
    *,
    order_by: list[OrderBy] | None = None,
    per_page: int | None = None,
    max_rows: int | None = None,
    page: int | None = None,
    after: str | None = None,
    before: str | None = None,
    include_total_items: bool | None = None,
):
    """Execute a stored query on behalf of an API request, sorted and paged as asked.

    Unlike the interactive path this is reachable from a web app: the SQL was written
    and vetted by a workspace member when the query was saved, not supplied by the
    caller, which is the whole point of the endpoint. The permission checked is still
    the workspace-database one, so a web app cannot reach a database its viewer could
    not query directly.

    A call with no ``order_by``, ``page``, ``after`` or ``before`` runs the stored
    text unwrapped, exactly as before those arguments existed. Otherwise the text is
    wrapped in a sorted, limited subquery and ``page_info`` describes the page. Raises
    ``PaginationError`` (logged as REJECTED) for arguments that cannot be honoured.
    """
    # Derived from the request rather than accepted as an argument: a client that
    # could name its own origin could disown the queries it ran.
    origin = (
        QueryLog.Origin.WEBAPP
        if getattr(request, "webapp", None) is not None
        else QueryLog.Origin.OTHER
    )
    workspace = saved_query.workspace
    query = saved_query.content
    ensure_can_run_query(request, workspace, query, origin, saved_query=saved_query)
    try:
        per_page = resolve_per_page(per_page, max_rows)
        prepared = PreparedQuery.from_text(query)
        page_request = build_page_request(
            prepared,
            order_by=order_by,
            per_page=per_page,
            page=page,
            after=after,
            before=before,
            include_total_items=include_total_items,
        )
    except (MultipleStatementsError, PaginationError) as e:
        log_rejected_query(
            request, workspace, query, origin, str(e), saved_query=saved_query
        )
        raise
    wants_total = isinstance(page_request, OffsetPage) and page_request.include_total
    result, total_items = _execute_and_log(
        request,
        workspace,
        query,
        origin,
        _wrap(prepared, page_request),
        saved_query=saved_query,
        max_rows=per_page,
        count=prepared if wants_total else None,
    )
    _restore_order(result, page_request)
    result["page_info"] = build_page_info(
        page_request,
        first_row=result["first_row"],
        last_row=result["last_row"],
        truncated=result["truncated"],
        sql_text=prepared.body,
        total_items=total_items,
    )
    # The deprecated field promises the same value as hasNextPage; on a backward
    # page the raw signal points the other way.
    result["truncated"] = result["page_info"]["has_next_page"]
    return result


class QueryExportAudit:
    """The audit entry of an export whose stream is still running.

    A streamed export only knows its outcome long after the request was accepted, but
    writing the entry that late would lose the trail exactly when it matters most — a
    worker killed mid-download. So the entry is written as soon as the query runs and
    updated once the stream ends, which is what ``QueryLog.Status.STREAMING`` marks:
    an entry left at that status means the end was never observed (a cancelled download,
    a dropped connection, a dead worker). See the app README.

    ``duration_ms`` here covers the whole export, not just database time: the stream is
    paced by the client consuming it, so it is not comparable to the interactive path's.
    """

    def __init__(self, log: QueryLog, started_at: float) -> None:
        self._log = log
        self._started_at = started_at

    async def _finish(self, **fields) -> None:
        try:
            await QueryLog.objects.filter(pk=self._log.pk).aupdate(
                duration_ms=elapsed_ms(self._started_at), **fields
            )
        except Exception:
            # Called from the response stream, where the export is already on the wire
            # and the entry already on record: a failed update must not abort the
            # download. Unlike the initial write, which fails the request closed.
            logger.exception(
                "Could not finalise the QueryLog entry %s of a streaming export",
                self._log.pk,
            )

    async def finish_success(self, row_count: int) -> None:
        await self._finish(
            status=QueryLog.Status.SUCCESS,
            result_code=QueryLog.SQLSTATE_SUCCESS,
            row_count=row_count,
        )

    async def finish_error(self, row_count: int, error: Exception) -> None:
        """Record a failure that hit mid-stream, keeping the rows streamed until then."""
        await self._finish(
            status=QueryLog.Status.ERROR,
            # Only a database error carries a SQLSTATE
            result_code=getattr(error, "pgcode", None),
            error_message=str(error).strip(),
            row_count=row_count,
        )


def stream_and_log_database_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
) -> tuple[list[str], Iterator[list[dict]], QueryExportAudit]:
    """Single point of entry for streaming a full result set on behalf of an API request.

    Streaming counterpart of :func:`run_and_log_database_query`, delegating to
    ``hexa.databases.utils.stream_database_query`` and logging every outcome the same
    way. What differs is that returning normally only means the query *started*, so the
    entry comes back unfinished as a :class:`QueryExportAudit` for the caller to close
    when the stream ends.

    The permission is not checked here: the caller enforces it through
    :func:`ensure_can_run_query` before reserving an export slot.
    """
    started_at = time.perf_counter()
    try:
        columns, row_batches = stream_database_query(workspace, query)
    except MultipleStatementsError as e:
        log_rejected_query(request, workspace, query, origin, str(e))
        raise
    except psycopg2.Error as e:
        _log_executed_query(
            request,
            workspace,
            query,
            origin,
            QueryLog.Status.ERROR,
            result_code=e.pgcode,
            error_message=str(e).strip(),
            duration_ms=elapsed_ms(started_at),
        )
        raise
    try:
        log = _log_executed_query(
            request, workspace, query, origin, QueryLog.Status.STREAMING
        )
    except Exception:
        # Fail closed on a broken audit trail, as the interactive path does. The query
        # is already running though, so its connection has to be handed back here —
        # the caller only takes ownership of it once this returns.
        row_batches.close()
        raise
    return columns, row_batches, QueryExportAudit(log, started_at)
