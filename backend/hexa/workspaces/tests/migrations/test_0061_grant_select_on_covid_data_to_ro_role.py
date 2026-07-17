from django.test import TransactionTestCase
from psycopg2 import sql
from psycopg2.errors import (
    InsufficientPrivilege,  # type: ignore[import-not-found] # psycopg2.errors is not in typeshed yet
)
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from hexa.core.test.migrator import Migrator
from hexa.databases.api import delete_database
from hexa.databases.tests.helpers import seed_demo_table
from hexa.databases.utils import (
    get_workspace_database_connection,
    get_workspace_database_ro_connection,
)
from hexa.files import storage
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


class Migration0061Test(TransactionTestCase):
    migrate_from = ("workspaces", "0060_grant_create_on_public_to_rw_role")
    migrate_to = ("workspaces", "0061_grant_select_on_covid_data_to_ro_role")

    def setUp(self):
        storage.reset()
        self.migrator = Migrator()
        self.migrator.migrate(*self.migrate_from)

        self.user = User.objects.create_user(
            "migration-test@example.com", "password", is_superuser=True
        )
        self.workspace = Workspace.objects.create_if_has_perm(
            self.user, name="Covid WS", description=""
        )
        seed_demo_table(self.workspace, [(1, "Kinshasa")], table_name="covid_data")
        conn = get_workspace_database_connection(self.workspace)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("REVOKE SELECT ON covid_data FROM {role};").format(
                    role=sql.Identifier(self.workspace.db_ro_username)
                )
            )
        conn.close()

    def tearDown(self):
        delete_database(self.workspace.db_name)

    def _count_covid_data_as_ro(self):
        conn = get_workspace_database_ro_connection(self.workspace)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM covid_data;")
                return cur.fetchone()[0]
        finally:
            conn.close()

    def test_migration_grants_ro_role_select_on_covid_data(self):
        with self.assertRaises(InsufficientPrivilege):
            self._count_covid_data_as_ro()

        self.migrator.migrate(*self.migrate_to)

        self.assertEqual(self._count_covid_data_as_ro(), 1)
