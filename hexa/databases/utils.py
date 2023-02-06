from typing import Dict, List, Tuple

import psycopg2
from psycopg2 import sql

from hexa.core.graphql import result_page
from hexa.workspaces.models import Workspace


def format_sample_data(columns, samples):
    res = []
    for sample in samples:
        res.append(
            [{"name": columns[j], "value": sample[j]} for j in range(len(sample))]
        )
    return res


def get_database_definition(
    workspace: Workspace, limit_per_table=4, page=1, per_page=10
):
    tables_summary = []
    IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]

    with psycopg2.connect(workspace.database.url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                """
                    SELECT table_name, pg_class.reltuples as row_count
                    FROM information_schema.tables
                    JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """
            )
            response: List[Tuple[str, str, int]] = cursor.fetchall()
            tables: Dict[str, Dict] = {
                x[0]: x for x in response if x[0] not in IGNORE_TABLES
            }

            for name, data in tables.items():
                row_count = data["row_count"]

                if data["row_count"] < 10_000:
                    cursor.execute(
                        sql.SQL("SELECT COUNT(*) as row_count FROM {};").format(
                            sql.Identifier(data["table_name"])
                        ),
                    )
                    response = cursor.fetchone()
                    row_count = response["row_count"]

                tables_summary.append(
                    {
                        "name": name,
                        "count": row_count,
                        "sample": get_table_data(
                            workspace, data["table_name"], limit_per_table
                        ),
                    }
                )

    return result_page(queryset=tables_summary, page=page, per_page=per_page)


def get_table_definition(workspace: Workspace, table):
    url = workspace.database.url
    row_count = 0
    columns = []
    with psycopg2.connect(url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                """
                    SELECT column_name, data_type FROM information_schema.columns WHERE table_name = (%s);
                """,
                (table,),
            )

            response: List[Tuple[str, str]] = cursor.fetchall()
            if not response:
                return None

            columns: List[Dict[str, str]] = [
                {"name": x[0], "type": x[1]} for x in response
            ]
            cursor.execute(
                sql.SQL("SELECT COUNT(*) as row_count FROM {};").format(
                    sql.Identifier(table)
                ),
            )
            response = cursor.fetchone()
            row_count = response["row_count"]

    return {"name": table, "columns": columns, "count": row_count}


def get_table_data(workspace: Workspace, table_name: str, rows: int = 4):
    with psycopg2.connect(workspace.database.url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                sql.SQL("SELECT * FROM {table} LIMIT %s;").format(
                    table=sql.Identifier(table_name),
                ),
                (rows,),
            )

            samples: List[Tuple[str, str, int]] = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]
    return format_sample_data(colnames, samples)
