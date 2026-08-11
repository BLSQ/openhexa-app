import enum
import json
import math
import time
from dataclasses import dataclass
from typing import Dict, List, NoReturn, Tuple

import psycopg2
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest
from psycopg2 import sql
from psycopg2.errors import UndefinedTable
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor

from hexa.data_studio.models import QueryLog
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace

from .api import get_db_server_credentials
from .query_text import MultipleStatementsError, PreparedQuery

IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]


class ResultJSONEncoder(DjangoJSONEncoder):
    """Make arbitrary query results JSON-safe."""

    def default(self, o):
        if isinstance(o, (bytes, bytearray, memoryview)):
            return "\\x" + bytes(o).hex()
        try:
            return super().default(o)
        except TypeError:
            return str(o)


def elapsed_ms(started_at: float) -> int:
    """Milliseconds elapsed since ``started_at``, a ``time.perf_counter()`` value."""
    return round((time.perf_counter() - started_at) * 1000)


def get_row_count_estimate(cursor, table_name: str) -> int:
    """Get a fast row count estimate using EXPLAIN."""
    cursor.execute(
        sql.SQL("EXPLAIN (FORMAT JSON) SELECT * FROM {};").format(
            sql.Identifier(table_name)
        ),
    )
    result = cursor.fetchone()
    explain_output = result[0] if isinstance(result, tuple) else result["QUERY PLAN"]
    if isinstance(explain_output, str):
        explain_output = json.loads(explain_output)
    return int(explain_output[0]["Plan"]["Plan Rows"])


def get_row_count(cursor, table_name: str, reltuples: float) -> int:
    """Return the row count for a table, using an accurate COUNT(*) for small tables
    and falling back to pg_class.reltuples estimates for large ones to avoid expensive full scans.
    """
    count = int(reltuples)
    # reltuples is -1 when not analyzed yet, which is the case for views
    if count < 0:
        count = get_row_count_estimate(cursor, table_name)
    # For the sake of performance we only run SELECT COUNT(*) for relatively small tables (< 10000 entries)
    # due to the fact PostgreSQL will need to scan either the entire table or the entirety of an index.
    if count < 10_000:
        cursor.execute(
            sql.SQL("SELECT COUNT(*) as row_count FROM {};").format(
                sql.Identifier(table_name)
            ),
        )
        return cursor.fetchone()["row_count"]
    return count


class TableNotFound(Exception):
    pass


class OrderByDirectionEnum(enum.Enum):
    ASC = "ASC"
    DESC = "DESC"


def get_workspace_database_connection(workspace: Workspace):
    credentials = get_db_server_credentials()
    host = credentials["host"]
    port = credentials["port"]

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=workspace.db_name,
        user=workspace.db_name,
        password=workspace.db_password,
    )


def get_workspace_database_ro_connection(workspace: Workspace):
    credentials = get_db_server_credentials()
    host = credentials["host"]
    port = credentials["port"]

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=workspace.db_name,
        user=workspace.db_ro_username,
        password=workspace.db_ro_password,
    )


def execute_database_query(
    workspace: Workspace,
    query: str,
    timeout_ms: int = 10_000,
    max_rows: int = 50,
):
    """Execute a SQL query against the workspace database using the read-only role.

    A per-statement timeout is set so that a single request cannot hold database
    resources for an extended period of time. At most ``max_rows`` rows are
    returned, capped to ``settings.WORKSPACE_DATABASE_QUERY_MAX_ROWS``;
    ``truncated`` indicates whether the result was capped.

    This function does no permission check and no audit logging: SQL executed
    on behalf of an API request must go through ``run_and_log_database_query``.
    """
    prepared = PreparedQuery.from_text(query)
    hard_limit = settings.WORKSPACE_DATABASE_QUERY_MAX_ROWS
    # A plan is bounded by query complexity, so let it through the hard limit
    # in full rather than clipping it to the (small) requested row cap.
    max_rows = hard_limit if prepared.is_explain else min(max_rows, hard_limit)
    conn = None
    try:
        conn = get_workspace_database_ro_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("SET LOCAL statement_timeout = {timeout};").format(
                    timeout=sql.Literal(timeout_ms)
                )
            )
            started_at = time.perf_counter()
            cursor.execute(prepared.sql)
            # cursor.description is None for statements that do not return rows
            columns = (
                [column.name for column in cursor.description]
                if cursor.description
                else []
            )
            # Fetch one extra row to detect (without returning) that more exist.
            fetched = cursor.fetchmany(max_rows + 1) if cursor.description else []
            duration_ms = elapsed_ms(started_at)
        truncated = len(fetched) > max_rows
        rows = json.loads(json.dumps(fetched[:max_rows], cls=ResultJSONEncoder))
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
            "duration_ms": duration_ms,
        }
    finally:
        if conn:
            conn.close()


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


