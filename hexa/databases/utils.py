import enum
from dataclasses import dataclass
from typing import Dict, List, Tuple

import psycopg2
from psycopg2 import sql
from psycopg2.errors import UndefinedTable
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.workspaces.models import Workspace

from .api import get_db_server_credentials

IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]


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


def get_database_definition(workspace: Workspace):
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                        SELECT table_name as name, pg_class.reltuples as count
                        FROM information_schema.tables
                        JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                        WHERE
                            table_schema = 'public'
                        ORDER BY table_name;
                """
            )

            response: List[Tuple[str, str, int]] = cursor.fetchall()
            tables: Dict[str, Dict] = {
                x["name"]: x for x in response if x["name"] not in IGNORE_TABLES
            }

            result = []
            for name, data in tables.items():
                # For the sake of performance we only run SELECT COUNT(*) for relatively small tables N_row < 10000 entries)
                # due to the fact PostgreSQL will need to scan either the entire table or the entirety of an index which includes all rows in the table.
                if data["count"] < 10_000:
                    cursor.execute(
                        sql.SQL("SELECT COUNT(*) as row_count FROM {};").format(
                            sql.Identifier(name)
                        ),
                    )
                    response = cursor.fetchone()
                    tables[name]["count"] = response["row_count"]

                result.append({"workspace": workspace, **data})
            return result
    finally:
        if conn:
            conn.close()


def get_table_definition(workspace: Workspace, table_name: str):
    columns = []
    conn = None
    try:
        conn = get_workspace_database_connection(workspace)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
            row_count = res["row_count"]
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
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
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
