from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.databases.api import get_database_connection
from hexa.databases.utils import get_workspace_database_connection


def seed_demo_table(workspace, rows, table_name="demo"):
    """Create a demo table with the read-write role.

    The read-only role is auto-granted SELECT on it via ALTER DEFAULT PRIVILEGES.
    """
    _seed_table(get_workspace_database_connection(workspace), rows, table_name)


def seed_demo_table_as_admin(workspace, rows, table_name="demo"):
    """Create a demo table with the admin role.

    The read-only role has no SELECT grant on it, reproducing tables like the
    tutorial ``covid_data``.
    """
    _seed_table(get_database_connection(workspace.db_name), rows, table_name)


def _seed_table(conn, rows, table_name):
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
