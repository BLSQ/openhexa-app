import psycopg2
from psycopg2 import sql

from hexa.workspaces.models import Workspace

from .api import get_database_connection


def get_database_definition(workspace: Workspace):
    conn = None
    try:
        conn = get_database_connection(workspace.db_name)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                        SELECT table_name as name, pg_class.reltuples as count
                        FROM information_schema.tables
                        JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                        WHERE
                            table_schema = 'public' AND
                            table_name NOT IN ('geography_columns', 'geometry_columns', 'spatial_ref_sys')
                        ORDER BY table_name;
                """
            )
            tables = []
            for row in cursor.fetchall():
                tables.append({"workspace": workspace, **row})
        return tables
    finally:
        if conn:
            conn.close()


def get_table_definition(workspace: Workspace, table_name: str):
    columns = []
    conn = None
    try:
        conn = get_database_connection(workspace.db_name)
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
        conn = get_database_connection(workspace.db_name)
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