def _deny_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    saved_query=None,
) -> NoReturn:
    """Record a refused query and raise, so denials are audited like any outcome."""
    _log_executed_query(
        request,
        workspace,
        query,
        origin,
        QueryLog.Status.DENIED,
        saved_query=saved_query,
    )
    raise PermissionDenied


def _execute_and_log(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    max_rows: int | None = None,
    saved_query=None,
):
    """Delegate to ``execute_database_query`` and record a ``QueryLog`` entry for
    every outcome, re-raising errors so that callers only have to translate them
    into API responses.

    Performs no permission check: every caller owns the question of who may run
    what, and they do not all answer it the same way.
    """

    def log(status, **fields):
        _log_executed_query(
            request, workspace, query, origin, status, saved_query=saved_query, **fields
        )

    max_rows_kwarg = {} if max_rows is None else {"max_rows": max_rows}
    started_at = time.perf_counter()
    try:
        result = execute_database_query(workspace, query, **max_rows_kwarg)
    except MultipleStatementsError as e:
        log(QueryLog.Status.REJECTED, error_message=str(e))
        raise
    except psycopg2.Error as e:
        # QueryCanceled (statement timeout) is a psycopg2.Error subclass and
        # needs no dedicated handling here: both outcomes log the same fields.
        log(
            QueryLog.Status.ERROR,
            result_code=e.pgcode,
            error_message=str(e).strip(),
            duration_ms=elapsed_ms(started_at),
        )
        raise
    log(
        QueryLog.Status.SUCCESS,
        result_code=QueryLog.SQLSTATE_SUCCESS,
        duration_ms=result["duration_ms"],
        row_count=result["row_count"],
        truncated=result["truncated"],
    )
    return result


def run_and_log_database_query(
    request: HttpRequest,
    workspace: Workspace,
    query: str,
    origin: str,
    max_rows: int | None = None,
):
    """Single point of entry for executing caller-supplied SQL on behalf of an API request.

    Checks the permission, then delegates to ``_execute_and_log``.
    """
    # A webapp may only run SQL the workspace already stored, never SQL of its
    # own: the GraphQL proxy validates top-level fields only, so the `workspace`
    # field that `USER_READ` grants would otherwise reach this endpoint through
    # `workspace { database { executeSQL } }` and turn the narrowest scope into
    # an unrestricted read of the workspace database.
    if getattr(request, "webapp", None) is not None:
        _deny_query(request, workspace, query, origin)
    if not request.user.has_perm("databases.run_query", workspace):
        _deny_query(request, workspace, query, origin)
    return _execute_and_log(request, workspace, query, origin, max_rows=max_rows)


def run_saved_query(request: HttpRequest, saved_query, max_rows: int | None = None):
    """Execute a stored query on behalf of an API request.

    Unlike ``run_and_log_database_query`` this is reachable from a web app: the
    SQL was written and vetted by a workspace member when the query was saved,
    not supplied by the caller, which is the whole point of the endpoint.
    """
    workspace = saved_query.workspace
    # Derived from the request rather than accepted as an argument: a client that
    # could name its own origin could disown the queries it ran.
    origin = (
        QueryLog.Origin.WEBAPP
        if getattr(request, "webapp", None) is not None
        else QueryLog.Origin.OTHER
    )
    if not request.user.has_perm("databases.run_query", workspace):
        _deny_query(
            request, workspace, saved_query.content, origin, saved_query=saved_query
        )
    return _execute_and_log(
        request,
        workspace,
        saved_query.content,
        origin,
        max_rows=max_rows,
        saved_query=saved_query,
    )


# EXPLAIN only parses and plans the query (it never executes it), so this is a
# generous ceiling that only guards against a pathological planning time.
_VALIDATE_QUERY_TIMEOUT_MS = 5_000


