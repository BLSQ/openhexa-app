from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.databases.api import create_database, delete_database
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


def provision_workspace_database(test_case, workspace):
    """Create the real Postgres database backing `workspace`, dropped on cleanup.

    Test workspaces get their provisioning mocked out (see
    hexa.workspaces.tests.testutils.create_workspace), so this is how a test that
    actually queries the workspace database gets a real one. The DROP goes in
    before the CREATE runs: CREATE DATABASE cannot be rolled back, and
    create_database fails in the middle often enough (a role that already exists,
    say) that registering afterwards would let those attempts leak.

    Pass the class from setUpTestData, the instance from setUp or a test method.
    """
    add_cleanup = (
        test_case.addClassCleanup
        if isinstance(test_case, type)
        else test_case.addCleanup
    )
    add_cleanup(delete_database, workspace.db_name)
    create_database(workspace.db_name, workspace.db_password, workspace.db_ro_password)
