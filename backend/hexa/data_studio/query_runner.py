import time

import psycopg2
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from hexa.databases.utils import (
    MultipleStatementsError,
    elapsed_ms,
    execute_database_query,
)
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

from .models import QueryLog


def _log_executed_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    status: str,
    **fields,
):
    user = request.user
    if not isinstance(user, User):
        # Service principals (PipelineRunUser, ...) expose the triggering human
        user = getattr(user, "real_user", None)
    QueryLog.objects.create(
        workspace=workspace,
        user=user,
        query=query,
        origin=origin,
        status=status,
        target="workspace_database",
        **fields,
    )


def run_and_log_database_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    max_rows: int | None = None,
):
    """Single point of entry for executing SQL on behalf of an API request.

    Checks the permission, delegates to ``hexa.databases.utils.execute_database_query``
    and records a ``QueryLog`` entry for every outcome, re-raising errors so that
    callers only have to translate them into API responses.

    The permission is ``databases.run_query``: whether a user may run SQL against a
    workspace database is a property of the database, not of the Data Studio.
    """
    if not request.user.has_perm("databases.run_query", workspace):
        _log_executed_query(request, workspace, query, origin, QueryLog.Status.DENIED)
        raise PermissionDenied
    max_rows_kwarg = {} if max_rows is None else {"max_rows": max_rows}
    started_at = time.perf_counter()
    try:
        result = execute_database_query(workspace, query, **max_rows_kwarg)
    except MultipleStatementsError as e:
        _log_executed_query(
            request,
            workspace,
            query,
            origin,
            QueryLog.Status.REJECTED,
            error_message=str(e),
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
    )
    return result
