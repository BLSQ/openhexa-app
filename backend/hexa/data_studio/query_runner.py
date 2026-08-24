import logging
import time
from typing import Iterator

import psycopg2
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.databases.query_text import MultipleStatementsError
from hexa.databases.utils import (
    elapsed_ms,
    execute_database_query,
    stream_database_query,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

from .models import QueryLog

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


def run_and_log_database_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    max_rows: int | None = None,
    saved_query=None,
):
    """Single point of entry for executing SQL on behalf of an API request.

    Checks the permission, delegates to ``hexa.databases.utils.execute_database_query``
    and records a ``QueryLog`` entry for every outcome, re-raising errors so that
    callers only have to translate them into API responses.
    """
    ensure_can_run_query(request, workspace, query, origin, saved_query=saved_query)
    max_rows_kwarg = {} if max_rows is None else {"max_rows": max_rows}
    started_at = time.perf_counter()
    try:
        result = execute_database_query(workspace, query, **max_rows_kwarg)
    except MultipleStatementsError as e:
        log_rejected_query(
            request, workspace, query, origin, str(e), saved_query=saved_query
        )
        raise
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
    return result


def run_saved_query(request: HttpRequest, saved_query, max_rows: int | None = None):
    """Execute a stored query on behalf of an API request.

    Unlike the interactive path this is reachable from a web app: the SQL was written
    and vetted by a workspace member when the query was saved, not supplied by the
    caller, which is the whole point of the endpoint. The permission checked is still
    the workspace-database one, so a web app cannot reach a database its viewer could
    not query directly.
    """
    # Derived from the request rather than accepted as an argument: a client that
    # could name its own origin could disown the queries it ran.
    origin = (
        QueryLog.Origin.WEBAPP
        if getattr(request, "webapp", None) is not None
        else QueryLog.Origin.OTHER
    )
    return run_and_log_database_query(
        request,
        saved_query.workspace,
        saved_query.content,
        origin,
        max_rows=max_rows,
        saved_query=saved_query,
    )


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
