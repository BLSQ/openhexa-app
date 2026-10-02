from unittest.mock import patch

import psycopg2
from django.conf import settings
from psycopg2.errors import (
    InsufficientPrivilege,  # type: ignore[import-not-found] # psycopg2.errors is not in typeshed yet
    ObjectInUse,  # type: ignore[import-not-found]
)

from hexa.core.test import TestCase
from hexa.databases.api import (
    DatabaseInUse,
    DatabaseNotEmpty,
    database_has_tables,
    get_cursor,
    get_db_server_credentials,
    replace_empty_database_with_copy,
)
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import (
    get_workspace_database_connection,
    get_workspace_database_ro_connection,
)
from hexa.user_management.models import User
from hexa.workspaces.tests.testutils import create_workspace


class ReplaceEmptyDatabaseWithCopyTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            "replace@bluesquarehub.com", "password", is_superuser=True
        )
        self.source = create_workspace(user, name="Source", provision_db_on=self)
        self.target = create_workspace(user, name="Target", provision_db_on=self)
        seed_demo_table(
            self.source, [(1, "copied from source")], table_name="source_table"
        )

    def _fetch(self, conn, query):
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    def assertNoStagingDatabase(self):
        with get_cursor(settings.WORKSPACES_DATABASE_DEFAULT_DB) as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s;",
                [f"{self.target.db_name}_copy"],
            )
            self.assertIsNone(cursor.fetchone())

    def assertTargetUntouched(self):
        self.assertEqual(
            self._fetch(
                get_workspace_database_connection(self.target),
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public';",
            ),
            [("spatial_ref_sys",)],
        )
        self.assertNoStagingDatabase()

    def test_copies_data(self):
        replace_empty_database_with_copy(self.source.db_name, self.target.db_name)

        self.assertEqual(
            self._fetch(
                get_workspace_database_connection(self.target),
                "SELECT id, label FROM source_table;",
            ),
            [(1, "copied from source")],
        )
        self.assertNoStagingDatabase()

    def test_target_roles_own_the_copy(self):
        replace_empty_database_with_copy(self.source.db_name, self.target.db_name)

        conn = get_workspace_database_connection(self.target)
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE source_table ADD COLUMN extra int;")
            cursor.execute("CREATE TABLE created_after_copy (id int);")
        conn.close()

        self.assertEqual(
            self._fetch(
                get_workspace_database_ro_connection(self.target),
                "SELECT (SELECT count(*) FROM source_table), (SELECT count(*) FROM created_after_copy);",
            ),
            [(1, 0)],
        )
        ro_conn = get_workspace_database_ro_connection(self.target)
        with self.assertRaises(InsufficientPrivilege):
            self._fetch(
                ro_conn, "INSERT INTO source_table (id) VALUES (2) RETURNING id;"
            )

    def test_source_is_left_intact(self):
        replace_empty_database_with_copy(self.source.db_name, self.target.db_name)

        self.assertEqual(
            self._fetch(
                get_workspace_database_ro_connection(self.source),
                "SELECT id FROM source_table;",
            ),
            [(1,)],
        )

    def test_copy_carries_workspace_database_settings(self):
        replace_empty_database_with_copy(self.source.db_name, self.target.db_name)

        with get_cursor(settings.WORKSPACES_DATABASE_DEFAULT_DB) as cursor:
            cursor.execute(
                "SELECT datconnlimit, has_database_privilege('public', datname, 'CONNECT') "
                "FROM pg_database WHERE datname = %s;",
                [self.target.db_name],
            )
            self.assertEqual(cursor.fetchone(), (50, False))

    def test_refuses_target_with_data(self):
        seed_demo_table(
            self.target, [(42, "already in target")], table_name="target_table"
        )

        with self.assertRaises(DatabaseNotEmpty):
            replace_empty_database_with_copy(self.source.db_name, self.target.db_name)

        self.assertNoStagingDatabase()
        self.assertEqual(
            self._fetch(
                get_workspace_database_connection(self.target),
                "SELECT id FROM target_table;",
            ),
            [(42,)],
        )

    def test_refuses_target_that_got_data_during_the_copy(self):
        with patch("hexa.databases.api.database_has_tables", side_effect=[False, True]):
            with self.assertRaises(DatabaseNotEmpty):
                replace_empty_database_with_copy(
                    self.source.db_name, self.target.db_name
                )

        self.assertTargetUntouched()

    def test_fails_early_when_source_has_open_connections(self):
        credentials = get_db_server_credentials()
        open_conn = psycopg2.connect(
            host=credentials["host"],
            port=credentials["port"],
            dbname=self.source.db_name,
            user=self.source.db_name,
            password=self.source.db_password,
            application_name="jupyter",
        )
        try:
            with self.assertRaises(DatabaseInUse) as ctx:
                replace_empty_database_with_copy(
                    self.source.db_name, self.target.db_name
                )
        finally:
            open_conn.close()

        self.assertIn(
            f"'{self.source.db_name}' has 1 open connection", str(ctx.exception)
        )
        self.assertTargetUntouched()

    def test_target_in_use_is_left_untouched(self):
        open_conn = get_workspace_database_connection(self.target)
        try:
            with self.assertRaises(ObjectInUse):
                replace_empty_database_with_copy(
                    self.source.db_name, self.target.db_name
                )
        finally:
            open_conn.close()

        self.assertTargetUntouched()


class DatabaseHasTablesTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            "objects@bluesquarehub.com", "password", is_superuser=True
        )
        self.workspace = create_workspace(user, provision_db_on=self)

    def test_fresh_database_is_empty(self):
        self.assertFalse(database_has_tables(self.workspace.db_name))

    def test_table_counts(self):
        seed_demo_table(self.workspace, [(1, "a")])

        self.assertTrue(database_has_tables(self.workspace.db_name))

    def test_view_in_another_schema_counts(self):
        conn = get_workspace_database_connection(self.workspace)
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("CREATE SCHEMA reporting;")
            cursor.execute("CREATE VIEW reporting.v AS SELECT 1 AS one;")
        conn.close()

        self.assertTrue(database_has_tables(self.workspace.db_name))