def validate_query(workspace: Workspace, query: str) -> None:
    """Check a query against the database without executing it.

    Runs ``EXPLAIN`` with the read-only role, which parses and plans the query,
    catching syntax errors and references to unknown tables or columns at
    near-zero cost. Raises ``MultipleStatementsError`` when more than one
    statement is submitted and ``psycopg2.Error`` when the query is invalid.

    A statement that is already an ``EXPLAIN`` is run as it stands, since
    PostgreSQL cannot nest them -- which means an ``EXPLAIN ANALYZE`` submitted
    here does run its inner query, bounded by the read-only role and the timeout.
    """
    prepared = PreparedQuery.from_text(query)
    conn = None
    try:
        conn = get_workspace_database_ro_connection(workspace)
        with conn.cursor() as cursor:
            cursor.execute(
                sql.SQL("SET LOCAL statement_timeout = {timeout};").format(
                    timeout=sql.Literal(_VALIDATE_QUERY_TIMEOUT_MS)
                )
            )
            cursor.execute(
                prepared.sql if prepared.is_explain else "EXPLAIN " + prepared.sql
            )
    finally:
        if conn:
            conn.close()


def get_database_definition(workspace: Workspace):
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                        SELECT table_name as name, pg_class.reltuples as count
                        FROM information_schema.tables
                        JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                        WHERE
                            table_schema = 'public'
                            -- Exclude child tables from inheritance hierarchies (e.g., partition children)
                            AND pg_class.oid NOT IN (SELECT inhrelid FROM pg_inherits)
                        ORDER BY table_name;
                """
            )

            response: List[Tuple[str, str, int]] = cursor.fetchall()
            tables: Dict[str, Dict] = {
                x["name"]: x for x in response if x["name"] not in IGNORE_TABLES
            }

            result = []
            for name, data in tables.items():
                data["count"] = get_row_count(cursor, name, data["count"])
                result.append({"workspace": workspace, **data})
            return result
    finally:
        if conn:
            conn.close()


# Filtering, ordering and slicing happen in SQL, and row counts are only
# computed for the tables of the requested page, so that listing tables stays
# cheap on workspaces with many (potentially large) tables.
_TABLES_FROM_CLAUSE = """
    FROM information_schema.tables
    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
    JOIN pg_namespace ON pg_class.relnamespace = pg_namespace.oid
        AND pg_namespace.nspname = information_schema.tables.table_schema
    WHERE
        table_schema = 'public'
        -- Exclude child tables from inheritance hierarchies (e.g., partition children)
        AND pg_class.oid NOT IN (SELECT inhrelid FROM pg_inherits)
        AND table_name <> ALL(%(ignore_tables)s)
