from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.databases.utils import get_workspace_database_connection


def seed_demo_table(workspace, rows, table_name="demo"):
    """Create a demo table on the workspace database using the read-write role."""
    conn = get_workspace_database_connection(workspace)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    table = sql.Identifier(table_name)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {};").format(table))
            cursor.execute(
                sql.SQL("CREATE TABLE {} (id int, label text);").format(table)
            )
            cursor.executemany(
                sql.SQL("INSERT INTO {} (id, label) VALUES (%s, %s);").format(table),
                rows,
            )
    finally:
        conn.close()
