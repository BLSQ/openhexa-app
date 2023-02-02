from typing import Dict, List, Tuple

import psycopg2
from psycopg2 import sql

from hexa.plugins.connector_postgresql.models import Database


def get_database_tables_summary(database: Database, table=None, limit_per_table=4):
    tables_summary = []
    IGNORE_TABLES = ["geography_columns", "geometry_columns", "spatial_ref_sys"]
    with psycopg2.connect(database.url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            if table is not None:
                cursor.execute(
                    """
                        SELECT table_name, pg_class.reltuples as row_count
                        FROM information_schema.tables
                        JOIN pg_class ON information_schema.tables.table_name = pg_class.relname
                        WHERE table_schema = 'public'
                        AND table_name=(%s);
                    """,
                    (table,),
                )

            else:
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
                cursor.execute(
                    sql.SQL("SELECT * FROM {table} LIMIT %s;").format(
                        table=sql.Identifier(data["table_name"]),
                    ),
                    (limit_per_table,),
                )
                sample_data = cursor.fetchall()

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
                        "total_count": row_count,
                        "sample": sample_data,
                        "database": database,
                    }
                )

    return tables_summary


def get_table_summary(database: Database, table):
    with psycopg2.connect(database.url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(
                """
                        SELECT column_name, data_type FROM information_schema.columns WHERE table_name = (%s);
                    """,
                (table,),
            )

            response: List[Tuple[str, str]] = cursor.fetchall()
            columns: List[Dict[str, str]] = [
                {"name": x[0], "type": x[1]} for x in response
            ]

    return columns
