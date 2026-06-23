from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.databases.utils import get_workspace_database_connection


def seed_demo_table(workspace, rows):
    """Create a `demo` table on the workspace database using the read-write role."""
    conn = get_workspace_database_connection(workspace)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS demo;")
            cursor.execute("CREATE TABLE demo (id int, label text);")
            cursor.executemany("INSERT INTO demo (id, label) VALUES (%s, %s);", rows)
    finally:
        conn.close()