"""


def _fetch_tables(cursor, workspace: Workspace, params: dict) -> List[Dict]:
    """Return the page of tables (name + raw ``reltuples`` estimate), without columns."""
    cursor.execute(
        "SELECT table_name AS name, pg_class.reltuples AS count"
        + _TABLES_FROM_CLAUSE
        + "ORDER BY table_name LIMIT %(limit)s OFFSET %(offset)s",
        params,
    )
    return [
        {"workspace": workspace, "name": row["name"], "count": row["count"]}
        for row in cursor.fetchall()
    ]


def _fetch_tables_with_columns(
    cursor, workspace: Workspace, params: dict
) -> List[Dict]:
    """Return the page of tables together with their columns in a single query.

    A LEFT JOIN on ``information_schema.columns`` fetches every column of every
    table on the page in one round trip (no per-table N+1) while still keeping
    columnless tables. Rows arrive grouped by table thanks to the ORDER BY.
    """
    cursor.execute(
        "WITH paged AS ("
        "SELECT table_name AS name, pg_class.reltuples AS count"
        + _TABLES_FROM_CLAUSE
        + "ORDER BY table_name LIMIT %(limit)s OFFSET %(offset)s"
        ") "
        "SELECT paged.name, paged.count, c.column_name, c.data_type "
        "FROM paged "
        "LEFT JOIN information_schema.columns AS c "
        "ON c.table_name = paged.name AND c.table_schema = 'public' "
        "ORDER BY paged.name, c.ordinal_position",
        params,
    )
    tables: Dict[str, Dict] = {}
    for row in cursor.fetchall():
        table = tables.get(row["name"])
        if table is None:
            table = {
                "workspace": workspace,
                "name": row["name"],
                "count": row["count"],
                "columns": [],
            }
            tables[row["name"]] = table
        if row["column_name"] is not None:
            table["columns"].append(
                {"name": row["column_name"], "type": row["data_type"]}
            )
    return list(tables.values())


def get_database_definition_page(
    workspace: Workspace,
    page: int = 1,
    per_page: int = 15,
    with_columns: bool = False,
    with_counts: bool = True,
):
    # Clamp caller-provided values: a GraphQL client can send any Int (or an
    # explicit null), and negative/zero values would end up in LIMIT/OFFSET.
    page = max(page or 1, 1)
    per_page = min(max(per_page or 1, 1), settings.GRAPHQL_MAX_PAGE_SIZE)
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS total" + _TABLES_FROM_CLAUSE,
                {"ignore_tables": IGNORE_TABLES},
            )
            total_items = cursor.fetchone()["total"]

            params = {
                "ignore_tables": IGNORE_TABLES,
                "limit": per_page,
                "offset": (page - 1) * per_page,
            }
            items = (
                _fetch_tables_with_columns(cursor, workspace, params)
                if with_columns
                else _fetch_tables(cursor, workspace, params)
            )

            # Row counts are computed separately (and skipped when not requested)
            # because they can trigger an expensive COUNT(*) per table.
            for item in items:
                item["count"] = (
                    get_row_count(cursor, item["name"], item["count"])
                    if with_counts
                    else None
                )
        return {
            "page_number": page,
            "total_pages": max(math.ceil(total_items / per_page), 1),
            "total_items": total_items,
            "items": items,
        }
    finally:
        if conn:
            conn.close()


def get_full_database_definition(workspace: Workspace) -> List[Dict]:
    """Return every table with its columns, without row counts.

    Used to inline the whole database schema into LLM agent instructions:
    row counts would trigger a potentially expensive COUNT(*) per table on
    every conversation turn, and the consumer needs all tables at once, so
    pagination does not apply.
    """
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # LIMIT NULL means "no limit" in PostgreSQL, which lets us reuse
            # the paginated query to fetch the full listing.
            params = {"ignore_tables": IGNORE_TABLES, "limit": None, "offset": 0}
            tables = _fetch_tables_with_columns(cursor, workspace, params)
        # The shared query also carries a reltuples-based ``count`` and the
        # workspace, but only names and columns are inlined into the LLM schema,
        # so keep just those (no COUNT(*) is ever run here).
        return [
            {"name": table["name"], "columns": table["columns"]} for table in tables
        ]
    finally:
        if conn:
            conn.close()


def get_table_definition(workspace: Workspace, table_name: str):
    columns = []
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                    SELECT column_name AS name, data_type AS type FROM information_schema.columns WHERE table_name = (%s);
                """,
                (table_name,),
            )

            columns = cursor.fetchall()

            if not columns:
                return None

            cursor.execute(
                """
                    SELECT pg_class.reltuples AS row_count
                    FROM information_schema.tables
                    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                    WHERE table_schema = 'public'
                    AND table_name=(%s);
                """,
                (table_name,),
            )
            res = cursor.fetchone()
            row_count = get_row_count(cursor, table_name, res["row_count"])
        return {
            "name": table_name,
            "columns": columns,
            "count": row_count,
            "workspace": workspace,
        }
    finally:
        if conn:
            conn.close()


def get_table_sample_data(workspace: Workspace, table_name: str, n_rows: int = 4):
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM {table} LIMIT %s;").format(
                    table=sql.Identifier(table_name),
                ),
                (n_rows,),
            )

            data = cursor.fetchall()
        return data
    finally:
        if conn:
            conn.close()


def delete_table(workspace: Workspace, table_name: str):
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                sql.SQL("DROP TABLE {table};").format(table=sql.Identifier(table_name)),
            )
    except UndefinedTable:
        raise TableNotFound
    finally:
        if conn:
            conn.close()


@dataclass
class TableRowsPage:
    has_previous: bool
    has_next: bool
    page: int
    items: list


def get_table_rows(
    workspace: Workspace,
    table_name: str,
    order_by: str,
    direction: OrderByDirectionEnum,
    page: int,
    per_page: int,
):
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if direction == OrderByDirectionEnum.ASC:
                sql_select = (
                    "SELECT * FROM {table} ORDER BY {order_by} ASC LIMIT %s OFFSET %s;"
                )
            else:
                sql_select = (
                    "SELECT * FROM {table} ORDER BY {order_by} DESC LIMIT %s OFFSET %s;"
                )
            cursor.execute(
                sql.SQL(sql_select).format(
                    table=sql.Identifier(table_name),
                    order_by=sql.Identifier(order_by),
                ),
                (per_page + 1, (page - 1) * per_page),
            )

            data = cursor.fetchall()

        return TableRowsPage(
            page=page,
            has_previous=page > 1,
            has_next=len(data) > per_page,
            items=data[:per_page],
        )
    finally:
        if conn:
            conn.close()
